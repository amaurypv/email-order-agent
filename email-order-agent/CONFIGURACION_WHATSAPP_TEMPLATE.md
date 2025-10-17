# Configuración de WhatsApp Message Templates para Twilio

## El Problema: Ventana de 24 Horas

WhatsApp Business API tiene una restricción importante:

- **Dentro de 24 horas**: Después de que un cliente te envía un mensaje, puedes responder libremente durante 24 horas
- **Fuera de 24 horas**: Solo puedes enviar **mensajes usando plantillas pre-aprobadas por WhatsApp**

## Error 63016

Si ves este error en la consola de Twilio:
```
63016 - Failed to send freeform message because you are outside the allowed window.
If you are using WhatsApp, please use a Message Template.
```

Significa que la ventana de 24 horas expiró y necesitas usar **Message Templates**.

---

## Solución: Crear un WhatsApp Message Template

### Paso 1: Acceder al Content Editor de Twilio

1. Ve a la consola de Twilio: https://console.twilio.com
2. Navega a **Messaging** → **Content Editor**
3. O directamente: https://console.twilio.com/us1/develop/sms/content-editor

### Paso 2: Crear un Nuevo Template

1. Haz clic en **"Create new Content"**
2. Selecciona el tipo: **WhatsApp Template**
3. Configura el template:

#### Información Básica
- **Template Name**: `nueva_orden_compra` (sin espacios, solo minúsculas y guiones bajos)
- **Language**: Spanish (es)
- **Category**: UTILITY (para notificaciones transaccionales)

#### Contenido del Template

**Header** (Opcional):
```
📋 NUEVA ORDEN DE COMPRA
```

**Body** (Cuerpo del mensaje):
```
Se ha recibido una nueva orden de compra.

Cliente: {{1}}
Detalles: {{2}}

El sistema ha detectado una nueva orden en el correo.
```

**Footer** (Opcional):
```
Sistema de Monitoreo - Química Guba
```

**Botones** (Opcional):
- No agregar botones por ahora

### Paso 3: Enviar para Aprobación

1. Haz clic en **"Submit for Approval"**
2. WhatsApp revisará tu template (puede tomar de **24 a 48 horas**)
3. Recibirás un email cuando sea aprobado o rechazado

### Paso 4: Obtener el Template SID

Una vez aprobado:

1. Ve al Content Editor
2. Busca tu template aprobado
3. Haz clic en él para ver los detalles
4. Copia el **Content SID** (formato: `HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### Paso 5: Configurar en el Sistema

1. Abre tu archivo `.env`
2. Agrega la línea:
```bash
TWILIO_WHATSAPP_TEMPLATE_SID=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
3. Reemplaza `HXxxxxxxxx...` con tu SID real
4. Guarda el archivo
5. Reinicia el sistema

---

## Alternativa Temporal: Mantener la Ventana Activa

Mientras esperas la aprobación del template, puedes usar el script `reopen_whatsapp_window.py`:

### Opción 1: Ejecutar Manualmente
```bash
python reopen_whatsapp_window.py
```

Esto enviará un mensaje de heartbeat cada 20 horas para mantener la ventana activa.

### Opción 2: Ejecutar con Cron (Automático)

Agrega esto a tu crontab:
```bash
# Cada 20 horas envía un heartbeat
0 */20 * * * cd /ruta/a/email-order-agent && /ruta/a/venv/bin/python reopen_whatsapp_window.py >> logs/heartbeat.log 2>&1
```

**IMPORTANTE**: Para que esto funcione, **tú debes responder al mensaje de heartbeat** al menos una vez cada 24 horas. Si no respondes, la ventana se cerrará de todos modos.

---

## Verificación

### Probar que el Template Funciona

Una vez configurado el template SID en `.env`:

```bash
# Edita whatsapp_notifier.py temporalmente y agrega al final:

if __name__ == "__main__":
    import config
    notifier = WhatsAppNotifier()

    # Probar con template
    success = notifier.send_purchase_order_notification(
        client_name="Provinsa S.A.",
        po_number="PO-12345",
        template_sid=config.TWILIO_WHATSAPP_TEMPLATE_SID
    )

    print(f"Template message sent: {success}")
```

Luego ejecuta:
```bash
python whatsapp_notifier.py
```

---

## Mejores Prácticas

1. **Siempre usa templates para sistemas automatizados** que envían notificaciones sin interacción del usuario
2. **Mantén los templates simples**: WhatsApp es muy estricto con las aprobaciones
3. **No uses emojis excesivos** en los templates
4. **Evita lenguaje promocional**: Los templates UTILITY son solo para notificaciones transaccionales
5. **Variables dinámicas**: Usa `{{1}}`, `{{2}}`, etc. para contenido que cambia

---

## Troubleshooting

### Template Rechazado

Si WhatsApp rechaza tu template:

1. Simplifica el mensaje
2. Elimina emojis
3. Asegúrate de que la categoría sea correcta (UTILITY para notificaciones)
4. No incluyas links o llamados a la acción comerciales
5. Intenta de nuevo

### Template Aprobado pero Falla

1. Verifica que copiaste el SID correcto (comienza con `HX`)
2. Asegúrate de que las variables `{{1}}`, `{{2}}` están en el orden correcto
3. Revisa los logs en `logs/email_monitor.log`

### Aún Recibo Error 63016

1. Verifica que el template SID está en tu `.env`
2. Reinicia el sistema: `systemctl restart email-monitor`
3. Verifica que el código detecta el SID: mira los logs

---

## Resumen de la Solución Implementada

El sistema ahora:

1. ✅ Detecta automáticamente si tienes un template configurado
2. ✅ Usa el template si está disponible (funciona 24/7)
3. ✅ Usa mensajes de texto libre si no hay template configurado (solo dentro de 24h)
4. ✅ Registra claramente en los logs qué método está usando
5. ✅ Maneja el error 63016 con un mensaje descriptivo

**No necesitas cambiar nada en el código** - solo agregar el `TWILIO_WHATSAPP_TEMPLATE_SID` al `.env` una vez que tengas el template aprobado.
