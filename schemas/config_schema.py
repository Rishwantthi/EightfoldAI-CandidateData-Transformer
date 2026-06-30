"""
Runtime Configuration Schema
Defines what config the pipeline accepts (CF1)
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class PipelineConfig(BaseModel):
    """
    Runtime configuration for output projection
    
    Example:
    {
        "fields": ["full_name", "emails", "company", "skills"],
        "include_confidence": true,
        "include_provenance": false,
        "on_missing": "omit"
    }
    """
    
    fields: List[str] = Field(
        default=["full_name", "emails", "phones", "company", "skills"],
        description="Which fields to include in output"
    )
    
    include_confidence: bool = Field(
        default=True,
        description="Add confidence scores for each field"
    )
    
    include_provenance: bool = Field(
        default=False,
        description="Add provenance (which sources) for each field"
    )
    
    on_missing: Literal["omit", "null", "error"] = Field(
        default="omit",
        description="How to handle missing values: omit (skip field), null (include with null), error (fail)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "fields": ["full_name", "emails", "company", "skills"],
                "include_confidence": True,
                "include_provenance": False,
                "on_missing": "omit"
            }
        }