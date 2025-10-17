#!/usr/bin/env python3
"""
Email Order Monitoring Agent
Monitors IMAP inbox for purchase order PDFs and sends WhatsApp notifications

Author: Química Guba
Version: 1.0.0
"""
import logging
import sys
import time
import schedule
from datetime import datetime

import config
from imap_client import IMAPClient


def setup_logging():
    """Configure logging for the application"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Silence verbose Twilio and HTTP logs in console
    logging.getLogger("twilio.http_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger


def print_banner():
    """Print application banner"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          EMAIL ORDER MONITORING AGENT                          ║
║          Química Guba - Purchase Order Tracker                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def validate_environment():
    """Validate configuration and environment"""
    logger = logging.getLogger(__name__)

    logger.info("Validating configuration...")

    try:
        config.validate_config()
        logger.info("✓ Configuration validated successfully")
        return True
    except ValueError as e:
        logger.error(f"✗ Configuration error: {str(e)}")
        logger.error("Please check your .env file")
        return False


def display_config():
    """Display current configuration (safe for logging)"""
    logger = logging.getLogger(__name__)

    cfg = config.get_config_summary()

    logger.info("\n" + "=" * 70)
    logger.info("CONFIGURATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"IMAP Server: {cfg['imap_server']}:{cfg['imap_port']}")
    logger.info(f"IMAP User: {cfg['imap_user']}")
    logger.info(f"Check Interval: {cfg['check_interval_minutes']} minutes")
    logger.info(f"Notification Provider: {cfg['notification_provider'].upper()}")

    if cfg['notification_provider'] == 'telegram':
        logger.info(f"Telegram Chat ID: {cfg.get('telegram_chat_id', 'Not configured')}")
        logger.info(f"Telegram API: {'✓ Configured' if cfg.get('telegram_configured') else '✗ Not configured'}")
    elif cfg['notification_provider'] == 'twilio':
        logger.info(f"WhatsApp Recipient: {cfg.get('whatsapp_to', 'Not configured')}")
        logger.info(f"Twilio API: {'✓ Configured' if cfg.get('twilio_configured') else '✗ Not configured'}")

    logger.info(f"Anthropic API: {'✓ Configured' if cfg['anthropic_configured'] else '✗ Not configured'}")
    logger.info("\nMonitored Clients:")
    for i, client in enumerate(cfg['monitored_clients'], 1):
        logger.info(f"  {i}. {client}")
    logger.info("=" * 70 + "\n")


def job_check_emails(imap_client: IMAPClient):
    """Scheduled job to check emails"""
    try:
        imap_client.run_monitoring_cycle()

    except Exception as e:
        logging.error(f"Error in scheduled job: {str(e)}")


def main():
    """Main application entry point"""
    # Print banner
    print_banner()

    # Setup logging
    logger = setup_logging()
    logger.info(f"Application started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {config.LOG_FILE}")

    # Validate configuration
    if not validate_environment():
        logger.error("Exiting due to configuration errors")
        sys.exit(1)

    # Display configuration
    display_config()

    # Initialize components
    logger.info("Initializing components...")

    try:
        imap_client = IMAPClient()
        logger.info("✓ All components initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize components: {str(e)}")
        sys.exit(1)

    # Send startup notification
    logger.info("\nSending startup notification...")
    try:
        if imap_client.notifier.send_startup_notification():
            logger.info("✓ Startup notification sent")
        else:
            logger.warning("⚠ Failed to send startup notification")
    except Exception as e:
        logger.error(f"✗ Error sending startup notification: {str(e)}")

    # Run first check immediately
    logger.info("\n" + "=" * 70)
    logger.info("Running initial email check...")
    logger.info("=" * 70 + "\n")

    try:
        imap_client.run_monitoring_cycle()
    except Exception as e:
        logger.error(f"Error in initial check: {str(e)}")

    # Schedule periodic checks
    interval_minutes = config.CHECK_INTERVAL_MINUTES
    logger.info(f"\nScheduling checks every {interval_minutes} minutes...")

    schedule.every(interval_minutes).minutes.do(job_check_emails, imap_client)

    logger.info("\n" + "=" * 70)
    logger.info("SYSTEM ACTIVE - Monitoring for purchase orders")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 70 + "\n")

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check for pending jobs every 30 seconds

    except KeyboardInterrupt:
        logger.info("\n\nShutdown signal received...")
        logger.info("Stopping email monitoring agent")
        logger.info("Goodbye!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
