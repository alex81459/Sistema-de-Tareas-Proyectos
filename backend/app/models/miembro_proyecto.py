from datetime import datetime, timezone
from app import db


class MiembroProyecto(db.Model):
    __tablename__ = "miembros_proyecto"

    PERMISOS_VALIDOS = ("lectura", "edicion", "administracion")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    permiso = db.Column(db.String(20), nullable=False, default="lectura")
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("proyecto_id", "usuario_id", name="uq_miembro_proyecto_usuario"),
    )

    def __repr__(self):
        return f"<MiembroProyecto proyecto={self.proyecto_id} usuario={self.usuario_id} permiso={self.permiso}>"
