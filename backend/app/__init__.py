from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    #blueprints
    from app.routes.autenticacion import auth_bp
    from app.routes.proyectos import proyectos_bp
    from app.routes.tareas import tareas_bp
    from app.routes.etiquetas import etiquetas_bp
    from app.routes.panel import panel_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.auditoria import auditoria_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/autenticacion")
    app.register_blueprint(proyectos_bp, url_prefix="/api/v1/proyectos")
    app.register_blueprint(tareas_bp, url_prefix="/api/v1/tareas")
    app.register_blueprint(etiquetas_bp, url_prefix="/api/v1/etiquetas")
    app.register_blueprint(panel_bp, url_prefix="/api/v1/panel")
    app.register_blueprint(usuarios_bp, url_prefix="/api/v1/usuarios")
    app.register_blueprint(auditoria_bp, url_prefix="/api/v1/auditoria")

    #JWT
    from app.models.usuario import Usuario
    from app.models.token_actualizacion import TokenActualizacion

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenActualizacion.query.filter_by(identificador_jti=jti).first()
        if token:
            return token.revocado
        return False

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, (int, str)):
            return str(user)
        return str(user.id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Usuario.query.get(int(identity))

    #errores de handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Recurso no encontrado"}, 404

    @app.errorhandler(422)
    def unprocessable(e):
        return {"error": "Datos no procesables"}, 422

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Error interno del servidor"}, 500

    return app
