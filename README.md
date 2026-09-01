# Sistema de Tareas y Proyectos (TaskFlowAS)

TaskFlowAS es una aplicación para organizar proyectos y tareas con autenticación, colaboración, control de permisos, filtros avanzados, paginación, auditoría y panel de estadísticas.

<img width="1917" height="926" alt="Panel principal de TaskFlowAS" src="https://github.com/user-attachments/assets/5d8550e0-4607-40ec-81d2-4e962905517d" />

## Tecnologías

- Frontend: Angular 19, PrimeNG, PrimeFlex y Chart.js.
- Backend: Flask, SQLAlchemy, Flask-Migrate y JWT sobre Python 3.12.
- Base de datos: MySQL 8.
- Infraestructura: Docker, Docker Compose, Gunicorn y Nginx.

## Características

### Autenticación y seguridad

- Registro e inicio de sesión con access y refresh tokens.
- Refresh token almacenado en cookie `HttpOnly`, con protección CSRF.
- Sesiones de 30 días o 90 días al seleccionar «Recordar sesión».
- Rate limiting por IP y bloqueo temporal tras intentos fallidos.
- Invalidación de sesiones al desactivar usuarios o restablecer contraseñas.
- Política de contraseña con longitud, mayúscula, minúscula, número y símbolo.
- Auditoría de accesos y operaciones sensibles.

### Proyectos y colaboración

- CRUD, archivado y restauración de proyectos.
- Miembros por proyecto con permisos de lectura, edición o administración.
- Asignación de tareas a participantes activos.
- Búsqueda, filtros y contadores por proyecto.

### Tareas

- Estados: pendiente, en progreso y completada.
- Prioridades: baja, media, alta y urgente.
- Fechas de vencimiento y detección automática de atrasos.
- Etiquetas múltiples, checklists, comentarios y menciones.
- Registro de actividad, vista Kanban y recordatorios.
- Exportación a Excel.

### Roles

- Administrador: acceso total, usuarios y auditoría.
- Jefe: visualización global y gestión de proyectos y tareas.
- Usuario: gestión de los recursos a los que tiene acceso.
- Visualizador: acceso de solo lectura.

### Panel de control

- Resumen de proyectos y tareas.
- Tareas vencidas y próximas a vencer.
- Gráficos por prioridad, estado, semana y proyecto.
- Etiquetas más utilizadas y progreso general.

## Inicio rápido con Docker

Requisitos: Docker y Docker Compose.

1. Copia la configuración y reemplaza todos los valores de ejemplo:

```bash
cp .env.example .env
```

2. Construye e inicia los servicios:

```bash
docker compose up --build
```

El contenedor de la API ejecuta automáticamente `flask db upgrade` antes de iniciar Gunicorn.

3. Opcionalmente, carga datos demo para desarrollo:

```bash
docker exec -it tareas_api python seed.py
```

También puedes establecer `RUN_DEMO_SEED=true` en `.env` para cargar el seed durante el arranque. No lo habilites en producción.

### Servicios

- Frontend: <http://localhost>
- API: <http://localhost:5000/api/v1>
- MySQL: `localhost:3306`

## Desarrollo local

### Backend

```bash
cd backend
python -m venv venv
```

En Windows:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
flask --app run:app db upgrade
python run.py
```

En Linux o macOS:

```bash
source venv/bin/activate
pip install -r requirements.txt
flask --app run:app db upgrade
python run.py
```

La API estará disponible en <http://localhost:5000/api/v1>.

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

El frontend de desarrollo estará disponible en <http://localhost:4200>.

## Migraciones

Después de modificar un modelo:

```bash
cd backend
flask --app run:app db migrate -m "descripción del cambio"
flask --app run:app db upgrade
```

Revisa siempre la migración generada antes de aplicarla.

Las bases creadas antes de adoptar Alembic deben respaldarse, actualizarse una única vez con los SQL heredados de `db/` y registrarse mediante:

```bash
flask --app run:app db stamp head
```

No ejecutes la migración inicial sobre una base que ya contiene las tablas.

## Datos demo

El seed crea usuarios de prueba exclusivamente para desarrollo. Sus credenciales se muestran al ejecutar `python seed.py`. El backend bloquea el seed cuando `APP_ENV=production`, salvo habilitación explícita con `ALLOW_DEMO_SEED=true`.

## Reglas de negocio

1. Los usuarios solo acceden a proyectos propios o compartidos, salvo los roles con visibilidad global.
2. Cada tarea pertenece a un proyecto.
3. Los permisos de proyecto son lectura, edición y administración.
4. Solo los participantes activos pueden recibir tareas o ser mencionados.
5. Completar una tarea registra automáticamente su fecha de finalización.
6. Una tarea está vencida cuando su fecha límite ya pasó y no está completada.
7. Los cambios relevantes se registran en la auditoría.
8. Eliminar un proyecto elimina sus tareas relacionadas mediante cascada.

## Mejoras futuras

### Seguridad

- Autenticación de dos factores mediante TOTP.
- Recuperación de contraseña por correo.

### Colaboración

- Equipos reutilizables para varios proyectos.
- Invitaciones con aceptación y vencimiento.
- Respuestas anidadas en comentarios.
- Notificaciones en tiempo real mediante WebSockets.

### Funcionalidad

- Tareas recurrentes.
- Vista de calendario.
- Historial detallado por campo.

### Interfaz

- Mejoras adicionales de accesibilidad y experiencia móvil.

## Licencia

Proyecto de código abierto para uso educativo y comercial.
