from datetime import datetime, timezone
from app import db


class ComentarioTarea(db.Model):
    __tablename__ = "comentarios_tarea"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey("tareas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ComentarioTarea {self.id}>"
