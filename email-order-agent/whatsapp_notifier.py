"""
WhatsApp Notifier Module
Sends WhatsApp messages using Twilio API
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from requests.exceptions import SSLError, ConnectionError, Timeout, RequestException
import config

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """Sends WhatsApp notifications using Twilio"""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        """
        Initialize Twilio client

        Args:
            max_retries: Maximum number of retry attempts for failed messages
            timeout: Timeout in seconds for Twilio API calls
        """
        try:
            self.client = Client(
                config.TWILIO_ACCOUNT_SID,
                config.TWILIO_AUTH_TOKEN
            )
            self.from_number = config.TWILIO_WHATSAPP_FROM
            self.to_number = config.TWILIO_WHATSAPP_TO
            self.last_message_file = config.LOGS_DIR / "last_whatsapp_message.txt"
            self.max_retries = max_retries
            self.timeout = timeout

            logger.info(
                f"WhatsApp notifier initialized. From: {self.from_number}, "
                f"To: {self.to_number}, Max retries: {max_retries}, Timeout: {timeout}s"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise

    def send_message(self, message: str) -> bool:
        """
        Send WhatsApp message via Twilio with automatic retry on network errors

        Args:
            message: Message text to send

        Returns:
            True if message sent successfully, False otherwise
        """
        # Twilio has a message limit, truncate if needed
        max_length = 1600  # Twilio limit
        if len(message) > max_length:
            logger.warning(
                f"Message too long ({len(message)} chars). Truncating to {max_length}"
            )
            message = message[:max_length - 50] + "\n\n... (mensaje truncado)"

        logger.info(f"Sending WhatsApp message ({len(message)} chars)")

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Send via Twilio (timeout is handled by underlying http client)
                twilio_message = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=self.to_number
                )

                logger.info(
                    f"WhatsApp message sent successfully. SID: {twilio_message.sid}, "
                    f"Status: {twilio_message.status}"
                )

                # Update last message timestamp
                self._update_last_message_time()

                return True

            except TwilioRestException as e:
                # Check for "outside allowed window" error (63016)
                if e.code == 63016:
                    logger.error(
                        f"WhatsApp 24-hour window expired (error 63016). "
                        "Cannot send freeform messages. Use send_template_message() instead."
                    )
                    return False
                # Other Twilio API errors (authentication, invalid numbers, etc.) - don't retry
                logger.error(f"Twilio API error (non-retryable): {e.code} - {e.msg}")
                return False

            except (SSLError, ConnectionError, Timeout) as e:
                # Network-related errors - retry with backoff
                attempt_num = attempt + 1
                error_type = type(e).__name__
                logger.warning(
                    f"Network error on attempt {attempt_num}/{self.max_retries}: "
                    f"{error_type} - {str(e)}"
                )

                if attempt_num < self.max_retries:
                    # Exponential backoff: 2, 4, 8 seconds
                    wait_time = 2 ** attempt_num
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to send WhatsApp message after {self.max_retries} attempts. "
                        f"Last error: {error_type} - {str(e)}"
                    )
                    return False

            except RequestException as e:
                # Other request errors - retry
                attempt_num = attempt + 1
                logger.warning(
                    f"Request error on attempt {attempt_num}/{self.max_retries}: {str(e)}"
                )

                if attempt_num < self.max_retries:
                    wait_time = 2 ** attempt_num
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to send WhatsApp message after {self.max_retries} attempts. "
                        f"Last error: {str(e)}"
                    )
                    return False

            except Exception as e:
                # Unexpected errors - log and don't retry
                logger.error(f"Unexpected error sending WhatsApp message: {type(e).__name__} - {str(e)}")
                return False

        return False

    def send_template_message(self, template_sid: str, content_variables: dict = None) -> bool:
        """
        Send WhatsApp message using an approved Content Template
        This works even outside the 24-hour conversation window

        Args:
            template_sid: The SID of the approved WhatsApp template (format: HXxxxx...)
            content_variables: Dictionary of variables to replace in template (1-indexed)
                              Example: {"1": "value1", "2": "value2"}

        Returns:
            True if message sent successfully, False otherwise
        """
        logger.info(f"Sending WhatsApp template message (SID: {template_sid})")

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Build message parameters
                message_params = {
                    "from_": self.from_number,
                    "to": self.to_number,
                    "content_sid": template_sid
                }

                # Add content variables if provided
                if content_variables:
                    # Convert to JSON string format required by Twilio
                    message_params["content_variables"] = str(content_variables)
                    logger.info(f"Template variables: {content_variables}")

                # Send via Twilio
                twilio_message = self.client.messages.create(**message_params)

                logger.info(
                    f"WhatsApp template message sent successfully. SID: {twilio_message.sid}, "
                    f"Status: {twilio_message.status}"
                )

                # Update last message timestamp
                self._update_last_message_time()

                return True

            except TwilioRestException as e:
                # Twilio API errors (authentication, invalid template, etc.) - don't retry
                logger.error(f"Twilio API error sending template: {e.code} - {e.msg}")
                return False

            except (SSLError, ConnectionError, Timeout) as e:
                # Network-related errors - retry with backoff
                attempt_num = attempt + 1
                error_type = type(e).__name__
                logger.warning(
                    f"Network error on attempt {attempt_num}/{self.max_retries}: "
                    f"{error_type} - {str(e)}"
                )

                if attempt_num < self.max_retries:
                    wait_time = 2 ** attempt_num
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to send template after {self.max_retries} attempts. "
                        f"Last error: {error_type} - {str(e)}"
                    )
                    return False

            except Exception as e:
                # Unexpected errors - log and don't retry
                logger.error(f"Unexpected error sending template: {type(e).__name__} - {str(e)}")
                return False

        return False

    def send_purchase_order_notification(self, client_name: str, po_number: str = "",
                                         template_sid: str = None) -> bool:
        """
        Send purchase order notification using either freeform or template
        Automatically uses template if provided or falls back to freeform

        Args:
            client_name: Name of the client who sent the order
            po_number: Purchase order number (optional)
            template_sid: WhatsApp template SID (optional, use for 24h+ window)

        Returns:
            True if notification sent successfully
        """
        if template_sid:
            # Use approved template (works outside 24h window)
            logger.info(f"Sending PO notification via template for client: {client_name}")

            # Prepare variables for template
            variables = {"1": client_name}
            if po_number:
                variables["2"] = po_number

            return self.send_template_message(template_sid, variables)
        else:
            # Use freeform message (only works within 24h window)
            logger.info(f"Sending PO notification via freeform for client: {client_name}")

            po_info = f" - PO: {po_number}" if po_number else ""
            message = f"""📋 NUEVA ORDEN DE COMPRA

