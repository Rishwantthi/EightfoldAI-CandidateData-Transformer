"""
STAGE 6: NORMALIZATION (N2)
Apply field-specific normalization to standardize values
Uses normalizers from utils/normalizers.py
"""

import logging
from typing import Dict, Any
from utils.normalizers import Normalizers

logger = logging.getLogger(__name__)


class ValueNormalizer:
    """
    Stage 6: Normalize field values
    
    Applies field-specific normalization:
    - Phones: Simple digits (Ph3)
    - Emails: Lowercase + validate (Em1)
    - Dates: YYYY-MM format (Da1)
    - Skills: Fuzzy-matched to canonical (Sk2)
    - Location: City, Country split (Lo1)
    
    Returns: {field: {normalized, confidence}}
    """
    
    def normalize(self, canonical_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Normalize all fields in canonical data
        
        Args:
            canonical_data: {canonical_field: value} from Stage 5
        
        Returns:
            {canonical_field: {normalized, confidence}}
        """
        logger.info(f"\n[STAGE 6] NORMALIZATION (N2)")
        logger.info(f"  Input fields: {len(canonical_data)}")
        
        normalized = {}
        
        for field, value in canonical_data.items():
            if value is None or value == '':
                continue
            
            # Apply field-specific normalization
            result = self._normalize_field(field, value)
            
            if result:
                normalized[field] = result
                confidence = result.get('confidence', 0.5)
                logger.info(f"    ✓ {field:20} → confidence: {confidence:.0%}")
        
        logger.info(f"  Output fields: {len(normalized)}")
        return normalized
    
    def _normalize_field(self, field: str, value: Any) -> Dict[str, Any]:
        """
        Normalize a single field value
        
        Returns: {normalized, confidence, method}
        """
        field_lower = field.lower()
        
        # Phone normalization
        if 'phone' in field_lower:

            if isinstance(value, list):

                normalized_phones = []

                for phone in value:

                    result = Normalizers.normalize_phone(phone)

                    if result:
                        normalized_phones.append(result["normalized"])

                return {
                    "normalized": normalized_phones,
                    "confidence": 0.95,
                    "method": "phone_list"
                }

            return Normalizers.normalize_phone(value)
        
        # Email normalization
        elif 'email' in field_lower:

            if isinstance(value, list):

                normalized_emails = []

                for email in value:

                    result = Normalizers.normalize_email(email)

                    if result:
                        normalized_emails.append(result["normalized"])

                return {
                    "normalized": normalized_emails,
                    "confidence": 0.99,
                    "method": "email_list"
                }

            return Normalizers.normalize_email(value)
        
        # Date normalization (for experience dates)
        elif 'date' in field_lower or 'start' in field_lower or 'end' in field_lower:
            return Normalizers.normalize_date(value)
        
        # Skill normalization
        elif 'skill' in field_lower:
            # Handle both single skills and lists
            if isinstance(value, list):
                normalized_skills = []
                for skill in value:
                    result = Normalizers.normalize_skill(skill)
                    if result:
                        normalized_skills.append(result)
                
                if normalized_skills:
                    # Average confidence
                    avg_confidence = sum(s.get('confidence', 0.5) for s in normalized_skills) / len(normalized_skills)
                    return {
                        'normalized': [s['normalized'] for s in normalized_skills],
                        'confidence': avg_confidence,
                        'method': 'skill_list_fuzzy_match'
                    }
            else:
                return Normalizers.normalize_skill(value)
        
        # Location normalization
        elif 'location' in field_lower or 'city' in field_lower or 'country' in field_lower:
            return Normalizers.normalize_location(value)
        
        # Years of experience - try to extract as integer
        elif 'year' in field_lower and 'experience' in field_lower:
            try:
                years = int(float(value))
                return {
                    'normalized': years,
                    'confidence': 0.95,
                    'method': 'numeric_conversion'
                }
            except:
                return {
                    'normalized': value,
                    'confidence': 0.5,
                    'method': 'no_normalization'
                }
        
        # No normalization needed for this field
        else:
            return {
                'normalized': value,
                'confidence': 0.8,
                'method': 'no_normalization'
            }


