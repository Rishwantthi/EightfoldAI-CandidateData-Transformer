"""
Normalization Utilities
Standardizes field values to canonical formats
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from dateutil import parser as date_parser
from fuzzywuzzy import fuzz


class Normalizers:
    """Collection of normalization functions"""
    
    # Canonical skill names (top 30 tech skills)
    CANONICAL_SKILLS = [
        "python", "javascript", "java", "go", "rust", "c++", "c#",
        "ruby", "php", "swift", "kotlin", "typescript",
        "react", "vue", "angular", "django", "flask", "nodejs",
        "sql", "postgresql", "mysql", "mongodb", "redis",
        "aws", "gcp", "azure", "docker", "kubernetes",
        "git", "ci/cd", "devops"
    ]
    
    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Dict[str, Any]:
        """
        Normalize phone to simple digits format (Ph3)
        
        Input: "555-1234", "(555) 123-4567", "+1-555-123-4567"
        Output: {"normalized": "5551234567", "confidence": 0.95}
        """
        if not phone:
            return None
        
        # Remove all non-digits
        cleaned = re.sub(r'\D', '', str(phone).strip())
        
        if len(cleaned) < 7:  # Too short
            return {
                "normalized": cleaned,
                "confidence": 0.3
            }
        
        # Standard US phone is 10 digits
        if len(cleaned) == 10:
            return {
                "normalized": cleaned,
                "confidence": 0.95
            }
        
        # With country code
        if len(cleaned) >= 11:
            return {
                "normalized": cleaned,
                "confidence": 0.90
            }
        
        return {
            "normalized": cleaned,
            "confidence": 0.60
        }
    
    @staticmethod
    def normalize_email(email: Optional[str]) -> Dict[str, Any]:
        """
        Normalize email (Em1: lowercase + validate)
        
        Input: "JOHN@EXAMPLE.COM", "john@example.com"
        Output: {"normalized": "john@example.com", "confidence": 0.99}
        """
        if not email:
            return None
        
        email = str(email).strip().lower()
        
        # Regex validation
        pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        
        if re.match(pattern, email):
            return {
                "normalized": email,
                "confidence": 0.99
            }
        
        # Invalid but return anyway
        return {
            "normalized": email,
            "confidence": 0.3
        }
    
    @staticmethod
    def normalize_date(date_str: Optional[str]) -> Dict[str, Any]:
        """
        Normalize date to YYYY-MM format (Da1: fuzzy)
        
        Input: "June 2020", "2020-06", "06/2020", "2020"
        Output: {"normalized": "2020-06", "confidence": 0.95}
        """
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # Try common formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %Y',
            '%b %Y',
            '%Y-%m',
            '%Y/%m',
            '%m/%Y',
            '%Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                normalized = parsed.strftime('%Y-%m')
                confidence = 0.95 if len(date_str) > 7 else 0.80
                return {
                    "normalized": normalized,
                    "confidence": confidence
                }
            except ValueError:
                continue
        
        # Try fuzzy parsing
        try:
            parsed = date_parser.parse(date_str, fuzzy=True)
            return {
                "normalized": parsed.strftime('%Y-%m'),
                "confidence": 0.85
            }
        except:
            pass
        
        # Give up
        return {
            "normalized": date_str,
            "confidence": 0.3
        }
    
    @staticmethod
    def normalize_skill(skill: Optional[str]) -> Dict[str, Any]:
        """
        Normalize skill using fuzzy matching (Sk2)
        
        Input: "python3", "Python", "py"
        Output: {"normalized": "python", "confidence": 0.99}
        """
        if not skill:
            return None
        
        skill_lower = str(skill).lower().strip()
        
        # Exact match first
        if skill_lower in Normalizers.CANONICAL_SKILLS:
            return {
                "normalized": skill_lower,
                "confidence": 0.99
            }
        
        # Fuzzy match (threshold 0.85)
        best_match = None
        best_score = 0
        
        for canonical in Normalizers.CANONICAL_SKILLS:
            score = fuzz.ratio(skill_lower, canonical) / 100.0
            if score > best_score and score >= 0.85:
                best_score = score
                best_match = canonical
        
        if best_match:
            return {
                "normalized": best_match,
                "confidence": best_score
            }
        
        # No good match, keep as-is with low confidence
        return {
            "normalized": skill_lower,
            "confidence": 0.5
        }
    
    @staticmethod
    def normalize_location(location: Optional[str]) -> Dict[str, Any]:
        """
        Normalize location by splitting (Lo1)
        
        Input: "San Francisco, CA", "SF, USA"
        Output: {"city": "San Francisco", "country": "CA", "confidence": 0.80}
        """
        if not location:
            return None
        
        location = str(location).strip()
        parts = [p.strip() for p in location.split(',')]
        
        result = {"confidence": 0.80}
        
        if len(parts) >= 2:
            result["city"] = parts[0]
            result["country"] = parts[1]
        elif len(parts) == 1:
            # Ambiguous - could be city or country
            result["city"] = parts[0]
            result["confidence"] = 0.5
        
        result["normalized"] = location  # Keep original too
        return result
    
    @staticmethod
    def normalize_value(field_name: str, value: Any) -> Dict[str, Any]:
        """
        Dispatch to appropriate normalizer based on field name
        """
        field_lower = field_name.lower()
        
        if 'phone' in field_lower:
            return Normalizers.normalize_phone(value)
        elif 'email' in field_lower:
            return Normalizers.normalize_email(value)
        elif 'date' in field_lower or 'start' in field_lower or 'end' in field_lower:
            return Normalizers.normalize_date(value)
        elif 'skill' in field_lower:
            return Normalizers.normalize_skill(value)
        elif 'location' in field_lower or 'city' in field_lower:
            return Normalizers.normalize_location(value)
        else:
            # No normalization needed
            return {
                "normalized": value,
                "confidence": 0.8
            }


# Example usage
if __name__ == "__main__":
    print("Phone:", Normalizers.normalize_phone("555-123-4567"))
    print("Email:", Normalizers.normalize_email("JOHN@EXAMPLE.COM"))
    print("Date:", Normalizers.normalize_date("June 2020"))
    print("Skill:", Normalizers.normalize_skill("python3"))
    print("Location:", Normalizers.normalize_location("San Francisco, CA"))