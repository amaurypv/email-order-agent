"""
PDF Processor Module
Extracts text content from PDF files using pdfplumber
"""
import logging
import pdfplumber
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction"""

    @staticmethod
    def extract_text(pdf_data: bytes, filename: str = "unknown.pdf") -> Optional[str]:
        """
        Extract text from PDF binary data

        Args:
            pdf_data: Binary PDF data
            filename: Name of the PDF file (for logging)

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info(f"Processing PDF: {filename}")

            text_content = []

            with pdfplumber.open(BytesIO(pdf_data)) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"PDF has {num_pages} pages")

                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(f"--- Page {page_num} ---\n{page_text}")
                            logger.debug(f"Extracted text from page {page_num}")
                        else:
                            logger.warning(f"No text found on page {page_num}")
                    except Exception as e:
                        logger.error(f"Error extracting page {page_num}: {str(e)}")
                        continue

            if not text_content:
                logger.warning(f"No text could be extracted from {filename}")
                return None

            full_text = "\n\n".join(text_content)
            logger.info(
                f"Successfully extracted {len(full_text)} characters from {filename}"
            )

            return full_text

        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            return None

    @staticmethod
    def extract_tables(pdf_data: bytes, filename: str = "unknown.pdf") -> list:
        """
        Extract tables from PDF (optional advanced feature)

        Args:
            pdf_data: Binary PDF data
            filename: Name of the PDF file

        Returns:
            List of tables found in the PDF
        """
        try:
            tables = []

            with pdfplumber.open(BytesIO(pdf_data)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_tables = page.extract_tables()
                        if page_tables:
                            tables.extend(page_tables)
                            logger.debug(
                                f"Found {len(page_tables)} tables on page {page_num}"
                            )
                    except Exception as e:
                        logger.error(f"Error extracting tables from page {page_num}: {str(e)}")
                        continue

            logger.info(f"Extracted {len(tables)} tables from {filename}")
            return tables

        except Exception as e:
            logger.error(f"Error extracting tables from {filename}: {str(e)}")
            return []

    @staticmethod
    def get_metadata(pdf_data: bytes, filename: str = "unknown.pdf") -> dict:
        """
        Get PDF metadata

        Args:
            pdf_data: Binary PDF data
            filename: Name of the PDF file

        Returns:
            Dictionary with PDF metadata
        """
        try:
            with pdfplumber.open(BytesIO(pdf_data)) as pdf:
                metadata = {
                    "num_pages": len(pdf.pages),
                    "metadata": pdf.metadata if hasattr(pdf, "metadata") else {},
                    "filename": filename,
                }
                logger.debug(f"Retrieved metadata for {filename}")
                return metadata
        except Exception as e:
            logger.error(f"Error getting metadata from {filename}: {str(e)}")
            return {
                "num_pages": 0,
                "metadata": {},
                "filename": filename,
            }
