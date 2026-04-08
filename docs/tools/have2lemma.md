# have2lemma

Extract `have` statements from proofs and convert them into standalone lemmas.

[Try this example in the web UI](https://axle.axiommath.ai/have2lemma#data=eyJjb250ZW50IjoidGhlb3JlbSBvdXRlciA6IDEgPSAxIDo9IGJ5XG4gIGhhdmUgaW5uZXIgOiAyID0gMiA6PSBieVxuICAgIGhhdmUgbmVzdGVkIDogMyA9IDMgOj0gYnkgcmZsXG4gICAgcmZsXG4gIHJmbCIsImluY2x1ZGVfaGF2ZV9ib2R5Ijp0cnVlLCJpbmNsdWRlX3dob2xlX2NvbnRleHQiOnRydWUsInJlY29uc3RydWN0X2NhbGxzaXRlIjp0cnVlLCJ2ZXJib3NpdHkiOjAsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

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

??? "`include_have_body` · bool · default: `False` · Include proof bodies in extracted lemmas"
    If `true`, extracted lemmas include the original proof. If `false`, they use `sorry` as placeholder. Defaults to false.

??? "`include_whole_context` · bool · default: `True` · Include whole context when extracting"
    If `true`, lemmas include all context variables. If `false`, attempts to minimize the context. Defaults to true.

??? "`reconstruct_callsite` · bool · default: `False` · Replace have statement with lemma call"
    If `true`, the original `have` is replaced with a call to the extracted lemma. Defaults to false.

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
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 900 seconds (15 minutes).


## Output Fields

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from have2lemma tool"
    Messages from the have2lemma tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · Lean code with have statements extracted as lemmas"
    The code with `have` statements lifted to top-level lemmas. Original theorems may reference these new lemmas.

??? "`lemma_names` · list · Names of newly created lemmas"
    Names are auto-generated based on the parent theorem.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.have2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    names=["main_theorem"],         # Optional
    include_have_body=False,        # Optional: use sorry instead
    include_whole_context=True,     # Optional
    reconstruct_callsite=False,     # Optional
    verbosity=0,                    # Optional: 0-2
)
print(result.content)
print(result.lemma_names)  # ["main_theorem.h1", "main_theorem.h2"]
```

## CLI

**Usage:** `axle have2lemma CONTENT [OPTIONS]`

```bash
# Extract all have statements
axle have2lemma theorem.lean --environment lean-4.28.0
# Extract from specific theorems
axle have2lemma theorem.lean --names main_proof,helper --environment lean-4.28.0
# Include proof bodies in extracted lemmas
axle have2lemma theorem.lean --include-have-body --environment lean-4.28.0
# Reconstruct callsites (replace have with lemma call)
axle have2lemma theorem.lean --reconstruct-callsite --environment lean-4.28.0
# Skip context cleanup
axle have2lemma theorem.lean --no-include-whole-context --environment lean-4.28.0
# Pipeline usage
cat theorem.lean | axle have2lemma - --environment lean-4.28.0 | axle check - --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/have2lemma \
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
  "content": "import Mathlib\n\nlemma foo.h1 : 1 = 1 := sorry\n\nlemma foo.h2 (h1 : 1 = 1) : 2 = 2 := sorry\n\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\n  have h1 : 1 = 1 := by rfl\n  have h2 : 2 = 2 := by rfl\n  exact ⟨h1, h2⟩",
  "lemma_names": ["foo.h1", "foo.h2"],
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}
```

## Demo

There are a lot of configurable options for `have2lemma`. Let's go through them and discuss why they exist.

### Options

There are three main options to discuss:

- `include_have_body`: Whether to include have bodies in extracted lemmas. If false, lemmas will use `sorry` instead. Defaults to false.
- `include_whole_context`: Whether to include the whole context (skip cleanup) when extracting have statements. Defaults to true.
- `reconstruct_callsite`: Whether to reconstruct the callsite (replace have statement with lemma call). Defaults to false.

#### Default behavior

Let's look at the simple following example.
```
theorem example_theorem (p q r : Prop) : p ∧ r → p ∨ q := by
  intro hpr
  have h1 : p := by simp_all
  have h2 : r := by simp_all
  left
  assumption
```
The default behavior sets `include_have_body=false`, `include_whole_context=true`, and `reconstruct_callsite=false`, giving us
```
lemma example_theorem.h1 (p q r : Prop) (hpr : p ∧ r) : p := sorry

lemma example_theorem.h2 (p q r : Prop) (hpr : p ∧ r) (h1 : p) : r := sorry

theorem example_theorem (p q r : Prop) : p ∧ r → p ∨ q := by
  intro hpr
  have h1 : p := by simp_all
  have h2 : r := by simp_all
  left
  assumption
```
Here,

- both generated lemmas are sorried out -- this is the result of `include_have_body=false`.
- in both lemmas, the entire local context is provided, which is the result of `include_whole_context=true`. This might include redundant variables -- in this case, `q` isn't relevant to the goal.
- the main theorem is left unchanged -- this is the result of `reconstruct_callsite=false`.

#### `include_have_body`

Let's see what happens if we set this value to true:
```
lemma example_theorem.h1 (p q r : Prop) (hpr : p ∧ r) : p := by simp_all

