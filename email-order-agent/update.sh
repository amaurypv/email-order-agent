#!/bin/bash

#############################################################################
# Script de Actualización Automática - Email Order Agent
#
# Este script automatiza el proceso de actualización del código desde GitHub
#
# Uso: ./update.sh
#############################################################################

set -e  # Detener si hay algún error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "================================================================"
echo "  Email Order Agent - Actualización Automática"
echo "================================================================"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: No se encontró main.py${NC}"
    echo "Asegúrate de ejecutar este script desde ~/apps/email-order-agent"
    exit 1
fi

# Paso 1: Detener el agente si está corriendo
echo -e "${YELLOW}[1/5] Verificando si el agente está corriendo...${NC}"
if pgrep -f "python3.*main.py" > /dev/null; then
    echo -e "${YELLOW}      Deteniendo agente...${NC}"
    pkill -f "python3.*main.py" || true
    sleep 2
    echo -e "${GREEN}      ✓ Agente detenido${NC}"
else
    echo -e "${GREEN}      ✓ Agente no estaba corriendo${NC}"
fi

# Paso 2: Hacer fetch de GitHub
echo -e "${YELLOW}[2/5] Descargando cambios desde GitHub...${NC}"
if git fetch origin main 2>/dev/null; then
    echo -e "${GREEN}      ✓ Cambios descargados${NC}"
else
    echo -e "${RED}      ❌ Error al descargar desde GitHub${NC}"
    echo "      Verifica tu conexión a internet"
    exit 1
fi

# Paso 3: Verificar si hay nuevos commits
echo -e "${YELLOW}[3/5] Verificando actualizaciones...${NC}"
LOCAL_COMMIT=$(git log origin/main --oneline -1 2>/dev/null | awk '{print $1}')
echo -e "      Último commit en GitHub: ${BLUE}${LOCAL_COMMIT}${NC}"

# Obtener lista de archivos Python en el repo
PYTHON_FILES=$(git ls-tree -r origin/main --name-only | grep "email-order-agent/.*\.py$" | sed 's/email-order-agent\///')

if [ -z "$PYTHON_FILES" ]; then
    echo -e "${RED}      ❌ No se encontraron archivos Python en el repositorio${NC}"
    exit 1
fi

# Paso 4: Actualizar archivos Python
echo -e "${YELLOW}[4/5] Actualizando archivos...${NC}"
UPDATED_COUNT=0
for file in $PYTHON_FILES; do
    if git show origin/main:email-order-agent/$file > $file 2>/dev/null; then
        echo -e "${GREEN}      ✓ Actualizado: ${file}${NC}"
        UPDATED_COUNT=$((UPDATED_COUNT + 1))
    else
        echo -e "${YELLOW}      ⚠ No se pudo actualizar: ${file}${NC}"
    fi
done

echo -e "${GREEN}      ✓ ${UPDATED_COUNT} archivos actualizados${NC}"

# Paso 5: Reiniciar el agente en tmux
echo -e "${YELLOW}[5/5] Reiniciando agente en tmux...${NC}"

# Verificar si hay una sesión de tmux activa
if tmux has-session 2>/dev/null; then
    # Hay sesión activa, enviar comandos
    TMUX_SESSION=$(tmux list-sessions -F "#{session_name}" | head -n 1)
    echo -e "      Usando sesión de tmux: ${BLUE}${TMUX_SESSION}${NC}"

    # Matar cualquier proceso Python que pueda quedar
    tmux send-keys -t $TMUX_SESSION C-c 2>/dev/null || true
    sleep 1

    # Activar venv y ejecutar main.py
    tmux send-keys -t $TMUX_SESSION "cd ~/apps/email-order-agent && source venv/bin/activate && python3 main.py" C-m

    echo -e "${GREEN}      ✓ Agente reiniciado en tmux${NC}"
else
    # No hay sesión, crear una nueva
    echo -e "      Creando nueva sesión de tmux..."
    tmux new-session -d -s email-agent "cd ~/apps/email-order-agent && source venv/bin/activate && python3 main.py"
    echo -e "${GREEN}      ✓ Agente iniciado en nueva sesión: email-agent${NC}"
fi

# Resumen final
echo -e ""
echo -e "${GREEN}================================================================"
echo -e "  ✓ Actualización completada exitosamente"
echo -e "================================================================${NC}"
echo -e ""
echo -e "Información:"
echo -e "  • Commit aplicado: ${BLUE}${LOCAL_COMMIT}${NC}"
echo -e "  • Archivos actualizados: ${GREEN}${UPDATED_COUNT}${NC}"
echo -e ""
echo -e "Comandos útiles:"
echo -e "  ${BLUE}tmux attach${NC}         - Ver el agente en ejecución"
echo -e "  ${BLUE}tail -f logs/email_monitor.log${NC} - Ver logs en tiempo real"
echo -e ""
echo -e "${YELLOW}Presiona Ctrl+B, luego D para salir de tmux sin detener el agente${NC}"
echo -e ""
