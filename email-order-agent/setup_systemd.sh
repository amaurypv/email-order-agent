#!/bin/bash
#
# Script para configurar el servicio systemd
# Permite que el agente se ejecute automáticamente al iniciar la VM
#

set -e

echo "======================================================================="
echo "  CONFIGURACIÓN DEL SERVICIO SYSTEMD"
echo "  Email Order Monitoring Agent"
echo "======================================================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar que no se ejecuta como root
if [ "$EUID" -eq 0 ]; then
   echo -e "${RED}❌ No ejecutes este script como root. Usa tu usuario normal.${NC}"
   exit 1
fi

# Obtener el directorio actual
APP_DIR="$(pwd)"
USER_NAME="$(whoami)"

echo -e "${BLUE}📋 Configuración:${NC}"
echo "   Usuario: $USER_NAME"
echo "   Directorio: $APP_DIR"
echo ""

# Verificar que existe main.py
if [ ! -f "$APP_DIR/main.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra main.py en $APP_DIR${NC}"
    echo "   Asegúrate de estar en el directorio correcto del proyecto."
    exit 1
fi

# Verificar que existe venv
if [ ! -d "$APP_DIR/venv" ]; then
    echo -e "${RED}❌ Error: No se encuentra el entorno virtual en $APP_DIR/venv${NC}"
    echo "   Ejecuta primero: ./setup_vm.sh"
    exit 1
fi

echo -e "${BLUE}📝 Paso 1: Creando archivo de servicio systemd...${NC}"

# Crear archivo de servicio
SERVICE_FILE="/tmp/email-order-agent.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Email Order Monitoring Agent
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Comando para ejecutar
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py

# Reiniciar si falla
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=email-order-agent

# Límites de recursos (opcional)
# LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Archivo de servicio creado${NC}"

echo ""
echo -e "${BLUE}📦 Paso 2: Instalando servicio systemd...${NC}"

# Copiar archivo de servicio
sudo cp "$SERVICE_FILE" /etc/systemd/system/email-order-agent.service
sudo chmod 644 /etc/systemd/system/email-order-agent.service

echo -e "${GREEN}✅ Servicio instalado en /etc/systemd/system/${NC}"

echo ""
echo -e "${BLUE}🔄 Paso 3: Recargando systemd...${NC}"
sudo systemctl daemon-reload

echo ""
echo -e "${BLUE}✅ Paso 4: Habilitando inicio automático...${NC}"
sudo systemctl enable email-order-agent.service

echo ""
echo -e "${GREEN}✅ Configuración completada!${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  COMANDOS ÚTILES:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Iniciar el servicio:"
echo "  sudo systemctl start email-order-agent"
echo ""
echo "Detener el servicio:"
echo "  sudo systemctl stop email-order-agent"
echo ""
echo "Ver estado del servicio:"
echo "  sudo systemctl status email-order-agent"
echo ""
echo "Ver logs en tiempo real:"
echo "  sudo journalctl -u email-order-agent -f"
echo ""
echo "Ver logs recientes:"
echo "  sudo journalctl -u email-order-agent -n 100"
echo ""
echo "Reiniciar el servicio:"
echo "  sudo systemctl restart email-order-agent"
echo ""
echo "Deshabilitar inicio automático:"
echo "  sudo systemctl disable email-order-agent"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}El servicio está configurado pero NO iniciado.${NC}"
echo -e "${GREEN}Para iniciarlo, ejecuta:${NC}"
echo ""
echo "  sudo systemctl start email-order-agent"
echo ""

# Limpiar archivo temporal
rm "$SERVICE_FILE"
