# Sistema de Heartbeat - Mantenimiento de Sesión WhatsApp

## ¿Qué es el Heartbeat?

El sistema de "heartbeat" (latido) mantiene activa la conexión con Twilio Sandbox de WhatsApp enviando mensajes automáticos cuando no hay actividad.

## ¿Por qué es necesario?

**Problema:** Twilio Sandbox desconecta tu número después de 72 horas de inactividad.

**Solución:** El sistema envía automáticamente un mensaje cada 48 horas si no se han enviado notificaciones de órdenes de compra.

## ¿Cómo funciona?

1. **Tracking de mensajes:**
   - Cada vez que se envía un mensaje (notificación o heartbeat), se guarda el timestamp en:
     ```
     logs/last_whatsapp_message.txt
     ```

2. **Verificación automática:**
   - En cada ciclo de monitoreo (cada 5 minutos), el sistema verifica:
     - ¿Cuánto tiempo ha pasado desde el último mensaje?
     - ¿Han pasado más de 48 horas?

3. **Envío automático:**
   - Si han pasado 48+ horas, se envía automáticamente:
     ```
     💚 SISTEMA ACTIVO

     El sistema de monitoreo de órdenes de compra está funcionando correctamente.

     ✅ Conexión WhatsApp activa
     ⏰ Monitoreando correos continuamente

     (Este es un mensaje automático para mantener la conexión activa)
     ```

## Ventajas

✅ **Automático:** No requiere intervención manual
✅ **Inteligente:** Solo se envía si no hay actividad real
✅ **Eficiente:** Mantiene la sesión activa sin spam
✅ **Confiable:** Evita desconexiones inesperadas

## Configuración

El umbral por defecto es **48 horas**. Se puede modificar en `main.py`:

```python
if whatsapp.should_send_heartbeat(hours_threshold=48):
    whatsapp.send_heartbeat()
```

Puedes cambiar `48` por otro valor si lo necesitas.

## Pruebas

Para probar el sistema manualmente:

```bash
source venv/bin/activate
python test_heartbeat_auto.py
```

Esto mostrará:
- Último mensaje enviado
- Tiempo transcurrido
- Si se necesita heartbeat
- Estado actual del sistema

## Monitoreo

Para ver el estado actual del último mensaje:

```bash
cat logs/last_whatsapp_message.txt
```

## Notas importantes

- Las **notificaciones de órdenes** también reinician el contador
- El heartbeat **solo se envía** si no ha habido actividad
- **No genera spam** - máximo 1 mensaje cada 48 horas si no hay órdenes
- Compatible con el Twilio Sandbox (72 horas de expiración)

## Historial de cambios

- **2025-10-13:** Implementación inicial del sistema de heartbeat
  - Tracking automático de mensajes
  - Verificación cada 5 minutos
  - Umbral de 48 horas
  - Pruebas exitosas
