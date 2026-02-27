from datetime import datetime, timezone
import bcrypt
from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    ROLES_VALIDOS = ("administrador", "jefe", "usuario", "visualizador")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hash_contrasena = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="usuario")
    esta_activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    proyectos = db.relationship("Proyecto", backref="usuario", lazy="dynamic", cascade="all,delete-orphan")
    etiquetas = db.relationship("Etiqueta", backref="usuario", lazy="dynamic", cascade="all,delete-orphan")
    tokens = db.relationship("TokenActualizacion", backref="usuario", lazy="dynamic", cascade="all,delete-orphan")

    def set_password(self, password: str):
        self.hash_contrasena = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.hash_contrasena.encode("utf-8"),
        )

    #ayuda por roles
    @property
    def es_admin(self) -> bool:
        return self.rol == "administrador"

    @property
    def es_jefe(self) -> bool:
        return self.rol == "jefe"

    @property
    def es_visualizador(self) -> bool:
        return self.rol == "visualizador"

    def tiene_rol(self, *roles) -> bool:
        return self.rol in roles

    @property
    def puede_escribir(self) -> bool:
        """Administrador, Jefe y Usuario pueden crear/editar. Visualizador no."""
        return self.rol in ("administrador", "jefe", "usuario")

    @property
    def puede_ver_todo(self) -> bool:
        """Administrador y Jefe pueden ver recursos de todos los usuarios."""
        return self.rol in ("administrador", "jefe")

    def __repr__(self):
        return f"<Usuario {self.correo}>"
