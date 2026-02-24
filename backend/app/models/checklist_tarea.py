from datetime import datetime, timezone
from app import db


class ChecklistTarea(db.Model):
    __tablename__ = "checklist_tarea"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey("tareas.id", ondelete="CASCADE"), nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=False)
    esta_completado = db.Column(db.Boolean, default=False, nullable=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ChecklistTarea {self.descripcion[:30]}>"
