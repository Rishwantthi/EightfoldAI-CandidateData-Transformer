"""
STAGE 3: SOURCE PARSER
Read each file type and extract raw data into Python dicts
"""

import csv
import json
import logging
import pdfplumber
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class SourceParser:
    """
    Stage 3: Parse source files
    
    Converts files into Python dictionaries:
    - CSV → dict (one row)
    - JSON → dict
    - Text → dict with 'full_text' key
    
    Returns: Raw dictionary (not normalized yet)
    """
    
    def parse_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Parse CSV file (single row - one candidate)
        
        Returns: Dictionary of {field: value}
        """
        logger.info(f"\n[STAGE 3.CSV] PARSING CSV")
        logger.info(f"  File: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    logger.warning(f"    ✗ CSV file is empty (no data rows)")
                    return {}
                
                # Take first row (one candidate per file)
                row = rows[0]
                
                # Clean up: remove empty values
                cleaned = {k: v for k, v in row.items() if v and v.strip()}
                
                logger.info(f"    ✓ Parsed 1 row, {len(cleaned)} fields")
                return cleaned
        
        except Exception as e:
            logger.error(f"    ✗ CSV parsing failed: {e}")
            return {}
    
    def parse_json(self, file_path: str) -> Dict[str, Any]:
        """
        Parse JSON file
        
        Returns: Dictionary
        """
        logger.info(f"\n[STAGE 3.JSON] PARSING JSON")
        logger.info(f"  File: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if not isinstance(data, dict):
                    logger.warning(f"    ⚠ JSON is not a dict (might be array)")
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                        logger.info(f"    → Using first element")
                
                logger.info(f"    ✓ Parsed JSON, {len(data)} fields")
                return data
        
        except json.JSONDecodeError as e:
            logger.error(f"    ✗ JSON parsing failed: {e}")
            return {}
        except Exception as e:
            logger.error(f"    ✗ Error reading JSON: {e}")
            return {}
    
    def parse_text(self, file_path: str) -> Dict[str, Any]:
        """
        Parse plain text file (resume, notes)
        
        Returns: Dictionary with 'full_text' key
        """
        logger.info(f"\n[STAGE 3.TEXT] PARSING TEXT")
        logger.info(f"  File: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                
                # Count lines and words
                lines = text.split('\n')
                words = text.split()
                
                logger.info(f"    ✓ Parsed text, {len(lines)} lines, {len(words)} words")
                
                return {
                    'full_text': text,
                    'line_count': len(lines),
                    'word_count': len(words)
                }
        
        except Exception as e:
            logger.error(f"    ✗ Text parsing failed: {e}")
            return {}
        
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume PDF using pdfplumber.

        Returns:
        {
            "full_text": "...",
            "line_count": ...,
            "word_count": ...
        }
        """

        logger.info("\n[STAGE 3.PDF] PARSING PDF")
        logger.info(f"  File: {file_path}")

        try:

            text = ""

            with pdfplumber.open(file_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

            lines = text.split("\n")
            words = text.split()

            logger.info(
                f"    ✓ Parsed PDF ({len(pdf.pages)} pages)"
            )

            logger.info(
                f"    ✓ {len(lines)} lines, {len(words)} words"
            )

            return {

                "full_text": text,

                "line_count": len(lines),

                "word_count": len(words)

            }

        except Exception as e:

            logger.error(f"    ✗ PDF parsing failed: {e}")

            return {}    
    
    def parse(self, file_path: str, source_type: str) -> Dict[str, Any]:
        """
        Main parse method - dispatch to appropriate parser
        
        Args:
            file_path: Path to file
            source_type: "csv", "json", or "text"
        
        Returns:
            Raw parsed data (dictionary)
        """
        source_type_lower = source_type.lower()
        
        if source_type_lower in ['csv', 'recruiter']:
            return self.parse_csv(file_path)
        elif source_type_lower in ['json', 'ats']:
            return self.parse_json(file_path)
        elif source_type_lower in ['pdf', 'resume']:
            return self.parse_pdf(file_path)
        elif source_type_lower in ['text', 'txt', 'notes']:
            return self.parse_text(file_path)
        else:
            logger.warning(f"Unknown source type: {source_type}, treating as text")
            return self.parse_text(file_path)


