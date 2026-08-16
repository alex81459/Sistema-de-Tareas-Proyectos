from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.proyecto import Proyecto
from app.models.miembro_proyecto import MiembroProyecto
from app.models.usuario import Usuario
from app.schemas import (
    ProyectoSchema, ProyectoCrearSchema, ProyectoActualizarSchema,
    MiembroProyectoSchema, MiembroProyectoCrearSchema, MiembroProyectoActualizarSchema,
)
from app.utils import (
    paginar, verificar_propiedad_proyecto, verificar_acceso_proyecto,
    obtener_uid, obtener_usuario_actual, escritura_requerida, registrar_log,
    ids_proyectos_accesibles, enriquecer_proyecto_con_acceso,
)

proyectos_bp = Blueprint("proyectos", __name__)
proyecto_schema = ProyectoSchema()
proyectos_schema = ProyectoSchema(many=True)
crear_schema = ProyectoCrearSchema()
actualizar_schema = ProyectoActualizarSchema()
miembro_schema = MiembroProyectoSchema()
miembros_schema = MiembroProyectoSchema(many=True)
crear_miembro_schema = MiembroProyectoCrearSchema()
actualizar_miembro_schema = MiembroProyectoActualizarSchema()


@proyectos_bp.route("", methods=["GET"])
@jwt_required()
def listar_proyectos():
    uid = obtener_uid()
    usuario = obtener_usuario_actual()
    if usuario.puede_ver_todo:
        query = Proyecto.query
    else:
        proyectos_ids = ids_proyectos_accesibles(uid)
        query = Proyecto.query.filter(Proyecto.id.in_(proyectos_ids)) if proyectos_ids else Proyecto.query.filter(db.false())

    # Filtro por estado
    estado = request.args.get("estado")
    if estado in ("activo", "archivado"):
        query = query.filter_by(estado=estado)

    # Búsqueda por nombre
    buscar = request.args.get("buscar", "").strip()
    if buscar:
        query = query.filter(Proyecto.nombre.ilike(f"%{buscar}%"))

    query = query.order_by(Proyecto.actualizado_en.desc())

    pagina = request.args.get("pagina", 1, type=int)
    tamano = request.args.get("tamano_pagina", 20, type=int)
    resultado = paginar(query, pagina, tamano)
    resultado["elementos"] = [enriquecer_proyecto_con_acceso(proyecto, usuario) for proyecto in resultado["elementos"]]
    resultado["elementos"] = proyectos_schema.dump(resultado["elementos"])
    return jsonify(resultado), 200


@proyectos_bp.route("", methods=["POST"])
@jwt_required()
@escritura_requerida
def crear_proyecto():
    data = request.get_json(silent=True) or {}
    errores = crear_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    uid = obtener_uid()
    proyecto = Proyecto(
        usuario_id=uid,
        nombre=data["nombre"].strip(),
        descripcion=data.get("descripcion"),
    )
    db.session.add(proyecto)
    db.session.commit()
    proyecto = enriquecer_proyecto_con_acceso(proyecto, obtener_usuario_actual())
    registrar_log("proyecto", "crear_proyecto", f"Proyecto creado: {proyecto.nombre}",
                  "proyecto", proyecto.id)
    db.session.commit()
    return jsonify(proyecto_schema.dump(proyecto)), 201


@proyectos_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def obtener_proyecto(id):
    uid = obtener_uid()
    proyecto = verificar_propiedad_proyecto(id, uid)
    return jsonify(proyecto_schema.dump(proyecto)), 200


@proyectos_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@escritura_requerida
def actualizar_proyecto(id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "edicion")

    data = request.get_json(silent=True) or {}
    errores = actualizar_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if "nombre" in data:
        proyecto.nombre = data["nombre"].strip()
    if "descripcion" in data:
        proyecto.descripcion = data["descripcion"]

    db.session.commit()
    return jsonify(proyecto_schema.dump(proyecto)), 200


