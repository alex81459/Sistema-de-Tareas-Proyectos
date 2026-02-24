from datetime import datetime, timezone
from app import db


class TokenActualizacion(db.Model):
    __tablename__ = "tokens_actualizacion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    identificador_jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    revocado = db.Column(db.Boolean, default=False, nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    reemplazado_por_jti = db.Column(db.String(36), nullable=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<TokenActualizacion {self.identificador_jti}>"
