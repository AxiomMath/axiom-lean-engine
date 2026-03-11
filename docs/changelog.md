# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).





## [Releases]

## v1.0.1 - March 11, 2026

### Added

- Added [Changelog](https://axle.axiommath.ai/v1/docs/changelog/) and [Troubleshooting](https://axle.axiommath.ai/v1/docs/troubleshooting/) to the documentation pages.

### Fixed

- Increased request limits and fixed a typo in the documentation. Users with an API key are now limited to 20 active requests, and anonymous users are limited to 10 active requests.
- Increased maximum timeout to 15 minutes (from 5 minutes).
- Environments are now sorted by prefix (alphabetically) and then by version number (more recent versions first)
- Fixed a bug with `disprove` failing to recognize implicit local variables. This bug was [found by Bulhwi Cha](https://leanprover.zulipchat.com/#narrow/channel/219941-Machine-Learning-for-Theorem-Proving/topic/Axiom.20Lean.20Engine/near/578064991) on Lean Zulip.


## v1.0.0 - March 4, 2026

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
