# check

Evaluate Lean code and collect all messages (errors, warnings, and info). Use this to check if code is valid without verification against a formal statement, or to get the output of `#check` / `#eval` statements.

[Try this example in the web UI](https://axle.axiommath.ai/check#data=eyJjb250ZW50IjoiI2NoZWNrIE5hdFxuI2NoZWNrIExpc3RcbiNldmFsIDEgKyAxIiwibWF0aGxpYl9saW50ZXIiOmZhbHNlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

## See Also

For interactive compilation feedback without an API, try the [Lean 4 Web Playground](https://live.lean-lang.org).

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

??? "`mathlib_linter` · bool · default: `False` · Enable Mathlib linters"
    If true, enables Mathlib's standard linter set. Linter messages appear in `lean_messages.warnings`.

??? "`ignore_imports` · bool · default: `False` · Ignore import mismatches"
    Controls import statement handling:

    - `false` (default): Validate that imports match the environment. Returns an error if they don't.
    - `true`: Ignore the imports in `content` and use the environment's default imports instead. See the troubleshooting page for more details.

??? "`environment` · str · required · Lean environment or version"
    The Lean environment to use for evaluation. Each environment includes a specific
    Lean version and pre-built dependencies (typically Mathlib).

    Available environments: `lean-4.28.0`, `lean-4.27.0`, `lean-4.26.0`, etc.

??? "`timeout_seconds` · float · default: `120` · Max execution time in seconds"
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 300 seconds (5 minutes).


## Output Fields

??? "`okay` · bool · True if the Lean code is valid"
    Returns `true` if the code compiles without errors. Warnings don't affect this value.

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from check tool"
    Messages from the check tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`failed_declarations` · list · Declaration names that failed validation"
    List of declaration names that have compilation or validation errors.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.check(
    content="import Mathlib\n#eval 2+2",
    environment="lean-4.28.0",
    mathlib_linter=False,     # Optional
    ignore_imports=False,     # Optional
    timeout_seconds=120,      # Optional
)

print(result.okay)  # True if code is valid
print(result.content)  # The processed Lean code
print(result.lean_messages.infos)  # ["4\n"]
```

## CLI

**Usage:** `axle check CONTENT [OPTIONS]`

```bash
# Basic usage
axle check theorem.lean --environment lean-4.28.0
# Pipeline usage
cat theorem.lean | axle check - --environment lean-4.28.0
# Exit non-zero if code is invalid
axle check theorem.lean --strict --environment lean-4.28.0
# Use in shell conditionals
if axle check theorem.lean --strict --environment lean-4.28.0 > /dev/null; then
    echo "Valid Lean code"
fi
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/check \
    -d '{"content": "import Mathlib\n#eval 2+2", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "okay": true,
  "content": "import Mathlib\n\n#eval 2+2\n",
  "lean_messages": {
    "errors": [],
    "warnings": [],
    "infos": ["4\n"]
  },
  "tool_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "timings": {
    "total_ms": 62
  },
  "failed_declarations": []
}
```
