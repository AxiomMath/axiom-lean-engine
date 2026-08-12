# sorry2lemma

Extract `sorry` placeholders and unsolved goals at error locations from Lean code and lift them into standalone top-level lemmas.

[Try this example in the web UI](https://axle.axiommath.ai/sorry2lemma#data=eyJjb250ZW50IjoidGhlb3JlbSBtdWx0aXBsZSAobiA6IE5hdCkgOiAxID0gMSDiiKcgMiA9IDIgOj0gYnkgY29uc3RydWN0b3IgPDs%2BIHNvcnJ5IiwiZXh0cmFjdF9zb3JyaWVzIjp0cnVlLCJleHRyYWN0X2Vycm9ycyI6dHJ1ZSwiaW5jbHVkZV93aG9sZV9jb250ZXh0Ijp0cnVlLCJyZWNvbnN0cnVjdF9jYWxsc2l0ZSI6dHJ1ZSwidmVyYm9zaXR5IjowLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

## See Also

This tool is partially powered by [`extract_goal`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/ExtractGoal.html), a Mathlib tactic for extracting goals into standalone declarations.

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

??? "`extract_sorries` · bool · default: `True` · Lift sorries into standalone lemmas"
    If `true`, `sorry` placeholders are extracted into standalone lemmas. Defaults to true.

??? "`extract_errors` · bool · default: `True` · Lift errors into standalone lemmas"
    If `true`, error positions (type mismatches, etc.) are extracted into standalone lemmas. Defaults to true.

??? "`include_whole_context` · bool · default: `True` · Include whole context when extracting"
    If `true`, lemmas include all context variables. If `false`, attempts to minimize the context. Defaults to true.

??? "`reconstruct_callsite` · bool · default: `False` · Replace sorry with lemma call"
    If `true`, the original `sorry` is replaced with a call to the extracted lemma. Defaults to false.

??? "`merge_duplicates` · bool · default: `False` · Merge duplicate extracted lemmas (by definitional equality)"
    If `true`, extracted lemmas within the same parent that are definitionally equal — to each other, or to the `theorem`/`lemma` they were extracted from — are merged: duplicates collapse into a single lemma that all callsites reference, and a sorry whose goal is definitionally equal to its parent theorem/lemma is dropped rather than lifted into a restatement (e.g. a top-level `:= sorry` / `:= by sorry`). The parent-restatement check applies only to `theorem`/`lemma` parents, not `def`/`instance`/etc. Defaults to false.

??? "`theorems_only` · bool · default: `True` · Process theorems/lemmas only"
    If `true` (default), only `theorem`/`lemma` declarations are processed. Set to `false` to process all declaration kinds (`def`/`instance`/`abbrev`/`opaque`/etc). When `false`, `names` and `indices` select over all declarations rather than just theorems.

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

??? "`reparse` · bool · default: `True` · Re-elaborate the transformed output"
    If `true` (default), the transformed content is re-elaborated. If `false`, re-elaboration is skipped. The resulting `lean_messages` is then returned empty.

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

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.); an empty `errors` list means the code compiles.

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

    If the request sets `reparse=false`, the transformed output is not re-elaborated and this field is returned empty.

??? "`tool_messages` · dict · Messages from sorry2lemma tool"
    Messages from the sorry2lemma tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`content` · string · Lean code with sorries/errors extracted as lemmas"
    The code with `sorry` and error positions lifted to top-level lemmas with their goals as types.

??? "`lemma_names` · list · Names of newly created lemmas"
    Names are auto-generated based on the parent theorem and position.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.sorry2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    names=["main_theorem"],         # Optional
    extract_sorries=True,           # Optional
    extract_errors=True,            # Optional
    include_whole_context=True,     # Optional
    reconstruct_callsite=False,     # Optional
    merge_duplicates=False,         # Optional
    theorems_only=True,             # Optional
    verbosity=0,                    # Optional: 0-2
)
print(result.content)
print(result.lemma_names)  # ["main_theorem.sorried", "main_theorem.unsolved"]
```

## CLI

**Usage:** `axle sorry2lemma CONTENT [OPTIONS]`

```bash
# Extract all sorries and errors
axle sorry2lemma theorem.lean --environment lean-4.31.0
# Extract from specific theorems
axle sorry2lemma theorem.lean --names main_proof,helper --environment lean-4.31.0
# Pipeline usage
cat theorem.lean | axle sorry2lemma - --environment lean-4.31.0 | axle check - --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/sorry2lemma \
    -d '{"content": "import Mathlib\ntheorem foo (p q : Prop) : p → q := by\n  intro hp\n  sorry", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "lean_messages": {
    "errors": [],
    "warnings": ["-:3:6-3:11: warning: declaration uses 'sorry'\n", "-:5:8-5:13: warning: declaration uses 'sorry'\n"],
    "infos": []
  },
  "tool_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "content": "import Mathlib\n\nlemma foo.sorried (p q : Prop) (hp : p) : q := sorry\n\ntheorem foo (p q : Prop) : p → q := by\n  intro hp\n  sorry",
  "lemma_names": ["foo.sorried"],
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}
```

## Demo

The `sorry2lemma` tool extracts `sorry` placeholders and unsolved goals at error locations into standalone lemmas. This is useful for breaking down incomplete proofs into subgoals that can be tackled independently.

### `extract_sorries` and `extract_errors`

You can control which types of goals are extracted:

```python
# Only extract sorries
result = await axle.sorry2lemma(content, environment="lean-4.28.0", extract_errors=False)

# Only extract errors
result = await axle.sorry2lemma(content, environment="lean-4.28.0", extract_sorries=False)

# Extract neither (effectively a no-op)
result = await axle.sorry2lemma(content, environment="lean-4.28.0", extract_sorries=False, extract_errors=False)
```

### `include_whole_context`, `reconstruct_callsite`
Refer to the [have2lemma documentation](have2lemma.md#demo) for a detailed description and examples of these fields. `sorry2lemma` handles them in mostly the same way.

**Multiple goals:** When a single sorry applies to multiple goals (e.g., after `<;>`), the tool generates multiple lemmas and combines them with `first`:
```lean
-- Input
theorem multiple (n : Nat) : 1 = 1 ∧ 2 = 2 := by constructor <;> sorry

-- Output with reconstruct_callsite=true
theorem multiple (n : Nat) : 1 = 1 ∧ 2 = 2 := by constructor <;> (first | exact multiple.sorried n | exact multiple.sorried_1 n)
```
