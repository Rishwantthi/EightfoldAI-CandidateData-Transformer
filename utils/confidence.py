"""
Confidence Calculation
Calculates confidence scores for merged data (C1 method)
"""

from typing import List, Dict, Any


class ConfidenceCalculator:
    """
    Calculate confidence scores using average of field confidences (C1)
    """
    
    # Source reliability weights (W2)
    SOURCE_WEIGHTS = {
        "resume": 0.90,        # Resume PDF - most authoritative
        "pdf": 0.90,
        "json": 0.85,          # ATS JSON - structured
        "ats": 0.85,
        "csv": 0.80,           # Recruiter CSV - may be older
        "notes": 0.60          # Text notes - least structured
    }
    
    @staticmethod
    def get_source_weight(source_name: str) -> float:
        """Get reliability weight for a source"""
        source_lower = source_name.lower()
        
        # Check exact match
        if source_lower in ConfidenceCalculator.SOURCE_WEIGHTS:
            return ConfidenceCalculator.SOURCE_WEIGHTS[source_lower]
        
        # Check if contains key
        for key, weight in ConfidenceCalculator.SOURCE_WEIGHTS.items():
            if key in source_lower:
                return weight
        
        # Default
        return 0.75
    
    @staticmethod
    def calculate_field_confidence(candidates: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence for a field with multiple candidate values
        
        Args:
            candidates: List of {value, source, confidence} dicts
        
        Returns:
            Confidence score 0-1
        """
        if not candidates:
            return 0.0
        
        # Group by unique value
        value_groups = {}
        for candidate in candidates:
            value = str(candidate.get('value', '')).lower().strip()
            if value not in value_groups:
                value_groups[value] = []
            value_groups[value].append(candidate)
        
        # Score each group
        best_score = 0.0
        best_group = None
        
        for value, group in value_groups.items():
            # Calculate score for this value
            score = ConfidenceCalculator._score_value_group(group)
            if score > best_score:
                best_score = score
                best_group = group
        
        return best_score
    
    @staticmethod
    def _score_value_group(candidates: List[Dict[str, Any]]) -> float:
        """
        Score a group of candidates that all have the same value
        
        Score = source reliability average + agreement bonus
        """
        # Get source weights
        source_scores = []
        for candidate in candidates:
            source = candidate.get('source', 'unknown')
            weight = ConfidenceCalculator.get_source_weight(source)
            source_scores.append(weight)
        
        # Base score: average source weight
        base_score = sum(source_scores) / len(source_scores)
        
        # Agreement bonus: more sources saying same thing = higher confidence
        agreement_bonus = min(0.1, len(candidates) * 0.02)
        
        total = min(0.99, base_score + agreement_bonus)
        return total
    
    @staticmethod
    def calculate_overall_confidence(field_confidences: Dict[str, float]) -> float:
        """
        Calculate overall candidate confidence (C1: average)
        
        Args:
            field_confidences: {field_name: confidence_score}
        
        Returns:
            Overall confidence 0-1
        """
        if not field_confidences:
            return 0.5
        
        # Remove null/missing fields
        scores = [c for c in field_confidences.values() if c is not None and c > 0]
        
        if not scores:
            return 0.5
        
        # Simple average
        overall = sum(scores) / len(scores)
        return min(0.99, overall)


# Example usage
if __name__ == "__main__":
    # Example: company field with 3 candidates
    candidates = [
        {"value": "Google", "source": "resume", "confidence": 0.95},
        {"value": "Google", "source": "csv", "confidence": 0.80},
        {"value": "Google LLC", "source": "notes", "confidence": 0.60}
    ]
    
    confidence = ConfidenceCalculator.calculate_field_confidence(candidates)
    print(f"Company field confidence: {confidence:.2f}")
    
    # Overall confidence
    field_scores = {
        "name": 0.99,
        "email": 0.95,
        "company": 0.88,
        "skills": 0.75
    }
    
    overall = ConfidenceCalculator.calculate_overall_confidence(field_scores)
    print(f"Overall confidence: {overall:.2f}")