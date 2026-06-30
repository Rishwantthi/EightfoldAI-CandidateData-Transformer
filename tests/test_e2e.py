import pytest

from pipeline import TransformerPipeline
from schemas.config_schema import PipelineConfig


def test_pipeline_runs():
    """
    End-to-End Test

    Checks:
    1. Pipeline executes without crashing
    2. Returns candidate profile
    3. Returns metadata
    4. Returns decision log
    """

    inputs = {
        "csv": "sample_data/recruiter.csv",
        "json": "sample_data/ats.json",
        "pdf": "sample_data/resume.pdf",
        "notes": "sample_data/recruiter_notes.txt"
    }

    config = PipelineConfig()

    pipeline = TransformerPipeline(config)

    result = pipeline.transform(inputs)

    # -------------------------
    # Assertions
    # -------------------------

    assert result is not None

    assert "candidate_profile" in result

    assert "metadata" in result

    assert "decision_log_internal" in result

    candidate = result["candidate_profile"]

    assert candidate["full_name"] is not None

    assert len(candidate["skills"]) > 0

    assert result["metadata"]["source_count"] == 4