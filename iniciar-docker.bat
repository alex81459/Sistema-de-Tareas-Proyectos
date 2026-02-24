@echo off
chcp 65001 >nul
title TaskFlowAS - Docker

echo ============================================
echo   TaskFlowAS - Inicio con Docker
echo ============================================
echo.

where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker no encontrado. Instálalo desde https://docker.com
    pause
    exit /b 1
)

where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose no encontrado.
    pause
    exit /b 1
)

echo [1/3] Construyendo e iniciando contenedores...
docker-compose up --build -d
echo.

echo [2/3] Esperando a que MySQL esté listo (30s)...
timeout /t 30 /nobreak >nul
echo.

echo [3/3] Creando tablas y datos iniciales...
docker exec -it tareas_api python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
docker exec -it tareas_api python seed.py
echo.

echo ============================================
echo   ✓ Todo listo!
echo.
echo   Frontend: http://localhost
echo   API:      http://localhost:5000/api/v1
echo.
echo   Usuario:  demo@ejemplo.com / Demo1234
echo.
echo   Para detener: docker-compose down
echo ============================================
echo.
pause
