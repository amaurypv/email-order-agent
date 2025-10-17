from whatsapp_notifier import WhatsAppNotifier
from twilio.base.exceptions import TwilioRestException

try:
    notifier = WhatsAppNotifier()
    print('From:', notifier.from_number)
    print('To:', notifier.to_number)
    print('\nEnviando mensaje de prueba...')
    result = notifier.send_test_message()
    print('Resultado:', 'OK' if result else 'FAILED')
except TwilioRestException as e:
    print('\nError Twilio:')
    print('Codigo:', e.code)
    print('Mensaje:', e.msg)
    if hasattr(e, 'details'):
        print('Detalles:', e.details)
except Exception as e:
    print('Error:', e)
