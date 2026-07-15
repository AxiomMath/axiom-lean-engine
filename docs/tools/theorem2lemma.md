# theorem2lemma

Convert between `theorem` and `lemma` declaration keywords.

[Try this example in the web UI](https://axle.axiommath.ai/theorem2lemma#data=eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiAxID0gMSA6PSBieSByZmxcbnRoZW9yZW0gbWFpbiA6IDIgPSAyIDo9IGJ5IHNvcnJ5IiwibmFtZXMiOlsiZm9vIl0sImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

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

??? "`target` · str · default: `lemma` · Target keyword (lemma or theorem)"
    The keyword to convert to. Use `lemma` or `theorem`. Defaults to `lemma`.

??? "`theorems_only` · bool · default: `True` · Process theorems/lemmas only"
    If `true` (default), only `theorem`/`lemma` declarations are processed. Set to `false` to process all declaration kinds (`def`/`instance`/`abbrev`/`opaque`/etc). When `false`, `names` and `indices` select over all declarations rather than just theorems.

    Note: on this tool, operations on non-theorem kinds are a no-op.

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

??? "`tool_messages` · dict · Messages from theorem2lemma tool"
    Messages from the theorem2lemma tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`content` · string · Lean code with updated declaration keywords"
    The code with `theorem` converted to `lemma` (or vice versa) for the specified declarations.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
# Convert all theorems to lemmas
result = await axle.theorem2lemma(content=lean_code, environment="lean-4.28.0")

# Convert specific theorems by name
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    names=["foo", "bar"],
)

# Convert by index
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    indices=[0, -1],  # first and last
)

# Convert to theorem instead
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    target="theorem",
)
```

## CLI

**Usage:** `axle theorem2lemma CONTENT [OPTIONS]`

```bash
# Convert all theorems to lemmas
axle theorem2lemma theorems.lean --environment lean-4.31.0
# Convert specific theorems by name
axle theorem2lemma theorems.lean --names foo,bar --environment lean-4.31.0
# Convert to theorem instead
axle theorem2lemma lemmas.lean --target theorem --environment lean-4.31.0
# Convert first and last theorems
axle theorem2lemma theorems.lean --indices 0,-1 --environment lean-4.31.0
# Pipeline usage
cat theorems.lean | axle theorem2lemma - --environment lean-4.31.0 | axle check - --environment lean-4.31.0
```

## HTTP API

```bash
# Convert all to lemmas
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2lemma \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := rfl\ntheorem bar : 2 = 2 := rfl", "environment": "lean-4.28.0"}' | jq

# Convert specific theorems by index to theorems
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2lemma \
    -d '{"content": "import Mathlib\nlemma foo : 1 = 1 := rfl\nlemma bar : 2 = 2 := rfl", "environment": "lean-4.28.0", "indices": [0], "target": "theorem"}' | jq
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
  "content": "import Mathlib\n\nlemma foo : 1 = 1 := rfl\n\nlemma bar : 2 = 2 := rfl",
  "timings": {
    "total_ms": 106,
    "parse_ms": 100
  }
}
```
