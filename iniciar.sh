#!/bin/bash
set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Sistema de Tareas y Proyectos - TaskFlowAS${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Verificar requisitos ──
echo -e "[1/7] Verificando requisitos..."

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}[ERROR] Python3 no encontrado.${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}[ERROR] Node.js no encontrado.${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}[ERROR] npm no encontrado.${NC}"; exit 1; }

echo -e "   ${GREEN}✓${NC} Python encontrado"
echo -e "   ${GREEN}✓${NC} Node.js encontrado"
echo -e "   ${GREEN}✓${NC} npm encontrado"
echo ""

# ── Backend: entorno virtual ──
echo "[2/7] Configurando entorno virtual de Python..."
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "   ${GREEN}✓${NC} Entorno virtual creado"
else
    echo -e "   ${GREEN}✓${NC} Entorno virtual ya existe"
fi

source venv/bin/activate

# ── Backend: dependencias ──
echo ""
echo "[3/7] Instalando dependencias del backend..."
pip install -r requirements.txt --quiet
echo -e "   ${GREEN}✓${NC} Dependencias del backend instaladas"
echo ""

# ── Backend: crear tablas ──
echo "[4/7] Creando tablas en la base de datos..."
python3 -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('   ✓ Tablas creadas')" || {
    echo ""
    echo -e "${RED}[ERROR] No se pudo conectar a MySQL.${NC}"
    echo "   Asegúrate de que MySQL esté corriendo y que la BD 'tareas_proyectos' exista."
    echo ""
    echo "   Ejecuta en MySQL:"
    echo "   CREATE DATABASE tareas_proyectos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo ""
    exit 1
}
echo ""

# ── Backend: seed ──
echo "[5/7] Cargando datos iniciales..."
python3 seed.py
echo ""

# ── Frontend: dependencias ──
echo "[6/7] Instalando dependencias del frontend..."
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    npm install
    echo -e "   ${GREEN}✓${NC} Dependencias del frontend instaladas"
else
    echo -e "   ${GREEN}✓${NC} node_modules ya existe"
fi
echo ""

# ── Arrancar todo ──
echo "[7/7] Iniciando servicios..."
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "  Iniciando Backend (Flask) en puerto 5000"
echo -e "  Iniciando Frontend (Angular) en puerto 4200"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "  Backend:  ${GREEN}http://localhost:5000/api/v1${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:4200${NC}"
echo ""
echo -e "  Usuario demo: ${YELLOW}demo@ejemplo.com${NC} / ${YELLOW}Demo1234${NC}"
echo ""
echo -e "  Presiona Ctrl+C para detener ambos servicios"
echo -e "${BLUE}============================================${NC}"
echo ""

# Función de limpieza al salir
cleanup() {
    echo ""
    echo "Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "Servicios detenidos."
    exit 0
}
trap cleanup SIGINT SIGTERM

# Iniciar backend en segundo plano
cd "$ROOT_DIR/backend"
source venv/bin/activate
python3 run.py &
BACKEND_PID=$!
echo "Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que backend esté listo
sleep 3

# Iniciar frontend en segundo plano
cd "$ROOT_DIR/frontend"
npx ng serve --open &
FRONTEND_PID=$!
echo "Frontend iniciado (PID: $FRONTEND_PID)"

# Esperar a ambos procesos
wait $BACKEND_PID $FRONTEND_PID
