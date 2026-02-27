from datetime import datetime, timezone
from app import db


class LogAuditoria(db.Model):
    #registro de auditoria de seguridad accesos y cambios de cosas sensibles
    __tablename__ = "logs_auditoria"

    CATEGORIAS = ("acceso", "usuario", "proyecto", "tarea", "etiqueta", "sistema")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_correo = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(30), nullable=False, index=True)
    accion = db.Column(db.String(80), nullable=False)
    detalle = db.Column(db.Text, nullable=True)
    entidad_tipo = db.Column(db.String(30), nullable=True)
    entidad_id = db.Column(db.Integer, nullable=True)
    direccion_ip = db.Column(db.String(45), nullable=True)
    agente_usuario = db.Column(db.String(500), nullable=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    usuario = db.relationship("Usuario", backref=db.backref("logs_auditoria", lazy="dynamic"))

    def __repr__(self):
        return f"<LogAuditoria {self.categoria}:{self.accion} por {self.usuario_correo}>"
