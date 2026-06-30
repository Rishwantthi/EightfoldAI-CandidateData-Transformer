"""
STAGE 5: CANONICAL MAPPING
Standardize field names to canonical form
Maps source field names to canonical field names
"""

import logging
from typing import Dict, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class CanonicalMapper:
    """
    Stage 5: Map source fields to canonical names
    
    Strategy: Exact match first, then fuzzy match, then keep as-is
    
    Returns: {canonical_field: value}
    """
    
    # Mapping table: canonical_name → list of source field variations
    CANONICAL_MAPPINGS = {
        'full_name': [
            'name', 'full_name', 'displayname', 'candidate_name',
            'person_name', 'candidate', 'applicant', 'employee_name',
            'first_name', 'last_name'
        ],
        'email': [
            'email', 'email_address', 'primary_email', 'work_email',
            'contact_email', 'mail', 'e_mail', 'emails'
        ],
        'phone': [
            'phone', 'phone_number', 'contact_phone', 'mobile',
            'cellular', 'telephone', 'phones'
        ],
        'location': [
            'location', 'city', 'address', 'current_location',
            'based_in', 'hometown', 'country'
        ],
        'company': [
            'company', 'current_company', 'employer', 'organization',
            'current_employer', 'works_at', 'employer'
        ],
        'headline': [
            'headline', 'title', 'job_title', 'current_title',
            'position', 'role', 'job_title', 'job_position'
        ],
        'skills': [
            'skills', 'expertise', 'competencies', 'abilities',
            'technical_skills', 'tech_skills'
        ],
        'years_experience': [
            'years_of_experience', 'years_exp', 'experience_years',
            'years_experience', 'total_experience', 'years'
        ]
    }
    
    def __init__(self):
        self.mapping_log = {}
    
    def map(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map extracted fields to canonical names
        
        Args:
            extracted_data: {source_field: value} from Stage 4
        
        Returns:
            {canonical_field: value}
        """
        logger.info(f"\n[STAGE 5] CANONICAL MAPPING")
        logger.info(f"  Input fields: {len(extracted_data)}")
        
        canonical = {}
        self.mapping_log = {}
        
        for source_field, value in extracted_data.items():
            if value is None or value == '':
                continue
            
            # Try to match to canonical
            canonical_field, confidence = self._match_field(source_field)
            
            # Store mapping
            self.mapping_log[source_field] = {
                'canonical': canonical_field,
                'confidence': confidence,
                'value': value
            }
            
            # Add to canonical (avoid duplicates - first match wins)
            if canonical_field not in canonical:
                canonical[canonical_field] = value
                logger.info(f"    ✓ {source_field:25} → {canonical_field:20} ({confidence:.0%})")
            else:
                logger.info(f"    ~ {source_field:25} → {canonical_field:20} (skipped, already have)")
        
        logger.info(f"  Output fields: {len(canonical)}")
        return canonical
    
    def _match_field(self, source_field: str) -> Tuple[str, float]:
        """
        Match a source field to canonical field
        
        Returns: (canonical_name, confidence)
        
        Strategy:
        1. Exact match (100% confidence)
        2. Fuzzy match (>80% confidence)
        3. Keep as-is (50% confidence)
        """
        source_lower = source_field.lower().strip()
        
        # Strategy 1: Exact match
        for canonical, variants in self.CANONICAL_MAPPINGS.items():
            if source_lower in variants:
                return canonical, 1.0  # 100% confidence
        
        # Strategy 2: Fuzzy match (similarity >= 0.80)
        best_match = None
        best_score = 0.0
        
        for canonical, variants in self.CANONICAL_MAPPINGS.items():
            for variant in variants:
                similarity = SequenceMatcher(None, source_lower, variant).ratio()
                
                if similarity >= 0.80 and similarity > best_score:
                    best_score = similarity
                    best_match = canonical
        
        if best_match:
            return best_match, best_score  # Fuzzy match confidence
        
        # Strategy 3: No match - keep as-is
        return source_lower, 0.5  # 50% confidence
    
    def get_mapping_log(self) -> Dict:
        """Return mapping log for audit trail"""
        return self.mapping_log


