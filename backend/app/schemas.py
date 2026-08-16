from app import ma
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.miembro_proyecto import MiembroProyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta
from app.models.comentario_tarea import ComentarioTarea
from app.models.mencion_comentario import MencionComentario
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
    rol = fields.String(
        validate=validate.OneOf(["administrador", "jefe", "usuario", "visualizador"]),
        load_default="usuario",
    )

    @validates("contrasena")
    def validar_contrasena(self, value):
        if not re.search(r"\d", value):
            raise ValidationError("La contrase\u00f1a debe contener al menos un n\u00famero.")


class UsuarioActualizarAdminSchema(ma.Schema):
    nombre_completo = fields.String(validate=validate.Length(min=2, max=150))
    correo = fields.Email()
    rol = fields.String(validate=validate.OneOf(["administrador", "jefe", "usuario", "visualizador"]))
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
    propietario = fields.Method("get_propietario")
    miembros = fields.Method("get_miembros")
    permiso_actual = fields.Method("get_permiso_actual")
    puede_administrar = fields.Method("get_puede_administrar")
    es_propietario = fields.Method("get_es_propietario")

    def get_propietario(self, obj):
        if not obj.usuario:
            return None
        return {
            "id": obj.usuario.id,
            "correo": obj.usuario.correo,
            "nombre_completo": obj.usuario.nombre_completo,
        }

    def get_miembros(self, obj):
        miembros = []
        for miembro in obj.miembros.order_by(MiembroProyecto.creado_en.asc()).all():
            if not miembro.usuario:
                continue
            miembros.append({
                "usuario_id": miembro.usuario_id,
                "correo": miembro.usuario.correo,
                "nombre_completo": miembro.usuario.nombre_completo,
                "permiso": miembro.permiso,
                "creado_en": miembro.creado_en.isoformat() if miembro.creado_en else None,
            })
        return miembros

    def get_permiso_actual(self, obj):
        permiso_actual = getattr(obj, "permiso_actual", None)
        if permiso_actual:
            return permiso_actual
        return "administracion" if getattr(obj, "es_propietario_actual", False) else None

    def get_puede_administrar(self, obj):
        return bool(getattr(obj, "puede_administrar_actual", False))

    def get_es_propietario(self, obj):
        return bool(getattr(obj, "es_propietario_actual", False))


class ProyectoCrearSchema(ma.Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=3, max=80))
    descripcion = fields.String(validate=validate.Length(max=2000), load_default=None)


class ProyectoActualizarSchema(ma.Schema):
    nombre = fields.String(validate=validate.Length(min=3, max=80))
    descripcion = fields.String(validate=validate.Length(max=2000))


class MiembroProyectoSchema(ma.Schema):
    usuario_id = fields.Integer(dump_only=True)
    correo = fields.Email(dump_only=True)
    nombre_completo = fields.String(dump_only=True)
    permiso = fields.String(validate=validate.OneOf(MiembroProyecto.PERMISOS_VALIDOS), required=True)
    creado_en = fields.DateTime(dump_only=True)


class MiembroProyectoCrearSchema(ma.Schema):
    correo = fields.Email(required=True)
    permiso = fields.String(
        required=True,
        validate=validate.OneOf(MiembroProyecto.PERMISOS_VALIDOS),
    )


class MiembroProyectoActualizarSchema(ma.Schema):
    permiso = fields.String(
        required=True,
        validate=validate.OneOf(MiembroProyecto.PERMISOS_VALIDOS),
    )


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
    asignado_a = fields.Method("get_asignado_a")

    def get_nombre_proyecto(self, obj):
        return obj.proyecto.nombre if obj.proyecto else None

    def get_asignado_a(self, obj):
        if not obj.asignado_a:
            return None
        return {
            "id": obj.asignado_a.id,
            "correo": obj.asignado_a.correo,
            "nombre_completo": obj.asignado_a.nombre_completo,
        }


class TareaCrearSchema(ma.Schema):
    proyecto_id = fields.Integer(required=True)
    asignado_a_usuario_id = fields.Integer(allow_none=True, load_default=None)
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
    asignado_a_usuario_id = fields.Integer(allow_none=True)
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

    autor = fields.Method("get_autor")
    menciones = fields.Method("get_menciones")

    def get_autor(self, obj):
        if not obj.usuario:
            return None
        return {
            "id": obj.usuario.id,
            "correo": obj.usuario.correo,
            "nombre_completo": obj.usuario.nombre_completo,
        }

    def get_menciones(self, obj):
        resultado = []
        for mencion in obj.menciones.order_by(MencionComentario.creado_en.asc()).all():
            if not mencion.usuario:
                continue
            resultado.append({
                "usuario_id": mencion.usuario.id,
                "correo": mencion.usuario.correo,
                "nombre_completo": mencion.usuario.nombre_completo,
            })
        return resultado


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
