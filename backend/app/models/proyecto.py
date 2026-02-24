from datetime import datetime, timezone
from app import db


class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="activo")  # activo | archivado
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tareas = db.relationship("Tarea", backref="proyecto", lazy="dynamic", cascade="all,delete-orphan")

    __table_args__ = (
        db.Index("idx_proyectos_nombre_ft", "nombre", mysql_prefix="FULLTEXT"),
    )

    def __repr__(self):
        return f"<Proyecto {self.nombre}>"
