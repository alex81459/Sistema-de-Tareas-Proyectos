@echo off
chcp 65001 >nul
title Sistema de Tareas y Proyectos - TaskFlowAS

echo ============================================
echo   Sistema de Tareas y Proyectos - TaskFlowAS
echo ============================================
echo.

:: ── Verificar requisitos ──
echo [1/7] Verificando requisitos...

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no encontrado. Instálalo desde https://python.org
    pause
    exit /b 1
)

where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no encontrado. Instálalo desde https://nodejs.org
    pause
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm no encontrado.
    pause
    exit /b 1
)

echo    ✓ Python encontrado
echo    ✓ Node.js encontrado
echo    ✓ npm encontrado
echo.

:: ── Directorio raíz ──
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

:: ── Backend: entorno virtual ──
echo [2/7] Configurando entorno virtual de Python...
cd backend

if not exist "venv" (
    python -m venv venv
    echo    ✓ Entorno virtual creado
) else (
    echo    ✓ Entorno virtual ya existe
)

call venv\Scripts\activate.bat

:: ── Backend: dependencias ──
echo.
echo [3/7] Instalando dependencias del backend...
pip install -r requirements.txt --quiet
echo    ✓ Dependencias del backend instaladas
echo.

:: ── Backend: crear tablas ──
echo [4/7] Creando tablas en la base de datos...
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('   ✓ Tablas creadas')"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo conectar a MySQL.
    echo    Asegúrate de que MySQL esté corriendo y que la BD 'tareas_proyectos' exista.
    echo.
    echo    Ejecuta en MySQL:
    echo    CREATE DATABASE tareas_proyectos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    echo.
    echo    Y verifica la conexión en backend\config.py
    pause
    exit /b 1
)
echo.

:: ── Backend: seed ──
echo [5/7] Cargando datos iniciales...
python seed.py
echo.

:: ── Frontend: dependencias ──
echo [6/7] Instalando dependencias del frontend...
cd "%ROOT_DIR%frontend"

if not exist "node_modules" (
    call npm install
    echo    ✓ Dependencias del frontend instaladas
) else (
    echo    ✓ node_modules ya existe
)
echo.

:: ── Arrancar todo ──
echo [7/7] Iniciando servicios...
echo.
echo ============================================
echo   Iniciando Backend (Flask) en puerto 5000
echo   Iniciando Frontend (Angular) en puerto 4200
echo ============================================
echo.
echo   Backend:  http://localhost:5000/api/v1
echo   Frontend: http://localhost:4200
echo.
echo   Usuario demo: demo@ejemplo.com / Demo1234
echo.
echo   Presiona Ctrl+C para detener ambos servicios
echo ============================================
echo.

:: Iniciar backend en segundo plano
cd "%ROOT_DIR%backend"
start "TaskFlowAS - Backend" cmd /k "call venv\Scripts\activate.bat && python run.py"

:: Iniciar frontend (queda en primer plano)
cd "%ROOT_DIR%frontend"
start "TaskFlowAS - Frontend" cmd /k "npx ng serve --open"

echo.
echo Ambos servicios iniciados en ventanas separadas.
echo Cierra esta ventana cuando quieras.
pause
