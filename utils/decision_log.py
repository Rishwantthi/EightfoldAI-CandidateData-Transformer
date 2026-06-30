"""
Decision Log
Internal audit trail for all field decisions (DL3: Medium detail)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class DecisionRecord:
    """Single decision for one field"""
    field: str
    selected_value: Any
    confidence: float
    provenance: List[str]  # Which sources provided this value
    reason: str
    all_candidates: List[Dict[str, Any]]  # All candidates considered
    discarded_values: List[Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DecisionLog:
    """
    Maintains audit trail of all decisions (DL3)
    Medium detail: shows reasoning + candidates but not overly verbose
    """
    
    def __init__(self):
        self.entries: List[DecisionRecord] = []
    
    def record_decision(
        self,
        field: str,
        selected_value: Any,
        confidence: float,
        provenance: List[str],
        reason: str,
        all_candidates: List[Dict[str, Any]],
        discarded_values: List[Any] = None
    ):
        """
        Record a field decision
        
        Args:
            field: Field name
            selected_value: Value that was chosen
            confidence: Confidence score 0-1
            provenance: List of sources that provided this value
            reason: Explanation of why this value was chosen
            all_candidates: All candidate values considered
            discarded_values: Values that were considered but rejected
        """
        if discarded_values is None:
            discarded_values = []
        
        record = DecisionRecord(
            field=field,
            selected_value=selected_value,
            confidence=confidence,
            provenance=provenance,
            reason=reason,
            all_candidates=all_candidates,
            discarded_values=discarded_values
        )
        
        self.entries.append(record)
    
    def get_decision(self, field: str) -> Optional[DecisionRecord]:
        """Get decision for specific field"""
        for entry in self.entries:
            if entry.field == field:
                return entry
        return None
    
    def get_all_decisions(self) -> List[DecisionRecord]:
        """Get all decisions"""
        return self.entries
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert to list of dicts for JSON serialization"""
        return [entry.to_dict() for entry in self.entries]
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        import json
        return json.dumps(self.to_dict_list(), indent=indent, default=str)
    
    def print_summary(self):
        """Print human-readable summary"""
        print(f"\n{'='*60}")
        print(f"DECISION LOG SUMMARY ({len(self.entries)} decisions)")
        print(f"{'='*60}\n")
        
        for entry in self.entries:
            print(f"Field: {entry.field}")
            print(f"  Selected: {entry.selected_value}")
            print(f"  Confidence: {entry.confidence:.2f}")
            print(f"  Provenance: {', '.join(entry.provenance)}")
            print(f"  Reason: {entry.reason}")
            if entry.discarded_values:
                print(f"  Discarded: {entry.discarded_values}")
            print()
    
    def get_field_explanation(self, field: str) -> Optional[str]:
        """
        Get human-readable explanation for a field decision
        
        Example:
            "Company: Google was selected because 2 sources agree
             (Resume: 0.90, CSV: 0.80). Google LLC from Notes
             was discarded (lower source reliability)."
        """
        decision = self.get_decision(field)
        if not decision:
            return None
        
        return decision.reason


# Example usage
if __name__ == "__main__":
    log = DecisionLog()
    
    # Record a decision
    log.record_decision(
        field="company",
        selected_value="Google",
        confidence=0.88,
        provenance=["resume", "csv", "json"],
        reason="Source-weighted vote: Resume (0.90) + JSON (0.85) + CSV (0.80) = 2.55 vs Google LLC (Notes 0.60) = 0.60. Selected highest score.",
        all_candidates=[
            {
                "value": "Google",
                "sources": ["resume", "csv", "json"],
                "score": 2.55
            },
            {
                "value": "Google LLC",
                "sources": ["notes"],
                "score": 0.60
            }
        ],
        discarded_values=["Google LLC"]
    )
    
    log.print_summary()
    print("\nJSON output:")
    print(log.to_json())