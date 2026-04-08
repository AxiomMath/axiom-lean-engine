# theorem2sorry

Strip proofs from theorems, replacing them with `sorry`.

[Try this example in the web UI](https://axle.axiommath.ai/theorem2sorry#data=eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiAxID0gMSA6PSBieSByZmxcbnRoZW9yZW0gbWFpbiA6IDIgPSAyIDo9IGJ5IHJmbCIsIm5hbWVzIjpbIm1haW4iXSwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D)

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

??? "`ignore_imports` · bool · default: `False` · Ignore import mismatches"
    Controls import statement handling:

    - `false` (default): Validate that imports match the environment. Returns an error if they don't.
    - `true`: Ignore the imports in `content` and use the environment's default imports instead. See the troubleshooting page for more details.

??? "`environment` · str · required · Lean environment or version"
    The Lean environment to use for evaluation. Each environment includes a specific
    Lean version and pre-built dependencies (typically Mathlib).

    Available environments: `lean-4.28.0`, `lean-4.27.0`, `lean-4.26.0`, etc.

??? "`timeout_seconds` · float · default: `120` · Max execution time in seconds"
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 900 seconds (15 minutes).


## Output Fields

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from theorem2sorry tool"
    Messages from the theorem2sorry tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · Lean code with proof bodies replaced by sorry"
    Useful for creating problem templates from solutions.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
# Convert all theorems
result = await axle.theorem2sorry(content=lean_code, environment="lean-4.28.0")

# Convert specific theorems by name
result = await axle.theorem2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    names=["foo"],
)

# Convert by index (supports negative indices)
result = await axle.theorem2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    indices=[0, -1],  # first and last
)
```

## CLI

**Usage:** `axle theorem2sorry CONTENT [OPTIONS]`

```bash
# Convert all theorems to sorry
axle theorem2sorry solution.lean -o problem.lean --environment lean-4.28.0
# Convert specific theorems by name
axle theorem2sorry solution.lean --names main_theorem,helper --environment lean-4.28.0
# Pipeline usage
cat solution.lean | axle theorem2sorry - --names main_theorem --environment lean-4.28.0 > problem.lean
```

## HTTP API

```bash
# Convert specific theorems by name
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2sorry \
    -d '{"content": "import Mathlib\ntheorem left_as_exercise : 1 = 1 := rfl\ntheorem the_tricky_one : 2 = 2 := rfl", "environment": "lean-4.28.0", "names": ["left_as_exercise"]}' | jq

# Convert all theorems
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2sorry \
    -d '{"content": "import Mathlib\ntheorem left_as_exercise : 1 = 1 := rfl\ntheorem the_tricky_one : 2 = 2 := rfl", "environment": "lean-4.28.0"}' | jq
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
  "content": "import Mathlib\n\ntheorem left_as_exercise : 1 = 1 := sorry\n\ntheorem the_tricky_one : 2 = 2 := rfl",
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  }
}
```
