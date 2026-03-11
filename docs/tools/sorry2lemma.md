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
    Names not found in the code are silently ignored.

??? "`indices` · list[str] · Theorem indices to process"
    Optional list of theorem indices to process (0-based). Supports negative indices:
    `-1` is the last theorem, `-2` is second-to-last, etc.
    If not specified, all theorems are processed.

??? "`extract_sorries` · bool · default: `True` · Lift sorries into standalone lemmas"
    If `true`, `sorry` placeholders are extracted into standalone lemmas. Defaults to true.

??? "`extract_errors` · bool · default: `True` · Lift errors into standalone lemmas"
    If `true`, error positions (type mismatches, etc.) are extracted into standalone lemmas. Defaults to true.

??? "`include_whole_context` · bool · default: `True` · Include whole context when extracting"
    If `true`, lemmas include all context variables. If `false`, attempts to minimize the context. Defaults to true.

??? "`reconstruct_callsite` · bool · default: `False` · Replace sorry with lemma call"
    If `true`, the original `sorry` is replaced with a call to the extracted lemma. Defaults to false.

??? "`verbosity` · float · default: `0` · Pretty-printer verbosity level (0-2)"
    0=default, 1=robust, 2=extra robust. Higher levels produce more explicit type annotations. Use when default output has ambiguity errors.

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

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from sorry2lemma tool"
    Messages from the sorry2lemma tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

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
    verbosity=0,                    # Optional: 0-2
)
print(result.content)
print(result.lemma_names)  # ["main_theorem.sorried", "main_theorem.unsolved"]
```

## CLI

**Usage:** `axle sorry2lemma CONTENT [OPTIONS]`

```bash
# Extract all sorries and errors
axle sorry2lemma theorem.lean --environment lean-4.28.0
# Extract from specific theorems
axle sorry2lemma theorem.lean --names main_proof,helper --environment lean-4.28.0
# Pipeline usage
cat theorem.lean | axle sorry2lemma - --environment lean-4.28.0 | axle check - --environment lean-4.28.0
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
    "warnings": ["-:3:6: warning: declaration uses 'sorry'\n", "-:5:8: warning: declaration uses 'sorry'\n"],
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

### `include_whole_context`, `reconstruct_callsite`, `verbosity`
Refer to the [have2lemma documentation](have2lemma.md#demo) for a detailed description and examples of these fields. `sorry2lemma` handles them in mostly the same way.

**Multiple goals:** When a single sorry applies to multiple goals (e.g., after `<;>`), the tool generates multiple lemmas and combines them with `first`:
```lean
-- Input
theorem multiple (n : Nat) : 1 = 1 ∧ 2 = 2 := by constructor <;> sorry

-- Output with reconstruct_callsite=true
theorem multiple (n : Nat) : 1 = 1 ∧ 2 = 2 := by constructor <;> (first | exact multiple.sorried n | exact multiple.sorried_1 n)
```
