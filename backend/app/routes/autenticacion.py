from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    current_user,
)
from app import db
from app.models.usuario import Usuario
from app.models.token_actualizacion import TokenActualizacion
from app.schemas import RegistroSchema, LoginSchema, UsuarioSchema
from app.utils import registrar_log
import uuid

auth_bp = Blueprint("autenticacion", __name__)
registro_schema = RegistroSchema()
login_schema = LoginSchema()
usuario_schema = UsuarioSchema()


@auth_bp.route("/registrar", methods=["POST"])
def registrar():
    data = request.get_json(silent=True) or {}
    errores = registro_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if Usuario.query.filter_by(correo=data["correo"].lower().strip()).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    usuario = Usuario(
        correo=data["correo"].lower().strip(),
        nombre_completo=data["nombre_completo"].strip(),
    )
    usuario.set_password(data["contrasena"])
    db.session.add(usuario)
    db.session.commit()

    registrar_log("acceso", "registro", f"Nuevo usuario registrado: {usuario.correo}",
                  "usuario", usuario.id, usuario.id, usuario.correo)
    db.session.commit()

    access_token = create_access_token(identity=str(usuario.id))
    jti = str(uuid.uuid4())
    refresh_token = create_refresh_token(identity=str(usuario.id), additional_claims={"jti": jti})

    guardar_refresh_token(usuario.id, jti, False)

    return jsonify({
        "mensaje": "Usuario registrado exitosamente",
        "usuario": usuario_schema.dump(usuario),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/iniciar-sesion", methods=["POST"])
def iniciar_sesion():
    data = request.get_json(silent=True) or {}
    errores = login_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    usuario = Usuario.query.filter_by(correo=data["correo"].lower().strip()).first()
    if not usuario or not usuario.check_password(data["contrasena"]):
        registrar_log("acceso", "login_fallido",
                      f"Intento fallido para: {data.get('correo', '???')}",
                      usuario_correo=data.get("correo", "desconocido"))
        db.session.commit()
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not usuario.esta_activo:
        registrar_log("acceso", "login_cuenta_inactiva",
                      f"Intento con cuenta desactivada: {usuario.correo}",
                      "usuario", usuario.id, usuario.id, usuario.correo)
        db.session.commit()
        return jsonify({"error": "Cuenta desactivada"}), 403

    access_token = create_access_token(identity=str(usuario.id))
    jti = str(uuid.uuid4())
    
    #si recordarSesion es true usar una duracion extendida para el refresh token
    recordar_sesion = data.get("recordarSesion", False)
    refresh_token = create_refresh_token(identity=str(usuario.id), additional_claims={"jti": jti})

    guardar_refresh_token(usuario.id, jti, recordar_sesion)

    registrar_log("acceso", "login_exitoso", f"Inicio de sesión: {usuario.correo}",
                  "usuario", usuario.id, usuario.id, usuario.correo)
    db.session.commit()

    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200


@auth_bp.route("/actualizar-token", methods=["POST"])
@jwt_required(refresh=True)
def actualizar_token():
    identity = get_jwt_identity()
    claims = get_jwt()
    old_jti = claims.get("jti")

    #revocar el refresh anterior
    token_viejo = TokenActualizacion.query.filter_by(identificador_jti=old_jti).first()
    if token_viejo:
        if token_viejo.revocado:
            return jsonify({"error": "Token ya fue revocado"}), 401
        token_viejo.revocado = True

    new_access = create_access_token(identity=identity)
    new_jti = str(uuid.uuid4())
    new_refresh = create_refresh_token(identity=identity, additional_claims={"jti": new_jti})

    guardar_refresh_token(int(identity), new_jti, False)

    if token_viejo:
        token_viejo.reemplazado_por_jti = new_jti

    db.session.commit()

    return jsonify({
        "access_token": new_access,
        "refresh_token": new_refresh,
    }), 200


@auth_bp.route("/cerrar-sesion", methods=["POST"])
@jwt_required()
def cerrar_sesion():
    jti = get_jwt().get("jti")
    token = TokenActualizacion.query.filter_by(identificador_jti=jti).first()
    if token:
        token.revocado = True
        db.session.commit()
    registrar_log("acceso", "logout", "Cierre de sesión")
    db.session.commit()
    return jsonify({"mensaje": "Sesión cerrada"}), 200


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    return jsonify(usuario_schema.dump(current_user)), 200


# ── Helpers ──
def guardar_refresh_token(usuario_id: int, jti: str, recordar_sesion: bool = False):
    from flask import current_app
    exp_delta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    
    # Si recordarSesion es true, extender la duración a 90 días
    if recordar_sesion:
        exp_delta = timedelta(days=90)
    
    token = TokenActualizacion(
        usuario_id=usuario_id,
        identificador_jti=jti,
        expira_en=datetime.now(timezone.utc) + exp_delta,
    )
    db.session.add(token)
    db.session.commit()
