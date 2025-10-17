# Guía de Despliegue en Oracle Cloud VM

Esta guía te ayudará a instalar y configurar el agente de monitoreo de órdenes de compra en una VM de Oracle Cloud para que funcione 24/7.

## 📋 Requisitos Previos

- VM de Oracle Cloud con Ubuntu (recomendado: Ubuntu 20.04 o 22.04)
- Acceso SSH a la VM
- Usuario con permisos sudo

## 🚀 Instalación Paso a Paso

### 1. Conectar a la VM

```bash
ssh usuario@IP_DE_TU_VM
```

### 2. Transferir los archivos

Desde tu Mac, en el directorio del proyecto:

```bash
# Comprimir el proyecto
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO
tar -czf email-order-agent.tar.gz email-order-agent/

# Transferir a la VM
scp email-order-agent.tar.gz usuario@IP_DE_TU_VM:~/
```

### 3. Descomprimir en la VM

Desde la VM:

```bash
cd ~
tar -xzf email-order-agent.tar.gz
cd email-order-agent
```

### 4. Ejecutar instalación

```bash
# Dar permisos de ejecución
chmod +x setup_vm.sh setup_systemd.sh

# Ejecutar instalación
./setup_vm.sh
```

Este script instalará:
- Python 3 y pip
- Entorno virtual
- Todas las dependencias necesarias

### 5. Configurar credenciales

```bash
# Copiar ejemplo de .env
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Configura todas las variables:
- `IMAP_PASSWORD`: Tu contraseña de email
- `ANTHROPIC_API_KEY`: Tu API key de Claude
- `TWILIO_ACCOUNT_SID`: Tu Account SID de Twilio
- `TWILIO_AUTH_TOKEN`: Tu Auth Token de Twilio
- `TWILIO_WHATSAPP_TO`: Tu número de WhatsApp con formato `whatsapp:+521XXXXXXXXXX`
- `MONITORED_CLIENTS`: Lista de emails a monitorear

Guarda con `Ctrl+O`, Enter, `Ctrl+X`

### 6. Probar la instalación

```bash
# Activar entorno virtual
source venv/bin/activate

# Probar conexión de WhatsApp
python test_whatsapp.py
```

Deberías recibir un mensaje de prueba en WhatsApp.

### 7. Configurar servicio systemd

```bash
# Ejecutar configuración del servicio
./setup_systemd.sh
```

Esto configurará el agente para:
- ✅ Iniciarse automáticamente al arrancar la VM
- ✅ Reiniciarse si falla
- ✅ Ejecutarse en segundo plano

### 8. Iniciar el servicio

```bash
# Iniciar el servicio
sudo systemctl start email-order-agent

# Verificar estado
sudo systemctl status email-order-agent

# Ver logs en tiempo real
sudo journalctl -u email-order-agent -f
```

## 🔧 Comandos Útiles

### Gestión del Servicio

```bash
# Ver estado
sudo systemctl status email-order-agent

# Iniciar
sudo systemctl start email-order-agent

# Detener
sudo systemctl stop email-order-agent

# Reiniciar
sudo systemctl restart email-order-agent

# Habilitar inicio automático
sudo systemctl enable email-order-agent

# Deshabilitar inicio automático
sudo systemctl disable email-order-agent
```

### Ver Logs

```bash
# Logs en tiempo real
sudo journalctl -u email-order-agent -f

# Últimos 100 logs
sudo journalctl -u email-order-agent -n 100

# Logs desde hoy
sudo journalctl -u email-order-agent --since today

# Logs de las últimas 2 horas
sudo journalctl -u email-order-agent --since "2 hours ago"
```

### Actualizar el Código

Cuando hagas cambios:

```bash
# 1. Detener el servicio
sudo systemctl stop email-order-agent

# 2. Actualizar archivos
cd ~/email-order-agent
# ... copia tus archivos actualizados ...

# 3. Reiniciar servicio
sudo systemctl start email-order-agent

# 4. Verificar que inició correctamente
sudo systemctl status email-order-agent
```

## 🔒 Seguridad

### Firewall

Oracle Cloud tiene reglas de firewall a nivel de consola. Para acceso SSH:

1. Ve a tu instancia en Oracle Cloud Console
2. Networking → Virtual Cloud Networks
3. Asegúrate que el puerto 22 (SSH) esté abierto

### Proteger el archivo .env

```bash
# Dar permisos solo al usuario
chmod 600 ~/email-order-agent/.env
```

### Actualizar sistema regularmente

```bash
sudo apt update && sudo apt upgrade -y
```

## 📊 Monitoreo

### Ver archivos procesados

```bash
cat ~/email-order-agent/logs/processed_emails.txt
```

### Ver último heartbeat

```bash
cat ~/email-order-agent/logs/last_whatsapp_message.txt
```

### Ver logs de la aplicación

```bash
tail -f ~/email-order-agent/logs/email_monitor.log
```

## 🔧 Solución de Problemas

### El servicio no inicia

```bash
# Ver error detallado
sudo journalctl -u email-order-agent -n 50

# Verificar archivo de configuración
cat ~/email-order-agent/.env

# Probar manualmente
cd ~/email-order-agent
source venv/bin/activate
python main.py
```

### No recibo mensajes de WhatsApp

1. Verificar que estás unido al Twilio Sandbox:
   ```bash
   source venv/bin/activate
   python check_twilio_status.py
   ```

2. Si ves error 63015, envía de nuevo el mensaje `join machinery-into` al número de Twilio

### Verificar que la VM tiene internet

```bash
ping -c 4 google.com
```

### Logs no se están creando

```bash
# Verificar permisos del directorio logs
ls -la ~/email-order-agent/logs/

# Si no existe, créalo
mkdir -p ~/email-order-agent/logs
```

## 🔄 Backup

Recomiendo hacer backup del archivo de emails procesados:

```bash
# Crear backup
cp ~/email-order-agent/logs/processed_emails.txt \
   ~/email-order-agent/logs/processed_emails.txt.backup

# O mejor, cron diario
echo "0 2 * * * cp ~/email-order-agent/logs/processed_emails.txt ~/email-order-agent/logs/processed_emails.txt.backup.\$(date +\%Y\%m\%d)" | crontab -
```

## 📈 Mantener la VM Activa

Oracle Cloud Free Tier mantiene las VMs activas, pero asegúrate de:

1. **No dejar la instancia inactiva por mucho tiempo**
2. **Tener el servicio corriendo** (genera actividad)
3. **Revisar logs regularmente**

## ✅ Checklist Final

- [ ] VM de Oracle Cloud creada y accesible
- [ ] Código transferido y descomprimido
- [ ] Dependencias instaladas (`./setup_vm.sh`)
- [ ] Archivo `.env` configurado con credenciales
- [ ] Prueba de WhatsApp exitosa
- [ ] Servicio systemd configurado (`./setup_systemd.sh`)
- [ ] Servicio iniciado y en ejecución
- [ ] Logs funcionando correctamente
- [ ] Mensaje de prueba recibido en WhatsApp
- [ ] Unido al Twilio Sandbox

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `sudo journalctl -u email-order-agent -n 100`
2. Verifica el estado: `sudo systemctl status email-order-agent`
3. Prueba manualmente: `cd ~/email-order-agent && source venv/bin/activate && python main.py`

---

**¡Listo! Tu sistema ahora funciona 24/7 en la nube.**
