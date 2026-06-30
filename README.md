# Eightfold AI - Multi-Source Candidate Profile Transformer

## Overview

This project implements a modular **10-stage data transformation pipeline** that consolidates candidate information from multiple heterogeneous sources into a single canonical candidate profile.

The pipeline validates, parses, extracts, normalizes, resolves identity and data conflicts across sources, and produces a configurable final profile while maintaining confidence scores, provenance, and decision traceability.

---

## Features

- Multi-source candidate profile consolidation
- Modular 10-stage data transformation pipeline
- Automatic source detection
- Structured information extraction
- Canonical field mapping
- Data normalization
- Multi-signal identity resolution
- Conflict resolution with explainable decision logs
- Configurable output projection
- Schema validation using Pydantic
- Command-line interface (CLI)
- Unit and end-to-end tests

---

## Architecture

```text
                    INPUT SOURCES
                           │
     ┌────────────┬──────────────┬────────────┬─────────────┐
     │            │              │            │
   CSV          JSON           PDF        Recruiter Notes
     │            │              │            │
     └────────────┴──────────────┴────────────┘
                      │
              Stage 1 - Input Validation
                      │
              Stage 2 - Source Detection
                      │
              Stage 3 - Source Parsing
                      │
           Stage 4 - Information Extraction
                      │
            Stage 5 - Canonical Mapping
                      │
             Stage 6 - Normalization
                      │
────────────────────────────────────────────────────
             Phase 2 (Across Sources)
────────────────────────────────────────────────────
                      │
         Stage 7 - Identity Resolution
                      │
          Stage 8 - Decision Engine
                      │
         Stage 9 - Projection Layer
                      │
        Stage 10 - Schema Validation
                      │
              Final Candidate Profile
```

---

# Pipeline Stages

## Stage 1 – Input Validation

- Validates file existence
- Checks supported file types
- Performs basic integrity checks

---

## Stage 2 – Source Detection

Detects the input source type using:

- Content sniffing
- CSV Sniffer
- JSON validation
- PDF extension detection
- Text heuristics

**Supported input formats:**

- CSV
- JSON
- PDF
- Plain Text

---

## Stage 3 – Source Parsing

Parses each source into a common intermediate representation.

**Supported parsers:**

- CSV Parser
- JSON Parser
- PDF Parser
- Text Parser

---

## Stage 4 – Information Extraction

Extracts structured candidate information using:

- Regular expression extraction
- Field alias detection
- Fuzzy field matching
- Schema variant mapping

**Example mappings:**

```text
primary_email     → email
contact_phone     → phone
employer          → company
job_title         → headline
technical_skills  → skills
```

---

## Stage 5 – Canonical Mapping

Maps extracted fields into a standardized internal canonical schema used throughout the pipeline.

**Example:**

```text
current_company
employer
organization

        ↓

company
```

---

## Stage 6 – Normalization

Normalizes candidate data into consistent formats to simplify comparison, matching, and conflict resolution.

**Examples:**

- Emails → lowercase
- Phones → digits only
- Skills → canonical names
- Dates → standard format
- Locations → structured format

---

## Stage 7 – Identity Resolution

Determines whether multiple input sources refer to the same candidate using multi-signal matching.

**Signals used:**

- Email match
- Phone match
- Name similarity

**Produces:**

- Identity confidence
- Matching explanation

---

## Stage 8 – Decision Engine

Resolves conflicting values using:

- Source-weighted voting
- Union and deduplication for multi-valued fields
- Confidence aggregation
- Decision logging for explainability

**Produces:**

- Final canonical profile
- Decision log
- Provenance

---

## Stage 9 – Projection Layer

Projects the internal canonical profile into the requested output schema based on runtime configuration.

Supports runtime configuration for:

- Selected fields
- Confidence inclusion
- Provenance inclusion
- Missing value policy

---

## Stage 10 – Schema Validation

Validates the final candidate profile against the defined schema using Pydantic before producing the final output.

**Ensures:**

- Correct field types
- Schema compliance
- Consistent output

---

# Project Structure

```text
.
├── pipeline.py
├── requirements.txt
│
├── schemas/
│   ├── canonical_schema.py
│   └── config_schema.py
│
├── stages/
│   ├── stage1_validation.py
│   ├── stage2_detection.py
│   ├── stage3_parser.py
│   ├── stage4_extraction.py
│   ├── stage5_canonical.py
│   ├── stage6_normalization.py
│   ├── stage7_identity.py
│   ├── stage8_decision.py
│   ├── stage9_projection.py
│   └── stage10_validation.py
│
├── utils/
│   ├── confidence.py
│   ├── decision_log.py
│   └── normalizers.py
│
├── configs/
├── sample_data/
├── output/
└── tests/
```

---

# Technologies Used

- Python 3.12
- Pydantic
- pdfplumber
- fuzzywuzzy
- python-Levenshtein
- python-dateutil
- pytest

---

# Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

# Command Line Interface (CLI)

The pipeline exposes a command-line interface for specifying multiple input sources and runtime configuration.

**Example:**

```bash
python pipeline.py --csv sample_data/recruiter.csv --json sample_data/ats.json --pdf sample_data/resume.pdf --notes sample_data/recruiter_notes.txt
```

---

# Configuration

The pipeline behavior is controlled through JSON configuration files.

- `configs/default_config.json` – Returns the complete candidate profile.
- `configs/custom_config.json` – Demonstrates selective field projection.

**Example:**

```bash
python pipeline.py --csv sample_data/recruiter.csv --json sample_data/ats.json --pdf sample_data/resume.pdf --notes sample_data/recruiter_notes.txt --config configs/custom_config.json
```

---

# Output

The pipeline generates:

```text
output/sample_run.json
```

Depending on the runtime configuration, the generated output may include:

- Canonical Candidate Profile
- Metadata
- Identity Confidence
- Decision Log (Explainability)
- Identity Resolution Reasoning
- Provenance (optional)
- Field Confidence Scores (optional)

---

# Running Tests

Execute the test suite using:

```bash
pytest -v
```

The repository includes:

- Unit tests
- End-to-end pipeline tests
- Basic edge case validation

---

# Sample Input Sources

The pipeline supports combining multiple heterogeneous sources simultaneously.

Example:

- Recruiter CSV
- ATS JSON
- Resume PDF
- Recruiter Notes

---

# Pipeline Characteristics

- Deterministic stage execution
- Explainable conflict resolution
- Schema-driven processing
- Runtime configurable output
- Modular and independently testable stages

---

# Design Decisions

This implementation emphasizes:

- Modular stage-based architecture
- Explainable decision logging
- Confidence scoring
- Provenance tracking
- Configurable output projection
- Schema-driven validation
- Multi-source conflict resolution
- Extensibility through independent pipeline stages

---

# Assumptions

- All input sources describe the same candidate unless identity resolution determines otherwise.
- Source confidence is derived during conflict resolution.
- Unknown or unsupported fields are ignored unless explicitly mapped through configured canonical field variants.
- Missing values are handled according to runtime configuration.
- PDFs are assumed to contain extractable text (non-scanned documents).

---

# Future Improvements

- OCR support for scanned PDFs
- LLM-assisted information extraction
- Advanced semantic skill normalization
- Knowledge graph-based identity resolution
- User-configurable source weighting
- REST API deployment
- Streaming and batch pipeline support

---

# Author

**Rishwantthi R**

B.E. Computer Science and Engineering

St. Joseph's College of Engineering