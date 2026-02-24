# Sistema de Tareas y Proyectos (TaskFlowAS)
Sistema de gestion de tareas y proyectos con autenticacion segura, multi-tenant, control de permisos, filtros avanzados, paginacion, validaciones robustas y reglas de negocio.

## Descripción General
TaskFlowAS es una solución empresarial para organizar y gestionar proyectos y tareas, permite a los usuarios 
crear proyectos, definir tareas con diferentes prioridades y estados, implementar checklists, añadir comentarios, 
registrar actividad de auditoria y visualizar análisis en tiempo real a través de dashboards interactivos.

## Tecnologias
Frontend - Angular + PrimeNG + TailwindCSS  19+ 
Backend - Flask + SQLAlchemy + JWT  Python 3.13 
Base de datos - MySQL  8.0.45 
Contenedores - Docker + Docker Compose  
Iconos - PrimeIcons v6+ 

## Caracteristicas Principales
# Autenticacion y Sesion
- Registro e Inicio de Sesión con JWT - JSON Web Tokens
- Recordar Sesion - Checkbox para extender tokens:
Sin recordar 30 dias de sesion
Con recordar 90 dias de sesion
- Refresh Tokens renovacion automatica de sesion
- Interceptor HTTP anexion automatica de tokens en todas las peticiones
- Multi-tenant cada usuario ve solo sus datos
- Sesion Persistente datos guardados en localStorage

# Proyectos
- CRUD completo crear, leer, actualizar y eliminar
- Archivar y restaurar proyectos
- Filtro por estado activos / archivados
- Busqueda por nombre
- Contador de tareas por proyecto

# Tareas
- Estados = Pendiente  En Progreso  Completada
- Prioridades = Baja  Media  Alta  Urgente
- Filtros Avanzados = Proyecto, estado, prioridad, etiquetas, rango de fechas, tareas vencidas
- Deadlines = detección automática de tareas vencidas
- Etiquetas Multiples = relacion con colores personalizados
- Checklist = Subtareas dentro de tareas
- Comentarios = notas colaborativas por tarea
- Registro de Actividad = auditoria automática de cambios
- Vista Kanban = arrastrar y soltar entre columnas
- Exportar Excel = descarga en formato .xlsx
- Recordatorios = panel de tareas proximas a vencer

# Panel de Control
- Estadisticas Proyectos activos, tareas pendientes y completadas, vencidas
- Graficas: 
Tareas por prioridad (Doughnut)
Creadas vs Completadas (Línea)
Completadas por semana (Barras)
Tareas por proyecto (Barras)
- Etiquetas Mas Usadas: Top 5 con contador
- Progreso General barra de progreso con porcentaje

# Inicio Rápido
### Con Docker (Lo Recomiendo para evitar problemas)
1. Copiar configuración del ambiente
cp .env.example .env

2. Levantar todos los servicios
docker-compose up --build

3. Crear tablas y datos iniciales
docker exec -it tareas_api python -c \
  "from app import create_app, db; \
   app=create_app(); \
   app.app_context().push(); \
   db.create_all()"
 
4. Ejecutar seed de datos (datros basicos para el funcionamineto y pruebas)
docker exec -it tareas_api python seed.py

URLs de Acceso:
- Frontend: http://localhost:4200
- API: http://localhost:5000/api/v1
- MySQL: localhost:1219

# Sin Docker (Desarrollo Local y pruebas)
cd backend

1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows

2. Instalar dependencias
pip install -r requirements.txt

# Configurar Base de Datos
1. Crear BD CREATE DATABASE tareas_proyectos;
2. Editar config.py con credenciales MySQL

3. Inicializar BD
python -c \
  "from app import create_app, db; \
   app=create_app(); \
   app.app_context().push(); \
   db.create_all()"

4. Llenar con datos de prueba
python seed.py

# Iniciar servidor (http://localhost:5000)
python run.py
cd frontend
npm install
ng serve --open

# Usuario Demo
Use estas credenciales para probar el sistema:
Correo:  demo@ejemplo.com
Contraseña:  Demo1234 

# Reglas de Negocio

1. Multi-tenant Seguro un usuario SOLO ve sus proyectos y tareas
2. Jerarquia una tarea siempre pertenece a un proyecto
3. Etiquetas N:N una tarea puede tener multiples etiquetas
4. Cierre Automatico si tarea = Completada se asigna fecha de completación
5. Overdue Automatico tarea vencida si fecha_vencimiento < hoy Y estado diferente a Completada
6. Auditoria todos los cambios se registran automaticamente
7. Refresh Token Flexible 30 días por defecto 90 dias si marco "Recordar Sesión"
8. Cascade Delete eliminar proyecto elimina tareas asociadas

------------------------------------------------------------------

#  Licencia
Proyecto de codigo abierto libre para uso educativo y comercial

# Proposito Educativo
Este proyecto fue desarrollado de forma local como iniciativa de aprendizaje y práctica para adquirir y mejorar en:
- Angular 19 Framework 
- Flask Backend ligero y flexible 
- TypeScript 
- RxJS Programacion reactiva
- SQLAlchemy ORM avanzado 
- JWT Autenticación segura con tokens
- Docker & Docker Compose para containers
- PrimeNG Componentes

# Mejoras Futuras Planeadas (que algun dia llegaran XD)
En versiones proximas se agregarasn las siguientes caracteristicas:

# Seguridad & Autenticacion
- 2FA (Two-Factor Authentication) Códigos TOTP
- Roles y Permisos Administrador, Jefe, Usuario, Visualizador
- Auditoria de Seguridad Logs de accesos y cambios sensibles

# Colaboracion
- Compartir Proyectos Permisos por usuario (read, edit, admin)
- Equipos Agrupación de usuarios para proyectos comunes
- Invitaciones Agregar miembros a proyectos
- Comentarios Anidados Respuestas a comentarios
- Historial de Cambios Detallado Quien cambio quq y cuando
- Notificaciones en Tiempo Real con WebSockets

# Funcionalidad
- Recurrencia de Tareas Tareas que se repiten (diaria, semanal, mensual)
- Calendario Integrado Vista de tareas por fecha

# UI/UX
- Modo Oscuro Completo
- Mejor compatibilidad Movil