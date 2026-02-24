"""Script de datos iniciales (seed)."""
from app import create_app, db
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta, tarea_etiquetas
from datetime import date, timedelta


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        #verificar si ya existe usuario demo
        if Usuario.query.filter_by(correo="demo@ejemplo.com").first():
            print("Seed ya ejecutado. Saliendo.")
            return

        #usuario demo
        usuario = Usuario(
            correo="demo@ejemplo.com",
            nombre_completo="Usuario Demo",
        )
        usuario.set_password("Demo1234")
        db.session.add(usuario)
        db.session.flush()

        #etiquetas demo
        etiquetas = []
        colores = {
            "Frontend": "#3B82F6",
            "Backend": "#10B981",
            "Bug": "#EF4444",
            "Mejora": "#F59E0B",
            "Documentación": "#8B5CF6",
            "Urgente": "#DC2626",
        }
        for nombre, color in colores.items():
            e = Etiqueta(usuario_id=usuario.id, nombre=nombre, color=color)
            db.session.add(e)
            etiquetas.append(e)
        db.session.flush()

        #proyecto demo 1
        proyecto1 = Proyecto(
            usuario_id=usuario.id,
            nombre="Mi Primer Proyecto",
            descripcion="Proyecto de ejemplo para demostración del sistema.",
        )
        db.session.add(proyecto1)

        #proyecto demo 2
        proyecto2 = Proyecto(
            usuario_id=usuario.id,
            nombre="Aplicación Móvil",
            descripcion="Desarrollo de la app móvil multiplataforma.",
        )
        db.session.add(proyecto2)
        db.session.flush()

        #tareas demo
        hoy = date.today()
        tareas_data = [
            {
                "proyecto_id": proyecto1.id,
                "titulo": "Configurar entorno de desarrollo",
                "descripcion": "Instalar todas las dependencias necesarias",
                "estado": "completada",
                "prioridad": "alta",
                "fecha_vencimiento": hoy - timedelta(days=5),
                "etiquetas": [etiquetas[1]],  #Backend
            },
            {
                "proyecto_id": proyecto1.id,
                "titulo": "Diseñar base de datos",
                "descripcion": "Crear el modelo ER y las migraciones",
                "estado": "completada",
                "prioridad": "alta",
                "fecha_vencimiento": hoy - timedelta(days=3),
                "etiquetas": [etiquetas[1], etiquetas[4]],  #Backend Documentacion
            },
            {
                "proyecto_id": proyecto1.id,
                "titulo": "Implementar autenticación JWT",
                "descripcion": "Login, registro, refresh tokens",
                "estado": "en_progreso",
                "prioridad": "urgente",
                "fecha_vencimiento": hoy + timedelta(days=2),
                "etiquetas": [etiquetas[1]],  #Backend
            },
            {
                "proyecto_id": proyecto1.id,
                "titulo": "Crear componentes de UI",
                "descripcion": "Formularios, tablas, modales con PrimeNG",
                "estado": "pendiente",
                "prioridad": "media",
                "fecha_vencimiento": hoy + timedelta(days=7),
                "etiquetas": [etiquetas[0]],  #Frontend
            },
            {
                "proyecto_id": proyecto1.id,
                "titulo": "Corregir bug en validaciones",
                "descripcion": "Las validaciones del formulario no muestran errores",
                "estado": "pendiente",
                "prioridad": "alta",
                "fecha_vencimiento": hoy - timedelta(days=1),
                "etiquetas": [etiquetas[0], etiquetas[2]],  #Frontend, Bug
            },
            {
                "proyecto_id": proyecto2.id,
                "titulo": "Diseñar wireframes",
                "descripcion": "Crear los wireframes de las pantallas principales",
                "estado": "pendiente",
                "prioridad": "media",
                "fecha_vencimiento": hoy + timedelta(days=10),
                "etiquetas": [etiquetas[0]],  #Frontend
            },
            {
                "proyecto_id": proyecto2.id,
                "titulo": "Configurar CI/CD",
                "descripcion": "Pipeline de integración continua",
                "estado": "pendiente",
                "prioridad": "baja",
                "fecha_vencimiento": hoy + timedelta(days=14),
                "etiquetas": [etiquetas[1], etiquetas[3]],  #Backend Mejora
            },
        ]

        for td in tareas_data:
            etqs = td.pop("etiquetas")
            tarea = Tarea(**td)
            if tarea.estado == "completada":
                tarea.completar()
            tarea.etiquetas = etqs
            db.session.add(tarea)

        db.session.commit()
        print("Seed ejecutado exitosamente!")
        print("Usuario: demo@ejemplo.com / Demo1234")


if __name__ == "__main__":
    seed()
