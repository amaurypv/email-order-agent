"""
Configuration module for email order monitoring agent
Loads and validates environment variables
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
PROCESSED_EMAILS_FILE = LOGS_DIR / "processed_emails.txt"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)

# IMAP Configuration
IMAP_SERVER = os.getenv("IMAP_SERVER", "mail.quimicaguba.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER", "ventas@quimicaguba.com")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Notification Configuration (choose one: telegram or twilio)
NOTIFICATION_PROVIDER = os.getenv("NOTIFICATION_PROVIDER", "telegram").lower()

# Telegram Configuration (RECOMMENDED - Simple and reliable)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Twilio WhatsApp Configuration (LEGACY - Has 24h window restrictions)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO", "whatsapp:+526141211388")
# WhatsApp Template SID (optional - for sending outside 24h window)
# Get this from: https://console.twilio.com/us1/develop/sms/content-editor
TWILIO_WHATSAPP_TEMPLATE_SID = os.getenv("TWILIO_WHATSAPP_TEMPLATE_SID")

# Monitoring Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))
DAYS_BACK_TO_SEARCH = int(os.getenv("DAYS_BACK_TO_SEARCH", "1"))  # How many days back to search for emails

# Monitored clients
MONITORED_CLIENTS = [
    email.strip()
    for email in os.getenv(
        "MONITORED_CLIENTS",
        "bpomex@vallen.com,svalois@aiig.com,rocio.santana@chemicollc.com,chihuahua@rshughes.com"
    ).split(",")
]

# Logging Configuration
LOG_FILE = LOGS_DIR / "email_monitor.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO


def validate_config():
    """
    Validate that all required configuration is present
    Raises ValueError if any required config is missing
    """
    missing = []

    if not IMAP_PASSWORD:
        missing.append("IMAP_PASSWORD")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")

    # Validate notification provider
    if NOTIFICATION_PROVIDER == "telegram":
        if not TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
    elif NOTIFICATION_PROVIDER == "twilio":
        if not TWILIO_ACCOUNT_SID:
            missing.append("TWILIO_ACCOUNT_SID")
        if not TWILIO_AUTH_TOKEN:
            missing.append("TWILIO_AUTH_TOKEN")
    else:
        raise ValueError(
            f"Invalid NOTIFICATION_PROVIDER: {NOTIFICATION_PROVIDER}\n"
            f"Must be 'telegram' or 'twilio'"
        )

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env file"
        )

    return True


def get_config_summary():
    """Return a summary of current configuration (safe for logging)"""
    summary = {
        "imap_server": IMAP_SERVER,
        "imap_port": IMAP_PORT,
        "imap_user": IMAP_USER,
        "check_interval_minutes": CHECK_INTERVAL_MINUTES,
        "monitored_clients": MONITORED_CLIENTS,
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "notification_provider": NOTIFICATION_PROVIDER,
    }

    if NOTIFICATION_PROVIDER == "telegram":
        summary["telegram_chat_id"] = TELEGRAM_CHAT_ID
        summary["telegram_configured"] = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    elif NOTIFICATION_PROVIDER == "twilio":
        summary["whatsapp_to"] = TWILIO_WHATSAPP_TO
        summary["twilio_configured"] = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)

    return summary
