from app import ma
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta
from app.models.comentario_tarea import ComentarioTarea
from app.models.checklist_tarea import ChecklistTarea
from app.models.registro_actividad import RegistroActividad
from marshmallow import fields, validate, validates, ValidationError, post_dump, EXCLUDE
import re


#Usuario
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
        exclude = ("hash_contrasena",)

    correo = fields.Email(required=True)
    nombre_completo = fields.String(required=True, validate=validate.Length(min=2, max=150))
    rol = fields.String(dump_only=True)


class UsuarioAdminSchema(ma.SQLAlchemyAutoSchema):
    """CRUD de usuarios desde el panel admin"""
    class Meta:
        model = Usuario
        load_instance = True
        exclude = ("hash_contrasena",)

    correo = fields.Email(required=True)
    nombre_completo = fields.String(required=True, validate=validate.Length(min=2, max=150))
    rol = fields.String(dump_only=True)
    esta_activo = fields.Boolean(dump_only=True)


class UsuarioCrearAdminSchema(ma.Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True, validate=validate.Length(min=8, max=128))
    nombre_completo = fields.String(required=True, validate=validate.Length(min=2, max=150))
    rol = fields.String(validate=validate.OneOf(["admin", "usuario"]), load_default="usuario")

    @validates("contrasena")
    def validar_contrasena(self, value):
        if not re.search(r"\d", value):
            raise ValidationError("La contrase\u00f1a debe contener al menos un n\u00famero.")


class UsuarioActualizarAdminSchema(ma.Schema):
    nombre_completo = fields.String(validate=validate.Length(min=2, max=150))
    correo = fields.Email()
    rol = fields.String(validate=validate.OneOf(["admin", "usuario"]))
    esta_activo = fields.Boolean()


class RegistroSchema(ma.Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
    )
    nombre_completo = fields.String(required=True, validate=validate.Length(min=2, max=150))

    @validates("contrasena")
    def validar_contrasena(self, value):
        if not re.search(r"\d", value):
            raise ValidationError("La contraseña debe contener al menos un numero")


class LoginSchema(ma.Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True)
    recordarSesion = fields.Boolean(load_default=False)

    class Meta:
        unknown = EXCLUDE


#Proyectos
class ProyectoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Proyecto
        load_instance = True
        include_fk = True

    nombre = fields.String(required=True, validate=validate.Length(min=3, max=80))
    estado = fields.String(dump_only=True)


class ProyectoCrearSchema(ma.Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=3, max=80))
    descripcion = fields.String(validate=validate.Length(max=2000), load_default=None)


class ProyectoActualizarSchema(ma.Schema):
    nombre = fields.String(validate=validate.Length(min=3, max=80))
    descripcion = fields.String(validate=validate.Length(max=2000))


#Etiquetas
class EtiquetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Etiqueta
        load_instance = True
        include_fk = True


class EtiquetaCrearSchema(ma.Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=30))
    color = fields.String(validate=validate.Length(max=7), load_default=None)

    @validates("color")
    def validar_color(self, value):
        if value and not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise ValidationError("Color debe tener formato #AABBCC.")


class EtiquetaActualizarSchema(ma.Schema):
    nombre = fields.String(validate=validate.Length(min=1, max=30))
    color = fields.String(validate=validate.Length(max=7))

    @validates("color")
    def validar_color(self, value):
        if value and not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise ValidationError("Color debe tener formato #AABBCC.")


#Tareas
class EtiquetaResumenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Etiqueta
        fields = ("id", "nombre", "color")


class TareaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tarea
        load_instance = True
        include_fk = True

    etiquetas = fields.Nested(EtiquetaResumenSchema, many=True, dump_only=True)
    esta_vencida = fields.Boolean(dump_only=True)
    nombre_proyecto = fields.Method("get_nombre_proyecto")

    def get_nombre_proyecto(self, obj):
        return obj.proyecto.nombre if obj.proyecto else None


class TareaCrearSchema(ma.Schema):
    proyecto_id = fields.Integer(required=True)
    titulo = fields.String(required=True, validate=validate.Length(min=3, max=120))
    descripcion = fields.String(validate=validate.Length(max=5000), load_default=None)
    estado = fields.String(
        validate=validate.OneOf(Tarea.ESTADOS_VALIDOS),
        load_default="pendiente",
    )
    prioridad = fields.String(
        validate=validate.OneOf(Tarea.PRIORIDADES_VALIDAS),
        load_default="media",
    )
    fecha_vencimiento = fields.Date(load_default=None)
    etiquetas_ids = fields.List(fields.Integer(), load_default=[])


class TareaActualizarSchema(ma.Schema):
    titulo = fields.String(validate=validate.Length(min=3, max=120))
    descripcion = fields.String(validate=validate.Length(max=5000))
    estado = fields.String(validate=validate.OneOf(Tarea.ESTADOS_VALIDOS))
    prioridad = fields.String(validate=validate.OneOf(Tarea.PRIORIDADES_VALIDAS))
    fecha_vencimiento = fields.Date(allow_none=True)
    etiquetas_ids = fields.List(fields.Integer())
    proyecto_id = fields.Integer()


#Comentarios
class ComentarioTareaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ComentarioTarea
        load_instance = True
        include_fk = True


class ComentarioCrearSchema(ma.Schema):
    contenido = fields.String(required=True, validate=validate.Length(min=1, max=5000))


#Checklists
class ChecklistTareaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ChecklistTarea
        load_instance = True
        include_fk = True


class ChecklistCrearSchema(ma.Schema):
    descripcion = fields.String(required=True, validate=validate.Length(min=1, max=255))
    esta_completado = fields.Boolean(load_default=False)


#Registros Actividades
class RegistroActividadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RegistroActividad
        load_instance = True
        include_fk = True


#Paginacion
class PaginacionSchema(ma.Schema):
    pagina = fields.Integer(dump_only=True)
    tamano_pagina = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)
    paginas = fields.Integer(dump_only=True)
    elementos = fields.Raw(dump_only=True)
