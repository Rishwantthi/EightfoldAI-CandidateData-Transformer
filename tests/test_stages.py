import pytest

from stages.stage6_normalization import ValueNormalizer
from stages.stage7_identity import IdentityResolver
from stages.stage1_validation import InputValidator


# ==========================================================
# Test 1 : Stage 6 Normalization
# ==========================================================

def test_normalization():

    normalizer = ValueNormalizer()

    data = {
        "email": "JOHN@EXAMPLE.COM",
        "phone": "(555) 123-4567",
        "skills": ["Python", "JavaScript", "React"]
    }

    result = normalizer.normalize(data)

    assert result["email"]["normalized"] == "john@example.com"

    assert result["phone"]["normalized"] == "5551234567"

    assert "python" in result["skills"]["normalized"]


# ==========================================================
# Test 2 : Stage 7 Identity Resolution
# ==========================================================

def test_identity_resolution():

    resolver = IdentityResolver()

    profiles = [

        {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "5551234567"
        },

        {
            "full_name": "Jonathan Doe",
            "email": "john@example.com",
            "phone": "5551234567"
        }

    ]

    same_person, confidence, reason = resolver.resolve(profiles)

    assert same_person is True

    assert confidence >= 0.80


# ==========================================================
# Test 3 : Missing File Edge Case
# ==========================================================

def test_missing_file():

    validator = InputValidator()

    valid, errors = validator.validate({

        "csv": "sample_data/does_not_exist.csv"

    })

    assert valid is False

    assert len(errors) > 0