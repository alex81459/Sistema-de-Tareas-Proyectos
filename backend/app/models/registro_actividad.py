from datetime import datetime, timezone
from app import db


class RegistroActividad(db.Model):
    __tablename__ = "registro_actividad_tarea"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey("tareas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    valor_anterior = db.Column(db.Text, nullable=True)
    valor_nuevo = db.Column(db.Text, nullable=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<RegistroActividad {self.accion}>"