@proyectos_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@escritura_requerida
def eliminar_proyecto(id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")
    db.session.delete(proyecto)
    registrar_log("proyecto", "eliminar_proyecto", f"Proyecto eliminado: {proyecto.nombre} (id: {id})",
                  "proyecto", id)
    db.session.commit()
    return jsonify({"mensaje": "Proyecto eliminado"}), 200


@proyectos_bp.route("/<int:id>/archivar", methods=["POST"])
@jwt_required()
@escritura_requerida
def archivar_proyecto(id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")
    proyecto.estado = "archivado"
    registrar_log("proyecto", "archivar_proyecto", f"Proyecto archivado: {proyecto.nombre}",
                  "proyecto", id)
    db.session.commit()
    return jsonify(proyecto_schema.dump(proyecto)), 200


@proyectos_bp.route("/<int:id>/restaurar", methods=["POST"])
@jwt_required()
@escritura_requerida
def restaurar_proyecto(id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")
    proyecto.estado = "activo"
    registrar_log("proyecto", "restaurar_proyecto", f"Proyecto restaurado: {proyecto.nombre}",
                  "proyecto", id)
    db.session.commit()
    return jsonify(proyecto_schema.dump(proyecto)), 200


@proyectos_bp.route("/<int:id>/miembros", methods=["GET"])
@jwt_required()
def listar_miembros(id):
    uid = obtener_uid()
    verificar_propiedad_proyecto(id, uid)
    miembros = MiembroProyecto.query.filter_by(proyecto_id=id).order_by(MiembroProyecto.creado_en.asc()).all()
    miembros_serializados = []
    for miembro in miembros:
        if not miembro.usuario:
            continue
        miembros_serializados.append({
            "usuario_id": miembro.usuario_id,
            "correo": miembro.usuario.correo,
            "nombre_completo": miembro.usuario.nombre_completo,
            "permiso": miembro.permiso,
            "creado_en": miembro.creado_en,
        })
    return jsonify(miembros_schema.dump(miembros_serializados)), 200


@proyectos_bp.route("/<int:id>/miembros", methods=["POST"])
@jwt_required()
@escritura_requerida
def agregar_miembro(id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")

    data = request.get_json(silent=True) or {}
    errores = crear_miembro_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    correo = data["correo"].lower().strip()
    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario:
        return jsonify({"error": "No existe un usuario con ese correo"}), 404
    if not usuario.esta_activo:
        return jsonify({"error": "No puedes agregar usuarios desactivados"}), 400
    if usuario.id == proyecto.usuario_id:
        return jsonify({"error": "El propietario ya tiene acceso total al proyecto"}), 400

    miembro_existente = MiembroProyecto.query.filter_by(proyecto_id=id, usuario_id=usuario.id).first()
    if miembro_existente:
        return jsonify({"error": "Ese usuario ya forma parte del proyecto"}), 409

    miembro = MiembroProyecto(
        proyecto_id=id,
        usuario_id=usuario.id,
        permiso=data["permiso"],
    )
    db.session.add(miembro)
    registrar_log(
        "proyecto",
        "agregar_miembro_proyecto",
        f"Miembro agregado al proyecto {proyecto.nombre}: {usuario.correo} ({miembro.permiso})",
        "proyecto",
        id,
    )
    db.session.commit()

    return jsonify({
        "usuario_id": usuario.id,
        "correo": usuario.correo,
        "nombre_completo": usuario.nombre_completo,
        "permiso": miembro.permiso,
        "creado_en": miembro.creado_en.isoformat() if miembro.creado_en else None,
    }), 201


@proyectos_bp.route("/<int:id>/miembros/<int:usuario_id>", methods=["PUT"])
@jwt_required()
@escritura_requerida
def actualizar_miembro(id, usuario_id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")

    data = request.get_json(silent=True) or {}
    errores = actualizar_miembro_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    miembro = MiembroProyecto.query.filter_by(proyecto_id=id, usuario_id=usuario_id).first()
    if not miembro:
        return jsonify({"error": "Miembro no encontrado en este proyecto"}), 404

    permiso_anterior = miembro.permiso
    miembro.permiso = data["permiso"]
    registrar_log(
        "proyecto",
        "actualizar_permiso_miembro",
        f"Permiso actualizado en proyecto {proyecto.nombre} para usuario {usuario_id}: {permiso_anterior} -> {miembro.permiso}",
        "proyecto",
        id,
    )
    db.session.commit()

    return jsonify({
        "usuario_id": miembro.usuario_id,
        "correo": miembro.usuario.correo if miembro.usuario else None,
        "nombre_completo": miembro.usuario.nombre_completo if miembro.usuario else None,
        "permiso": miembro.permiso,
        "creado_en": miembro.creado_en.isoformat() if miembro.creado_en else None,
    }), 200


@proyectos_bp.route("/<int:id>/miembros/<int:usuario_id>", methods=["DELETE"])
@jwt_required()
@escritura_requerida
def eliminar_miembro(id, usuario_id):
    uid = obtener_uid()
    proyecto = verificar_acceso_proyecto(id, uid, "administracion")

    miembro = MiembroProyecto.query.filter_by(proyecto_id=id, usuario_id=usuario_id).first()
    if not miembro:
        return jsonify({"error": "Miembro no encontrado en este proyecto"}), 404

    correo = miembro.usuario.correo if miembro.usuario else f"usuario {usuario_id}"
    db.session.delete(miembro)
    registrar_log(
        "proyecto",
        "eliminar_miembro_proyecto",
        f"Miembro eliminado del proyecto {proyecto.nombre}: {correo}",
        "proyecto",
        id,
    )
    db.session.commit()
    return jsonify({"mensaje": "Miembro eliminado del proyecto"}), 200
