# Email Order Monitoring Agent

Sistema automatizado que monitorea una bandeja de entrada IMAP, detecta órdenes de compra en archivos PDF usando Claude AI, y envía notificaciones en tiempo real por WhatsApp vía Twilio.

## Características Principales

- Monitoreo automático de emails cada 10 minutos
- Detección inteligente de PDFs con Claude Haiku
- Notificaciones instantáneas por WhatsApp
- Prevención de duplicados
- Logs detallados
- Bajo costo operativo (~$0.50/mes por 100 PDFs)

## Requisitos

- Python 3.10+
- Cuenta Anthropic (Claude API)
- Cuenta Twilio con WhatsApp Sandbox
- Cuenta de email con IMAP habilitado

## Inicio Rápido

```bash
# 1. Navegar al directorio del agente
cd email-order-agent

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Ejecutar el agente
python3 main.py
```

## Estructura del Proyecto

```
mensajeriaPO/
├── email-order-agent/          # Directorio principal del agente
│   ├── main.py                 # Punto de entrada
│   ├── config.py               # Gestión de configuración
│   ├── imap_client.py          # Cliente IMAP
│   ├── pdf_processor.py        # Procesamiento de PDFs
│   ├── claude_analyzer.py      # Análisis con Claude AI
│   ├── whatsapp_notifier.py    # Notificaciones WhatsApp
│   ├── telegram_notifier.py    # Notificaciones Telegram
│   ├── requirements.txt        # Dependencias
│   ├── .env.example            # Plantilla de configuración
│   └── README.md               # Documentación detallada
├── .env.example                # Plantilla de configuración (raíz)
└── README.md                   # Este archivo
```

## Documentación Completa

Para instrucciones detalladas de instalación, configuración y uso, consulta:

**[📖 Documentación Completa](email-order-agent/README.md)**

Documentación adicional disponible:
- [QUICK_START.md](email-order-agent/QUICK_START.md) - Guía de inicio rápido
- [DEPLOYMENT_GUIDE.md](email-order-agent/DEPLOYMENT_GUIDE.md) - Guía de deployment
- [ORACLE_SETUP_GUIDE.md](email-order-agent/ORACLE_SETUP_GUIDE.md) - Configuración en Oracle VM
- [CONFIGURACION_WHATSAPP_TEMPLATE.md](email-order-agent/CONFIGURACION_WHATSAPP_TEMPLATE.md) - Configuración de WhatsApp

## Clientes Monitoreados

- bpomex@vallen.com
- svalois@aiig.com
- rocio.santana@chemicollc.com
- chihuahua@rshughes.com

## Costos Operacionales

| Servicio | Uso Mensual | Costo |
|----------|-------------|-------|
| Claude Haiku | 100 PDFs | $0.50 |
| Twilio Sandbox | Ilimitado | GRATIS |
| **Total** | | **$0.50** |

## Soporte

Para problemas o preguntas:
1. Revisa los logs en `email-order-agent/logs/`
2. Consulta la [documentación completa](email-order-agent/README.md)
3. Verifica la configuración en `.env`

## Licencia

Uso interno - Química Guba

---

**Versión**: 1.0.0
**Última actualización**: Octubre 2025
**Desarrollado para**: Química Guba
