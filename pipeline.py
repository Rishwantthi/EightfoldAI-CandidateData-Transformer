"""
Main Pipeline Orchestrator
Coordinates all 10 stages
"""

import json
import logging
import argparse
from typing import Dict, Any

from schemas.config_schema import PipelineConfig

# Stage imports
from stages.stage1_validation import InputValidator
from stages.stage2_detection import SourceDetector
from stages.stage3_parser import SourceParser
from stages.stage4_extraction import InformationExtractor
from stages.stage5_canonical import CanonicalMapper
from stages.stage6_normalization import ValueNormalizer
from stages.stage7_identity import IdentityResolver
from stages.stage8_decision import DecisionEngine
from stages.stage9_projection import ProjectionLayer
from stages.stage10_validation import SchemaValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class TransformerPipeline:
    """
    Main orchestrator for the 10-stage pipeline
    
    PHASE 1: Process each source independently
    - Stage 1: Input Validation
    - Stage 2: Source Detection
    - Stage 3: Source Parser
    - Stage 4: Information Extraction
    - Stage 5: Canonical Mapping
    - Stage 6: Normalization
    
    PHASE 2: Merge and decide across sources
    - Stage 7: Identity Resolution
    - Stage 8: Decision Engine
    - Stage 9: Projection Layer
    - Stage 10: Schema Validation
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.phase1_intermediates = {}
        self.decision_log = None

        # ---------- Phase 1 Stages ----------
        self.validator = InputValidator()
        self.detector = SourceDetector()
        self.parser = SourceParser()
        self.extractor = InformationExtractor()
        self.mapper = CanonicalMapper()
        self.normalizer = ValueNormalizer()

        # ---------- Phase 2 Stages ----------
        self.identity = IdentityResolver()
        self.decision = DecisionEngine()
        self.projector = ProjectionLayer(self.config)
        self.schema = SchemaValidator()
    
    def transform(self, inputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Main transformation pipeline
        
        Args:
            inputs: Dict mapping source type to file path
                   {"csv": "/path/to/recruiter.csv", 
                    "json": "/path/to/ats.json",
                    "pdf": "/path/to/resume.pdf",
                    "notes": "/path/to/recruiter_notes.txt"}
        
        Returns:
            Dict with final profile, metadata, and internal decision log
        """
        
        logger.info("=" * 60)
        logger.info("STARTING PIPELINE")
        logger.info("=" * 60)
        
        # PHASE 1: Process each source
        logger.info("\n[PHASE 1] Processing individual sources...")
        self._phase1_process_sources(inputs)
        
        if not self.phase1_intermediates:
            return {"error": "No valid sources processed"}
        
        # PHASE 2: Merge and decide
        logger.info("\n[PHASE 2] Merging across sources...")
        output = self._phase2_merge_and_decide()
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        
        return output
    
    def _phase1_process_sources(self, inputs: Dict[str, str]):
        """
        PHASE 1: Process each source independently through Stages 1-6
        """

        # =====================================================
        # Stage 1: Input Validation
        # =====================================================
        
        logger.info("\n[STAGE 1] INPUT VALIDATION")
        valid, errors = self.validator.validate(inputs)

        if not valid:
            logger.error(f"Validation Failed:\n{errors}")
            return

        # =====================================================
        # Process each valid source
        # =====================================================

        for source_name, file_path in inputs.items():

            logger.info(f"\n--- Processing source: {source_name} ---")

            try:
                # =====================================================
                # Stage 2: Source Detection
                # =====================================================
                
                source_type, reason = self.detector.detect(file_path)
                logger.info(f"[STAGE 2] Detected as: {source_type.value} ({reason})")

                # =====================================================
                # Stage 3: Source Parser
                # =====================================================
                
                raw_data = self.parser.parse(file_path, source_type.value)
                logger.info(f"[STAGE 3] Parsed successfully")

                # =====================================================
                # Stage 4: Information Extraction
                # =====================================================
                
                # NOTE: extract() requires both raw_data AND source_type.value
                extracted = self.extractor.extract(raw_data, source_type.value)
                logger.info(f"[STAGE 4] Extracted {len(extracted)} fields")

                # =====================================================
                # Stage 5: Canonical Mapping
                # =====================================================
                
                canonical = self.mapper.map(extracted)
                logger.info(f"[STAGE 5] Mapped to canonical schema")

                # =====================================================
                # Stage 6: Normalization
                # =====================================================
                
                normalized = self.normalizer.normalize(canonical)
                logger.info(f"[STAGE 6] Normalized successfully")

                # Store intermediate result
                self.phase1_intermediates[source_name] = normalized

            except Exception as e:
                logger.error(f"[PHASE 1] Error processing {source_name}: {e}")
                continue

        logger.info(f"\n✓ Phase 1 Complete ({len(self.phase1_intermediates)} sources processed)")

    
    def _phase2_merge_and_decide(self) -> Dict[str, Any]:
        """
        PHASE 2: Merge and decide across sources through Stages 7-10
        """

        # =====================================================
        # Collect normalized profiles from Phase 1
        # =====================================================
        
        profiles = list(self.phase1_intermediates.values())
        source_names = list(self.phase1_intermediates.keys())

        # =====================================================
        # Stage 7: Identity Resolution
        # =====================================================
        
        logger.info("\n[STAGE 7] IDENTITY RESOLUTION")
        same_person, confidence, identity_reason = self.identity.resolve(profiles)

        logger.info(f"Same person: {same_person} (confidence: {confidence:.2f})")
        logger.info(f"Reason: {identity_reason}")

        if not same_person:
            logger.error("Identity Resolution Failed: Sources appear to describe different candidates")
            return {"error": "Identity resolution failed"}

        # =====================================================
        # Stage 8: Decision Engine
        # =====================================================
        
        logger.info("\n[STAGE 8] DECISION ENGINE")
        merged_profile, decision_log = self.decision.decide(profiles, source_names)
        
        self.decision_log = decision_log
        logger.info(f"✓ Merged {len(merged_profile)} fields with reasoning")

        # =====================================================
        # Stage 9: Projection Layer
        # =====================================================
        
        logger.info("\n[STAGE 9] PROJECTION LAYER")
        # NOTE: project() requires both merged_profile AND decision_log
        projected_profile = self.projector.project(merged_profile, self.decision_log)
        logger.info(f"✓ Projected to {len(projected_profile)} output fields")

        # =====================================================
        # Stage 10: Schema Validation
        # =====================================================
        
        logger.info("\n[STAGE 10] SCHEMA VALIDATION")
        validated_profile = self.schema.validate(projected_profile)
        logger.info(f"✓ Schema validation passed")

        # =====================================================
        # Return final output
        # =====================================================
        
        return {
            "candidate_profile": validated_profile,
            "metadata": {
                "identity_confidence": confidence,
                "sources_used": source_names,
                "source_count": len(source_names),
                "identity_reasoning": identity_reason
            },
            "decision_log_internal": self.decision_log.to_dict_list() if self.decision_log else []
        }
    
    def get_decision_log(self):
        """Return internal decision log"""
        return self.decision_log


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Multi-Source Candidate Profile Transformation Pipeline"
    )

    parser.add_argument(
        "--csv",
        required=True,
        help="Path to recruiter CSV file"
    )

    parser.add_argument(
        "--json",
        required=True,
        help="Path to ATS JSON file"
    )

    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to resume PDF file"
    )

    parser.add_argument(
        "--notes",
        required=True,
        help="Path to recruiter notes text file"
    )

    parser.add_argument(
        "--config",
        default="configs/custom_config.json",
        help="Path to pipeline configuration JSON"
    )

    args = parser.parse_args()

    # ========== INPUTS ==========
    inputs = {
        "csv": args.csv,
        "json": args.json,
        "pdf": args.pdf,
        "notes": args.notes
    }

    # ========== CONFIG ==========
    # NOTE: Use INTERNAL field names (email, phone)
    # Stage 10 will rename them to emails, phones
    import json

    with open(args.config, "r") as f:
        config_data = json.load(f)

    config = PipelineConfig(**config_data)
    # ========== RUN PIPELINE ==========
    print(config)
    pipeline = TransformerPipeline(config)
    result = pipeline.transform(inputs)
    
    if "error" in result:
        logger.error(result["error"])
        exit(1)

    # ========== SAVE OUTPUT ==========
    import os
    os.makedirs("output", exist_ok=True)
    
    with open("output/sample_run.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info("\n✓ Output saved to output/sample_run.json")
    
    # ========== DISPLAY SUMMARY ==========
    print("\n" + "=" * 60)
    print("FINAL OUTPUT SUMMARY")
    print("=" * 60)
    if "candidate_profile" in result:
        print(f"Candidate Profile Fields: {list(result['candidate_profile'].keys())}")
        print(f"Sources Processed: {result['metadata']['sources_used']}")
        print(f"Identity Confidence: {result['metadata']['identity_confidence']:.2f}")
    else:
        print(f"Error: {result.get('error')}")