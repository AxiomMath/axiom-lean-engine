# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).





## [Releases]

## v1.1.1 - April 8, 2026

### Changed

- [!] We are turning *on* the `autoImplicit` and turning *off* the `pp.unicode.fun` Lean options. AXLE will now automatically insert implicit variables when they are missing. **This is a significant behavioral change, check your code!** These settings are consistent with Lean's default. The previous options were remnants from internal use preferences.
- [!] **We have renamed `mathlib_linter` to `mathlib_options`**, which now sets `linter.mathlibStandardSet` to true, `autoImplicit` to false, `relaxedAutoImplicit` to false, and `pp.unicode.fun` to true. Use this toggle to enable the stricter defaults that Mathlib uses by convention.

### Added

- Added Lean 4.29.0 support.
- Added support for glob patterns in the `permitted_sorries` field for `verify_proof`. See the `verify_proof` documentation page under the `permitted_sorries` field for example use cases.

### Fixed

- Fixed a bug causing timeouts to be capped at 10 minutes. All requests now max out at 15 minutes (with documentation updated correspondingly).

## v1.1.0 - April 1, 2026

### Changed

- [!] Removed `document_messages` from the response of `extract_theorems` — to replicate old behavior, run the `content` field of the resulting documents through the `check` tool. This change significantly improves the speed of `extract_theorems`.
- [!] `includeEndPos` has been turned on for Lean messages. This changes the format from:
`-:4:38: error: Function expected at...`
to (when endPos is available):
`-:4:38-4:43: error: Function expected at...`
This change affects all tools with Lean messages.
- Significantly reworked the Lean executor pool backend.
    - Latency has been decreased by 50% in most cases. For longer requests, the new executors can be more than 5 times faster!
    - Previously, the first request to each environment required a ~10s warmup. This is no longer the case, and so requests will be more faithful to their Lean timeout limits (not including queueing / waiting for available slots).
    - Eliminates a security risk involving persistent Lean workers.
- Improved the Lean worker warm-up pipeline. Worker scale-up is also more aggressive than before. In the worst case, when all workers are completely occupied / offline, users should expect no more than a 2-3 minute delay before more worker capacity spins up.

### Fixed

- Removed redundant parsing resulting in occasional speedups in `repair_proofs`, `normalize`, etc. when content does not change.
- Pruned missing executors from the gateway registry. Fixes a bug with autoscaling improperly triggering.


## v1.0.2 - March 18, 2026

### Added

- Added explicit `okay` return value to `repair_proofs`

### Changed

- Improved error messages for unknown options in `simplify_theorems`, `repair_proofs`, `normalize`
- Improved error messages for `ignore_imports` error (with links to relevant docs)
- Improved the efficiency of `merge`, bringing down the time spent on large requests by 20-30%.


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
