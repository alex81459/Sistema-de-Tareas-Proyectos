#!/bin/bash
#script para inicializar el proyecto

echo "=== Esperando a que la base de datos esté lista ==="
sleep 10

echo "=== Creando tablas ==="
cd /app
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Tablas creadas!')"

echo "=== Ejecutando seed ==="
python seed.py

echo "=== Iniciando API ==="
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
