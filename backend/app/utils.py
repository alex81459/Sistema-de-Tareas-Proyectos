from functools import wraps
from flask import abort, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta
from app.models.registro_actividad import RegistroActividad
from app import db
from datetime import datetime, timezone


def obtener_uid() -> int:
    #obtener ID del usuario actual como entero
    return int(get_jwt_identity())


def admin_requerido(fn):
    #exige rol='admin' en el JWT del usuario actual
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from app.models.usuario import Usuario
        uid = obtener_uid()
        usuario = Usuario.query.get(uid)
        if not usuario or usuario.rol != 'admin':
            return jsonify({"error": "Acceso denegado: se requiere rol de administrador"}), 403
        return fn(*args, **kwargs)
    return wrapper


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
    #verifica que el proyecto pertenezca al usuario
    proyecto = Proyecto.query.get(proyecto_id)
    if not proyecto or proyecto.usuario_id != usuario_id:
        abort(404, description="Proyecto no encontrado")
    return proyecto


def verificar_propiedad_tarea(tarea_id: int, usuario_id: int) -> Tarea:
    #verifica que la tarea pertenezca al usuario vía proyecto
    tarea = Tarea.query.get(tarea_id)
    if not tarea:
        abort(404, description="Tarea no encontrada")
    proyecto = Proyecto.query.get(tarea.proyecto_id)
    if not proyecto or proyecto.usuario_id != usuario_id:
        abort(404, description="Tarea no encontrada")
    return tarea


def verificar_propiedad_etiqueta(etiqueta_id: int, usuario_id: int) -> Etiqueta:
    #verifica que la etiqueta pertenezca al usuario
    etiqueta = Etiqueta.query.get(etiqueta_id)
    if not etiqueta or etiqueta.usuario_id != usuario_id:
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
