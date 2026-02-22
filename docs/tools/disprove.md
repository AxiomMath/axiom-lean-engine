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
    Names not found in the code are silently ignored.

??? "`indices` · list[str] · Theorem indices to process"
    Optional list of theorem indices to process (0-based). Supports negative indices:
    `-1` is the last theorem, `-2` is second-to-last, etc.
    If not specified, all theorems are processed.

??? "`terminal_tactics` · list[str] · default: `['grind']` · Tactics to try when attempting to disprove"
    Tactics tried in order to prove the negation. `grind` often works for false statements. Defaults to 'grind'.

??? "`ignore_imports` · bool · default: `False` · Ignore import mismatches"
    Controls import statement handling:

    - `false` (default): Validate that imports match the environment. Returns an error if they don't.
    - `true`: Ignore the imports in `content` and use the environment's default imports instead. See the usage notes page for more details.

??? "`environment` · str · required · Lean environment or version"
    The Lean environment to use for evaluation. Each environment includes a specific
    Lean version and pre-built dependencies (typically Mathlib).

    Available environments: `lean-4.28.0`, `lean-4.27.0`, `lean-4.26.0`, etc.

??? "`timeout_seconds` · float · default: `120` · Max execution time in seconds"
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead.


## Output Fields

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from disprove tool"
    Messages from the disprove tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`results` · dict · Map from theorem name to disprove result"
    Each theorem maps to a string indicating the outcome of the disprove attempt.

??? "`disproved_theorems` · list · List of theorems that were disproved"
    Names of theorems where the negation was successfully proven.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.

## Python API

```python
result = await axle.disprove(
    content=lean_code,
    environment="lean-4.28.0",
    names=["conjecture1", "conjecture2"],  # Optional
    ignore_imports=False,                   # Optional
)
print(result.disproved_theorems)  # ["conjecture2"]
print(result.results)  # Per-theorem results
print(result.content)  # The processed Lean code
```

## CLI

**Usage:** `axle disprove CONTENT [OPTIONS]`

```bash
# Disprove all theorems
axle disprove theorems.lean --environment lean-4.28.0
# Disprove specific theorems by name
axle disprove theorems.lean --names main_theorem,helper --environment lean-4.28.0
# Disprove specific theorems by index
axle disprove theorems.lean --indices 0,-1 --environment lean-4.28.0
# Pipeline usage
cat theorems.lean | axle disprove - --environment lean-4.28.0
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
    "solid_fact": "Disprove: failed to prove negation. Remaining goal: `1 = 1`\n",
    "bold_claim": "Disprove: goal is false! Proof of negation by plausible.\n\n===================\nFound a counter-example!\nissue: 2 = 3 does not hold\n(0 shrinks)\n-------------------\n"
  },
  "disproved_theorems": ["bold_claim"],
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  }
}
```
