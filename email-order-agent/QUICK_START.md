# Quick Start - Desplegar a Oracle VM en 10 minutos

## Paso 1: Crear VM en Oracle Cloud (5 min)

1. Ve a https://cloud.oracle.com/
2. Inicia sesión (o crea cuenta gratuita)
3. Click: ☰ → **Compute** → **Instances** → **Create Instance**
4. Configuración:
   - **Nombre:** email-order-agent
   - **Image:** Ubuntu 22.04
   - **Shape:** VM.Standard.E2.1.Micro (Always Free)
   - **SSH Keys:** Click "Generate a key pair for me"
     - **IMPORTANTE:** Descarga y guarda `oracle-vm-key.pem`
5. Click **Create**
6. Espera 2 minutos
7. **Anota la IP pública** (ej: 132.145.123.45)

## Paso 2: Preparar clave SSH (1 min)

```bash
# Mover clave SSH
mv ~/Downloads/ssh-key-2025-10-15.key ~/.ssh/

# Cambiar permisos
chmod 600 ~/.ssh/ssh-key-2025-10-15.key
```

## Paso 3: Desplegar automáticamente (3 min)

```bash
# Ir al directorio del proyecto
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent

# Ejecutar script de deployment (reemplaza con tu IP)
./deploy_to_vm.sh 132.145.123.45
```

El script te preguntará si quieres transferir el `.env`:
- Si ya tienes `.env` configurado → presiona `s`
- Si no → presiona `n` (lo configurarás manualmente)

## Paso 4: Conectar y probar (2 min)

```bash
# Conectar a la VM
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>

# Ir al directorio
cd ~/apps/email-order-agent

# Si no transferiste .env, verificar que esté configurado
cat .env

# Activar entorno virtual
source venv/bin/activate

# Probar el agente
python3 main.py
```

Si ves el banner y "Sistema activo" → **¡Funciona!** ✅

Presiona `Ctrl+C` para detener.

## Paso 5: Ejecutar 24/7 con tmux (1 min)

```bash
# Crear sesión de tmux
tmux new -s email-agent

# Activar entorno y ejecutar
cd ~/apps/email-order-agent
source venv/bin/activate
python3 main.py

# Salir sin detener: Ctrl+B, luego D
```

## Paso 6: Reabrir ventana de WhatsApp (1 min)

Desde tu Mac:

```bash
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>
cd ~/apps/email-order-agent
source venv/bin/activate
python3 reopen_whatsapp_window.py
```

## ✅ ¡Listo!

Tu agente ahora está corriendo 24/7 en la nube.

---

## 🔄 Actualizar el Código cuando hagas Cambios

### En tu Mac (desarrollo local):

```bash
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent

# 1. Haces tus modificaciones en cualquier archivo .py

# 2. Subes los cambios a GitHub
git add .
git commit -m "Descripción de tus cambios"
git push origin main
```

### En la VM (aplicar cambios):

```bash
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>
cd ~/apps/email-order-agent

# ¡Un solo comando actualiza TODO!
./update.sh
```

**El script `update.sh` hace automáticamente:**
- ✅ Detiene el agente si está corriendo
- ✅ Descarga los cambios desde GitHub
- ✅ Actualiza todos los archivos Python
- ✅ Reinicia el agente en tmux
- ✅ Muestra resumen de lo actualizado

**Eso es todo.** No necesitas detener manualmente ni reiniciar nada.

---

### Para reconectar más tarde:

```bash
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>
tmux attach -t email-agent
```

### Para ver logs:

```bash
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>
tail -f ~/apps/email-order-agent/logs/email_monitor.log
```

### Para detener manualmente (si es necesario):

```bash
ssh -i ~/.ssh/oracle-vm-key.pem ubuntu@<TU_IP>
tmux attach -t email-agent
# Presiona Ctrl+C
```

---

## Troubleshooting

### No puedo conectarme por SSH
1. Verifica que la VM está "Running" (verde) en Oracle Cloud
2. Verifica permisos de la clave: `chmod 400 ~/.ssh/oracle-vm-key.pem`
3. Verifica la IP es correcta

### Error al instalar dependencias
```bash
# En la VM
sudo apt update
sudo apt install -y python3-dev build-essential
pip install -r requirements.txt
```

### El agente se detiene
- Verifica que está en tmux: `tmux ls`
- Revisa los logs: `tail -100 ~/apps/email-order-agent/logs/email_monitor.log`

---

**Guía completa:** Ver `GUIA_ORACLE_VM.md`
