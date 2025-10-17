# Guía de Deployment desde GitHub a Oracle VM

Esta guía explica cómo desplegar el agente de monitoreo de emails desde GitHub a una VM de Oracle Cloud, ideal para instalaciones limpias o actualizaciones.

## Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Opción A: Instalación Nueva](#opción-a-instalación-nueva)
3. [Opción B: Migración desde Instalación Manual](#opción-b-migración-desde-instalación-manual)
4. [Configuración y Pruebas](#configuración-y-pruebas)
5. [Configurar Servicio Systemd](#configurar-servicio-systemd)
6. [Actualizaciones desde GitHub](#actualizaciones-desde-github)

---

## Requisitos Previos

### En Oracle Cloud

- VM creada y corriendo (Ubuntu 20.04+ recomendado)
- IP pública asignada
- Acceso SSH configurado
- Reglas de firewall para SSH (puerto 22)

### En tu máquina local

- Llave SSH para conectar a la VM
- Credenciales preparadas:
  - IMAP (servidor, usuario, password)
  - Anthropic API Key (Claude)
  - Telegram Bot Token y Chat ID (o Twilio si usas WhatsApp)

---

## Opción A: Instalación Nueva

Para VMs nuevas o primeras instalaciones.

### 1. Conectar a la VM

```bash
# Desde tu Mac/PC local
ssh -i ~/.ssh/oracle_vm ubuntu@<IP_PUBLICA>
```

### 2. Instalar dependencias del sistema

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Python, Git y herramientas
sudo apt install -y python3 python3-pip python3-venv git tmux htop

# Verificar versiones
python3 --version  # Debe ser 3.9+
git --version
```

### 3. Clonar repositorio desde GitHub

```bash
# Crear estructura de directorios
mkdir -p ~/apps
cd ~/apps

# Clonar repositorio
git clone https://github.com/amaurypv/email-order-agent.git
cd email-order-agent

# Verificar que se clonó correctamente
ls -la
```

### 4. Configurar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Configurar todas las variables necesarias:

```env
# IMAP Configuration
IMAP_SERVER=mail.tudominio.com
IMAP_PORT=993
IMAP_USER=tu-email@tudominio.com
IMAP_PASSWORD=tu_password_real

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx_tu_key_real

# Notification Provider (telegram o twilio)
NOTIFICATION_PROVIDER=telegram

# Telegram (RECOMENDADO)
TELEGRAM_BOT_TOKEN=1234567890:ABCdef_tu_token_real
TELEGRAM_CHAT_ID=tu_chat_id_real

# Twilio WhatsApp (opcional)
TWILIO_ACCOUNT_SID=ACxxxxxx
TWILIO_AUTH_TOKEN=tu_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+52XXXXXXXXXX

# Monitoring
CHECK_INTERVAL_MINUTES=10
DAYS_BACK_TO_SEARCH=1

# Monitored Clients
MONITORED_CLIENTS=cliente1@email.com,cliente2@email.com
```

Guardar: `Ctrl+O`, Enter, `Ctrl+X`

### 6. Crear directorios necesarios

```bash
# Crear directorio de logs
mkdir -p logs
```

### 7. Probar la instalación

```bash
# Con entorno virtual activado
source venv/bin/activate

# Ejecutar el agente
python3 main.py

# Deberías ver:
# - Banner del sistema
# - Configuración validada
# - Notificación de inicio enviada
# - Sistema monitoreando emails

# Detener con: Ctrl+C
```

---

## Opción B: Migración desde Instalación Manual

Si ya tienes el agente corriendo desde archivos transferidos manualmente.

### Estrategia: Instalación Paralela (Sin interrumpir servicio actual)

```bash
# 1. Conectar a VM
ssh -i ~/.ssh/oracle_vm ubuntu@<IP_PUBLICA>

# 2. Verificar servicio actual
tmux ls
# Deberías ver: email-agent (o similar)

# 3. Clonar repositorio en directorio paralelo
cd ~/apps
git clone https://github.com/amaurypv/email-order-agent.git email-order-agent-github
cd email-order-agent-github

# 4. Configurar entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Copiar configuración desde instalación actual
cp ~/apps/email-order-agent/.env .

# 6. Verificar que el .env es correcto
cat .env

# 7. Probar nueva instalación (en nueva sesión tmux)
tmux new -s test-github

cd ~/apps/email-order-agent-github
source venv/bin/activate
python3 main.py

# Observar que funciona correctamente
# Salir: Ctrl+B, luego D
```

### Migrar a la nueva versión (cuando estés listo)

```bash
# 1. Detener servicio actual
tmux attach -t email-agent
# Presionar Ctrl+C para detener

# 2. Hacer backup de instalación antigua
cd ~/apps
mv email-order-agent email-order-agent-backup-$(date +%Y%m%d)

# 3. Renombrar nueva instalación
mv email-order-agent-github email-order-agent

# 4. Iniciar desde nueva instalación
cd ~/apps/email-order-agent
source venv/bin/activate
python3 main.py

# 5. Si todo funciona bien, puedes eliminar backup después
# rm -rf ~/apps/email-order-agent-backup-YYYYMMDD
```

### Rollback si hay problemas

```bash
# Detener nueva versión
# Presionar Ctrl+C en tmux

# Restaurar versión anterior
cd ~/apps
mv email-order-agent email-order-agent-github-failed
mv email-order-agent-backup-YYYYMMDD email-order-agent

# Reiniciar versión antigua
cd email-order-agent
source venv/bin/activate
python3 main.py
```

---

## Configuración y Pruebas

### Verificar conectividad IMAP

```bash
# Activar entorno virtual
source venv/bin/activate

# El script main.py hace esto automáticamente al iniciar
# Si ves errores de IMAP, verifica:
# - IMAP_SERVER es correcto
# - Puerto 993 está abierto
# - Credenciales son correctas
```

### Probar notificaciones

```bash
# Para Telegram
source venv/bin/activate
python3 -c "
from telegram_notifier import TelegramNotifier
notifier = TelegramNotifier()
notifier.send_test_message()
"

# Para WhatsApp (Twilio)
python3 test_whatsapp.py
```

---

## Configurar Servicio Systemd

Para que el agente corra 24/7 automáticamente y se reinicie en caso de fallas.

### 1. Ejecutar script de configuración

```bash
cd ~/apps/email-order-agent

# Dar permisos de ejecución
chmod +x setup_systemd.sh

# Ejecutar
./setup_systemd.sh
```

### 2. Administrar el servicio

```bash
# Iniciar servicio
sudo systemctl start email-order-agent

# Habilitar auto-inicio en boot
sudo systemctl enable email-order-agent

# Ver estado
sudo systemctl status email-order-agent

# Ver logs en tiempo real
sudo journalctl -u email-order-agent -f

# Detener servicio
sudo systemctl stop email-order-agent

# Reiniciar servicio
sudo systemctl restart email-order-agent
```

---

## Actualizaciones desde GitHub

Cuando hagas cambios en el código y los subas a GitHub.

### Actualizar código en la VM

```bash
# 1. Conectar a VM
ssh -i ~/.ssh/oracle_vm ubuntu@<IP_PUBLICA>

# 2. Ir al directorio del proyecto
cd ~/apps/email-order-agent

# 3. Detener el servicio (si usa systemd)
sudo systemctl stop email-order-agent

# O detener tmux (si usas tmux)
tmux attach -t email-agent
# Ctrl+C

# 4. Hacer backup del .env (por seguridad)
cp .env .env.backup

# 5. Actualizar código desde GitHub
git pull origin main

# 6. Actualizar dependencias (si requirements.txt cambió)
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 7. Restaurar .env si fue sobrescrito
# (Git no debería tocarlo si está en .gitignore)
# Si es necesario:
cp .env.backup .env

# 8. Reiniciar servicio
sudo systemctl start email-order-agent

# O con tmux:
python3 main.py
```

### Script de actualización rápida

Puedes crear un script para automatizar actualizaciones:

```bash
# Crear script
nano ~/update-agent.sh
```

Contenido:

```bash
#!/bin/bash

echo "🔄 Actualizando Email Order Agent..."

# Detener servicio
echo "⏸️  Deteniendo servicio..."
sudo systemctl stop email-order-agent

# Ir al directorio
cd ~/apps/email-order-agent

# Backup .env
echo "💾 Backup de configuración..."
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)

# Actualizar código
echo "📥 Descargando actualizaciones..."
git pull origin main

# Actualizar dependencias
echo "📦 Actualizando dependencias..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Reiniciar servicio
echo "▶️  Reiniciando servicio..."
sudo systemctl start email-order-agent

echo "✅ Actualización completada!"
echo ""
echo "📊 Estado del servicio:"
sudo systemctl status email-order-agent --no-pager

echo ""
echo "📋 Ver logs:"
echo "sudo journalctl -u email-order-agent -f"
```

Dar permisos y usar:

```bash
chmod +x ~/update-agent.sh

# Ejecutar cuando quieras actualizar
~/update-agent.sh
```

---

## Estructura Final del Proyecto

```
~/apps/email-order-agent/
├── .env                          # Configuración (NO en Git)
├── .env.example                  # Plantilla de configuración
├── .gitignore                    # Archivos ignorados por Git
├── claude_analyzer.py            # Análisis con Claude AI
├── config.py                     # Gestión de configuración
├── imap_client.py                # Cliente IMAP
├── main.py                       # Punto de entrada principal
├── pdf_processor.py              # Procesamiento de PDFs
├── telegram_notifier.py          # Notificaciones Telegram
├── whatsapp_notifier.py          # Notificaciones WhatsApp
├── requirements.txt              # Dependencias Python
├── setup_systemd.sh              # Script de configuración systemd
├── setup_vm.sh                   # Script de setup para VM
├── venv/                         # Entorno virtual Python
└── logs/                         # Logs de aplicación
    ├── email_monitor.log         # Log principal
    └── processed_emails.txt      # Emails procesados
```

---

## Solución de Problemas

### Error: "git: command not found"

```bash
sudo apt update
sudo apt install -y git
```

### Error: "Permission denied (publickey)"

Verifica que estás usando la llave SSH correcta:

```bash
ssh -i ~/.ssh/oracle_vm ubuntu@<IP>
```

### Error al hacer git pull

```bash
# Si hay conflictos con archivos locales
git stash              # Guardar cambios locales
git pull origin main   # Actualizar
git stash pop          # Restaurar cambios locales
```

### Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u email-order-agent -n 50 --no-pager

# Verificar archivo .env
cat .env

# Probar manualmente
cd ~/apps/email-order-agent
source venv/bin/activate
python3 main.py
```

---

## Checklist de Deployment

### Instalación Nueva

- [ ] VM creada en Oracle Cloud
- [ ] SSH funcionando
- [ ] Python 3.9+ instalado
- [ ] Git instalado
- [ ] Repositorio clonado desde GitHub
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado con credenciales reales
- [ ] Directorio logs/ creado
- [ ] Prueba manual exitosa (`python3 main.py`)
- [ ] Servicio systemd configurado
- [ ] Servicio iniciado y corriendo
- [ ] Auto-inicio habilitado

### Migración desde Instalación Manual

- [ ] Backup de instalación actual
- [ ] Nueva instalación en paralelo
- [ ] .env copiado y verificado
- [ ] Prueba exitosa en sesión tmux paralela
- [ ] Migración completada
- [ ] Servicio anterior detenido
- [ ] Servicio nuevo corriendo
- [ ] Backup antiguo eliminado (después de confirmar)

---

## Ventajas de usar GitHub

✅ **Actualizaciones simples**: `git pull` en lugar de transferir archivos manualmente

✅ **Control de versiones**: Historial completo de cambios

✅ **Rollback fácil**: `git checkout` a versión anterior si hay problemas

✅ **Deployment consistente**: Misma versión en desarrollo y producción

✅ **Colaboración**: Múltiples desarrolladores pueden contribuir

✅ **Documentación integrada**: README y guías siempre actualizadas

---

## Recursos

- **Repositorio GitHub**: https://github.com/amaurypv/email-order-agent
- **Oracle Cloud Console**: https://cloud.oracle.com/
- **Documentación Git**: https://git-scm.com/doc

---

**¡Tu agente está listo para deployment profesional desde GitHub! 🚀**
