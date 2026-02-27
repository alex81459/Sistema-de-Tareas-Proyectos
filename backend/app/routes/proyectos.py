from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.proyecto import Proyecto
from app.schemas import ProyectoSchema, ProyectoCrearSchema, ProyectoActualizarSchema
from app.utils import paginar, verificar_propiedad_proyecto, obtener_uid, obtener_usuario_actual, escritura_requerida, registrar_log

proyectos_bp = Blueprint("proyectos", __name__)
proyecto_schema = ProyectoSchema()
proyectos_schema = ProyectoSchema(many=True)
crear_schema = ProyectoCrearSchema()
actualizar_schema = ProyectoActualizarSchema()


@proyectos_bp.route("", methods=["GET"])
@jwt_required()
def listar_proyectos():
    uid = obtener_uid()
    usuario = obtener_usuario_actual()
    if usuario.puede_ver_todo:
        query = Proyecto.query
    else:
        query = Proyecto.query.filter_by(usuario_id=uid)

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
    proyecto = verificar_propiedad_proyecto(id, uid)

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
    proyecto = verificar_propiedad_proyecto(id, uid)
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
    proyecto = verificar_propiedad_proyecto(id, uid)
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
    proyecto = verificar_propiedad_proyecto(id, uid)
    proyecto.estado = "activo"
    registrar_log("proyecto", "restaurar_proyecto", f"Proyecto restaurado: {proyecto.nombre}",
                  "proyecto", id)
    db.session.commit()
    return jsonify(proyecto_schema.dump(proyecto)), 200
