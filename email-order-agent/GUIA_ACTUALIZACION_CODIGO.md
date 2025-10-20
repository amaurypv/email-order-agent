# Guía de Actualización del Código

Esta guía explica paso por paso cómo actualizar el código del agente cuando hagas modificaciones.

---

## 📋 Flujo General

```
Mac (local) → GitHub (repositorio) → VM Oracle (producción)
```

---

## 🖥️ PARTE 1: En tu Mac (Máquina Local)

### Paso 1: Hacer las modificaciones
Edita los archivos Python que necesites modificar usando tu editor favorito.

### Paso 2: Verificar qué archivos cambiaron
```bash
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent

git status
```

Esto te mostrará los archivos modificados.

### Paso 3: Agregar los archivos al staging
```bash
# Agregar un archivo específico
git add nombre_archivo.py

# O agregar todos los archivos modificados
git add .
```

### Paso 4: Hacer commit
```bash
git commit -m "Descripción breve de los cambios realizados"
```

**Ejemplo de buen mensaje de commit:**
```bash
git commit -m "Fix: Corregir validación de emails duplicados"
```

### Paso 5: Subir a GitHub (push)
```bash
git push origin main
```

### Paso 6: Verificar que se subió correctamente
```bash
git log --oneline -3
```

Deberías ver tu nuevo commit en la lista.

---

## 🌩️ PARTE 2: En tu VM de Oracle

### Paso 1: Conectarte a la VM
```bash
ssh ubuntu@IP_DE_TU_VM
```

### Paso 2: Ir al directorio del proyecto
```bash
cd ~/apps/email-order-agent
```

### Paso 3: Conectarte a la sesión de tmux
```bash
tmux attach
```

### Paso 4: Detener el agente
Presiona `Ctrl + C` en la terminal donde está corriendo el agente.

Verás que regresa el prompt:
```
(venv) ubuntu@email-order-agent:~/apps/email-order-agent$
```

### Paso 5: Descargar la información de GitHub
```bash
git fetch origin main
```

### Paso 6: Ver qué commit quieres aplicar
```bash
git log origin/main --oneline -5
```

Copia el **hash del commit** que quieres aplicar (los primeros 7 caracteres, ejemplo: `d5bd24f`)

### Paso 7: Actualizar los archivos desde GitHub

**Opción A - Actualizar un archivo específico:**
```bash
# Reemplaza HASH_COMMIT con el hash que copiaste
# Reemplaza nombre_archivo.py con el archivo que modificaste

git show HASH_COMMIT:email-order-agent/nombre_archivo.py > nombre_archivo.py
```

**Ejemplo real:**
```bash
git show d5bd24f:email-order-agent/imap_client.py > imap_client.py
```

**Opción B - Actualizar todos los archivos:**
```bash
git reset --hard origin/main
```

⚠️ **CUIDADO:** La Opción B sobrescribirá TODOS los archivos, incluyendo `.env` si existe en el repo.

### Paso 8: Verificar que el código se actualizó
```bash
# Busca alguna línea de código nueva que agregaste
grep -n "texto_que_agregaste" nombre_archivo.py
```

### Paso 9: Reiniciar el agente
```bash
python3 main.py
```

El agente se iniciará y comenzará a monitorear correos.

### Paso 10: Hacer "detach" de tmux (dejar corriendo en background)
Presiona: `Ctrl + B`, luego suelta y presiona `D`

Verás un mensaje como:
```
[detached (from session 0)]
```

El agente seguirá corriendo aunque cierres la sesión SSH.

---

## 🔄 Comandos Útiles de Tmux

### Ver sesiones activas
```bash
tmux ls
```

### Conectarte a una sesión
```bash
tmux attach
```

### Crear una nueva sesión con nombre
```bash
tmux new -s email-agent
```

### Conectarte a una sesión específica
```bash
tmux attach -t email-agent
```

### Matar una sesión
```bash
tmux kill-session -t email-agent
```

### Desconectarte de tmux (sin detener el agente)
`Ctrl + B`, luego `D`

---

## 🐛 Solución de Problemas Comunes

### Problema: "fatal: invalid object name"
**Solución:** Olvidaste hacer `git fetch origin main`
```bash
git fetch origin main
```

### Problema: "fatal: not a git repository"
**Solución:** No estás en el directorio correcto
```bash
cd ~/apps/email-order-agent
```

### Problema: El código no se actualiza
**Solución:** Verifica que hiciste push desde tu Mac
```bash
# En tu Mac:
git log --oneline -3

# Luego en la VM:
git fetch origin main
git log origin/main --oneline -3

# Deberían mostrar el mismo commit más reciente
```

### Problema: El agente sigue corriendo después de Ctrl+C
**Solución:** Matar el proceso manualmente
```bash
pkill -f "python3.*main.py"
```

### Problema: Perdí la sesión de tmux
**Solución:** Listar y reconectar
```bash
tmux ls
tmux attach
```

---

## 📝 Checklist Rápida

### En tu Mac:
- [ ] Hacer modificaciones
- [ ] `git add .`
- [ ] `git commit -m "mensaje"`
- [ ] `git push origin main`
- [ ] Verificar con `git log`

### En la VM:
- [ ] `tmux attach`
- [ ] `Ctrl + C` (detener agente)
- [ ] `git fetch origin main`
- [ ] `git show HASH:email-order-agent/archivo.py > archivo.py`
- [ ] Verificar con `grep`
- [ ] `python3 main.py`
- [ ] `Ctrl + B, D` (detach)

---

## 🔍 Verificar que Todo Funciona

Después de actualizar, puedes ver los logs en tiempo real:

```bash
# Conectarte a tmux
tmux attach

# Ver los logs del agente (deberías ver el monitoreo activo)

# Si quieres salir sin detener, presiona: Ctrl + B, luego D
```

O ver el archivo de log:
```bash
tail -f ~/apps/email-order-agent/logs/email_monitor.log
```

---

## 📞 Información Adicional

**Estructura del repositorio en GitHub:**
```
/
├── email-order-agent/          ← Los archivos están aquí
│   ├── imap_client.py
│   ├── main.py
│   ├── config.py
│   └── ...
```

**Estructura en tu VM:**
```
~/apps/email-order-agent/       ← Trabajas directamente aquí
├── imap_client.py
├── main.py
├── config.py
└── ...
```

Por eso usamos `git show HASH:email-order-agent/archivo.py` para extraer desde la subcarpeta.

---

**Última actualización:** Octubre 2025
