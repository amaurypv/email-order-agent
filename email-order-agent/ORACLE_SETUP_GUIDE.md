# Guía Completa: Configurar VM en Oracle Cloud

## PASO 1: ✅ Cuenta Verificada
Ya completado ✓

## PASO 2: Generar Llaves SSH en tu Mac

Las llaves SSH te permitirán conectarte de forma segura a tu VM.

### Comandos a ejecutar:

```bash
# 1. Crear directorio para llaves si no existe
mkdir -p ~/.ssh

# 2. Generar llave SSH (presiona Enter en todo lo que pregunte)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_vm -N ""

# 3. Ver la llave pública (cópiala completa)
cat ~/.ssh/oracle_vm.pub
```

**Guarda la salida del último comando** - es tu llave pública, la necesitarás en el siguiente paso.

---

## PASO 3: Crear la VM en Oracle Cloud

### 3.1 Acceder a la Consola

1. Ve a: https://cloud.oracle.com/
2. Click en "Sign in to Cloud"
3. Ingresa tu email y contraseña

### 3.2 Crear Instancia (VM)

1. En el Dashboard, busca **"Create a VM instance"** o ve a:
   - Menú hamburguesa (☰) → **Compute** → **Instances**

2. Click en **"Create Instance"**

### 3.3 Configurar la Instancia

**Nombre:**
- Nombre: `email-order-agent` (o el que prefieras)

**Placement:**
- Availability Domain: Deja el que viene por defecto

**Image and Shape:**
- **Image:**
  - Click en "Change Image"
  - Selecciona: **Canonical Ubuntu** (22.04 o 20.04)
  - Click "Select Image"

- **Shape:**
  - Click en "Change Shape"
  - Selecciona: **VM.Standard.E2.1.Micro** (Always Free)
  - Click "Select Shape"

**Networking:**
- VCN: Deja el default
- Subnet: Deja el default
- **Assign a public IPv4 address:** ✅ (Muy importante - debe estar marcado)

**Add SSH Keys:**
- Selecciona: **"Paste public keys"**
- Pega tu llave pública (la que obtuviste con `cat ~/.ssh/oracle_vm.pub`)

**Boot Volume:**
- Deja todo por defecto

### 3.4 Crear

1. Click en **"Create"** (botón azul abajo)
2. Espera 1-2 minutos mientras se crea la instancia
3. El estado cambiará de "PROVISIONING" a "RUNNING" (verde)

### 3.5 Obtener la IP Pública

Una vez que esté en estado "RUNNING":

1. En la página de detalles de la instancia, busca:
   - **Public IP address:** `XX.XX.XX.XX`
2. **COPIA ESTA IP** - la necesitarás para conectarte

---

## PASO 4: Configurar Reglas de Firewall

Oracle Cloud tiene un firewall estricto por defecto. Vamos a asegurarnos que puedes conectarte.

### 4.1 Reglas en la Consola

1. En la página de tu instancia, en **"Primary VNIC"**:
   - Click en el nombre de tu **Subnet** (algo como "subnet-20240101...")

2. En la página del subnet:
   - Click en **"Default Security List for..."**

3. Verifica que existe una regla para SSH:
   - **Ingress Rules** → Debe haber una regla:
     - Source: `0.0.0.0/0`
     - Destination Port: `22`
   - Si NO existe, créala:
     - Click "Add Ingress Rules"
     - Source CIDR: `0.0.0.0/0`
     - Destination Port Range: `22`
     - Description: `SSH access`
     - Click "Add Ingress Rules"

### 4.2 Firewall en la VM (lo haremos después de conectarnos)

```bash
# Esto lo ejecutaremos una vez conectados a la VM
sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT
sudo netfilter-persistent save
```

---

## PASO 5: Conectarse a la VM

### 5.1 Agregar configuración SSH en tu Mac

```bash
# Editar archivo de configuración SSH
nano ~/.ssh/config
```

Agrega esto (reemplaza XX.XX.XX.XX con tu IP):

```
Host oracle-vm
    HostName XX.XX.XX.XX
    User ubuntu
    IdentityFile ~/.ssh/oracle_vm
    StrictHostKeyChecking no
```

Guarda: `Ctrl+O`, Enter, `Ctrl+X`

### 5.2 Conectar

```bash
# Primera conexión
ssh ubuntu@XX.XX.XX.XX -i ~/.ssh/oracle_vm

# O usando el alias:
ssh oracle-vm
```

Si te pregunta "Are you sure you want to continue connecting?", escribe: `yes`

---

## PASO 6: Configurar Firewall en la VM

Una vez conectado, ejecuta:

```bash
# Permitir SSH
sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT

# Guardar reglas
sudo apt-get update
sudo apt-get install -y iptables-persistent
# Presiona "Yes" en las preguntas que aparezcan
```

---

## PASO 7: Transferir el Proyecto

Desde tu Mac (en otra terminal, NO en la VM):

```bash
# Ir al directorio del proyecto
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent

# Transferir archivos
./deploy_to_vm.sh ubuntu@XX.XX.XX.XX
```

O manualmente:

```bash
# Comprimir
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO
tar -czf email-order-agent.tar.gz email-order-agent/

# Transferir
scp -i ~/.ssh/oracle_vm email-order-agent.tar.gz ubuntu@XX.XX.XX.XX:~/
```

---

## PASO 8: Instalar en la VM

En la VM (terminal SSH):

```bash
# Si usaste deploy_to_vm.sh:
cd ~/email-order-agent-new

# Si transferiste manualmente:
tar -xzf email-order-agent.tar.gz
cd email-order-agent

# Dar permisos
chmod +x setup_vm.sh setup_systemd.sh

# Instalar
./setup_vm.sh
```

---

## PASO 9: Configurar Credenciales

```bash
# Copiar ejemplo
cp .env.example .env

# Editar
nano .env
```

Configura todas las variables y guarda: `Ctrl+O`, Enter, `Ctrl+X`

---

## PASO 10: Probar

```bash
# Activar entorno virtual
source venv/bin/activate

# Probar WhatsApp
python test_whatsapp.py
```

---

## PASO 11: Configurar Servicio

```bash
# Configurar systemd
./setup_systemd.sh

# Iniciar servicio
sudo systemctl start email-order-agent

# Ver logs
sudo journalctl -u email-order-agent -f
```

---

## ✅ CHECKLIST COMPLETO

- [ ] Cuenta Oracle Cloud verificada
- [ ] Llaves SSH generadas en Mac
- [ ] VM creada (Ubuntu, Always Free)
- [ ] IP pública asignada y anotada
- [ ] Reglas de firewall configuradas
- [ ] Conexión SSH exitosa
- [ ] Archivos transferidos
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado
- [ ] WhatsApp probado exitosamente
- [ ] Servicio systemd configurado
- [ ] Servicio corriendo 24/7

---

## 🆘 Solución de Problemas

### No puedo conectarme por SSH

1. Verifica la IP: `ping XX.XX.XX.XX`
2. Verifica reglas de firewall en Oracle Console
3. Verifica que la VM esté "RUNNING"
4. Prueba: `ssh -v ubuntu@XX.XX.XX.XX -i ~/.ssh/oracle_vm`

### Permission denied (publickey)

```bash
# Verificar permisos de la llave
chmod 600 ~/.ssh/oracle_vm
chmod 644 ~/.ssh/oracle_vm.pub
```

### Connection timeout

- Verifica las reglas de ingreso en Security List
- Espera 5 minutos y vuelve a intentar
- Verifica que la IP sea correcta

---

**¿Listo para empezar?** Sigue los pasos en orden y avísame donde necesites ayuda.
