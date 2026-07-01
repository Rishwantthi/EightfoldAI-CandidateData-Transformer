"""
STAGE 9: PROJECTION LAYER (P2)

Purpose:
Project the internal canonical profile into the final
output format based on the runtime configuration.

Responsibilities:
- Select requested fields
- Handle missing fields
- Include/Exclude confidence
- Include/Exclude provenance
"""

import logging
from typing import Dict, Any

from schemas.config_schema import PipelineConfig

logger = logging.getLogger(__name__)


class ProjectionLayer:
    """
    Stage 9: Projection Layer

    Applies the runtime configuration (CF1)
    to reshape the merged profile.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config

    def project(
        self,
        merged_profile: Dict[str, Any],
        decision_log=None
    ) -> Dict[str, Any]:

        logger.info("\n[STAGE 9] PROJECTION LAYER")

        projected = {}

        # ----------------------------------------------------
        # STEP 1 : Keep only requested fields
        # ----------------------------------------------------

        projected = self._filter_fields(
            merged_profile
        )

        # ----------------------------------------------------
        # STEP 2 : Handle missing fields
        # ----------------------------------------------------

        projected = self._handle_missing(
            projected
        )
        
        # ----------------------------------------------------
        # STEP 2.5 : Project nested skill objects
        # ----------------------------------------------------

        if "skills" in projected:

            cleaned_skills = []

            for skill in projected["skills"]:

                # If skill is already a string, keep it
                if not isinstance(skill, dict):
                    cleaned_skills.append(skill)
                    continue

                item = {
                    "name": skill.get("name")
                }

                if self.config.include_confidence:
                    item["confidence"] = skill.get("confidence")

                if self.config.include_provenance:
                    item["sources"] = skill.get("sources", [])

                cleaned_skills.append(item)

            projected["skills"] = cleaned_skills

        # ----------------------------------------------------
        # STEP 3 : Confidence
        # ----------------------------------------------------

        if not self.config.include_confidence:

            projected.pop(
                "overall_confidence",
                None
            )

        # ----------------------------------------------------
        # STEP 4 : Provenance
        # ----------------------------------------------------

        if self.config.include_provenance and decision_log:

            projected["provenance"] = (
                decision_log.to_dict_list()
            )

        logger.info(
            f"Projected {len(projected)} fields."
        )

        return projected
        ###########################################################
    # FILTER REQUESTED FIELDS
    ###########################################################

    def _filter_fields(
        self,
        merged_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Keep only the fields requested in PipelineConfig.
        """

        result = {}

        # If no fields specified, return everything
        if not self.config.fields:
            return dict(merged_profile)

        for field in self.config.fields:

            if field in merged_profile:
                result[field] = merged_profile[field]

        # Preserve confidence separately if present
        if (
            "overall_confidence" in merged_profile
            and self.config.include_confidence
        ):
            result["overall_confidence"] = (
                merged_profile["overall_confidence"]
            )

        return result

    ###########################################################
    # HANDLE MISSING FIELDS
    ###########################################################

    def _handle_missing(
        self,
        projected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply missing field policy.

        Policies:
        omit -> remove missing fields
        null -> include missing fields with None
        """

        if not self.config.fields:
            return projected

        if self.config.on_missing == "omit":
            return projected

        if self.config.on_missing == "null":

            for field in self.config.fields:

                if field not in projected:
                    projected[field] = None

        return projected
    
