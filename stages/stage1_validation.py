"""
STAGE 1: INPUT VALIDATION (V2)
Check that input files exist and are readable
"""

import os
import logging
from typing import Dict, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Stage 1: Validate input files
    
    Checks:
    - File exists
    - File is readable
    - File is not empty
    
    Returns: (is_valid: bool, errors: List[str])
    """
    
    def __init__(self):
        self.errors = []
    
    def validate(self, inputs: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate all input files
        
        Args:
            inputs: Dict mapping source type to file path
                   {"csv": "/path/to/recruiter.csv", ...}
        
        Returns:
            (is_valid, error_messages)
        """
        self.errors = []  # Reset errors
        
        if not inputs:
            self.errors.append("No inputs provided")
            return False, self.errors
        
        logger.info(f"\n[STAGE 1] INPUT VALIDATION")
        logger.info(f"Validating {len(inputs)} input(s)...")
        
        for source_type, file_path in inputs.items():
            logger.info(f"\n  Checking {source_type}: {file_path}")
            
            # Check 1: File path provided
            if not file_path:
                error = f"[{source_type}] No file path provided"
                self.errors.append(error)
                logger.warning(f"    ✗ {error}")
                continue
            
            # Check 2: File exists
            if not os.path.exists(file_path):
                error = f"[{source_type}] File does not exist: {file_path}"
                self.errors.append(error)
                logger.warning(f"    ✗ {error}")
                continue
            
            # Check 3: File is readable
            if not os.access(file_path, os.R_OK):
                error = f"[{source_type}] File not readable (permission denied): {file_path}"
                self.errors.append(error)
                logger.warning(f"    ✗ {error}")
                continue
            
            # Check 4: File is not empty
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                error = f"[{source_type}] File is empty: {file_path}"
                self.errors.append(error)
                logger.warning(f"    ✗ {error}")
                continue
            
            # All checks passed for this file
            logger.info(f"    ✓ Valid ({file_size} bytes)")
        
        # Summary
        valid = len(self.errors) == 0
        if valid:
            logger.info(f"\n✓ All inputs validated successfully")
        else:
            logger.warning(f"\n✗ Validation failed with {len(self.errors)} error(s)")
        
        return valid, self.errors
    
    def get_errors(self) -> List[str]:
        """Return list of validation errors"""
        return self.errors


