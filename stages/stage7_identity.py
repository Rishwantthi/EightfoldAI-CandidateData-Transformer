"""
STAGE 7: IDENTITY RESOLUTION (1-B: Multi-Signal Matching)
Confirm all sources describe the same person
Uses multiple signals: email, name, phone
"""

import logging
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class IdentityResolver:
    """
    Stage 7: Identity Resolution
    
    Strategy: 1-B (Multi-signal matching)
    - Email match (high priority - 0.95 confidence if match)
    - Name similarity (medium - fuzzy string match)
    - Phone match (high priority - 0.95 confidence if match)
    
    If 2+ signals match → Same person
    
    Returns: (is_same_person, confidence, reasoning)
    """
    
    def resolve(self, sources: List[Dict[str, Any]]) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Check if all sources describe the same person
        
        Args:
            sources: List of intermediate profiles from Stage 6
        
        Returns:
            (is_same_person, confidence, reasoning)
        """
        logger.info(f"\n[STAGE 7] IDENTITY RESOLUTION (1-B)")
        logger.info(f"  Checking {len(sources)} sources...")
        
        if len(sources) <= 1:
            logger.info(f"  → Only 1 source, assuming same person")
            return True, 1.0, {'reason': 'Single source only'}
        
        signals = []
        reasoning = {}
        
        # Signal 1: Email matching
        email_match = self._check_email_match(sources)
        if email_match['confidence'] > 0:
            signals.append(email_match['confidence'])
            reasoning['email'] = email_match
            logger.info(f"  ✓ Email signal: {email_match['reason']} ({email_match['confidence']:.0%})")
        
        # Signal 2: Name similarity
        name_match = self._check_name_similarity(sources)
        if name_match['confidence'] > 0:
            signals.append(name_match['confidence'])
            reasoning['name'] = name_match
            logger.info(f"  ✓ Name signal: {name_match['reason']} ({name_match['confidence']:.0%})")
        
        # Signal 3: Phone matching
        phone_match = self._check_phone_match(sources)
        if phone_match['confidence'] > 0:
            signals.append(phone_match['confidence'])
            reasoning['phone'] = phone_match
            logger.info(f"  ✓ Phone signal: {phone_match['reason']} ({phone_match['confidence']:.0%})")
        
        # Decision logic
        if not signals:
            logger.warning(f"  ⚠️  No signals available to match")
            return False, 0.5, {'reason': 'Insufficient data for matching'}
        
        # Calculate overall confidence
        overall_confidence = sum(signals) / len(signals)
        
        # Decision: Need 2+ matching signals
        matching_signals = len(signals)
        is_same_person = matching_signals >= 2 or overall_confidence >= 0.70
        
        reasoning['overall'] = {
            'is_same_person': is_same_person,
            'matching_signals': matching_signals,
            'confidence': overall_confidence,
            'decision_reason': f"Matched on {matching_signals} signal(s). Overall confidence: {overall_confidence:.0%}"
        }
        
        logger.info(f"  → Same person: {is_same_person}, Confidence: {overall_confidence:.0%}")
        
        return is_same_person, overall_confidence, reasoning
    
    def _check_email_match(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if emails match across sources.

        Handles Stage 6 normalized output:
        {
            "normalized": "...",
            "confidence": ...
        }
        """

        emails = []

        for source in sources:

            email = source.get("email")

            if not email:
                continue

            # Stage 6 normalized dictionary
            if isinstance(email, dict):

                normalized = email.get("normalized")

                if normalized:
                    emails.append(str(normalized).lower().strip())

            # List of emails
            elif isinstance(email, list):

                for e in email:

                    if isinstance(e, dict):
                        normalized = e.get("normalized")

                        if normalized:
                            emails.append(str(normalized).lower().strip())

                    else:
                        emails.append(str(e).lower().strip())

            # Plain string
            else:
                emails.append(str(email).lower().strip())

        if not emails:
            return {
                "confidence": 0,
                "reason": "No emails found"
            }

        unique_emails = set(emails)

        if len(unique_emails) == 1:
            return {
                "confidence": 0.99,
                "reason": "Exact email match across sources",
                "matched_email": list(unique_emails)[0]
            }

        if len(unique_emails) == len(emails):
            return {
                "confidence": 0,
                "reason": f"All emails different: {unique_emails}"
            }

        return {
            "confidence": 0.85,
            "reason": f"Partial email match ({len(emails)-len(unique_emails)}/{len(emails)} agree)"
        }
    def _check_name_similarity(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if names are similar
        
        Strategy: Fuzzy string matching between names
        """
        names = [str(s.get('full_name', '')).lower().strip() 
                 for s in sources if s.get('full_name')]
        
        if not names or len(names) < 2:
            return {'confidence': 0, 'reason': 'Insufficient names to compare'}
        
        # Compare all pairs
        similarities = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                ratio = SequenceMatcher(None, names[i], names[j]).ratio()
                similarities.append(ratio)
        
        if not similarities:
            return {'confidence': 0, 'reason': 'No name pairs to compare'}
        
        avg_similarity = sum(similarities) / len(similarities)
        
        if avg_similarity > 0.90:
            return {
                'confidence': 0.95,
                'reason': f'High name similarity ({avg_similarity:.0%})',
                'similarity_score': avg_similarity
            }
        elif avg_similarity > 0.75:
            return {
                'confidence': 0.80,
                'reason': f'Medium name similarity ({avg_similarity:.0%})',
                'similarity_score': avg_similarity
            }
        else:
            return {
                'confidence': 0.4,
                'reason': f'Low name similarity ({avg_similarity:.0%})',
                'similarity_score': avg_similarity
            }
    
    def _check_phone_match(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if phones match across sources.

        Stage 6 stores phones as:
        {
            "normalized": "...",
            "confidence": ...
        }

        We compare only the normalized value.
        """

        phones = []

        for source in sources:

            phone = source.get("phone")

            if not phone:
                continue

            # Stage 6 output
            if isinstance(phone, dict):
                normalized = phone.get("normalized")
                if normalized:
                    phones.append(str(normalized).strip())

            # List of phones
            elif isinstance(phone, list):

                for p in phone:

                    if isinstance(p, dict):
                        normalized = p.get("normalized")
                        if normalized:
                            phones.append(str(normalized).strip())

                    else:
                        phones.append(str(p).strip())

            # Plain string
            else:
                phones.append(str(phone).strip())

        if not phones:
            return {
                "confidence": 0,
                "reason": "No phones found"
            }

        unique_phones = set(phones)

        if len(unique_phones) == 1:
            return {
                "confidence": 0.95,
                "reason": "Exact phone match across sources",
                "matched_phone": list(unique_phones)[0]
            }

        if len(unique_phones) == len(phones):
            return {
                "confidence": 0,
                "reason": "All phones different"
            }

        return {
            "confidence": 0.85,
            "reason": f"Partial phone match ({len(phones)-len(unique_phones)}/{len(phones)} agree)"
        }


