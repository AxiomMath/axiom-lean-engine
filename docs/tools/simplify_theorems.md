# simplify_theorems

Simplify theorem proofs by removing unnecessary tactics and cleaning up code.

[Try this example in the web UI](https://axle.axiommath.ai/simplify_theorems#data=eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcblxudGhlb3JlbSBmb28gKGEgYiA6IE5hdCkgOlxuICAgIGEg4omkIGEgKyBiIDo9IGJ5XG4gIGhhdmUgaCA6IGEgKyAwIOKJpCBhICsgYiA6PSBieVxuICAgIGFwcGx5IE5hdC5hZGRfbGVfYWRkX2xlZnQgO1xuICAgIGV4YWN0IE5hdC56ZXJvX2xlIF9cbiAgc2ltcCIsImlnbm9yZV9pbXBvcnRzIjpmYWxzZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

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

??? "`simplifications` · list[str] · List of simplifications to apply"
    If not specified, all simplifications are applied. See below for available simplifications.

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

??? "`tool_messages` · dict · Messages from simplify_theorems tool"
    Messages from the simplify_theorems tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · Lean code with simplified theorem proofs"
    May be shorter and cleaner than input.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.

??? "`simplification_stats` · dict · Count of each simplification type applied"
    Maps simplification names to counts (e.g., `{"remove_unused_tactics": 3}`).


## Available Simplifications

??? "`remove_unused_tactics`"
    Removes tactics that don't contribute to the proof.

    In `theorem foo : 1 = 1 := by rfl <;> rfl`, the second `rfl` is useless and should be removed.

??? "`remove_unused_haves`"
    Removes unused `have` statements.

    ```lean
    theorem foo (a b : Nat) :
        a ≤ a + b := by
      have h : a + 0 ≤ a + b := by
        apply Nat.add_le_add_left ;
        exact Nat.zero_le _
      simp
    ```

    In the above theorem, `h` is useless and should be removed.

??? "`rename_unused_vars`"
    Cleans up unused variable names.

    In `theorem triv (arg : ℕ) : True := trivial`, the variable `arg` is useless. We do *not* remove it, because that would change the signature of the theorem, but we can clean things up a bit by replacing it with an underscore, as in: `theorem triv (_ : ℕ) : True := trivial`.

<!-- Not functional
#### `simplify_have_exact`
```
theorem h₁ : (5 : ℝ) ≤ Real.sqrt 26 := by
  have h : 5 ≤ Real.sqrt 26 := by apply Real.le_sqrt_of_sq_le ; norm_num
  exact h
```
In `h₁`, the `have` statement, followed by `exact` is redundant. The goal can just be proved directly:
```
theorem h₁ : (5 : ℝ) ≤ Real.sqrt 26 := by
  apply Real.le_sqrt_of_sq_le ; norm_num
```
However, this causes problems with indentation and formatting that cannot be easily fixed, so this has been disabled for now.


#### `remove_unnecessary_seq_focus`
```
theorem h₁ : (5 : ℝ) ≤ Real.sqrt 26 := by
  apply Real.le_sqrt_of_sq_le <;>
  norm_num
```
In `h₁`, the `<;>` sequence is bad style, and should be removed or replaced with `;`.
However, in the following example, even though the linter generates the same warning, it is in fact unsound to replace `<;>` with `;`.
```
theorem ref : 1 = 1 ∨ False := by
  (try left <;>
    try rfl)
```
-->


<!--
### Unsupported Features

#### `remove_unnecessary_rw_simp_arg`
In `theorem triv : 1 = 1 := by simp [Nat.add_assoc]`, the `Nat.add_assoc` argument is unnecessary and can be removed.

However, the linter is not always correct, which can sometimes result in the simplification being unsound.

#### `replace_unnecessary_simpa`
It's generally seen as bad style to use `simpa` when `simp` would suffice. This generates the linter warning "try 'simp' instead of 'simpa'". However, this doesn't always work, and also I don't really see the benefit in this simplification.

#### `remove_redundant_have`
```
theorem duh (h : 1 + 4 = 5) : 1 = 1 := by
  have h' : 1 + 4 = 5 := h
  have h'' : 1 + 4 = 5 ∨ False := by left; exact h'
  rfl
```
In this theorem, `h'` is obvious -- it's the exact same as `h`, so we should remove it. However, this has not been implemented because it also requires renaming any occurrences of `h'`. This gets a little messy because we are now dealing with local variables, which are not unique (unlike global constants). Punting for now.

-->

## Python API

```python
# Simplify all theorems with all simplifications
result = await axle.simplify_theorems(content=lean_code, environment="lean-4.28.0")

# Simplify specific theorems
result = await axle.simplify_theorems(
    content=lean_code,
    environment="lean-4.28.0",
    names=["complex_theorem"],
)

# Apply only specific simplifications
result = await axle.simplify_theorems(
    content=lean_code,
    environment="lean-4.28.0",
    simplifications=["remove_unused_tactics"],
)

print(result.content)
print(result.simplification_stats)
```

## CLI

**Usage:** `axle simplify-theorems CONTENT [OPTIONS]`

```bash
# Simplify all theorems
axle simplify-theorems complex.lean --environment lean-4.28.0
# Simplify specific theorems
axle simplify-theorems complex.lean --names main_theorem,helper --environment lean-4.28.0
# Apply only specific simplifications
axle simplify-theorems complex.lean --simplifications remove_unused_tactics --environment lean-4.28.0
# Pipeline usage
cat complex.lean | axle simplify-theorems - --environment lean-4.28.0 | axle check - --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/simplify_theorems \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := by rfl <;> rfl", "environment": "lean-4.28.0", "names": ["foo"]}' | jq
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
    "infos": ["simplify_theorems completed in 1 iterations"]
  },
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := by rfl",
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  },
  "simplification_stats": {
    "remove_unused_tactics": 1,
    "rename_unused_vars": 0,
    "remove_unused_haves": 0
  }
}
```
