from datetime import datetime, timezone
from app import db


tarea_etiquetas = db.Table(
    "tarea_etiquetas",
    db.Column("tarea_id", db.Integer, db.ForeignKey("tareas.id", ondelete="CASCADE"), primary_key=True),
    db.Column("etiqueta_id", db.Integer, db.ForeignKey("etiquetas.id", ondelete="CASCADE"), primary_key=True),
)


class Etiqueta(db.Model):
    __tablename__ = "etiquetas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(7), nullable=True)  # #AABBCC
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("usuario_id", "nombre", name="uq_etiqueta_usuario_nombre"),
    )

    def __repr__(self):
        return f"<Etiqueta {self.nombre}>"
