from datetime import datetime, timezone
from app import db


class MencionComentario(db.Model):
    __tablename__ = "menciones_comentario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comentario_id = db.Column(db.Integer, db.ForeignKey("comentarios_tarea.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("comentario_id", "usuario_id", name="uq_mencion_comentario_usuario"),
    )

    def __repr__(self):
        return f"<MencionComentario comentario={self.comentario_id} usuario={self.usuario_id}>"
