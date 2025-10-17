#!/bin/bash
#
# Script para transferir el proyecto a Oracle Cloud VM
# Uso: ./deploy_to_vm.sh <IP_VM>
#

if [ -z "$1" ]; then
    echo "❌ Error: Debes proporcionar la IP de la VM"
    echo ""
    echo "Uso: ./deploy_to_vm.sh <IP_VM>"
    echo "Ejemplo: ./deploy_to_vm.sh 132.145.123.45"
    exit 1
fi

VM_IP="$1"
VM_USER="ubuntu"

# Buscar la clave SSH (acepta múltiples nombres)
if [ -f "$HOME/.ssh/oracle-vm-key.pem" ]; then
    SSH_KEY="$HOME/.ssh/oracle-vm-key.pem"
elif [ -f "$HOME/.ssh/ssh-key-2025-10-15.key" ]; then
    SSH_KEY="$HOME/.ssh/ssh-key-2025-10-15.key"
else
    # Buscar cualquier archivo .key en .ssh
    SSH_KEY=$(find "$HOME/.ssh" -name "*.key" -o -name "*oracle*.pem" 2>/dev/null | head -n 1)
fi

VM_TARGET="$VM_USER@$VM_IP"

echo "======================================================================="
echo "  DESPLIEGUE A ORACLE CLOUD VM"
echo "  Email Order Monitoring Agent"
echo "======================================================================="
echo ""
echo "Destino: $VM_TARGET"
echo ""

# Verificar que existe la clave SSH
if [ -z "$SSH_KEY" ] || [ ! -f "$SSH_KEY" ]; then
    echo "❌ No se encuentra ninguna clave SSH de Oracle"
    echo "   Archivos buscados:"
    echo "   - ~/.ssh/oracle-vm-key.pem"
    echo "   - ~/.ssh/ssh-key-2025-10-15.key"
    echo "   - Cualquier archivo .key en ~/.ssh/"
    echo ""
    echo "   Verifica que descargaste la clave y está en ~/.ssh/"
    echo "   Archivos actuales en ~/.ssh:"
    ls -1 "$HOME/.ssh/" 2>/dev/null | grep -E '\.(key|pem)$' || echo "   (ninguno encontrado)"
    exit 1
fi

echo "🔑 Usando clave SSH: $SSH_KEY"

# Corregir permisos si es necesario
chmod 400 "$SSH_KEY" 2>/dev/null

# Verificar conexión SSH
echo "🔍 Verificando conexión SSH..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$VM_TARGET" exit 2>/dev/null; then
    echo "❌ No se puede conectar a $VM_TARGET"
    echo "   Asegúrate de que:"
    echo "   1. La IP es correcta: $VM_IP"
    echo "   2. La VM está corriendo en Oracle Cloud"
    echo "   3. Las reglas de firewall permiten SSH (puerto 22)"
    exit 1
fi

echo "✅ Conexión SSH exitosa"
echo ""

# Archivos a transferir (excluir venv, logs, cache, etc.)
echo "📦 Preparando archivos para transferir..."

EXCLUDE_PATTERNS=(
    "--exclude=venv"
    "--exclude=__pycache__"
    "--exclude=*.pyc"
    "--exclude=.DS_Store"
    "--exclude=logs/*.log"
    "--exclude=logs/processed_emails.txt"
    "--exclude=.env"
    "--exclude=*.tar.gz"
)

# Crear lista de archivos a transferir
FILES=(
    "*.py"
    "requirements.txt"
    ".env.example"
    "setup_vm.sh"
    "setup_systemd.sh"
    "DEPLOYMENT_GUIDE.md"
    "HEARTBEAT_INFO.md"
    "README.md"
)

echo "📤 Transferiendo archivos a VM..."
echo ""

# Crear directorio remoto si no existe
ssh -i "$SSH_KEY" "$VM_TARGET" "mkdir -p ~/apps/email-order-agent/logs"

# Transferir archivos Python principales
echo "📤 Transfiriendo archivos Python..."
scp -i "$SSH_KEY" \
    main.py \
    config.py \
    imap_client.py \
    whatsapp_notifier.py \
    pdf_processor.py \
    claude_analyzer.py \
    reopen_whatsapp_window.py \
    "$VM_TARGET:~/apps/email-order-agent/"

# Transferir requirements
echo "📤 Transfiriendo requirements..."
scp -i "$SSH_KEY" requirements_vm.txt "$VM_TARGET:~/apps/email-order-agent/requirements.txt"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Archivos transferidos exitosamente"
else
    echo ""
    echo "❌ Error al transferir archivos"
    exit 1
fi

# Copiar .env si existe (con confirmación)
if [ -f ".env" ]; then
    echo ""
    read -p "¿Deseas transferir también el archivo .env con credenciales? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "📤 Transfiriendo .env..."
        scp -i "$SSH_KEY" .env "$VM_TARGET:~/apps/email-order-agent/"
        echo "✅ .env transferido"
    else
        echo "⏭️  .env no transferido (deberás configurarlo manualmente)"
    fi
fi

# Instalar Python y dependencias en la VM
echo ""
echo "🔧 Configurando entorno en la VM..."
ssh -i "$SSH_KEY" "$VM_TARGET" << 'ENDSSH'
cd ~/apps/email-order-agent

# Instalar Python y herramientas si no están instaladas
if ! command -v python3 &> /dev/null; then
    echo "📦 Instalando Python3 y herramientas..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv tmux htop
fi

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar e instalar dependencias
echo "📚 Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "✅ Configuración completada"
ENDSSH

echo ""
echo "======================================================================="
echo "  ✅ DEPLOYMENT COMPLETADO"
echo "======================================================================="
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1️⃣  Conectarte a la VM:"
echo "   ssh -i $SSH_KEY $VM_TARGET"
echo ""
echo "2️⃣  Verificar que .env está configurado:"
echo "   cd ~/apps/email-order-agent"
echo "   cat .env"
echo ""
echo "3️⃣  Probar el agente:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo "   (Ctrl+C para detener)"
echo ""
echo "4️⃣  Si funciona, ejecutar en tmux para 24/7:"
echo "   tmux new -s email-agent"
echo "   cd ~/apps/email-order-agent"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo "   (Ctrl+B, luego D para salir sin detener)"
echo ""
echo "5️⃣  Para reconectar más tarde:"
echo "   ssh -i $SSH_KEY $VM_TARGET"
echo "   tmux attach -t email-agent"
echo ""
echo "✅ ¡Listo para usar!"
