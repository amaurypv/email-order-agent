"""
Claude Analyzer Module
Uses Claude Haiku API to analyze PDF content and extract purchase order information
"""
import logging
import json
from typing import Optional, Dict
from anthropic import Anthropic
import config

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Analyzes documents using Claude Haiku for cost-effective processing"""

    def __init__(self):
        """Initialize Claude client with API key"""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-haiku-20241022"  # Most cost-effective model
        logger.info(f"Initialized Claude Analyzer with model: {self.model}")

    def analyze_purchase_order(
        self, pdf_text: str, sender_email: str, filename: str
    ) -> Optional[Dict]:
        """
        Analyze PDF text to extract purchase order information

        Args:
            pdf_text: Extracted text from PDF
            sender_email: Email address of sender
            filename: Name of the PDF file

        Returns:
            Dictionary with extracted information or None if analysis fails
        """
        try:
            # Limit text to first 4000 characters to optimize costs
            # Most PO info is in the first pages
            text_sample = pdf_text[:4000] if len(pdf_text) > 4000 else pdf_text

            logger.info(f"Analyzing PDF: {filename} from {sender_email}")
            logger.debug(f"Text length: {len(text_sample)} characters")

            prompt = self._build_analysis_prompt(text_sample, sender_email, filename)

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract response
            response_text = message.content[0].text

            # Log token usage for cost tracking
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            logger.info(
                f"Claude API call completed. Tokens: {input_tokens} input, "
                f"{output_tokens} output"
            )

            # Parse JSON response
            analysis_result = self._parse_claude_response(response_text)

            if analysis_result:
                analysis_result["sender_email"] = sender_email
                analysis_result["filename"] = filename
                analysis_result["tokens_used"] = input_tokens + output_tokens

                logger.info(
                    f"Analysis complete. Is PO: {analysis_result.get('is_purchase_order')}"
                )

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing PDF with Claude: {str(e)}")
            return None

    def _build_analysis_prompt(
        self, text: str, sender_email: str, filename: str
    ) -> str:
        """Build the prompt for Claude API"""
        return f"""Analyze the following document that may be a purchase order.

Sender: {sender_email}
Filename: {filename}

Document content:
{text}

Extract the following information and respond ONLY with valid JSON:

{{
    "is_purchase_order": true/false,
    "client_name": "company or client name",
    "order_number": "PO number or null",
    "order_date": "date or null",
    "products": [
        {{
            "name": "product name",
            "quantity": "quantity with units",
            "unit_price": "price or null"
        }}
    ],
    "total_amount": "total amount or null",
    "special_notes": "any important notes or null",
    "confidence": "high/medium/low"
}}

If this is NOT a purchase order, set is_purchase_order to false and briefly explain what it is in special_notes.
Respond with ONLY valid JSON, no additional text."""

    def _parse_claude_response(self, response_text: str) -> Optional[Dict]:
        """Parse Claude's JSON response"""
        try:
            # Find JSON in response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                logger.error("No JSON found in Claude response")
                return None

            json_text = response_text[start_idx:end_idx]
            result = json.loads(json_text)

            logger.debug("Successfully parsed Claude JSON response")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            return None

    def format_for_whatsapp(self, analysis: Dict) -> str:
        """
        Format analysis results for WhatsApp message

        Args:
            analysis: Analysis dictionary from Claude

        Returns:
            Formatted WhatsApp message
        """
        if not analysis.get("is_purchase_order", False):
            # Not a purchase order
            return f"""⚠️ DOCUMENTO RECIBIDO (No es orden de compra)

👤 Cliente: {analysis.get('client_name', 'Desconocido')}
📧 De: {analysis.get('sender_email', 'Desconocido')}

ℹ️ {analysis.get('special_notes', 'Documento no identificado como orden de compra')}"""

        # Build purchase order message
        message_parts = [
            "🔔 NUEVA ORDEN DE COMPRA\n",
            f"👤 Cliente: {analysis.get('client_name', 'Desconocido')}",
            f"📧 De: {analysis.get('sender_email', 'Desconocido')}",
        ]

        if analysis.get("order_date"):
            message_parts.append(f"📅 {analysis['order_date']}")

        if analysis.get("order_number"):
            message_parts.append(f"\n📄 Orden: {analysis['order_number']}")

        # Products
        products = analysis.get("products", [])
        if products:
            message_parts.append("\n\n📦 Productos:")
            for product in products:
                name = product.get("name", "Sin nombre")
                qty = product.get("quantity", "N/A")
                price = product.get("unit_price")

                product_line = f"- {name} - {qty}"
                if price:
                    product_line += f" @ {price}"
                message_parts.append(product_line)

        # Total
        if analysis.get("total_amount"):
            message_parts.append(f"\n💰 Total: {analysis['total_amount']}")

        # Special notes
        if analysis.get("special_notes"):
            message_parts.append(f"\n📝 {analysis['special_notes']}")

        # Add filename
        if analysis.get("filename"):
            message_parts.append(f"\n📎 Archivo: {analysis['filename']}")

        # Confidence indicator
        confidence = analysis.get("confidence", "medium")
        confidence_emoji = {"high": "✅", "medium": "⚠️", "low": "❓"}
        message_parts.append(
            f"\n{confidence_emoji.get(confidence, '⚠️')} Confianza: {confidence}"
        )

        return "\n".join(message_parts)
