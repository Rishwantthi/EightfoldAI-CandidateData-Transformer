"""
STAGE 2: SOURCE DETECTION (D2 - Content Sniffing)
Detect what type of source each file is (CSV, JSON, PDF, Text)
by reading and analyzing the actual content
"""

import os
import json
import csv
import logging
from enum import Enum
from typing import Tuple

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Supported source types"""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    TEXT = "text"
    UNKNOWN = "unknown"


class SourceDetector:
    """
    Stage 2: Detect source type
    
    Strategy: Content sniffing (read file and analyze)
    Fallback: File extension
    
    Returns: (source_type, detection_reason)
    """
    
    def detect(self, file_path: str) -> Tuple[SourceType, str]:
        """
        Detect source type by examining file content
        
        Args:
            file_path: Path to file
        
        Returns:
            (source_type, reasoning)
        """
        logger.info(f"\n[STAGE 2] SOURCE DETECTION")
        logger.info(f"  Detecting: {file_path}")
        
        # Try extension first (fast path)
        ext = os.path.splitext(file_path)[1].lower()
        
        # PDF detection by extension (binary file, hard to sniff)
        if ext == '.pdf':
            logger.info(f"    → Detected by extension: PDF")
            return SourceType.PDF, "PDF file extension"
        
        # For text files, read and analyze content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove leading/trailing whitespace
            content = content.strip()
            
            if not content:
                logger.warning(f"    → Empty file, treating as TEXT")
                return SourceType.TEXT, "Empty file"
            
            # ===== JSON DETECTION =====
            # Strategy: Check if starts with { or [ AND contains JSON-like patterns
            if content[0] in '{[':
                # JSON files typically have colons and quotes
                # Look for pattern: "key": value
                if '":' in content or '": ' in content:
                    try:
                        # Try to parse the ENTIRE content
                        json.loads(content)
                        logger.info(f"    → Detected by content: JSON (valid parse)")
                        return SourceType.JSON, "Valid JSON detected"
                    except json.JSONDecodeError:
                        pass
            
            # ===== CSV DETECTION =====

            lines = [
                line
                for line in content.splitlines()
                if line.strip()
            ]

            # -------------------------------------------------
            # NEW CODE: Detect recruiter notes / prose first
            # -------------------------------------------------

            prose_lines = sum(
                1
                for line in lines[:10]
                if line.strip().endswith(":")
                or line.strip().startswith("-")
            )

            if prose_lines >= 3:
                logger.info(
                    "    → Detected by content: TEXT (prose)"
                )
                return (
                    SourceType.TEXT,
                    "Structured notes detected"
                )

            # -------------------------------------------------
            # Existing CSV detection
            # -------------------------------------------------

            if len(lines) >= 2:

                try:

                    sample = "\n".join(lines[:5])

                    dialect = csv.Sniffer().sniff(sample)

                    reader = csv.reader(lines, dialect)

                    rows = list(reader)

                    if len(rows) >= 2:

                        header_cols = len(rows[0])
                        data_cols = len(rows[1])

                        if (
                            header_cols >= 2
                            and header_cols == data_cols
                        ):

                            logger.info(
                                "    → Detected by content: CSV"
                            )

                            return (
                                SourceType.CSV,
                                "CSV detected using csv.Sniffer"
                            )

                except csv.Error:
                    pass
                
                    
                # ===== DEFAULT: TEXT =====
                logger.info(f"    → Detected by content: TEXT (unstructured)")
                return SourceType.TEXT, "Unstructured text"
        
        except Exception as e:
            logger.warning(f"    → Error during detection: {e}, assuming TEXT")
            return SourceType.TEXT, f"Error during detection: {str(e)}"
    
    def detect_batch(self, inputs: dict) -> dict:
        """
        Detect multiple files at once
        
        Args:
            inputs: {"csv": "/path", "json": "/path", ...}
        
        Returns:
            {"csv": (SourceType.CSV, reason), ...}
        """
        logger.info(f"\n[STAGE 2] BATCH DETECTION ({len(inputs)} files)")
        
        results = {}
        for source_name, file_path in inputs.items():
            source_type, reason = self.detect(file_path)
            results[source_name] = (source_type, reason)
            logger.info(f"  {source_name}: {source_type.value} ({reason})")
        
        return results


