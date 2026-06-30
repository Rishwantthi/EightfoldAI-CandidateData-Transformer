"""
STAGE 10 : SCHEMA VALIDATION (Sc1)

Validate the projected profile against the canonical output schema.

Responsibilities
----------------
1. Convert internal field names to schema fields
2. Convert simple skill strings to SkillInfo objects
3. Validate using Pydantic
4. Return validated dictionary
"""

import logging
from typing import Dict, Any

from pydantic import ValidationError

from schemas.canonical_schema import (
    OutputProfile,
    SkillInfo,
    LocationInfo
)

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Stage 10

    Validate final projected output.
    """

    def validate(
        self,
        projected_profile: Dict[str, Any]
    ) -> Dict[str, Any]:

        logger.info("\n[STAGE 10] SCHEMA VALIDATION")

        profile = dict(projected_profile)

        # ---------------------------------------------
        # Rename internal fields
        # ---------------------------------------------

        if "email" in profile:
            profile["emails"] = profile.pop("email")

        if "phone" in profile:
            profile["phones"] = profile.pop("phone")

        # ---------------------------------------------
        # Skills
        # Convert ["python","java"]
        # ->
        # [
        #   SkillInfo(...)
        # ]
        # ---------------------------------------------

        if "skills" in profile:

            skill_objects = []

            for skill in profile["skills"]:

                if isinstance(skill, SkillInfo):
                    skill_objects.append(skill)

                else:

                    skill_objects.append(

                        SkillInfo(
                            name=str(skill),
                            confidence=1.0,
                            sources=[]
                        )

                    )

            profile["skills"] = skill_objects

        # ---------------------------------------------
        # Location
        # ---------------------------------------------

        if "location" in profile:

            # Already a dictionary
            if isinstance(profile["location"], dict):

                profile["location"] = LocationInfo(
                    **profile["location"]
                )

            # String like "San Francisco, CA"
            elif isinstance(profile["location"], str):

                parts = [p.strip() for p in profile["location"].split(",")]

                profile["location"] = LocationInfo(
                    city=parts[0] if len(parts) > 0 else None,
                    country=parts[1] if len(parts) > 1 else None
                )
        # ---------------------------------------------
        # Validate
        # ---------------------------------------------

        try:

            validated = OutputProfile(**profile)

            logger.info(
                "✓ Output schema validated successfully"
            )

            return validated.model_dump(exclude_none=True)

        except ValidationError as e:

            logger.error(
                "Schema validation failed."
            )

            logger.error(str(e))

            raise
       
