"""
IMAP Client Module
Monitors email inbox for new messages from specific clients
Detects PDF attachments and processes them
"""
import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import config
from pdf_processor import PDFProcessor
from claude_analyzer import ClaudeAnalyzer

logger = logging.getLogger(__name__)


class IMAPClient:
    """Monitors IMAP inbox for purchase order emails"""

    def __init__(self):
        """Initialize IMAP client and dependencies"""
        self.server = config.IMAP_SERVER
        self.port = config.IMAP_PORT
        self.username = config.IMAP_USER
        self.password = config.IMAP_PASSWORD
        self.monitored_clients = config.MONITORED_CLIENTS

        # Initialize processors
        self.pdf_processor = PDFProcessor()
        self.claude_analyzer = ClaudeAnalyzer()

        # Initialize notification provider based on config
        if config.NOTIFICATION_PROVIDER == "telegram":
            from telegram_notifier import TelegramNotifier
            self.notifier = TelegramNotifier()
            logger.info("Using Telegram for notifications")
        elif config.NOTIFICATION_PROVIDER == "twilio":
            from whatsapp_notifier import WhatsAppNotifier
            self.notifier = WhatsAppNotifier()
            logger.info("Using Twilio WhatsApp for notifications")
        else:
            raise ValueError(f"Invalid notification provider: {config.NOTIFICATION_PROVIDER}")

        # Track processed emails
        self.processed_emails = self._load_processed_emails()

        logger.info(f"IMAP Client initialized for {self.username}")
        logger.info(f"Monitoring {len(self.monitored_clients)} clients")

    def _load_processed_emails(self) -> Set[str]:
        """Load set of already processed email IDs"""
        try:
            if config.PROCESSED_EMAILS_FILE.exists():
                with open(config.PROCESSED_EMAILS_FILE, "r") as f:
                    emails = {line.strip() for line in f if line.strip()}
                logger.info(f"Loaded {len(emails)} processed email IDs")
                if emails:
                    # Show first 5 IDs for debugging
                    sample = list(emails)[:5]
                    logger.info(f"Sample of processed IDs: {sample}")
                return emails
            return set()
        except Exception as e:
            logger.error(f"Error loading processed emails: {str(e)}")
            return set()

    def _save_processed_email(self, email_id: str):
        """Save email ID as processed"""
        try:
            self.processed_emails.add(email_id)
            with open(config.PROCESSED_EMAILS_FILE, "a") as f:
                f.write(f"{email_id}\n")
            logger.info(f"Saved processed email: {email_id}")
        except Exception as e:
            logger.error(f"Error saving processed email: {str(e)}")

    def connect(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Connect to IMAP server with SSL

        Returns:
            IMAP connection or None if connection fails
        """
        try:
            logger.info(f"Connecting to {self.server}:{self.port}")
            mail = imaplib.IMAP4_SSL(self.server, self.port)
            mail.login(self.username, self.password)
            logger.info("IMAP connection successful")
            return mail
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return None

    def _decode_header(self, header_value) -> str:
        """Decode email header (subject, from, etc.)"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        result = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result += part.decode(encoding or "utf-8", errors="ignore")
                except:
                    result += part.decode("utf-8", errors="ignore")
            else:
                result += str(part)

        return result

    def _extract_email_address(self, from_header: str) -> str:
        """Extract email address from From header"""
        try:
            # Format: "Name <email@domain.com>" or "email@domain.com"
            if "<" in from_header and ">" in from_header:
                start = from_header.index("<") + 1
                end = from_header.index(">")
                return from_header[start:end].lower().strip()
            return from_header.lower().strip()
        except:
            return from_header.lower().strip()

    def _get_pdf_attachments(self, msg) -> List[Dict]:
        """
        Extract PDF attachments from email message

        Returns:
            List of dictionaries with PDF filename and binary data
        """
        pdf_attachments = []

        for part in msg.walk():
            # Skip multipart containers
            if part.get_content_maintype() == "multipart":
                continue

            # Check if this is an attachment
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()

            # Check if it's a PDF
            if filename and filename.lower().endswith(".pdf"):
                pdf_data = part.get_payload(decode=True)
                if pdf_data:
                    pdf_attachments.append({"filename": filename, "data": pdf_data})
                    logger.info(f"Found PDF attachment: {filename}")

        return pdf_attachments

    def check_emails(self):
        """
        Check inbox for new emails from monitored clients
        Process any PDF attachments found
        """
        mail = self.connect()
        if not mail:
            logger.error("Cannot check emails - connection failed")
            return

        try:
            # Select inbox
            status, _ = mail.select("INBOX")
            if status != "OK":
                logger.error("Failed to select INBOX")
                return

            # Check each monitored client
            for client_email in self.monitored_clients:
                logger.info(f"Checking emails from: {client_email}")

                # Calculate search date in IMAP format (DD-Mon-YYYY)
                days_back = config.DAYS_BACK_TO_SEARCH
                search_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

                # Search for emails from this client since the search date
                # This will get both read and unread emails from that date onwards
                search_criteria = f'(FROM "{client_email}" SINCE {search_date})'
                status, message_ids = mail.search(None, search_criteria)

                logger.debug(f"Search criteria: {search_criteria}")

                if status != "OK":
                    logger.warning(f"Search failed for {client_email}")
                    continue

                email_ids = message_ids[0].split()
                logger.info(f"Found {len(email_ids)} new emails from {client_email}")

                # Process each email
                for email_id in email_ids:
                    self._process_email(mail, email_id, client_email)

        except Exception as e:
            logger.error(f"Error checking emails: {str(e)}")

        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

    def _process_email(self, mail, email_id: bytes, expected_sender: str):
        """Process a single email"""
        try:
            # Fetch email first to get Message-ID
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                logger.error(f"Failed to fetch email {email_id.decode()}")
                return

            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])

            # Use Message-ID as unique identifier (permanent, doesn't change)
            message_id = msg.get("Message-ID", "").strip()
            if not message_id:
                # Fallback: use combination of From, Subject, Date if Message-ID missing
                from_header = self._decode_header(msg["From"])
                subject = self._decode_header(msg["Subject"])
                date = msg["Date"]
                message_id = f"{from_header}_{subject}_{date}"
                logger.warning(f"No Message-ID found, using fallback: {message_id[:50]}")

            # Skip if already processed
            if message_id in self.processed_emails:
                logger.info(f"Email already processed (Message-ID: {message_id[:50]}...), skipping")
                return

            # Extract metadata
            subject = self._decode_header(msg["Subject"])
            from_header = self._decode_header(msg["From"])
            sender_email = self._extract_email_address(from_header)
            date = msg["Date"]

            logger.info(f"Processing NEW email: '{subject}' from {sender_email}")
            logger.info(f"Message-ID: {message_id[:80]}")

            # Mark email as processed FIRST to prevent reprocessing even if errors occur
            self._save_processed_email(message_id)

            # Get PDF attachments
            pdf_attachments = self._get_pdf_attachments(msg)

            if not pdf_attachments:
                logger.info(f"No PDF attachments found in email from {sender_email}")
                return

            logger.info(f"Found {len(pdf_attachments)} PDF(s) in email")

            # Process all PDFs and collect results
            pdf_analyses = []
            for pdf_info in pdf_attachments:
                analysis_result = self._analyze_pdf(pdf_info, sender_email)
                if analysis_result:
                    pdf_analyses.append(analysis_result)

            # Send single WhatsApp notification with all PDFs
            if pdf_analyses:
                self._send_grouped_notification(pdf_analyses, sender_email, subject, date)

            # Mark as read in inbox (optional)
            # mail.store(email_id, '+FLAGS', '\\Seen')

        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")

    def _analyze_pdf(self, pdf_info: Dict, sender_email: str) -> Optional[Dict]:
        """Analyze a single PDF and return the analysis result"""
        try:
            filename = pdf_info["filename"]
            pdf_data = pdf_info["data"]

            logger.info(f"Processing PDF: {filename}")

            # Step 1: Extract text from PDF
            pdf_text = self.pdf_processor.extract_text(pdf_data, filename)

            if not pdf_text:
                logger.warning(f"Could not extract text from {filename}")
                return None

            # Step 2: Analyze with Claude
            logger.info(f"Analyzing {filename} with Claude...")
            analysis = self.claude_analyzer.analyze_purchase_order(
                pdf_text, sender_email, filename
            )

            if not analysis:
                logger.error(f"Claude analysis failed for {filename}")
                return None

            logger.info(f"Successfully analyzed {filename}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            return None

    def _send_grouped_notification(
        self, pdf_analyses: List[Dict], sender_email: str, subject: str, date: str
    ):
        """Send a single WhatsApp notification for all PDFs in an email"""
        try:
            # Build header
            num_pdfs = len(pdf_analyses)
            message_parts = [
                f"{'🔔 NUEVA ORDEN DE COMPRA' if num_pdfs == 1 else '🔔 NUEVAS ÓRDENES DE COMPRA'}",
                f"\n📧 De: {sender_email}",
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"📎 {num_pdfs} PDF(s) adjunto(s)",
                f"\n{'='*40}\n"
            ]

            # Add each PDF analysis
            for i, analysis in enumerate(pdf_analyses, 1):
                if num_pdfs > 1:
                    message_parts.append(f"\n📄 PDF #{i}: {analysis.get('filename', 'Unknown')}")

                # Format this PDF's info
                pdf_msg = self.claude_analyzer.format_for_whatsapp(analysis)
                message_parts.append(pdf_msg)

                if i < num_pdfs:
                    message_parts.append(f"\n{'-'*40}")

            # Add email metadata at the end
            message_parts.append(f"\n\n📧 Asunto: {subject[:100]}")

            # Join all parts
            full_message = "\n".join(message_parts)

            # Send notification
            logger.info(f"Sending notification for {num_pdfs} PDF(s)...")

            # For Telegram, send the full detailed message
            if config.NOTIFICATION_PROVIDER == "telegram":
                success = self.notifier.send_message(full_message)

            # For Twilio WhatsApp, use template if configured, otherwise freeform
            elif config.NOTIFICATION_PROVIDER == "twilio":
                template_sid = config.TWILIO_WHATSAPP_TEMPLATE_SID

                if template_sid:
                    logger.info("Using WhatsApp template for notification")
                    client_name = pdf_analyses[0].get('client_name', sender_email)
                    success = self.notifier.send_purchase_order_notification(
                        client_name=client_name,
                        po_number=f"{num_pdfs} PDF(s)",
                        template_sid=template_sid
                    )
                else:
                    logger.info("Using freeform WhatsApp message")
                    success = self.notifier.send_message(full_message)
            else:
                logger.error(f"Unknown notification provider: {config.NOTIFICATION_PROVIDER}")
                success = False

            if success:
                logger.info(f"Successfully sent notification for {num_pdfs} PDF(s)")
            else:
                logger.error(f"Failed to send notification")

        except Exception as e:
            logger.error(f"Error sending grouped notification: {str(e)}")

    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("=" * 70)
        logger.info("Starting email monitoring cycle")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Monitored clients: {', '.join(self.monitored_clients)}")
        logger.info("=" * 70)

        try:
            self.check_emails()
            logger.info("Monitoring cycle completed successfully")
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {str(e)}")
            # Optionally send error notification
            # self.whatsapp.send_error_notification(str(e))

        logger.info("=" * 70 + "\n")