Cliente: {client_name}{po_info}

Se ha detectado una nueva orden de compra en el correo."""

            return self.send_message(message)

    def send_test_message(self) -> bool:
        """
        Send a test message to verify configuration

        Returns:
            True if test message sent successfully
        """
        test_message = """🤖 PRUEBA DE SISTEMA

Este es un mensaje de prueba del sistema de monitoreo de órdenes de compra.

✅ La configuración de Twilio WhatsApp es correcta.

Sistema activo y listo para monitorear correos."""

        logger.info("Sending test WhatsApp message")
        return self.send_message(test_message)

    def send_startup_notification(self) -> bool:
        """
        Send notification that system has started

        Returns:
            True if notification sent successfully
        """
        num_clients = len(config.MONITORED_CLIENTS)
        check_interval = config.CHECK_INTERVAL_MINUTES

        message = f"""🚀 SISTEMA INICIADO

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
        message = f"""⚠️ ERROR EN EL SISTEMA

{error_description}

Por favor revisa los logs para más detalles."""

        logger.info("Sending error notification")
        return self.send_message(message)

    def get_message_history(self, limit: int = 10) -> list:
        """
        Retrieve recent message history (optional)

        Args:
            limit: Number of recent messages to retrieve

        Returns:
            List of recent messages
        """
        try:
            messages = self.client.messages.list(
                from_=self.from_number,
                limit=limit
            )

            history = []
            for msg in messages:
                history.append({
                    "sid": msg.sid,
                    "to": msg.to,
                    "status": msg.status,
                    "date_sent": msg.date_sent,
                    "body_preview": msg.body[:50] if msg.body else ""
                })

            logger.info(f"Retrieved {len(history)} messages from history")
            return history

        except Exception as e:
            logger.error(f"Error retrieving message history: {str(e)}")
            return []

    def _update_last_message_time(self):
        """Update the timestamp of the last sent message"""
        try:
            with open(self.last_message_file, "w") as f:
                f.write(datetime.now().isoformat())
            logger.debug("Updated last message timestamp")
        except Exception as e:
            logger.error(f"Error updating last message time: {str(e)}")

    def _get_last_message_time(self) -> Optional[datetime]:
        """Get the timestamp of the last sent message"""
        try:
            if self.last_message_file.exists():
                with open(self.last_message_file, "r") as f:
                    timestamp_str = f.read().strip()
                    return datetime.fromisoformat(timestamp_str)
            return None
        except Exception as e:
            logger.error(f"Error reading last message time: {str(e)}")
            return None

    def should_send_heartbeat(self, hours_threshold: int = 48) -> bool:
        """
        Check if a heartbeat message should be sent

        Args:
            hours_threshold: Number of hours of inactivity before sending heartbeat

        Returns:
            True if heartbeat should be sent, False otherwise
        """
        last_message_time = self._get_last_message_time()

        if last_message_time is None:
            # No record of last message, send heartbeat
            logger.info("No record of last message, heartbeat needed")
            return True

        time_since_last = datetime.now() - last_message_time
        hours_since_last = time_since_last.total_seconds() / 3600

        if hours_since_last >= hours_threshold:
            logger.info(
                f"Last message was {hours_since_last:.1f} hours ago "
                f"(threshold: {hours_threshold}h), heartbeat needed"
            )
            return True
        else:
            logger.debug(
                f"Last message was {hours_since_last:.1f} hours ago, "
                f"heartbeat not needed yet"
            )
            return False

    def send_heartbeat(self) -> bool:
        """
        Send a heartbeat message to keep Twilio Sandbox session active

        Returns:
            True if heartbeat sent successfully
        """
        message = """💚 SISTEMA ACTIVO

El sistema de monitoreo de órdenes de compra está funcionando correctamente.

✅ Conexión WhatsApp activa
⏰ Monitoreando correos continuamente

(Este es un mensaje automático para mantener la conexión activa)"""

        logger.info("Sending heartbeat message to keep session alive")
        return self.send_message(message)
