from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.etiqueta import Etiqueta
from app.schemas import EtiquetaSchema, EtiquetaCrearSchema, EtiquetaActualizarSchema
from app.utils import verificar_propiedad_etiqueta, obtener_uid

etiquetas_bp = Blueprint("etiquetas", __name__)
etiqueta_schema = EtiquetaSchema()
etiquetas_schema = EtiquetaSchema(many=True)


@etiquetas_bp.route("", methods=["GET"])
@jwt_required()
def listar_etiquetas():
    uid = obtener_uid()
    etiquetas = Etiqueta.query.filter_by(usuario_id=uid).order_by(Etiqueta.nombre.asc()).all()
    return jsonify(etiquetas_schema.dump(etiquetas)), 200


@etiquetas_bp.route("", methods=["POST"])
@jwt_required()
def crear_etiqueta():
    uid = obtener_uid()
    data = request.get_json(silent=True) or {}
    errores = EtiquetaCrearSchema().validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    nombre = data["nombre"].strip()
    existente = Etiqueta.query.filter_by(usuario_id=uid, nombre=nombre).first()
    if existente:
        return jsonify({"error": "Ya existe una etiqueta con ese nombre"}), 409

    etiqueta = Etiqueta(
        usuario_id=uid,
        nombre=nombre,
        color=data.get("color"),
    )
    db.session.add(etiqueta)
    db.session.commit()
    return jsonify(etiqueta_schema.dump(etiqueta)), 201


@etiquetas_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_etiqueta(id):
    uid = obtener_uid()
    etiqueta = verificar_propiedad_etiqueta(id, uid)

    data = request.get_json(silent=True) or {}
    errores = EtiquetaActualizarSchema().validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if "nombre" in data:
        nombre = data["nombre"].strip()
        existente = Etiqueta.query.filter(
            Etiqueta.usuario_id == uid,
            Etiqueta.nombre == nombre,
            Etiqueta.id != id,
        ).first()
        if existente:
            return jsonify({"error": "Ya existe una etiqueta con ese nombre"}), 409
        etiqueta.nombre = nombre

    if "color" in data:
        etiqueta.color = data["color"]

    db.session.commit()
    return jsonify(etiqueta_schema.dump(etiqueta)), 200


@etiquetas_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_etiqueta(id):
    uid = obtener_uid()
    etiqueta = verificar_propiedad_etiqueta(id, uid)
    db.session.delete(etiqueta)
    db.session.commit()
    return jsonify({"mensaje": "Etiqueta eliminada"}), 200
