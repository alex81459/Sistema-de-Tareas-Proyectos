#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  TaskFlowAS - Inicio con Docker${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker no encontrado."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "[ERROR] docker-compose no encontrado."; exit 1; }

echo "[1/3] Construyendo e iniciando contenedores..."
docker-compose up --build -d
echo ""

echo "[2/3] Esperando a que MySQL esté listo (30s)..."
sleep 30
echo ""

echo "[3/3] Creando tablas y datos iniciales..."
docker exec -it tareas_api python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
docker exec -it tareas_api python seed.py
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "  ${GREEN}✓ Todo listo!${NC}"
echo ""
echo -e "  Frontend: ${GREEN}http://localhost${NC}"
echo -e "  API:      ${GREEN}http://localhost:5000/api/v1${NC}"
echo ""
echo -e "  Usuario:  ${YELLOW}demo@ejemplo.com${NC} / ${YELLOW}Demo1234${NC}"
echo ""
echo -e "  Para detener: docker-compose down"
echo -e "${BLUE}============================================${NC}"
