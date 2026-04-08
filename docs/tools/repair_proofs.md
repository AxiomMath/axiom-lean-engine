# repair_proofs

Attempt to repair broken theorem proofs.

[Try this example in the web UI](https://axle.axiommath.ai/repair_proofs#data=eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcblxudGhlb3JlbSBwYXJhbGxlbF9nb2Fsc19leHRyYW5lb3VzXG4gICh5IDog4oSCKSAoeCA6IOKEnSkgKGggOiB4IOKJpSAyKSA6XG4gIDcgKiAoMyAqIHkgKyAyKSA9IDIxICogeSArIDE0XG4gIOKIpyB4XjIg4omlIDFcbiAgOj0gYnlcbiAgY29uc3RydWN0b3JcbiAgYWxsX2dvYWxzIHNvcnJ5XG4gIGdyaW5kXG4gIHJmbFxuICBzb3JyeSIsImlnbm9yZV9pbXBvcnRzIjpmYWxzZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

??? "Known Limitations"
    - The repair tool does not guarantee that repaired proofs will be semantically correct or complete
    - Some repairs may introduce new errors or conflicts
    - Complex proofs with multiple goals may require manual intervention
    - The tool works best on simple, localized proof issues

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

??? "`repairs` · list[str] · List of repairs to apply"
    If not specified, all repairs are applied. See below for available repairs.

??? "`terminal_tactics` · list[str] · default: `['grind']` · Tactics to try for closing goals"
    Used when 'apply_terminal_tactics' repair is applied. Tactics tried in order; stops on first success. Defaults to 'grind'.

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

??? "`tool_messages` · dict · Messages from repair_proofs tool"
    Messages from the repair_proofs tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · Lean code with repair attempts applied"
    Check `okay` to see if repairs succeeded.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.

??? "`repair_stats` · dict · Count of each repair type applied"
    Maps repair names to counts (e.g., `{"apply_terminal_tactics": 2}`).

??? "`okay` · bool · Whether the proof compiles after repair and all repairs succeed"
    `True` when the file compiles after repair and all repairs succeed; `False` otherwise.


## Available Repairs

??? "`remove_extraneous_tactics`"
    When a proof is already complete but has extra tactics afterward, this repair removes the extraneous tactics.

    **Before:**
    ```lean
    theorem extra_tactics : 1 = 1 := by
      rfl
      simp  -- This tactic is never reached
      omega
    ```

    **After:**
    ```lean
    theorem extra_tactics : 1 = 1 := by
      rfl
    ```

??? "`apply_terminal_tactics`"
    Tries terminal tactics in place of sorries.

    In `theorem foo : 1 = 1 := by sorry`, the proof is incomplete. This repair attempts to apply terminal tactics to complete the proof. The tactics to try can be customized via the `terminal_tactics` parameter (default: `["grind"]`).

    **Before:**
    ```lean
    theorem simple_eq : 1 + 1 = 2 := by
      sorry
    ```

    **After:**
    ```lean
    theorem simple_eq : 1 + 1 = 2 := by
      grind
    ```

??? "`replace_unsafe_tactics`"
    Replaces unsafe tactics with safer alternatives.

    Some tactics like `native_decide` use native code execution which can be unsafe. This repair replaces them with safer alternatives.

    **Before:**
    ```lean
    theorem check_prime : Nat.Prime 7 := by
      native_decide
    ```

    **After:**
    ```lean
    theorem check_prime : Nat.Prime 7 := by
      decide +kernel
    ```

## Python API

```python
# Repair all theorems with all repairs
result = await axle.repair_proofs(content=broken_code, environment="lean-4.28.0")

# Repair specific theorems
result = await axle.repair_proofs(
    content=broken_code,
    environment="lean-4.28.0",
    names=["broken_theorem"],
)

# Apply only specific repairs
result = await axle.repair_proofs(
    content=broken_code,
    environment="lean-4.28.0",
    repairs=["remove_extraneous_tactics"],
)

# Use custom terminal tactics
result = await axle.repair_proofs(
    content=broken_code,
    environment="lean-4.28.0",
    repairs=["apply_terminal_tactics"],
    terminal_tactics=["aesop", "simp", "rfl"],
)

print(result.content)
print(result.repair_stats)
```

## CLI

**Usage:** `axle repair-proofs CONTENT [OPTIONS]`

```bash
# Repair all theorems
axle repair-proofs broken.lean --environment lean-4.28.0
# Repair specific theorems
axle repair-proofs broken.lean --names main_theorem,helper --environment lean-4.28.0
# Apply only specific repairs
axle repair-proofs broken.lean --repairs remove_extraneous_tactics --environment lean-4.28.0
# Pipeline usage
cat broken.lean | axle repair-proofs - --environment lean-4.28.0 | axle check - --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/repair_proofs \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := by\n  rfl\n  simp\n  omega", "environment": "lean-4.28.0", "names": ["foo"]}' | jq
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
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := by\n  rfl",
  "timings": {
    "total_ms": 102,
    "parse_ms": 95
  },
  "repair_stats": {
    "remove_extraneous_tactics": 2,
    "apply_terminal_tactics": 0,
    "replace_unsafe_tactics": 0
  },
  "okay": true
}
```
