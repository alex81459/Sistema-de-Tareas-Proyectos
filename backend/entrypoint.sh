#!/bin/sh
set -e

echo "=== Aplicando migraciones ==="
cd /app
flask --app run:app db upgrade

if [ "${RUN_DEMO_SEED:-false}" = "true" ]; then
    echo "=== Ejecutando seed demo ==="
    python seed.py
fi

echo "=== Iniciando API ==="
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
