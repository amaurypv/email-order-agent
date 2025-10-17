#!/bin/bash

# Script de actualización automática del Email Order Agent desde GitHub
# Uso: ./update_from_github.sh

set -e  # Detener si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_DIR="$HOME/apps/email-order-agent"
SERVICE_NAME="email-order-agent"
BACKUP_DIR="$HOME/backups/email-order-agent"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔄 Email Order Agent - Actualización desde GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio $PROJECT_DIR no existe${NC}"
    echo -e "${YELLOW}💡 Ejecuta primero la instalación desde GitHub${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar que es un repositorio Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: $PROJECT_DIR no es un repositorio Git${NC}"
    echo -e "${YELLOW}💡 Esta instalación no fue hecha desde GitHub${NC}"
    exit 1
fi

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

# Verificar si hay cambios locales
echo -e "${YELLOW}🔍 Verificando cambios locales...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Hay cambios locales sin guardar${NC}"
    echo -e "${YELLOW}📦 Guardando cambios locales (git stash)...${NC}"
    git stash
    STASHED=true
else
    STASHED=false
    echo -e "${GREEN}✅ No hay cambios locales${NC}"
fi

# Backup del archivo .env
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
echo -e "${YELLOW}💾 Creando backup de .env...${NC}"
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup-$TIMESTAMP"
    echo -e "${GREEN}✅ Backup guardado: $BACKUP_DIR/.env.backup-$TIMESTAMP${NC}"
else
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
fi

# Backup de logs
echo -e "${YELLOW}💾 Creando backup de logs...${NC}"
if [ -d "logs" ]; then
    tar -czf "$BACKUP_DIR/logs-backup-$TIMESTAMP.tar.gz" logs/
    echo -e "${GREEN}✅ Logs respaldados: $BACKUP_DIR/logs-backup-$TIMESTAMP.tar.gz${NC}"
fi

# Verificar si el servicio está corriendo (systemd)
SERVICE_RUNNING=false
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    SERVICE_RUNNING=true
    echo -e "${YELLOW}⏸️  Deteniendo servicio systemd...${NC}"
    sudo systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}✅ Servicio detenido${NC}"
fi

# Actualizar código desde GitHub
echo -e "${BLUE}📥 Descargando actualizaciones desde GitHub...${NC}"
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}✅ Ya estás en la última versión${NC}"
else
    echo -e "${YELLOW}🔄 Actualizando código...${NC}"
    git pull origin main
    echo -e "${GREEN}✅ Código actualizado${NC}"
fi

# Restaurar cambios locales si fueron guardados
if [ "$STASHED" = true ]; then
    echo -e "${YELLOW}📦 Restaurando cambios locales...${NC}"
    git stash pop || echo -e "${YELLOW}⚠️  Algunos cambios pueden requerir resolución manual${NC}"
fi

# Activar entorno virtual y actualizar dependencias
echo -e "${BLUE}📦 Actualizando dependencias Python...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install --upgrade -r requirements.txt -q
echo -e "${GREEN}✅ Dependencias actualizadas${NC}"

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠️  Archivo .env no encontrado!${NC}"
    echo -e "${YELLOW}📋 Copiando desde .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ IMPORTANTE: Edita .env con tus credenciales reales${NC}"
    echo -e "${YELLOW}   nano .env${NC}"
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Crear directorios necesarios
mkdir -p logs

# Reiniciar servicio si estaba corriendo
if [ "$SERVICE_RUNNING" = true ]; then
    echo -e "${BLUE}▶️  Reiniciando servicio systemd...${NC}"
    sudo systemctl start "$SERVICE_NAME"
    sleep 2

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Servicio reiniciado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al reiniciar servicio${NC}"
        echo -e "${YELLOW}📋 Ver logs: sudo journalctl -u $SERVICE_NAME -n 50${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  El servicio no estaba corriendo antes de la actualización${NC}"
    echo -e "${YELLOW}💡 Para iniciar: sudo systemctl start $SERVICE_NAME${NC}"
fi

# Mostrar estado final
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Actualización completada!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Mostrar versión actual
CURRENT_COMMIT=$(git rev-parse --short HEAD)
CURRENT_DATE=$(git log -1 --format=%cd --date=short)
echo -e "${BLUE}📌 Versión actual:${NC}"
echo -e "   Commit: $CURRENT_COMMIT"
echo -e "   Fecha:  $CURRENT_DATE"
echo ""

# Mostrar estado del servicio
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${GREEN}📊 Estado del servicio: ACTIVO ✅${NC}"
else
    echo -e "${YELLOW}📊 Estado del servicio: INACTIVO${NC}"
fi

echo ""
echo -e "${BLUE}📋 Comandos útiles:${NC}"
echo -e "${YELLOW}   Ver logs:${NC}          sudo journalctl -u $SERVICE_NAME -f"
echo -e "${YELLOW}   Ver estado:${NC}        sudo systemctl status $SERVICE_NAME"
echo -e "${YELLOW}   Reiniciar:${NC}         sudo systemctl restart $SERVICE_NAME"
echo -e "${YELLOW}   Backups en:${NC}        $BACKUP_DIR"
echo ""

deactivate 2>/dev/null || true
