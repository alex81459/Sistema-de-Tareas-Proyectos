from functools import wraps
from flask import abort, jsonify, request as flask_request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta
from app.models.registro_actividad import RegistroActividad
from app.models.log_auditoria import LogAuditoria
from app import db
from datetime import datetime, timezone


def obtener_uid() -> int:
    #obtener ID del usuario actual como entero
    return int(get_jwt_identity())


def obtener_usuario_actual():
    #obtiene la instancia completa del usuario que incio sesion
    from app.models.usuario import Usuario
    return Usuario.query.get(obtener_uid())


def rol_requerido(*roles_permitidos):
    #exige que el usuario tenga uno de los roles asignados
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            from app.models.usuario import Usuario
            uid = obtener_uid()
            usuario = Usuario.query.get(uid)
            if not usuario or usuario.rol not in roles_permitidos:
                return jsonify({"error": "Acceso denegado: permisos insuficientes"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_requerido(fn):
    #pide permiso de admin
    return rol_requerido("administrador")(fn)


def escritura_requerida(fn):
    #bloquea acceso de escritura al rol visualizador
    return rol_requerido("administrador", "jefe", "usuario")(fn)


def paginar(query, pagina: int = 1, tamano_pagina: int = 20):
    #pagina una query de SQLAlchemy y retorna dict con metadatos
    tamano_pagina = min(max(tamano_pagina, 1), 100)
    pagina = max(pagina, 1)
    paginacion = query.paginate(page=pagina, per_page=tamano_pagina, error_out=False)
    return {
        "elementos": paginacion.items,
        "pagina": paginacion.page,
        "tamano_pagina": paginacion.per_page,
        "total": paginacion.total,
        "paginas": paginacion.pages,
    }


def verificar_propiedad_proyecto(proyecto_id: int, usuario_id: int) -> Proyecto:
    """Verifica que el proyecto exista. Admin/Jefe acceden a cualquiera; el resto solo a los suyos."""
    from app.models.usuario import Usuario
    proyecto = Proyecto.query.get(proyecto_id)
    if not proyecto:
        abort(404, description="Proyecto no encontrado")
    usuario = Usuario.query.get(usuario_id)
    if usuario and usuario.puede_ver_todo:
        return proyecto
    if proyecto.usuario_id != usuario_id:
        abort(404, description="Proyecto no encontrado")
    return proyecto


def verificar_propiedad_tarea(tarea_id: int, usuario_id: int) -> Tarea:
    #verifica sea admin o jefe acceden a cualquiera, restringuidos a sus tareas
    from app.models.usuario import Usuario
    tarea = Tarea.query.get(tarea_id)
    if not tarea:
        abort(404, description="Tarea no encontrada")
    usuario = Usuario.query.get(usuario_id)
    if usuario and usuario.puede_ver_todo:
        return tarea
    proyecto = Proyecto.query.get(tarea.proyecto_id)
    if not proyecto or proyecto.usuario_id != usuario_id:
        abort(404, description="Tarea no encontrada")
    return tarea


def verificar_propiedad_etiqueta(etiqueta_id: int, usuario_id: int) -> Etiqueta:
    #verifica sea admin o jefe acceden a cualquiera, restringidos a sus etiquetas
    from app.models.usuario import Usuario
    etiqueta = Etiqueta.query.get(etiqueta_id)
    if not etiqueta:
        abort(404, description="Etiqueta no encontrada")
    usuario = Usuario.query.get(usuario_id)
    if usuario and usuario.puede_ver_todo:
        return etiqueta
    if etiqueta.usuario_id != usuario_id:
        abort(404, description="Etiqueta no encontrada")
    return etiqueta


def registrar_actividad(tarea_id: int, usuario_id: int, accion: str,
                        valor_anterior: str = None, valor_nuevo: str = None):
    #crea entrada de auditoría para una tarea
    registro = RegistroActividad(
        tarea_id=tarea_id,
        usuario_id=usuario_id,
        accion=accion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
    )
    db.session.add(registro)


def registrar_log(categoria: str, accion: str, detalle: str = None,
                  entidad_tipo: str = None, entidad_id: int = None,
                  usuario_id: int = None, usuario_correo: str = None):
    #registra un evento en el log de auditoria de seguridad
    #si no se pasan datos de usuario intentar obtenerlos del JWT
    if usuario_id is None:
        try:
            verify_jwt_in_request(optional=True)
            uid = get_jwt_identity()
            if uid:
                usuario_id = int(uid)
                from app.models.usuario import Usuario
                u = Usuario.query.get(usuario_id)
                if u:
                    usuario_correo = u.correo
        except Exception:
            pass

    if not usuario_correo:
        usuario_correo = "sistema"

    ip = None
    agente = None
    try:
        ip = flask_request.remote_addr
        agente = flask_request.headers.get("User-Agent", "")[:500]
    except RuntimeError:
        pass

    log = LogAuditoria(
        usuario_id=usuario_id,
        usuario_correo=usuario_correo,
        categoria=categoria,
        accion=accion,
        detalle=detalle,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        direccion_ip=ip,
        agente_usuario=agente,
    )
    db.session.add(log)
