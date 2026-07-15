# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).




## [Releases]

## v1.5.0 - July 15, 2026

### Added
- Added `LeanResourceExceeded` and `LeanTimeout` exceptions. The Lean worker exceeding its memory cap or time budget now raises a distinct, non-retryable exception instead of the generic `AxleRuntimeError`, so callers can record it as a deterministic outcome rather than retrying.
- `check`, `extract_decls`, and `extract_theorems` now accept optional `names` and `indices` arguments (as `theorem2sorry` and similar tools already do) to select which declarations to process. The returned documents / messages are restricted to them, and elaboration is skipped for the proofs of unselected declarations. This is a speed feature and should be used when elaborating the whole file is too slow. Note that this changes the behavior of the tool: the returned Lean messages will be incomplete, and the per-document `content` field for `extract_decls` and `extract_theorems` is returned empty. See the [`check`](https://axle.axiommath.ai/v1/docs/tools/check) and [`extract_decls`](https://axle.axiommath.ai/v1/docs/tools/extract_decls) pages for more details. Regular users with no speed concerns can disregard these options.
- `extract_decls` documents now include an `unfolded_type_hash` field: the type hash after unfolding module-local elaboration auxiliaries (e.g. `foo.match_1`), so types differing only by such an auto-generated name deduplicate where `type_hash` would not. See the [`extract_decls` page](https://axle.axiommath.ai/v1/docs/tools/extract_decls) for details. The behavior of the base `type_hash` field is unchanged.
- `verify_proof` now accepts a `verify_negation` option (default `false`). When set, `verify_proof` additionally checks whether `content` proves the *negation* of `formal_statement` — i.e. whether it disproves the statement — and reports the result in a new `negation` field, which carries the same `okay`, `tool_messages`, and `failed_declarations` as the top-level result. The field is omitted unless `verify_negation` is set. Regular users can ignore this option.
- `disprove` and `extract_decls` now accept a `verbosity` parameter (0=default, 1=robust, 2=extra robust), which affects the pretty-printed types output by the tools (the `negated` field in `disprove`, and the per-document `type` field in `extract_decls`). Higher verbosity levels make the pretty-printer more explicit, which helps when the default output re-elaborates ambiguously. This is the same behavior as existing tools with the `verbosity` parameter, e.g. `have2lemma`, `sorry2lemma`.
- Added `AxleClient.get_latest_environment()`, which fetches the available Lean+Mathlib environments and returns the latest one.
- Added instructions for citing AXLE in the documentation. See [Citing AXLE](https://axle.axiommath.ai/v1/docs/#citing-axle).
- Added Lean 4.32.0 support.

### Fixed
- Fixed a bug in tools that analyze term-mode goals (`have2lemma`, `sorry2lemma`, `disprove`) causing goal extraction to silently fail with `include_whole_context=false`. For example, [this request](https://axle.axiommath.ai/sorry2lemma#r=604f708c-99f1-49f0-9c4a-dd987d2ad024) failed in previous versions, leaving the content unchanged.
- `verify_proof` is now module-aware. Previously, module dependencies would be treated as disallowed axioms when not using the default header. For example, [this request](https://axle.axiommath.ai/verify_proof#r=24ac6a65-5afc-4119-bfb8-a7a1e6af43dd) was wrongfully rejected but now passes.

### Changed
- Various tools now *skip proof elaboration* for unselected declarations when `names` or `indices` is provided. This is a speed change; however, any outputs pertaining to the unselected declarations (e.g. Lean messages from their proofs) are unreliable and should not be used.




## v1.4.0 - July 1, 2026

AXLE will be presented at the 3rd AI for Math Workshop at ICML 2026 as a contributed talk! Read the technical report on [arXiv](https://arxiv.org/abs/2606.26442).

### Changed

- `ignore_imports` now defaults to `true`. When your code's imports don't match the environment's default header, AXLE substitutes the default header (reusing the cached environment) instead of raising an error. Setting `ignore_imports=false` no longer errors on a mismatch; instead AXLE processes your imports as written, which is significantly slower and may give incorrect results if a required dependency such as `Mathlib.Tactic` is missing (a warning is returned in these cases). See [Import Mismatches](https://axle.axiommath.ai/v1/docs/troubleshooting/#import-mismatches) for details.

- Reworked the `tool_messages` and `okay` fields for a few tools. See [Interpreting the `okay` field](https://axle.axiommath.ai/v1/docs/troubleshooting/#interpreting-the-okay-field) for details.

    - `check` now reports validation findings (`sorry`, disallowed axioms, unsafe definitions) as `tool_messages` warnings instead of errors. `okay` continues to reflect compilation only, and the offending declarations remain listed in `failed_declarations`.
    - `repair_proofs` now reports failed repairs (e.g. terminal tactics that fail to prove a `sorry`) as `tool_messages` errors instead of warnings, so `okay` is `True` only when the repaired code compiles *and* all repairs succeed.

- Many tools now inspect values of opaques: `opaque` and `partial def` (and `theorem` in 4.30+).

    - `merge` now considers opaque bodies, not just types, when de-duplicating.
    - `extract_decls` now populates value fields for opaques.

- In `check` and `verify_proof`, file-level validation errors now invalidate all contained declarations — e.g. use of `open private` results in every declaration being added to `failed_declarations`.
- Reworded one of the `verify_proof`/`check` error messages to be more descriptive.

    - Before: `Declaration '{name}' uses 'sorry' which is not allowed in a valid proof`
    - After: `Declaration '{name}' is incomplete (uses 'sorry' or has errors)`

### Added
- Added Lean 4.30.0 and 4.31.0 support.
- Added a `relax_defeq_transparency` repair pass to `repair_proofs` (on by default). Lean 4.29's `backward.isDefEq.respectTransparency` (default `true`) keeps `isDefEq` from unfolding reducible/instance definitions when unifying implicit arguments, breaking proofs that relied on it. Mathlib turns it off per-theorem. This repair prepends `set_option backward.isDefEq.respectTransparency false in` when the fix gets the proof further (all errors resolved, or the first error appears later in the source). On environments without the option, the repair is a no-op.
- `extract_decls` and `extract_theorems` report four new per-declaration fields: `type_depth`, `term_depth`, `wall_ms`, and `heartbeats`. See the [`extract_decls` page](https://axle.axiommath.ai/v1/docs/tools/extract_decls) for more details.

### Removed
- Removed the `http2` parameter from the `AxleClient` constructor, which was slowing the client down. The client now uses HTTP/1.1 exclusively (via `aiohttp`); the optional HTTP/2 transport and its `httpx` dependency have been dropped. Code that passed `http2=...` should remove that argument.

### Fixed
- Fixed `extract_decls` bug for opaques where value dependencies were misclassified as type dependencies.
- Fixed `disprove` bug negating only the goal instead of negating the entire declaration type. The negated goal is now returned in a new `negated` field (a map from theorem name to negated goal) instead of being appended to each `results` message.
- Browser-based clients (web apps, extensions, in-page demos) can call AXLE directly! The HTTP API now supports cross-origin (CORS) requests: `OPTIONS` preflights return `204` with `Access-Control-Allow-*` headers, and every `/api/v1/` response carries `Access-Control-Allow-Origin`.
- Fixed HTTP status codes on `/api/v1/` endpoints: an unknown tool name now returns `404` (previously `200` with a `user_error` body), and methods other than `POST` return `405` with an `Allow` header (previously `422`).
- Fixed a rare bug resulting in lost executor slots. This bug used to cause a rare user-side failure or, more commonly, very high latency for some requests.


Thanks to @SSingh-07 on Github for submitting a few issues, which we have fixed in this update!!

## v1.3.0 - June 3, 2026

### Added

- Added *link shortening* to the gateway. The web UI has been updated correspondingly. Try it out: [https://axle.axiommath.ai/check#r=7d70453f-813f-4d19-8de9-44793dafa835](https://axle.axiommath.ai/check#r=7d70453f-813f-4d19-8de9-44793dafa835)
- Added Claude web, desktop, and mobile support to the [`axiom-axle-mcp`](https://pypi.org/project/axiom-axle-mcp/) MCP server via a hosted endpoint at `https://mcp.axiommath.ai/mcp`. See the [Quick Start](https://axle.axiommath.ai/v1/docs/quickstart/#mcp-server) for details. Thanks to Andrew Sutherland for suggestions on setting up this hosted instance.
- Added three new fields to the `info` field of every response to identify the executor version your request was handled on: `_executor_commit_sha`, `_executor_docker_image_id`, and `_executor_artifact_sha256`.

### Changed

- Added a new option `theorems_only` (default `true`) to all tools that select over theorems/lemmas. These tools now have the ability to select over **all declaration kinds**: `theorem2lemma`, `theorem2sorry`, `simplify_theorems`, `repair_proofs`, `have2lemma`, `have2sorry`, `sorry2lemma`, `disprove`:

    - To use this feature, set `theorems_only` to `false`. For backwards compatibility (default), keep `theorems_only` set to `true`.
    - You can now sorry out any declaration body, simplify/repair any declaration containing a proof, and extract lemmas from any `sorry` locations and any `have` statement locations in any declarations, including definitions, opaques, instances, etc.
    - For `theorem2lemma` and `disprove`, the new setting is a no-op on non-theorem kinds.
    - Note that the value of `theorems_only` affects what the `names` and `indices` fields select over. When `theorems_only` is `false`, names and indices refer to **all** declarations, not just theorem kinds.

- Reworked `repair_proofs` (the first of several planned changes):

    - Added two new passes to `repair_proofs`: `remove_unknown_options`, which strips unknown options both at the command-level and within proofs/terms, and `enable_autoImplicit`, which restores the `autoImplicit` option at the beginning of a theorem if an unknown identifier error occurs in a theorem's type signature.
    - Added command-level re-elaboration to `repair_proofs`, allowing repairs to stack (for example, when applying terminal tactics reveals another error to fix).
    - `replace_unsafe_tactics` now warns the user when replacing `native_decide` with `decide +kernel` fails. The tactic location is now left untouched.
    - `apply_terminal_tactics` now warns when no terminal tactics could be successfully applied at a given location in `repair_proofs`.
    - Fixed a bug in `apply_terminal_tactics` allowing malformed proofs with metavariables to be counted as successes in `repair_proofs`.

- `verify_proof` now permits `partial def` and `opaque`. These checks were overly strict previously and do not raise soundness concerns.
- `merge` now deduplicates other declaration kinds: axioms, opaques, inductives, classes, structures, etc. Previously, only theorems and definitions were eligible for deduplication.
- `extract_decls` now names anonymous declarations (examples, anonymous instances) by their start position, line then column (e.g. `_example_12_0`), rather than a running counter (e.g. `_example_0`), so the placeholder is stable and remains unique across a file even when several share a line.
- Added the `merge_duplicates` (default `false`) option to `sorry2lemma`, which merges extracted lemmas that are duplicates (either with other lemmas, or to the existing top-level theorem/lemma from which they are extracted) by definitional equality into a single lemma with all callsites pointing at it. Existing behavior can be retained with the default setting `merge_duplicates=false`.


### Fixed

- Added faster, more graceful retries on certain classes of connection errors. Minor change.


## v1.2.1 - April 29, 2026

### Deprecated

- `extract_theorems` has been deprecated and will no longer be updated. Please use `extract_decls` instead, which supports all declaration kinds (def, theorem, lemma, abbrev, instance, structure, etc.).

### Changed

- The AXLE client now uses HTTP/2 by default. We don't expect any significant performance differences from this change, but feel free to file a bug report if this is not the case. Users may set the `http2` parameter to false in the client constructor to revert back to the original HTTP/1.1 settings.

### Added

- Added a new option `expand_scoped_notations` to the `normalize` tool, which delaborates scoped notations into their expanded forms. See the [`normalize` documentation page](https://axle.axiommath.ai/v1/docs/tools/normalize/#available-normalizations) for details.

### Fixed

- Fixed a bug in the executors causing requests to hang, occasionally resulting in abnormally high latencies.

## v1.2.0 - April 15, 2026

### Added

- Added two new fields in `extract_theorems` to be consistent with `extract_decls` (see below):
    - `kind`: always `theorem` for `extract_theorems`.
    - `declaration_messages`: same content as `theorem_messages`. `theorem_messages` is now deprecated and will be removed in a future update.
- Added `extract_decls`, an upgraded version of `extract_theorems` that extracts all declaration kinds.
    - New `kind` field in each document. Possible values: `theorem`, `def`, `abbrev`, `axiom`, `opaque`, `structure`, `class`, `class inductive`, `inductive`, `instance`, `example`, `unknown`
    - Note: Not all fields are meaningful for all declaration kinds (e.g., `proof_length`/`tactic_counts` only apply to theorems/lemmas with tactic proofs.)
    - This tool should be used instead of `extract_theorems` as it is a strict superset of functionality. `extract_theorems` will be deprecated in a future update.

### Fixed

- Added "Last Used" and "Requests (24h)" columns to the API key console page for better visibility into API key usage.


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
