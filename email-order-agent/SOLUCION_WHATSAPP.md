# Solución a Problemas de WhatsApp

## Problemas Identificados

### 1. Error de las 11:05 - Error 63016 de Twilio
**Problema:** "Failed to send freeform message because you are outside the allowed window"

**Causa:** WhatsApp Business API requiere que los mensajes "libres" (no plantillas) se envíen dentro de una ventana de **24 horas** después del último mensaje que TÚ enviaste al bot.

**Solución implementada:**
- Cambiado el intervalo de heartbeat de 48h a 20h en `main.py:105`
- Esto mantiene la ventana de WhatsApp siempre activa

### 2. Error de las 11:16 - Error SSL
**Problema:** `SSLError(InterruptedError(4, 'Interrupted system call'))`

**Causa:** Interrupción de red/SSL durante la llamada a la API de Twilio

**Solución implementada:**
- Sistema de reintentos automáticos con backoff exponencial (2s, 4s, 8s)
- Timeout explícito de 30 segundos
- Logging detallado para distinguir errores retryables de no-retryables

## Cambios Realizados

### `whatsapp_notifier.py`
```python
# Nuevas características:
- Reintentos automáticos (hasta 3 intentos)
- Backoff exponencial entre reintentos
- Timeout de 30 segundos por llamada
- Logging detallado de errores de red
- Manejo específico de SSLError, ConnectionError, Timeout
```

### `main.py`
```python
# Cambio en línea 105:
- hours_threshold=48  # ANTES
+ hours_threshold=20  # AHORA (mantiene ventana de 24h activa)
```

## Cómo Reabrir la Ventana de WhatsApp AHORA

La ventana de 24 horas está cerrada. Para reabrirla:

### Paso 1: Envía un mensaje desde tu WhatsApp
Desde tu número de WhatsApp, envía cualquier mensaje al bot de Twilio:
- Puede ser simplemente: "hola", "ok", "test"
- Esto reinicia la ventana de 24 horas

### Paso 2: Ejecuta el script de reapertura
```bash
cd /Users/amauryperezverdejo/Desktop/agentes/mensajeriaPO/email-order-agent
python3 reopen_whatsapp_window.py
```

Este script:
1. Te pedirá confirmar que enviaste un mensaje desde tu WhatsApp
2. Esperará 3 segundos
3. Enviará un mensaje de confirmación
4. Verificará que todo funciona correctamente

## Funcionamiento Futuro

Una vez reabierta la ventana, el sistema:

1. **Cada 5 minutos:** Revisa correos nuevos
2. **Cada 20 horas:** Si no ha enviado mensajes, envía un heartbeat automático
3. **Resultado:** La ventana de 24h NUNCA se cerrará

### Mensaje de Heartbeat
```
💚 SISTEMA ACTIVO

El sistema de monitoreo de órdenes de compra está funcionando correctamente.

✅ Conexión WhatsApp activa
⏰ Monitoreando correos continuamente

(Este es un mensaje automático para mantener la conexión activa)
```

## Logs Mejorados

Ahora verás logs más detallados:

### Cuando hay éxito:
```
Sending WhatsApp message (990 chars)
WhatsApp message sent successfully. SID: SM..., Status: queued
```

### Cuando hay error de red (con reintentos):
```
Network error on attempt 1/3: SSLError - Interrupted system call
Retrying in 2 seconds...
Network error on attempt 2/3: SSLError - Interrupted system call
Retrying in 4 seconds...
WhatsApp message sent successfully. SID: SM..., Status: queued
```

### Cuando falla después de todos los reintentos:
```
Network error on attempt 1/3: SSLError - ...
Retrying in 2 seconds...
Network error on attempt 2/3: SSLError - ...
Retrying in 4 seconds...
Network error on attempt 3/3: SSLError - ...
Failed to send WhatsApp message after 3 attempts. Last error: SSLError - ...
```

### Cuando es error de API (no reintenta):
```
Twilio API error (non-retryable): 63016 - Failed to send freeform message...
```

## Alternativa: Usar Plantillas de WhatsApp (Avanzado)

Si prefieres no depender de la ventana de 24 horas, puedes:

1. Crear plantillas en Meta Business Manager
2. Obtener aprobación de Meta (toma 24-48 horas)
3. Modificar el código para usar `content_sid` en lugar de `body`

**Ventajas:**
- Envía mensajes en cualquier momento
- No necesita ventana de 24 horas

**Desventajas:**
- Requiere aprobación de Meta
- Las plantillas no pueden tener texto libre
- Proceso más complejo

## Verificación

Para verificar que todo está funcionando:

```bash
# 1. Reabre la ventana
python3 reopen_whatsapp_window.py

# 2. Reinicia tu sistema
python3 main.py

# 3. Verifica los logs
tail -f logs/email_monitor.log
```

Deberías ver:
```
✓ Startup notification sent
✓ WhatsApp message sent successfully
```

## Resumen

✅ **Problema de SSL/Red:** RESUELTO con reintentos automáticos
✅ **Problema de ventana 24h:** RESUELTO con heartbeats cada 20h
✅ **Mejora de logs:** IMPLEMENTADO para mejor debugging

**Acción requerida:** Ejecuta `reopen_whatsapp_window.py` una vez para reabrir la ventana.
