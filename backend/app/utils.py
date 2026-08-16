from functools import wraps
import re
from flask import abort, jsonify, request as flask_request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.proyecto import Proyecto
from app.models.miembro_proyecto import MiembroProyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta
from app.models.usuario import Usuario
from app.models.registro_actividad import RegistroActividad
from app.models.log_auditoria import LogAuditoria
from app.models.mencion_comentario import MencionComentario
from app import db
from datetime import datetime, timezone

NIVELES_PERMISO_PROYECTO = {
    "lectura": 1,
    "edicion": 2,
    "administracion": 3,
}

PATRON_MENCION_COMENTARIO = re.compile(r"@\[([^\]]+)\]")


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


def obtener_membresia_proyecto(proyecto_id: int, usuario_id: int):
    return MiembroProyecto.query.filter_by(proyecto_id=proyecto_id, usuario_id=usuario_id).first()


def obtener_permiso_en_proyecto(proyecto: Proyecto, usuario) -> str | None:
    if not proyecto or not usuario:
        return None
    if usuario.puede_ver_todo:
        return "administracion"
    if proyecto.usuario_id == usuario.id:
        return "administracion"
    membresia = obtener_membresia_proyecto(proyecto.id, usuario.id)
    return membresia.permiso if membresia else None


def obtener_participantes_proyecto(proyecto: Proyecto):
    participantes = {}

    propietario = Usuario.query.get(proyecto.usuario_id)
    if propietario and propietario.esta_activo:
        participantes[propietario.id] = propietario

    for miembro in proyecto.miembros.all():
        if miembro.usuario and miembro.usuario.esta_activo:
            participantes[miembro.usuario.id] = miembro.usuario

    return list(participantes.values())


def validar_usuario_asignado_en_proyecto(proyecto: Proyecto, asignado_a_usuario_id):
    if asignado_a_usuario_id is None:
        return None

    usuario = Usuario.query.get(asignado_a_usuario_id)
    if not usuario or not usuario.esta_activo:
        abort(400, description="El usuario asignado no existe o está inactivo")

    participantes = {participante.id for participante in obtener_participantes_proyecto(proyecto)}
    if asignado_a_usuario_id not in participantes:
        abort(400, description="Solo puedes asignar tareas a participantes del proyecto")

    return usuario


def extraer_correos_mencionados(contenido: str):
    return [correo.strip().lower() for correo in PATRON_MENCION_COMENTARIO.findall(contenido or "")]


def crear_menciones_comentario(comentario_id: int, proyecto: Proyecto, contenido: str):
    correos_mencionados = extraer_correos_mencionados(contenido)
    if not correos_mencionados:
        return []

    participantes = {
        participante.correo.lower(): participante
        for participante in obtener_participantes_proyecto(proyecto)
    }

    menciones_creadas = []
    correos_vistos = set()
    for correo in correos_mencionados:
        if correo in correos_vistos:
            continue
        correos_vistos.add(correo)

        usuario = participantes.get(correo)
        if not usuario:
            abort(400, description=f"La mención @{correo} no pertenece a un participante del proyecto")

        mencion = MencionComentario(
            comentario_id=comentario_id,
            usuario_id=usuario.id,
        )
        db.session.add(mencion)
        menciones_creadas.append(usuario)

    return menciones_creadas


def enriquecer_proyecto_con_acceso(proyecto: Proyecto, usuario):
    permiso = obtener_permiso_en_proyecto(proyecto, usuario)
    proyecto.permiso_actual = permiso
    proyecto.es_propietario_actual = bool(usuario and proyecto.usuario_id == usuario.id)
    proyecto.puede_administrar_actual = permiso == "administracion"
    return proyecto


def ids_proyectos_accesibles(usuario_id: int):
    from app.models.usuario import Usuario
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return []
    if usuario.puede_ver_todo:
        return [fila.id for fila in db.session.query(Proyecto.id).all()]

    propios = {
        fila.id for fila in db.session.query(Proyecto.id).filter_by(usuario_id=usuario_id).all()
    }
    compartidos = {
        fila.proyecto_id
        for fila in db.session.query(MiembroProyecto.proyecto_id).filter_by(usuario_id=usuario_id).all()
    }
    return list(propios | compartidos)


def verificar_acceso_proyecto(proyecto_id: int, usuario_id: int, permiso_requerido: str = "lectura") -> Proyecto:
    """Verifica que el usuario pueda acceder al proyecto con el permiso solicitado."""
    from app.models.usuario import Usuario
    proyecto = Proyecto.query.get(proyecto_id)
    if not proyecto:
        abort(404, description="Proyecto no encontrado")
    usuario = Usuario.query.get(usuario_id)
    permiso_actual = obtener_permiso_en_proyecto(proyecto, usuario)
    if not permiso_actual:
        abort(404, description="Proyecto no encontrado")
    if NIVELES_PERMISO_PROYECTO[permiso_actual] < NIVELES_PERMISO_PROYECTO[permiso_requerido]:
        abort(403, description="Acceso denegado: permisos insuficientes")
    return enriquecer_proyecto_con_acceso(proyecto, usuario)


def verificar_propiedad_proyecto(proyecto_id: int, usuario_id: int) -> Proyecto:
    return verificar_acceso_proyecto(proyecto_id, usuario_id, "lectura")


def verificar_propiedad_tarea(tarea_id: int, usuario_id: int, permiso_requerido: str = "lectura") -> Tarea:
    #verifica sea admin o jefe acceden a cualquiera, restringuidos a sus tareas
    from app.models.usuario import Usuario
    tarea = Tarea.query.get(tarea_id)
    if not tarea:
        abort(404, description="Tarea no encontrada")
    usuario = Usuario.query.get(usuario_id)
    if usuario and usuario.puede_ver_todo:
        return tarea
    proyecto = verificar_acceso_proyecto(tarea.proyecto_id, usuario_id, permiso_requerido)
    if not proyecto:
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
