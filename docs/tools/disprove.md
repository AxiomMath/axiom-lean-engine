# disprove

Attempt to disprove theorems by proving the negation.

[Try this example in the web UI](https://axle.axiommath.ai/disprove#data=eyJjb250ZW50IjoidGhlb3JlbSBmaXJzdCA6IOKIgCBuIDog4oSVLCBuIDwgMTBeMTAwIDo9IHNvcnJ5XG50aGVvcmVtIHNlY29uZCA6IDIgPSAxIDo9IGJ5IHNvcnJ5IiwidGVybWluYWxfdGFjdGljcyI6WyJhZXNvcCJdLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

## See Also

This tool is partially powered by [Plausible](https://github.com/leanprover-community/plausible), a Lean 4 library for property-based testing and counterexample generation.

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

??? "`names` · list[str] · Theorem names to process"
    Optional list of theorem names to process. If not specified, all theorems are processed.
    Requesting a name not found in the code returns an error.
    When `theorems_only` is `false`, these select over all declarations (not just theorems).

??? "`indices` · list[int] · Theorem indices to process"
    Optional list of theorem indices to process (0-based). Supports negative indices:
    `-1` is the last theorem, `-2` is second-to-last, etc.
    If not specified, all theorems are processed.
    When `theorems_only` is `false`, these select over all declarations (not just theorems).

??? "`terminal_tactics` · list[str] · default: `['grind']` · Tactics to try when attempting to disprove"
    Tactics tried in order to prove the negation. `grind` often works for false statements. Defaults to 'grind'.

??? "`theorems_only` · bool · default: `True` · Process theorems/lemmas only"
    If `true` (default), only `theorem`/`lemma` declarations are processed. Set to `false` to process all declaration kinds (`def`/`instance`/`abbrev`/`opaque`/etc). When `false`, `names` and `indices` select over all declarations rather than just theorems.

    Note: on this tool, operations on non-theorem kinds are a no-op.

??? "`verbosity` · float · default: `0` · Pretty-printer verbosity level (0-2)"
    Preset buckets of pretty-printer options, addressing the ambiguity problem described under `delab_options`:

    - `verbosity=0` (default): Standard pretty-printing options
    - `verbosity=1`: Robust options with additional explicitness
    - `verbosity=2`: Extra robust options with maximum explicitness (e.g. `pp.explicit=true`)

    **Rule of thumb:** If you encounter type inference errors in the output—especially involving coercions, casts, or polymorphic functions—try increasing the verbosity level. Do note that at `verbosity=2`, type signatures may become incredibly complex and unreadable, so it should be used sparingly.

    For finer-grained control over individual pretty-printer options, see `delab_options`, whose overrides apply on top of this preset.

??? "`delab_options` · dict · Pretty-printer option overrides"
    A dictionary of Lean pretty-printer options (JSON format), applied on top of the options this tool pretty-prints with. Only `pp.*` options are accepted.

    **Why override pretty-printer options?** Pretty-printed output can be ambiguous: the printed form loses information and fails to re-elaborate. Consider this example involving coercions:
    ```
    theorem explicit_coercion_test (n : ℕ) (hn : n > 0) : True := by
      have h : (∑ i : Fin n, (1 : ℝ) / (i.val + 1)) ≤ (harmonic n : ℝ) + 1 := by
        sorry
      trivial
    ```

    With default options, the coercion `(harmonic n : ℝ)` may be pretty-printed as `Rat.cast (harmonic n)`, losing the target type `ℝ`. This causes Lean to fail with errors like "failed to synthesize RatCast ℕ" because it can't infer the correct target type for the coercion. Setting `{"pp.explicit": true}` preserves the target type information and produces valid output.

    This is a known limitation of the Lean pretty-printer (for more details, see [this Zulip thread](https://leanprover.zulipchat.com/#narrow/stream/113488-general/topic/RFC.3A.20printing.20coercions.20with.20type.20ascriptions)).

    For preset buckets of suggested options, see the `verbosity` field (available on some tools).

??? "`mathlib_options` · bool · default: `False` · Enable Mathlib options"
    If true, enables conventional Mathlib options. This toggle sets `linter.mathlibStandardSet` to true, `autoImplicit` to false, `relaxedAutoImplicit` to false, and `pp.unicode.fun` to true. It also runs the `#lint` environment linters and reports their findings in `lean_messages`.

??? "`global_options` · dict · Lean option overrides"
    A dictionary of Lean options (JSON format), applied to everything the request parses and elaborates, on top of the defaults and the `mathlib_options` preset. For example, `{"maxHeartbeats": 400000}` raises the elaboration heartbeats budget.

    Each name must be a registered Lean option, and its value must match the type the option was declared with: a boolean, an integer, or a string.

    For pretty-printer overrides on the tools that pretty-print output, see `delab_options`.

??? "`ignore_imports` · bool · default: `True` · Ignore import mismatches"
    Controls import statement handling:

    - `true` (default): Ignore the imports in `content` and substitute the environment's default header. This uses the pre-built cached environment, so it is fast. The substituted code is returned in the `content` field.
    - `false`: Process the imports in `content` exactly as written. This is significantly slower (the cached environment cannot be reused) and may produce inconsistent or incorrect results if a required dependency such as `Mathlib.Tactic` is missing. A warning is returned in these cases. See the troubleshooting page for more details.

??? "`environment` · str · required · Lean environment or version"
    The Lean environment to use for evaluation. Each environment includes a specific
    Lean version and pre-built dependencies (typically Mathlib).

    Available environments: `lean-4.28.0`, `lean-4.27.0`, `lean-4.26.0`, etc.

??? "`timeout_seconds` · float · default: `120` · Max execution time in seconds"
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 900 seconds (15 minutes).


## Output Fields

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.); an empty `errors` list means the code compiles.

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`tool_messages` · dict · Messages from disprove tool"
    Messages from the disprove tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`results` · dict · Map from theorem name to disprove result"
    Each theorem maps to a string indicating the outcome of the disprove attempt.

??? "`negated` · dict · Map from theorem name to negated goal"
    Each theorem maps to the negated goal type that was attempted (the statement whose proof would disprove the theorem).

??? "`disproved_theorems` · list · List of theorems that were disproved"
    List of theorems that were disproved

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.disprove(
    content=lean_code,
    environment="lean-4.28.0",
    names=["conjecture1", "conjecture2"],  # Optional
    ignore_imports=True,                   # Optional
)
print(result.disproved_theorems)  # ["conjecture2"]
print(result.results)  # Per-theorem results
print(result.negated)  # Per-theorem negated goals
print(result.content)  # The processed Lean code
```

## CLI

**Usage:** `axle disprove CONTENT [OPTIONS]`

```bash
# Disprove all theorems
axle disprove theorems.lean --environment lean-4.31.0
# Disprove specific theorems by name
axle disprove theorems.lean --names main_theorem,helper --environment lean-4.31.0
# Disprove specific theorems by index
axle disprove theorems.lean --indices 0,-1 --environment lean-4.31.0
# Pipeline usage
cat theorems.lean | axle disprove - --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/disprove \
    -d '{"content": "import Mathlib\ntheorem solid_fact : 1 = 1 := rfl\ntheorem bold_claim : 2 = 3 := rfl", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "content": "import Mathlib\n\ntheorem solid_fact : 1 = 1 := rfl\ntheorem bold_claim : 2 = 3 := rfl\n",
  "lean_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "tool_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "results": {
    "solid_fact": "Disprove: failed to prove negation.",
    "bold_claim": "Disprove: goal is false! Proof of negation by plausible.\n\n===================\nFound a counter-example!\nissue: 2 = 3 does not hold\n(0 shrinks)\n-------------------\n"
  },
  "negated": {
    "solid_fact": "¬1 = 1",
    "bold_claim": "¬2 = 3"
  },
  "disproved_theorems": ["bold_claim"],
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  }
}
```
