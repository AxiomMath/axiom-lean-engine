# extract_proof_states

Extract the tactic proof state at the end of each line of the given Lean code, as shown in a Lean editor's goal panel. Lines with no tactic proof state are omitted.

[Try this example in the web UI](https://axle.axiommath.ai/extract_proof_states#data=eyJjb250ZW50IjogImltcG9ydCBNYXRobGliXG50aGVvcmVtIGZvbyAobiA6IE5hdCkgOiBuICsgMCA9IG4gOj0gYnlcbiAgaW5kdWN0aW9uIG4gd2l0aFxuICB8IHplcm8gPT4gcmZsXG4gIHwgc3VjYyBrIGloID0%2BIHNpbXAiLCAiaWdub3JlX2ltcG9ydHMiOiB0cnVlLCAiZW52aXJvbm1lbnQiOiAibGVhbi00LjI4LjAiLCAidGltZW91dF9zZWNvbmRzIjogMTIwfQ%3D%3D)

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

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

??? "`proof_states` · list · Per-line proof states"
    List of `{line, proof_state}` objects, one per line that has a tactic proof state, in file order. `line` is the 1-based line number in `content`. `proof_state` is the pretty-printed goal state at the end of that line — what an editor's goal panel shows with the cursor there.

    The total size of this field is capped at 10,000,000 characters. When the cap is reached, proof states for the remaining lines are omitted, `truncated` is set to `true`, and a warning is added to `tool_messages`.

??? "`truncated` · bool · True if proof states were omitted due to the size cap"
    Returns `true` if `proof_states` hit the 10,000,000-character cap and states for the remaining lines were omitted. A warning in `tool_messages` reports the line where truncation occurred.

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.); an empty `errors` list means the code compiles.

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`tool_messages` · dict · Messages from extract_proof_states tool"
    Messages from the extract_proof_states tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.extract_proof_states(
    content="import Mathlib\ntheorem foo (n : Nat) : n + 0 = n := by\n  induction n with\n  | zero => rfl\n  | succ k ih => simp",
    environment="lean-4.28.0",
    ignore_imports=True,  # Optional
    timeout_seconds=120,   # Optional
)

for state in result.proof_states:
    print(f"line {state.line}:\n{state.proof_state}")
```

## CLI

**Usage:** `axle extract-proof-states CONTENT [OPTIONS]`

```bash
# Basic usage
axle extract-proof-states proof.lean --environment lean-4.31.0
# Pipeline usage
cat proof.lean | axle extract-proof-states - --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/extract_proof_states \
    -d '{"content": "import Mathlib\ntheorem foo (n : Nat) : n + 0 = n := by\n  induction n with\n  | zero => rfl\n  | succ k ih => simp", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "proof_states": [
    {"line": 2, "proof_state": "n : ℕ\n⊢ n + 0 = n"},
    {"line": 3, "proof_state": "n : ℕ\n⊢ n + 0 = n"},
    {"line": 4, "proof_state": "no goals"},
    {"line": 5, "proof_state": "no goals"}
  ],
  "truncated": false,
  "content": "import Mathlib\ntheorem foo (n : Nat) : n + 0 = n := by\n  induction n with\n  | zero => rfl\n  | succ k ih => simp",
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
  "timings": {
    "total_ms": 113,
    "parse_ms": 112
  }
}
```
