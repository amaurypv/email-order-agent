#!/usr/bin/env python3
"""
Script para verificar el estado de los mensajes en Twilio
"""
from whatsapp_notifier import WhatsAppNotifier
from twilio.base.exceptions import TwilioRestException
import config

try:
    print("=" * 70)
    print("VERIFICACIÓN DE TWILIO WHATSAPP")
    print("=" * 70)

    notifier = WhatsAppNotifier()

    print(f"\n📱 Configuración:")
    print(f"   De: {notifier.from_number}")
    print(f"   Para: {notifier.to_number}")
    print(f"   Account SID: {config.TWILIO_ACCOUNT_SID}")

    print(f"\n📜 Últimos 20 mensajes enviados desde Twilio:\n")

    # Obtener historial completo de mensajes
    messages = notifier.client.messages.list(limit=20)

    if not messages:
        print("   ❌ No se encontraron mensajes")
    else:
        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. SID: {msg.sid}")
            print(f"   Para: {msg.to}")
            print(f"   Estado: {msg.status}")
            print(f"   Fecha: {msg.date_created}")
            print(f"   Error Code: {msg.error_code if msg.error_code else 'None'}")
            print(f"   Error Message: {msg.error_message if msg.error_message else 'None'}")
            if msg.body:
                preview = msg.body[:80].replace('\n', ' ')
                print(f"   Mensaje: {preview}...")
            print(f"   Dirección: {msg.direction}")

    print("\n" + "=" * 70)
    print("\n💡 ESTADOS POSIBLES:")
    print("   - queued: En cola, esperando envío")
    print("   - sent: Enviado a Twilio, pero no entregado")
    print("   - delivered: Entregado exitosamente")
    print("   - failed: Falló el envío")
    print("   - undelivered: No se pudo entregar")

    print("\n💡 NOTA IMPORTANTE:")
    print("   Si estás usando Twilio Sandbox (número +14155238886):")
    print("   1. Debes unirte al sandbox enviando un código específico")
    print("   2. Ve a: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
    print("   3. Envía el mensaje indicado desde tu WhatsApp al número sandbox")

except TwilioRestException as e:
    print(f"\n❌ ERROR DE TWILIO:")
    print(f"   Código: {e.code}")
    print(f"   Mensaje: {e.msg}")
    if hasattr(e, 'details'):
        print(f"   Detalles: {e.details}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
