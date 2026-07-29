# have2sorry

Replace `have` statements in proofs with `sorry`. Useful for creating problem templates from solutions while keeping the overall proof structure intact.

[Try this example in the web UI](https://axle.axiommath.ai/have2sorry#data=eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiBUcnVlIDo9IGJ5XG4gIGhhdmUgOiAxID0gMiA6PSByZmxcbiAgdHJpdmlhbCIsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

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

??? "`theorems_only` · bool · default: `True` · Process theorems/lemmas only"
    If `true` (default), only `theorem`/`lemma` declarations are processed. Set to `false` to process all declaration kinds (`def`/`instance`/`abbrev`/`opaque`/etc). When `false`, `names` and `indices` select over all declarations rather than just theorems.

??? "`reparse` · bool · default: `True` · Re-elaborate the transformed output"
    If `true` (default), the transformed content is re-elaborated. If `false`, re-elaboration is skipped. The resulting `lean_messages` is then returned empty.

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

??? "`tool_messages` · dict · Messages from have2sorry tool"
    Messages from the have2sorry tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`content` · string · Lean code with have proof bodies replaced by sorry"
    The `have` structure is preserved.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.have2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    names=["main_theorem"],  # Optional
)
print(result.content)
```

## CLI

**Usage:** `axle have2sorry CONTENT [OPTIONS]`

```bash
# Replace all have statements
axle have2sorry theorem.lean --environment lean-4.31.0
# Replace from specific theorems
axle have2sorry theorem.lean --names main_proof,helper --environment lean-4.31.0
# Pipeline usage
cat theorem.lean | axle have2sorry - --environment lean-4.31.0 | axle check - --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/have2sorry \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\n  have h1 : 1 = 1 := by rfl\n  have h2 : 2 = 2 := by rfl\n  exact ⟨h1, h2⟩", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
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
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\n  have h1 : 1 = 1 := sorry\n  have h2 : 2 = 2 := sorry\n  exact ⟨h1, h2⟩",
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}
```
