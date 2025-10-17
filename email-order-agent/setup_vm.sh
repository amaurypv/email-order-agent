#!/bin/bash
#
# Script de instalación para VM Oracle Cloud
# Prepara el entorno para ejecutar el agente de monitoreo de órdenes
#

set -e  # Salir si hay errores

echo "======================================================================="
echo "  INSTALACIÓN DEL AGENTE DE MONITOREO DE ÓRDENES DE COMPRA"
echo "  Oracle Cloud VM Setup"
echo "======================================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que se ejecuta como usuario normal (no root)
if [ "$EUID" -eq 0 ]; then
   echo -e "${YELLOW}⚠️  No ejecutes este script como root. Usa tu usuario normal.${NC}"
   exit 1
fi

echo -e "${BLUE}📦 Paso 1: Actualizando sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${BLUE}📦 Paso 2: Instalando dependencias del sistema...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

echo ""
echo -e "${BLUE}📂 Paso 3: Creando directorio de la aplicación...${NC}"
APP_DIR="$HOME/email-order-agent"

if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}⚠️  El directorio $APP_DIR ya existe.${NC}"
    read -p "¿Deseas sobrescribirlo? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Eliminando directorio existente..."
        rm -rf "$APP_DIR"
    else
        echo "Instalación cancelada."
        exit 1
    fi
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo ""
echo -e "${BLUE}🐍 Paso 4: Creando entorno virtual de Python...${NC}"
python3 -m venv venv
source venv/bin/activate

echo ""
echo -e "${BLUE}📚 Paso 5: Instalando dependencias de Python...${NC}"
pip install --upgrade pip

# Crear requirements.txt temporal si no existe
cat > requirements.txt << 'EOF'
# Core dependencies
anthropic>=0.40.0
twilio>=9.0.0
python-dotenv>=1.0.0
schedule>=1.2.0

# PDF processing
pdfplumber>=0.11.0

# Utilities
python-dateutil>=2.8.2
EOF

pip install -r requirements.txt

echo ""
echo -e "${BLUE}📝 Paso 6: Configurando archivo .env...${NC}"
cat > .env.example << 'EOF'
# IMAP Configuration
IMAP_SERVER=mail.quimicaguba.com
IMAP_PORT=993
IMAP_USER=ventas@quimicaguba.com
IMAP_PASSWORD=TU_PASSWORD_AQUI

# Claude API (Anthropic)
ANTHROPIC_API_KEY=TU_API_KEY_AQUI

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=TU_ACCOUNT_SID
TWILIO_AUTH_TOKEN=TU_AUTH_TOKEN
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+521XXXXXXXXXX

# Monitoring Configuration
CHECK_INTERVAL_MINUTES=5
DAYS_BACK_TO_SEARCH=1

# Monitored Client Emails (comma-separated)
MONITORED_CLIENTS=email1@example.com,email2@example.com
EOF

echo ""
echo -e "${GREEN}✅ Instalación básica completada!${NC}"
echo ""
echo -e "${YELLOW}SIGUIENTES PASOS:${NC}"
echo ""
echo "1. Copia tus archivos Python al directorio:"
echo "   ${APP_DIR}"
echo ""
echo "2. Crea el archivo .env con tus credenciales:"
echo "   cd ${APP_DIR}"
echo "   cp .env.example .env"
echo "   nano .env  # Edita y agrega tus credenciales"
echo ""
echo "3. Prueba la aplicación:"
echo "   source venv/bin/activate"
echo "   python test_whatsapp.py"
echo ""
echo "4. Ejecuta el script de configuración del servicio systemd:"
echo "   ./setup_systemd.sh"
echo ""
echo -e "${GREEN}Directorio de instalación: ${APP_DIR}${NC}"
