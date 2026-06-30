"""
Canonical Schema - Internal representation of a candidate profile
This is what each source gets converted to after normalization
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SkillInfo(BaseModel):
    """Single skill entry"""
    name: str
    confidence: float = Field(ge=0, le=1)
    sources: List[str] = []  # Which sources provided this skill


class LocationInfo(BaseModel):
    """Location with city and country"""
    city: Optional[str] = None
    country: Optional[str] = None


class CanonicalProfile(BaseModel):
    """
    Internal canonical representation of a candidate
    This is what Phase 1 produces for each source
    """
    # Basic info
    full_name: Optional[str] = None
    emails: List[str] = []
    phones: List[str] = []
    location: Optional[LocationInfo] = None
    
    # Professional info
    headline: Optional[str] = None
    company: Optional[str] = None
    years_experience: Optional[int] = None
    
    # Skills
    skills: List[SkillInfo] = []
    
    # Metadata
    overall_confidence: float = 0.5
    sources_used: List[str] = []  # Which sources contributed to this profile
    
    class Config:
        extra = 'allow'  # Allow additional fields
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "emails": ["john@example.com"],
                "phones": ["5551234567"],
                "headline": "Senior Engineer",
                "company": "Google",
                "years_experience": 8,
                "skills": [
                    {"name": "python", "confidence": 0.99, "sources": ["resume", "csv"]}
                ]
            }
        }


class OutputProfile(BaseModel):
    """
    Final output profile after configuration projection
    """
    full_name: Optional[str] = None
    emails: Optional[List[str]] = None
    phones: Optional[List[str]] = None
    location: Optional[LocationInfo] = None
    headline: Optional[str] = None
    company: Optional[str] = None
    years_experience: Optional[int] = None
    skills: Optional[List[SkillInfo]] = None
    overall_confidence: Optional[float] = None
    
    class Config:
        extra = 'allow'


# Decision log entry (for internal audit trail)
class DecisionLogEntry(BaseModel):
    """
    Single decision log entry for one field
    """
    field: str
    selected_value: Any
    confidence: float
    provenance: List[str]  # Which sources provided this value
    reason: str
    all_candidates: List[Dict[str, Any]] = []
    discarded_values: List[Any] = []
    timestamp: datetime = Field(default_factory=datetime.now)