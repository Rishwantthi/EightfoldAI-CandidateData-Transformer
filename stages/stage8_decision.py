"""
STAGE 8: DECISION ENGINE (De3)

Purpose:
Resolve conflicts between multiple normalized candidate profiles.

Strategies:
- Single-value fields -> Source Weighted Voting
- Email -> Union + Deduplication
- Phone -> Union + Deduplication
- Skills -> Union + Deduplication

Produces:
- Final Canonical Profile
- Field Confidence
- Decision Log
- Provenance
"""

import logging
from typing import List, Dict, Any, Tuple

from utils.confidence import ConfidenceCalculator
from utils.decision_log import DecisionLog

logger = logging.getLogger(__name__)


class DecisionEngine:

    SOURCE_WEIGHTS = {
        "resume": 0.90,
        "pdf": 0.90,
        "json": 0.85,
        "ats": 0.85,
        "csv": 0.80,
        "notes": 0.60
    }

    def __init__(self):
        self.confidence = ConfidenceCalculator()
        self.decision_log = DecisionLog()

    def decide(
        self,
        profiles: List[Dict[str, Any]],
        source_names: List[str]
    ) -> Tuple[Dict[str, Any], DecisionLog]:

        logger.info("\n[STAGE 8] DECISION ENGINE")

        merged_profile = {}
        field_confidences = {}

        all_fields = set()

        # Collect every available field
        for profile in profiles:
            all_fields.update(profile.keys())

        # Resolve one field at a time
        for field in sorted(all_fields):

            candidates = self._collect_candidates(
                field,
                profiles,
                source_names
            )

            if not candidates:
                continue

            result = self._resolve_field(
                field,
                candidates
            )

            merged_profile[field] = result["value"]
            field_confidences[field] = result["confidence"]

            self.decision_log.record_decision(
                field=field,
                selected_value=result["value"],
                confidence=result["confidence"],
                provenance=result["provenance"],
                reason=result["reason"],
                all_candidates=result["all_candidates"],
                discarded_values=result["discarded_values"]
            )

            logger.info(
                f"✓ {field:20} -> {str(result['value'])[:40]}"
            )

        merged_profile["overall_confidence"] = (
            self.confidence.calculate_overall_confidence(
                field_confidences
            )
        )

        return merged_profile, self.decision_log
        ###########################################################
    # COLLECT CANDIDATES
    ###########################################################

    def _collect_candidates(
        self,
        field: str,
        profiles: List[Dict[str, Any]],
        source_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Collect all candidate values for a field from every source.
        """

        candidates = []

        for i, profile in enumerate(profiles):

            if field not in profile:
                continue

            value_data = profile[field]

            # Stage 6 output
            if isinstance(value_data, dict):

                value = value_data.get("normalized", value_data)

                confidence = value_data.get(
                    "confidence",
                    0.80
                )

            else:

                value = value_data
                confidence = 0.80

            if value is None:
                continue

            source = source_names[i]

            candidates.append({

                "value": value,

                "confidence": confidence,

                "source": source,

                "weight": self.SOURCE_WEIGHTS.get(
                    source.lower(),
                    0.75
                )

            })

        return candidates

    ###########################################################
    # FIELD ROUTER
    ###########################################################

    def _resolve_field(
        self,
        field: str,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Route each field to its merge strategy.
        """

        field = field.lower()

        # ---------- Skills ----------
        if field in ["skills", "skill"]:

            return self._merge_skills(candidates)

        # ---------- Emails ----------
        elif field in ["email", "emails"]:

            return self._merge_emails(candidates)

        # ---------- Phones ----------
        elif field in ["phone", "phones"]:

            return self._merge_phones(candidates)

        # ---------- Everything else ----------
        else:

            return self._weighted_vote(
                field,
                candidates
            )
    ###########################################################
    # WEIGHTED VOTING
    ###########################################################

    def _weighted_vote(
        self,
        field: str,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts for single-value fields using
        source-weighted voting.
        """

        # Group candidates by value
        value_groups = {}

        for candidate in candidates:

            key = str(candidate["value"]).strip().lower()

            if key not in value_groups:
                value_groups[key] = []

            value_groups[key].append(candidate)

        scored_candidates = []

        # Score each unique value
        for group in value_groups.values():

            weighted_score = sum(
                c["weight"] for c in group
            )

            avg_confidence = (
                sum(c["confidence"] for c in group)
                / len(group)
            )

            scored_candidates.append({

                "value": group[0]["value"],

                "score": weighted_score,

                "confidence": avg_confidence,

                "sources": [
                    c["source"]
                    for c in group
                ]

            })

        # Highest score wins
        scored_candidates.sort(
            key=lambda x: (
                x["score"],
                x["confidence"]
            ),
            reverse=True
        )

        winner = scored_candidates[0]

        reason = (
            f"Selected '{winner['value']}' using "
            f"source-weighted voting "
            f"(score={winner['score']:.2f})."
        )

        discarded = [
            item["value"]
            for item in scored_candidates[1:]
        ]

        return {

            "value": winner["value"],

            "confidence": winner["confidence"],

            "provenance": winner["sources"],

            "reason": reason,

            "all_candidates": scored_candidates,

            "discarded_values": discarded

        }        
        ###########################################################
    # EMAIL MERGE
    ###########################################################

    def _merge_emails(
        self,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge all unique emails.
        """

        merged = []
        provenance = []

        for candidate in candidates:

            value = candidate["value"]

            values = value if isinstance(value, list) else [value]

            for email in values:

                email = str(email).strip().lower()

                if email and email not in merged:
                    merged.append(email)
                    provenance.append(candidate["source"])

        confidence = (
            sum(c["confidence"] for c in candidates)
            / len(candidates)
        )

        return {

            "value": merged,

            "confidence": confidence,

            "provenance": list(set(provenance)),

            "reason":
                "Merged all unique email addresses using union + deduplication.",

            "all_candidates": [
                c["value"] for c in candidates
            ],

            "discarded_values": []

        }

    ###########################################################
    # PHONE MERGE
    ###########################################################

    def _merge_phones(
        self,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge all unique phone numbers.
        """

        merged = []
        provenance = []

        for candidate in candidates:

            value = candidate["value"]

            values = value if isinstance(value, list) else [value]

            for phone in values:

                phone = str(phone).strip()

                if phone and phone not in merged:
                    merged.append(phone)
                    provenance.append(candidate["source"])

        confidence = (
            sum(c["confidence"] for c in candidates)
            / len(candidates)
        )

        return {

            "value": merged,

            "confidence": confidence,

            "provenance": list(set(provenance)),

            "reason":
                "Merged all unique phone numbers using union + deduplication.",

            "all_candidates": [
                c["value"] for c in candidates
            ],

            "discarded_values": []

        }

    ###########################################################
    # SKILL MERGE
    ###########################################################

    def _merge_skills(
        self,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge all unique normalized skills.
        """

        merged = []
        provenance = []

        for candidate in candidates:

            value = candidate["value"]

            values = value if isinstance(value, list) else [value]

            for skill in values:

                skill = str(skill).strip().lower()

                if skill and skill not in merged:
                    merged.append(skill)
                    provenance.append(candidate["source"])

        merged.sort()

        confidence = (
            sum(c["confidence"] for c in candidates)
            / len(candidates)
        )

        return {

            "value": merged,

            "confidence": confidence,

            "provenance": list(set(provenance)),

            "reason":
                "Merged all unique normalized skills using union + deduplication.",

            "all_candidates": [
                c["value"] for c in candidates
            ],

            "discarded_values": []

        }    
        
