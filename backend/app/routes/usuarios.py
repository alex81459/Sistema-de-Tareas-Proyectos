from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.usuario import Usuario
from app.schemas import UsuarioAdminSchema, UsuarioCrearAdminSchema, UsuarioActualizarAdminSchema
from app.utils import admin_requerido, paginar

usuarios_bp = Blueprint("usuarios", __name__)
usuario_schema = UsuarioAdminSchema()
usuarios_schema = UsuarioAdminSchema(many=True)
crear_schema = UsuarioCrearAdminSchema()
actualizar_schema = UsuarioActualizarAdminSchema()


@usuarios_bp.route("", methods=["GET"])
@jwt_required()
@admin_requerido
def listar():
    """Listar usuarios con filtros opcionales (solo admin)."""
    query = Usuario.query

    buscar = request.args.get("buscar", "").strip()
    if buscar:
        filtro = f"%{buscar}%"
        query = query.filter(
            db.or_(
                Usuario.nombre_completo.ilike(filtro),
                Usuario.correo.ilike(filtro),
            )
        )

    rol = request.args.get("rol")
    if rol and rol in ("admin", "usuario"):
        query = query.filter_by(rol=rol)

    activo = request.args.get("activo")
    if activo is not None:
        query = query.filter_by(esta_activo=activo.lower() == "true")

    query = query.order_by(Usuario.creado_en.desc())

    pagina = int(request.args.get("pagina", 1))
    tamano = int(request.args.get("tamano_pagina", 20))
    resultado = paginar(query, pagina, tamano)
    resultado["elementos"] = usuarios_schema.dump(resultado["elementos"])
    return jsonify(resultado), 200


@usuarios_bp.route("/<int:usuario_id>", methods=["GET"])
@jwt_required()
@admin_requerido
def obtener(usuario_id):
    """Obtener detalle de un usuario (solo admin)."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario_schema.dump(usuario)), 200


@usuarios_bp.route("", methods=["POST"])
@jwt_required()
@admin_requerido
def crear():
    """Crear un nuevo usuario desde admin."""
    data = request.get_json(silent=True) or {}
    errores = crear_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if Usuario.query.filter_by(correo=data["correo"].lower().strip()).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    usuario = Usuario(
        correo=data["correo"].lower().strip(),
        nombre_completo=data["nombre_completo"].strip(),
        rol=data.get("rol", "usuario"),
    )
    usuario.set_password(data["contrasena"])
    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        "mensaje": "Usuario creado exitosamente",
        "usuario": usuario_schema.dump(usuario),
    }), 201


@usuarios_bp.route("/<int:usuario_id>", methods=["PUT"])
@jwt_required()
@admin_requerido
def actualizar(usuario_id):
    """Editar un usuario (nombre, correo, rol, activo)."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    errores = actualizar_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if "correo" in data:
        nuevo_correo = data["correo"].lower().strip()
        existente = Usuario.query.filter_by(correo=nuevo_correo).first()
        if existente and existente.id != usuario_id:
            return jsonify({"error": "El correo ya está en uso"}), 409
        usuario.correo = nuevo_correo

    if "nombre_completo" in data:
        usuario.nombre_completo = data["nombre_completo"].strip()
    if "rol" in data:
        usuario.rol = data["rol"]
    if "esta_activo" in data:
        usuario.esta_activo = data["esta_activo"]

    db.session.commit()
    return jsonify({
        "mensaje": "Usuario actualizado",
        "usuario": usuario_schema.dump(usuario),
    }), 200


@usuarios_bp.route("/<int:usuario_id>", methods=["DELETE"])
@jwt_required()
@admin_requerido
def eliminar(usuario_id):
    """Eliminar un usuario (solo admin, no puede eliminarse a sí mismo)."""
    from app.utils import obtener_uid
    if obtener_uid() == usuario_id:
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 400

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado"}), 200


@usuarios_bp.route("/<int:usuario_id>/reset-password", methods=["PUT"])
@jwt_required()
@admin_requerido
def reset_password(usuario_id):
    """Resetear la contraseña de un usuario (solo admin)."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    nueva = data.get("contrasena", "").strip()
    if len(nueva) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    usuario.set_password(nueva)
    db.session.commit()
    return jsonify({"mensaje": "Contraseña actualizada exitosamente"}), 200
