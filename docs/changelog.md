# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).





## [Releases]

## v1.0.0

### Added

- Initial release of AXLE Python client
- Async client (`AxleClient`) with all 14 API tools:
    - `verify_proof` - Verify proofs against formal statements
    - `check` - Check Lean code for errors
    - `extract_theorems` - Extract theorems with dependencies
    - `rename` - Rename declarations
    - `theorem2lemma` - Convert theorem/lemma keywords
    - `theorem2sorry` - Replace proofs with sorry
    - `merge` - Combine multiple Lean files
    - `simplify_theorems` - Simplify proofs
    - `repair_proofs` - Repair broken proofs
    - `have2lemma` - Extract have statements to lemmas
    - `have2sorry` - Replace have statements with sorry
    - `sorry2lemma` - Extract sorries and errors to lemmas
    - `disprove` - Attempt to disprove theorems
    - `normalize` - Standardize formatting
- CLI tool with commands for all tools
- Helper functions for string manipulation
- Configuration via environment variables
- Type hints and PEP 561 compliance
- Comprehensive documentation
