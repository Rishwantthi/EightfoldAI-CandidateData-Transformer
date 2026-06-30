"""
Stage 4: Information Extraction
Extract candidate information from parsed content (E2: fuzzy field matching)
"""

import logging
import re
from typing import Dict, Any, List, Optional
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


class InformationExtractor:
    """Extract candidate information from various formats"""
    
    # Canonical field names we're looking for
    CANONICAL_FIELDS = [
        "full_name", "name",
        "email", "emails",
        "phone", "phones",
        "company",
        "headline",
        "location",
        "skills",
        "years_experience"
    ]
    FIELD_VARIANTS = {
    "full_name": ["full_name", "name", "candidate_name"],
    "email": ["email", "emails", "primary_email", "work_email", "personal_email"],
    "phone": ["phone", "phones", "contact_phone", "mobile", "telephone"],
    "company": ["company", "current_company", "employer", "organization"],
    "headline": ["headline", "title", "job_title", "designation"],
    "years_experience": ["years_experience", "years_exp", "experience", "exp"],
    "skills": ["skills", "technical_skills", "tech_stack", "technologies"],
    "location": ["location", "city", "address"]
    }
    
    # Fuzzy matching threshold
    FUZZY_THRESHOLD = 0.75
    
    @staticmethod
    def extract_from_dict(data: Dict[str, Any], source_type: str = "json") -> Dict[str, Any]:
        """
        Extract fields from dictionary (CSV row or JSON object)
        
        Args:
            data: Dictionary with candidate info
            source_type: "csv" or "json"
        
        Returns:
            Extracted fields
        """
        extracted = {}
        
        # For each field in the data
        for key, value in data.items():
            # Find best matching canonical field
            best_match = InformationExtractor._fuzzy_match_field(key)
            
            if best_match:
                # Parse value based on field type
                parsed_value = InformationExtractor._parse_value(best_match, value)
                if parsed_value is not None:
                    extracted[best_match] = parsed_value
        
        logger.info(f"Extracted {len(extracted)} fields from {source_type}")
        return extracted
    
    @staticmethod
    def extract_from_text(text: str) -> Dict[str, Any]:
        """
        Extract fields from free-form text (PDF or notes)
        
        Args:
            text: Raw text content
        
        Returns:
            Extracted fields
        """
        extracted = {}
        
        # Extract emails
        emails = InformationExtractor._extract_emails(text)
        if emails:
            extracted["emails"] = emails
        
        # Extract phones
        phones = InformationExtractor._extract_phones(text)
        if phones:
            extracted["phones"] = phones
        
        # Extract name (look for patterns)
        name = InformationExtractor._extract_name(text)
        if name:
            extracted["full_name"] = name
        
        # Extract company (look for common patterns)
        company = InformationExtractor._extract_company(text)
        if company:
            extracted["company"] = company
        
        # Extract skills (look for tech keywords)
        skills = InformationExtractor._extract_skills(text)
        if skills:
            extracted["skills"] = skills
        
        # Extract location - ✅ BUG FIX: Now stops at line boundaries
        location = InformationExtractor._extract_location(text)
        if location:
            extracted["location"] = location
        
        logger.info(f"Extracted {len(extracted)} fields from text")
        return extracted
    
    @staticmethod
    def _fuzzy_match_field(field_name: str) -> Optional[str]:
        """
        Find best matching canonical field name.
        First checks known field variants,
        then falls back to fuzzy matching.
        """

        field_lower = field_name.lower().strip()

        # ---------------------------------
        # Step 1: Exact variant lookup
        # ---------------------------------

        for canonical, variants in InformationExtractor.FIELD_VARIANTS.items():
            if field_lower in variants:
                return canonical

        # ---------------------------------
        # Step 2: Fuzzy matching
        # ---------------------------------

        best_match = None
        best_score = 0

        for canonical in InformationExtractor.CANONICAL_FIELDS:

            score = fuzz.ratio(field_lower, canonical) / 100.0

            if score > best_score and score >= InformationExtractor.FUZZY_THRESHOLD:
                best_score = score
                best_match = canonical

        return best_match
    
    @staticmethod
    def _parse_value(field_name: str, value: Any) -> Any:
        """
        Parse value based on field type
        """
        if value is None or value == "":
            return None
        
        if field_name in ["email", "emails", "phone", "phones", "skills"]:
            # These should be lists
            if isinstance(value, list):
                return [str(v).strip() for v in value if v]
            elif isinstance(value, str):
                # Split by comma or semicolon
                return [v.strip() for v in re.split(r'[,;]', value) if v.strip()]
            else:
                return [str(value)]
        
        # Otherwise just convert to string
        return str(value).strip() if value else None
    
    @staticmethod
    def _extract_emails(text: str) -> List[str]:
        """Extract email addresses from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Deduplicate
    
    @staticmethod
    def _extract_phones(text: str) -> List[str]:
        """Extract phone numbers from text"""
        pattern = r'[\+]?1?\s?[\(]?[\d]{3}[\)]?\s?[\d]{3}[\-]?[\d]{4}\b'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Deduplicate
    
    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """
        Extract person's name from text
        Look for capitalized words at the beginning
        """
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            words = line.strip().split()
            if len(words) >= 2:
                # Check if starts with capital letters (name pattern)
                if words[0][0].isupper() and words[1][0].isupper():
                    return ' '.join(words[:2])
        return None
    
    @staticmethod
    def _extract_company(text: str) -> Optional[str]:
        """
        Extract company name from text
        Look for patterns like "at Google" or "Google Inc"
        """
        # Common company patterns
        patterns = [
            r'(?:at|working at|employed at)\s+([A-Z][a-zA-Z\s&.]+)',
            r'([A-Z][a-zA-Z\s&.]+(?:Inc|Corp|LLC|Ltd))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        return None
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """
        Extract technical skills from text
        Look for known tech keywords
        """
        tech_keywords = [
            "python", "javascript", "java", "go", "rust", "c++", "c#",
            "ruby", "php", "swift", "kotlin", "typescript",
            "react", "vue", "angular", "django", "flask", "nodejs",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "aws", "gcp", "azure", "docker", "kubernetes",
            "git", "devops", "ci/cd"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in tech_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def _extract_location(text: str) -> Optional[str]:
        """
        Extract location from text
        Look for city, state/country patterns
        BUG FIX CRITICAL: Use (?=\n|$) to stop at line boundaries
        This prevents capturing multiple lines of text
        """
        # Pattern 1: Labeled location (Location:, Based in:, etc.)
        # CRITICAL: (?=\n|$) ensures we stop at newline or end of string
        pattern = r'(?:Location|Located|Based|Current Location)[\s:]*([A-Z][a-z\s]+?),\s*([A-Z]{2}|[A-Z][a-z\s]+?)(?=\n|$)'
        matches = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            city = matches.group(1).strip()
            state = matches.group(2).strip()
            return f"{city}, {state}"
        
        # Pattern 2: Fallback - Simple City, State pattern
        # Also uses (?=\n|$) to stop at line boundary
        pattern2 = r'([A-Z][a-zA-Z\s]+?)\s*,\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+?)(?=\n|$)'
        matches = re.search(pattern2, text)
        if matches:
            return f"{matches.group(1)}, {matches.group(2)}"
        
        return None
    
    
    def extract(self, raw_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """
        Main dispatcher for Stage 4
        """

        if source_type.lower() in ["csv", "json"]:
            return self.extract_from_dict(raw_data, source_type)

        elif source_type.lower() in ["text", "pdf"]:
            text = raw_data.get("full_text", "")
            return self.extract_from_text(text)

        else:
            logger.warning(f"Unknown source type: {source_type}")
            return {}