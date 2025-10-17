#!/usr/bin/env python3
"""
Script para probar la funcionalidad del heartbeat (versión automática)
"""
from whatsapp_notifier import WhatsAppNotifier
from datetime import datetime, timedelta

print("=" * 70)
print("PRUEBA DE HEARTBEAT - Sistema de mantenimiento de sesión")
print("=" * 70)

# Inicializar notificador
notifier = WhatsAppNotifier()

print(f"\n📱 Configuración:")
print(f"   De: {notifier.from_number}")
print(f"   Para: {notifier.to_number}")
print(f"   Archivo de tracking: {notifier.last_message_file}")

# Verificar último mensaje
last_time = notifier._get_last_message_time()

if last_time:
    print(f"\n⏰ Último mensaje enviado:")
    print(f"   Fecha/Hora: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")

    time_since = datetime.now() - last_time
    hours = time_since.total_seconds() / 3600
    print(f"   Hace: {hours:.1f} horas")
else:
    print(f"\n⏰ No hay registro de mensajes previos")

# Verificar si se necesita heartbeat con diferentes umbrales
print(f"\n🔍 Verificación de umbrales:")

for threshold in [1, 24, 48]:
    needs = notifier.should_send_heartbeat(hours_threshold=threshold)
    status = "✅ Necesario" if needs else "❌ No necesario"
    print(f"   {threshold} horas: {status}")

# Enviar heartbeat si se necesita (con umbral de 48 horas)
print(f"\n📤 Verificando con umbral de producción (48 horas)...")
if notifier.should_send_heartbeat(hours_threshold=48):
    print("   ✅ Se necesita heartbeat - Enviando...")
    success = notifier.send_heartbeat()

    if success:
        print("   ✅ Heartbeat enviado exitosamente")

        # Verificar actualización
        new_time = notifier._get_last_message_time()
        if new_time:
            print(f"   📅 Nuevo timestamp: {new_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("   ❌ Error al enviar heartbeat")
else:
    print(f"   ✅ No se necesita heartbeat todavía")

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)

print("\n💡 CÓMO FUNCIONA:")
print("   1. Cada vez que se envía un mensaje, se guarda el timestamp")
print("   2. En cada ciclo de monitoreo (cada 5 minutos):")
print("      - Se verifica cuánto tiempo ha pasado desde el último mensaje")
print("      - Si han pasado 48+ horas, se envía un heartbeat automático")
print("   3. Esto mantiene activa la sesión del Twilio Sandbox")
print("   4. Las notificaciones de órdenes también cuentan y reinician el contador")