lemma example_theorem.h2 (p q r : Prop) (hpr : p ∧ r) (h1 : p) : r := by simp_all
```
The output now includes the proof body!

**Why bother making this configurable?**

This option is NOT guaranteed to be robust, and might introduce errors into the file. In this example:
```
theorem complex_types : ∀ (n : Nat), n + 0 = n := by
  intro n
  have base : 0 + 0 = 0 := by rfl
  have step : ∀ m, m + 0 = m → (m + 1) + 0 = m + 1 := by
    intro m ih
    rfl
  sorry
```
the second generated lemma is
```
lemma complex_types.step : ∀ (n : ℕ), 0 + 0 = 0 → ∀ (m : ℕ), m + 0 = m → m + 1 + 0 = m + 1 := by
    intro m ih
    rfl
```
**This does not compile!!!** Notice that Lean has decided to revert `n` in the type. This means the proof will fail, because there is a missing `intro n ...`.

#### `include_whole_context`

Now let's set this option to false. In our original example, this gives us:
```
lemma example_theorem.h1 (p r : Prop) (hpr : p ∧ r) : p := sorry
lemma example_theorem.h2 (p r : Prop) (hpr : p ∧ r) (h1 : p) : r := sorry
```

Notice that the tool has now removed the `q` variable from both lemmas, as it is irrelevant to the goal and hypotheses.

**Why make this configurable?**

In general, Lean's dependency analysis is purely based on heuristics. See the source:

> A variable is *relevant* if (1) it occurs in the target type, (2) there is a relevant variable that depends on it, or (3) the type of the variable is a proposition that depends on a relevant variable.

Therefore, it's possible that a hypothesis in the context is useful even though Lean judges it to be irrelevant. In rare cases, it can break the proof when used in conjunction with `include_have_body=true`. For example:
```
theorem foo : Odd 5 ∨ Even 5 := by
  have odd : Odd 5 := by exists 2
  have sol : Odd 5 ∨ Even 5 := by
    left
    assumption
  exact sol
```
When running with `include_have_body=true` and `include_whole_context=false`, the tool will output the lemmas
```
lemma foo.odd : Odd 5 := by exists 2

lemma foo.sol : Odd 5 ∨ Even 5 := by
    left
    assumption
```
Notably, in the second lemma, Lean judged the hypothesis `odd` as irrelevant -- no good! The proof body now breaks on `assumption`.

#### `reconstruct_callsite`

Our final option is the most intricate. Let's try enabling this option:
```
...

theorem example_theorem (p q r : Prop) : p ∧ r → p ∨ q := by
  intro hpr
  have h1 : p := example_theorem.h1 p q r hpr
  have h2 : r := example_theorem.h2 p q r hpr h1
  left
  assumption
```
Here, in the main theorem, we removed the body of the have statement, replacing it with an application of the lemmas we just generated!

**Why make this configurable?**

Let's make a very small change to our original proof. Instead of running `intro hpr`, we'll have Lean generate the name for us, and just run `intros`.
```
theorem example_theorem (p q r : Prop) : p ∧ r → p ∨ q := by
  intros
  have h1 : p := by simp_all
  ...
```
Now we'll run `have2lemma` again.
```
lemma example_theorem.h1 (p q r : Prop) (a : p ∧ r) : p := sorry

lemma example_theorem.h2 (p q r : Prop) (a : p ∧ r) (h1 : p) : r := sorry

theorem example_theorem (p q r : Prop) : p ∧ r → p ∨ q := by
  intros
  have h1 : p := sorry /- try using example_theorem.h1 here -/
  have h2 : r := sorry /- try using example_theorem.h2 here -/
  left
  assumption
```
Uh oh. What happened? Notice that when we run `intros`, we introduce a new hypothesis with type `p ∧ r` -- but we haven't given it a name! This means we can't ever refer to it explicitly (i.e., it is *inaccessible*). (This is a Lean quirk which can be disabled, but hygienic names are generally a good thing.) `have2lemma` automatically generated the name `a` in the lemmas, but we can't assign anything to it -- so our tool complains that we've encountered an inaccessible variable, and gives up.

### Verbosity

The `verbosity` parameter controls how explicit the pretty-printer is when generating lemma signatures. Higher verbosity levels produce more explicit output, which can help avoid ambiguity in complex type situations.

- `verbosity=0` (default): Standard pretty-printing options
- `verbosity=1`: Robust options with additional explicitness
- `verbosity=2`: Extra robust options with maximum explicitness

#### When to use higher verbosity

Consider this example involving coercions:
```
theorem explicit_coercion_test (n : ℕ) (hn : n > 0) : True := by
  have h : (∑ i : Fin n, (1 : ℝ) / (i.val + 1)) ≤ (harmonic n : ℝ) + 1 := by
    sorry
  trivial
```

With default verbosity (`verbosity=0`), the coercion `(harmonic n : ℝ)` may be pretty-printed as `Rat.cast (harmonic n)`, losing the target type `ℝ`. This causes Lean to fail with errors like "failed to synthesize RatCast ℕ" because it can't infer the correct target type for the coercion.

With `verbosity=2`, the pretty-printer uses `pp.explicit=true`, which preserves the target type information and produces a valid lemma signature.

**Rule of thumb:** If you encounter type inference errors in generated lemmas—especially involving coercions, casts, or polymorphic functions—try increasing the verbosity level.

Do note that at `verbosity=2`, type signatures may become incredibly complex and unreadable, so it should be used sparingly.

### Summary

These configuration options provide some flexibility around usage, at the cost of correctness in some cases. Try to keep this in mind when generating bug reports -- some of these errors aren't fixable without significant effort.
