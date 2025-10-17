#!/usr/bin/env python3
"""
Script para reabrir la ventana de 24 horas de WhatsApp
Este script te guía para responder al bot de WhatsApp y luego envía un mensaje de confirmación.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from whatsapp_notifier import WhatsAppNotifier
import config
import logging

# Setup simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("\n" + "="*70)
    print("REABRIR VENTANA DE WHATSAPP (24 HORAS)")
    print("="*70)
    print(f"\nNúmero de WhatsApp configurado: {config.TWILIO_WHATSAPP_TO}")
    print(f"Número de Twilio: {config.TWILIO_WHATSAPP_FROM}")

    print("\n⚠️  IMPORTANTE: Para reabrir la ventana de 24 horas:")
    print("1. Desde tu WhatsApp, envía CUALQUIER mensaje al número de Twilio")
    print(f"   {config.TWILIO_WHATSAPP_FROM}")
    print("2. Puede ser simplemente: 'hola' o 'ok'")
    print("3. Esto reinicia la ventana de 24 horas")
    print("\n")

    response = input("¿Ya enviaste un mensaje desde tu WhatsApp? (s/n): ").lower()

    if response != 's':
        print("\n❌ Por favor envía primero un mensaje desde tu WhatsApp.")
        print("   Luego ejecuta este script de nuevo.")
        sys.exit(0)

    print("\n✅ Perfecto! Ahora el sistema enviará un mensaje de confirmación...")
    print("   Esperando 3 segundos para asegurar que tu mensaje llegó...\n")
    time.sleep(3)

    try:
        # Initialize WhatsApp notifier
        whatsapp = WhatsAppNotifier()

        # Send confirmation message
        message = """✅ VENTANA DE WHATSAPP REABIERTA

¡La ventana de 24 horas ha sido reactivada exitosamente!

El sistema ahora puede enviarte mensajes libremente durante las próximas 24 horas.

📌 El sistema enviará automáticamente mensajes de heartbeat cada 20 horas para mantener la ventana siempre activa.

Sistema listo para enviar notificaciones de órdenes de compra."""

        logger.info("Enviando mensaje de confirmación...")

        if whatsapp.send_message(message):
            print("\n" + "="*70)
            print("✅ ÉXITO - Ventana de WhatsApp reabierta")
            print("="*70)
            print("\n✓ El mensaje de confirmación fue enviado exitosamente")
            print("✓ La ventana de 24 horas está ahora activa")
            print("✓ El sistema enviará heartbeats automáticos cada 20 horas")
            print("\nTu sistema está listo para funcionar correctamente.")
            print("="*70 + "\n")
        else:
            print("\n" + "="*70)
            print("❌ ERROR - No se pudo enviar el mensaje")
            print("="*70)
            print("\nPosibles causas:")
            print("1. Verifica que enviaste un mensaje desde tu WhatsApp")
            print("2. Revisa tus credenciales de Twilio en el archivo .env")
            print("3. Revisa los logs para más detalles")
            print("="*70 + "\n")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print("\n❌ Error al intentar enviar mensaje.")
        print(f"   Detalles: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
