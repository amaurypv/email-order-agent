"""
Telegram Notifier Module
Sends Telegram messages using Telegram Bot API
Much simpler and more reliable than WhatsApp/Twilio
"""
import logging
import requests
from typing import Optional
from datetime import datetime
import time
import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends Telegram notifications using Bot API"""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        """
        Initialize Telegram Bot client

        Args:
            max_retries: Maximum number of retry attempts for failed messages
            timeout: Timeout in seconds for API calls
        """
        try:
            self.bot_token = config.TELEGRAM_BOT_TOKEN
            self.chat_id = config.TELEGRAM_CHAT_ID
            self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
            self.max_retries = max_retries
            self.timeout = timeout

            logger.info(
                f"Telegram notifier initialized. Chat ID: {self.chat_id}, "
                f"Max retries: {max_retries}, Timeout: {timeout}s"
            )

            # Test connection
            self._test_connection()

        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {str(e)}")
            raise

    def _test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"{self.api_base_url}/getMe"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    bot_name = bot_info["result"].get("username", "Unknown")
                    logger.info(f"✓ Telegram bot connected: @{bot_name}")
                    return True

            logger.error(f"Telegram connection test failed: {response.text}")
            return False

        except Exception as e:
            logger.error(f"Error testing Telegram connection: {str(e)}")
            return False

    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send Telegram message with automatic retry on network errors

        Args:
            message: Message text to send
            parse_mode: Message formatting (HTML, Markdown, or None)

        Returns:
            True if message sent successfully, False otherwise
        """
        # Telegram has a message limit of 4096 characters
        max_length = 4000
        if len(message) > max_length:
            logger.warning(
                f"Message too long ({len(message)} chars). Truncating to {max_length}"
            )
            message = message[:max_length - 50] + "\n\n... (mensaje truncado)"

        logger.info(f"Sending Telegram message ({len(message)} chars)")

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                url = f"{self.api_base_url}/sendMessage"

                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": parse_mode
                }

                response = requests.post(url, json=payload, timeout=self.timeout)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        message_id = result["result"]["message_id"]
                        logger.info(
                            f"Telegram message sent successfully. Message ID: {message_id}"
                        )
                        return True
                    else:
                        logger.error(f"Telegram API error: {result}")
                        return False
                else:
                    logger.error(
                        f"Telegram API returned status {response.status_code}: {response.text}"
                    )

                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return False

            except requests.exceptions.Timeout as e:
                attempt_num = attempt + 1
                logger.warning(
                    f"Timeout on attempt {attempt_num}/{self.max_retries}: {str(e)}"
                )

                if attempt_num < self.max_retries:
                    wait_time = 2 ** attempt_num
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to send Telegram message after {self.max_retries} attempts")
                    return False

            except requests.exceptions.RequestException as e:
                attempt_num = attempt + 1
                logger.warning(
                    f"Request error on attempt {attempt_num}/{self.max_retries}: {str(e)}"
                )

                if attempt_num < self.max_retries:
                    wait_time = 2 ** attempt_num
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to send Telegram message after {self.max_retries} attempts")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error sending Telegram message: {type(e).__name__} - {str(e)}")
                return False

        return False

    def send_test_message(self) -> bool:
        """
        Send a test message to verify configuration

        Returns:
            True if test message sent successfully
        """
        test_message = """🤖 <b>PRUEBA DE SISTEMA</b>

Este es un mensaje de prueba del sistema de monitoreo de órdenes de compra.

✅ La configuración de Telegram es correcta.

Sistema activo y listo para monitorear correos."""

        logger.info("Sending test Telegram message")
        return self.send_message(test_message)

    def send_startup_notification(self) -> bool:
        """
        Send notification that system has started

        Returns:
            True if notification sent successfully
        """
        num_clients = len(config.MONITORED_CLIENTS)
        check_interval = config.CHECK_INTERVAL_MINUTES

        message = f"""🚀 <b>SISTEMA INICIADO</b>

El agente de monitoreo de órdenes de compra está activo.

⏰ Revisión automática cada {check_interval} minutos
👥 Monitoreando {num_clients} clientes
📧 Buzón: ventas@quimicaguba.com

El sistema enviará notificaciones cuando detecte nuevas órdenes de compra."""

        logger.info("Sending startup notification")
        return self.send_message(message)

    def send_error_notification(self, error_description: str) -> bool:
        """
        Send error notification

        Args:
            error_description: Description of the error

        Returns:
            True if notification sent successfully
        """
        message = f"""⚠️ <b>ERROR EN EL SISTEMA</b>

{error_description}

Por favor revisa los logs para más detalles."""

        logger.info("Sending error notification")
        return self.send_message(message)

    def send_purchase_order_notification(self, client_name: str, details: str = "") -> bool:
        """
        Send purchase order notification

        Args:
            client_name: Name of the client who sent the order
            details: Additional details about the order

        Returns:
            True if notification sent successfully
        """
        logger.info(f"Sending PO notification for client: {client_name}")

        message = f"""📋 <b>NUEVA ORDEN DE COMPRA</b>

<b>Cliente:</b> {client_name}
{f'<b>Detalles:</b> {details}' if details else ''}

Se ha detectado una nueva orden de compra en el correo."""

        return self.send_message(message)
