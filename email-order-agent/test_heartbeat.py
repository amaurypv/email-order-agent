#!/usr/bin/env python3
"""
Script para probar la funcionalidad del heartbeat
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

# Verificar si se necesita heartbeat
print(f"\n🔍 Verificando necesidad de heartbeat...")
print(f"   Umbral configurado: 48 horas")

needs_heartbeat = notifier.should_send_heartbeat(hours_threshold=48)

if needs_heartbeat:
    print(f"   ✅ Se necesita heartbeat")

    response = input("\n¿Deseas enviar el heartbeat ahora? (s/n): ")

    if response.lower() == 's':
        print("\n📤 Enviando heartbeat...")
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
        print("\n⏭️  Heartbeat cancelado por el usuario")
else:
    print(f"   ✅ No se necesita heartbeat todavía")

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)

print("\n💡 INFORMACIÓN:")
print("   - El heartbeat se enviará automáticamente cada 48 horas")
print("   - Solo si no se han enviado otros mensajes en ese periodo")
print("   - Esto mantiene activa la sesión del Twilio Sandbox")
print("   - Los mensajes de notificaciones también reinician el contador")
