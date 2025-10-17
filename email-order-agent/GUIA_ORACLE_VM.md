# Guía Completa: Desplegar Agente en Oracle Cloud VM

## Tabla de Contenidos
1. [Crear VM en Oracle Cloud](#paso-1-crear-vm-en-oracle-cloud)
2. [Conectar por SSH](#paso-2-conectar-por-ssh)
3. [Configurar el Servidor](#paso-3-configurar-el-servidor)
4. [Transferir el Código](#paso-4-transferir-el-código)
5. [Instalar Dependencias](#paso-5-instalar-dependencias)
6. [Configurar y Probar](#paso-6-configurar-y-probar)
7. [Ejecutar 24/7 con tmux](#paso-7-ejecutar-247-con-tmux)
8. [Monitoreo y Mantenimiento](#paso-8-monitoreo-y-mantenimiento)

---

## Paso 1: Crear VM en Oracle Cloud

### 1.1 Crear Cuenta (si no la tienes)
1. Ve a: https://www.oracle.com/cloud/free/
2. Click en "Start for free"
3. Completa el registro (necesitas tarjeta de crédito pero NO te cobran)
4. Verifica tu email

### 1.2 Crear la VM (Compute Instance)
1. Inicia sesión en: https://cloud.oracle.com/
2. Click en el menú hamburguesa (☰) → **Compute** → **Instances**
3. Click en **"Create Instance"**

### 1.3 Configuración de la VM

**Nombre:**
```
email-order-agent
```

**Image and Shape:**
- **Image:** Ubuntu 22.04 (recomendado) o Ubuntu 20.04
- **Shape:**
  - VM.Standard.E2.1.Micro (Always Free)
  - 1 OCPU, 1 GB RAM
  - Click "Change Shape" si no está seleccionado

**Networking:**
- Deja los valores por defecto
- Asegúrate que "Assign a public IPv4 address" esté seleccionado

**Add SSH Keys:**
- Selecciona "Generate a key pair for me"
- Click **"Save Private Key"** → Guárdalo como `oracle-vm-key.pem`
- **MUY IMPORTANTE:** No pierdas esta clave, la necesitarás para conectarte

**Boot Volume:**
- Deja el tamaño por defecto (47 GB es suficiente)

4. Click en **"Create"**
5. Espera 2-3 minutos a que esté en estado "Running" (verde)
6. **Anota la IP pública** que aparece (ej: 132.145.123.45)

---

## Paso 2: Conectar por SSH

### 2.1 Preparar la clave SSH en tu Mac

```bash
# Mover la clave a tu carpeta .ssh
mkdir -p ~/.ssh
mv ~/Downloads/oracle-vm-key.pem ~/.ssh/

# Cambiar permisos (IMPORTANTE)
chmod 400 ~/.ssh/oracle-vm-key.pem
```

### 2.2 Configurar reglas de firewall en Oracle Cloud

1. En la página de tu instancia, click en la subnet (ej: "subnet-...")
2. Click en la Security List por defecto
3. Click en "Add Ingress Rules"
4. Agrega esta regla (para debugging si lo necesitas):
   - Source CIDR: `0.0.0.0/0`
   - Destination Port Range: `22`
   - Description: `SSH access`

### 2.3 Conectar por SSH

```bash
# Reemplaza <IP_PUBLICA> con la IP de tu VM
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<IP_PUBLICA>

# Ejemplo:
# ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@132.145.123.45

# La primera vez dirá: "Are you sure you want to continue connecting?"
# Escribe: yes
```

✅ Si ves algo como `ubuntu@email-order-agent:~$` estás dentro de la VM

---

## Paso 3: Configurar el Servidor

### 3.1 Actualizar el sistema

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y
```

### 3.2 Instalar Python 3.9+ y herramientas

```bash
# Instalar Python y pip
sudo apt install -y python3 python3-pip python3-venv

# Instalar herramientas útiles
sudo apt install -y git tmux htop

# Verificar versión de Python
python3 --version
# Debería mostrar: Python 3.10.x o superior
```

### 3.3 Crear estructura de directorios

```bash
# Crear directorio para el proyecto
mkdir -p ~/apps/email-order-agent
cd ~/apps/email-order-agent
```

---

## Paso 4: Transferir el Código

### 4.1 Opción A: Usar SCP (desde tu Mac)

Abre una NUEVA terminal en tu Mac (no cierres la conexión SSH):

```bash
# Ve al directorio del proyecto
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent

# Transferir todos los archivos (reemplaza <IP_PUBLICA>)
scp -i ~/.ssh/oracle-vm-key.pem -r \
  *.py \
  .env \
  ubuntu@<IP_PUBLICA>:~/apps/email-order-agent/

# Si tienes otros archivos necesarios, transfiérelos también
```

### 4.2 Opción B: Usar Git (si tienes el código en un repositorio)

```bash
# Desde la VM
cd ~/apps/email-order-agent
git clone <TU_REPOSITORIO>
cd <nombre-del-repo>
```

### 4.3 Verificar que se transfirió

```bash
# Desde la VM
cd ~/apps/email-order-agent
ls -la

# Deberías ver:
# main.py, config.py, whatsapp_notifier.py, etc.
```

---

## Paso 5: Instalar Dependencias

### 5.1 Crear entorno virtual

```bash
cd ~/apps/email-order-agent

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Deberías ver (venv) al inicio de tu prompt
```

### 5.2 Crear/transferir requirements.txt

Si no tienes un `requirements.txt`, créalo con las dependencias que necesitas:

```bash
# Desde tu Mac, crea el archivo requirements.txt
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent
pip3 freeze > requirements.txt

# Transferir a la VM
scp -i ~/.ssh/oracle-vm-key.pem requirements.txt \
  ubuntu@<IP_PUBLICA>:~/apps/email-order-agent/
```

### 5.3 Instalar dependencias

```bash
# Desde la VM (con venv activado)
pip install --upgrade pip
pip install -r requirements.txt

# Verificar que se instalaron
pip list
```

---

## Paso 6: Configurar y Probar

### 6.1 Verificar archivo .env

```bash
# Desde la VM
cd ~/apps/email-order-agent
cat .env

# Verifica que todas las variables estén configuradas:
# - IMAP_SERVER, IMAP_PORT, IMAP_USER, IMAP_PASSWORD
# - ANTHROPIC_API_KEY
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
# - TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO
```

### 6.2 Crear directorios necesarios

```bash
# Crear directorios para logs
mkdir -p logs
```

### 6.3 Probar el agente

```bash
# Activar entorno virtual si no está activo
source venv/bin/activate

# Ejecutar el agente
python3 main.py

# Deberías ver:
# - El banner del sistema
# - Configuración validada
# - Startup notification enviado
# - Sistema activo

# Para detener: Ctrl+C
```

---

## Paso 7: Ejecutar 24/7 con tmux

### 7.1 Crear sesión de tmux

```bash
# Crear sesión llamada "email-agent"
tmux new -s email-agent
```

### 7.2 Ejecutar el agente dentro de tmux

```bash
# Dentro de tmux
cd ~/apps/email-order-agent
source venv/bin/activate
python3 main.py

# Deberías ver el agente corriendo
```

### 7.3 Desconectarte de tmux (sin cerrar el agente)

```
Presiona: Ctrl+B
Suelta las teclas
Presiona: D

# Verás: "[detached (from session email-agent)]"
# El agente sigue corriendo en segundo plano
```

### 7.4 Verificar que está corriendo

```bash
# Ver sesiones activas
tmux ls

# Debería mostrar:
# email-agent: 1 windows (created ...)

# Reconectar a la sesión
tmux attach -t email-agent

# Verás el agente corriendo
# Para salir otra vez: Ctrl+B, luego D
```

### 7.5 Cerrar SSH sin detener el agente

```bash
# Simplemente cierra la terminal o escribe:
exit

# El agente sigue corriendo en tmux ✅
```

---

## Paso 8: Monitoreo y Mantenimiento

### 8.1 Reconectar y ver el agente

```bash
# Desde tu Mac, conecta a la VM
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<IP_PUBLICA>

# Reconectar a tmux
tmux attach -t email-agent

# Verás los logs en tiempo real
```

### 8.2 Ver logs sin entrar a tmux

```bash
# Conectar a la VM
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<IP_PUBLICA>

# Ver logs
cd ~/apps/email-order-agent
tail -f logs/email_monitor.log

# Para salir: Ctrl+C
```

### 8.3 Reiniciar el agente

```bash
# Conectar a tmux
tmux attach -t email-agent

# Detener el agente: Ctrl+C

# Reiniciar
python3 main.py

# Salir de tmux: Ctrl+B, luego D
```

### 8.4 Ver uso de recursos

```bash
# Ver CPU y memoria
htop

# Para salir: Q

# Ver espacio en disco
df -h

# Ver procesos de Python
ps aux | grep python
```

### 8.5 Comandos útiles de tmux

```bash
# Listar sesiones
tmux ls

# Crear nueva sesión
tmux new -s nombre

# Reconectar a sesión
tmux attach -t nombre

# Matar sesión (detiene el agente)
tmux kill-session -t email-agent

# Dentro de tmux:
# Ctrl+B, luego D → Desconectar
# Ctrl+B, luego [ → Scroll en los logs (Q para salir)
# Ctrl+B, luego ? → Ayuda
```

---

## Paso 9: Configuración para Múltiples Apps (Futuro)

### 9.1 Estructura recomendada

```
~/apps/
├── email-order-agent/      (tu agente actual)
├── app2/                   (futura app)
└── app3/                   (futura app)
```

### 9.2 Sesiones de tmux separadas

```bash
# App 1
tmux new -s email-agent
cd ~/apps/email-order-agent && python3 main.py
# Ctrl+B, D

# App 2
tmux new -s app2
cd ~/apps/app2 && python3 main.py
# Ctrl+B, D

# Ver todas las sesiones
tmux ls
```

---

## Solución de Problemas

### Problema: No puedo conectarme por SSH

**Solución:**
```bash
# Verifica permisos de la clave
chmod 400 ~/.ssh/oracle-vm-key.pem

# Verifica que la VM está corriendo en Oracle Cloud
# Verifica que estás usando la IP correcta
```

### Problema: "Permission denied" al conectar

**Solución:**
```bash
# Asegúrate de usar el usuario correcto: ubuntu (no root)
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<IP>
```

### Problema: El agente se detiene

**Solución:**
```bash
# Verifica que está en tmux
tmux ls

# Revisa los logs
tail -100 ~/apps/email-order-agent/logs/email_monitor.log

# Verifica que no haya errores de configuración
```

### Problema: Error al instalar dependencias

**Solución:**
```bash
# Actualiza pip
pip install --upgrade pip

# Instala dependencias del sistema que puedan faltar
sudo apt install -y python3-dev build-essential
```

---

## Checklist Final

Antes de desconectarte, verifica:

- [ ] La VM está corriendo (estado "Running" en Oracle Cloud)
- [ ] Puedes conectarte por SSH
- [ ] Python 3.9+ está instalado
- [ ] El código está transferido
- [ ] Las dependencias están instaladas
- [ ] El archivo .env está configurado
- [ ] El agente corre correctamente con `python3 main.py`
- [ ] tmux está instalado
- [ ] El agente está corriendo en tmux
- [ ] Te puedes desconectar y reconectar sin problemas
- [ ] Los logs se están guardando correctamente

---

## Próximos Pasos

1. **Ahora:** Reabrir ventana de WhatsApp (ejecuta `reopen_whatsapp_window.py` desde la VM)
2. **Monitoreo:** Revisa los logs cada día durante la primera semana
3. **Backups:** Considera hacer backups del código y configuración
4. **Alertas:** Configura alertas si el agente falla (futuro)

---

## Recursos Útiles

- Oracle Cloud Console: https://cloud.oracle.com/
- Documentación Oracle Free Tier: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- Tmux cheatsheet: https://tmuxcheatsheet.com/

---

**¡Tu agente ahora está corriendo 24/7 en la nube! 🚀**
