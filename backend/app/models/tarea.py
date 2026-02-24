from datetime import datetime, date, timezone
from app import db


class Tarea(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False, index=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    prioridad = db.Column(db.String(20), nullable=False, default="media")
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    completado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    etiquetas = db.relationship(
        "Etiqueta",
        secondary="tarea_etiquetas",
        backref=db.backref("tareas", lazy="dynamic"),
        lazy="joined",
    )
    comentarios = db.relationship("ComentarioTarea", backref="tarea", lazy="dynamic", cascade="all,delete-orphan")
    checklist = db.relationship("ChecklistTarea", backref="tarea", lazy="dynamic", cascade="all,delete-orphan")
    actividad = db.relationship("RegistroActividad", backref="tarea", lazy="dynamic", cascade="all,delete-orphan")

    ESTADOS_VALIDOS = ("pendiente", "en_progreso", "completada")
    PRIORIDADES_VALIDAS = ("baja", "media", "alta", "urgente")

    __table_args__ = (
        db.Index("idx_tareas_titulo_ft", "titulo", mysql_prefix="FULLTEXT"),
        db.Index("idx_tareas_titulo_desc_ft", "titulo", "descripcion", mysql_prefix="FULLTEXT"),
    )

    @property
    def esta_vencida(self) -> bool:
        if self.fecha_vencimiento and self.estado != "completada":
            return self.fecha_vencimiento < date.today()
        return False

    def completar(self):
        self.estado = "completada"
        self.completado_en = datetime.now(timezone.utc)

    def reabrir(self):
        self.estado = "pendiente"
        self.completado_en = None

    def __repr__(self):
        return f"<Tarea {self.titulo}>"
