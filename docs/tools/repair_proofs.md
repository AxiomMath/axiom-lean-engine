# repair_proofs

Attempt to repair broken theorem proofs. Available repairs:

- `remove_extraneous_tactics` — truncate trailing tactics after the proof closes
- `apply_terminal_tactics` — try terminal tactics in place of `sorry`
- `replace_unsafe_tactics` — replace `native_decide` with `decide +kernel`
- `remove_unknown_options` — strip `set_option` commands referencing an unknown option
- `enable_autoImplicit` — set `autoImplicit true` when a command needs auto-implicit binders
- `relax_defeq_transparency` — set `backward.isDefEq.respectTransparency false` when a command fails due to improper reducibility/transparency settings for implicit arguments (Lean ≥ 4.29 only)

If `repairs` is omitted, all of the above run. Pass an explicit list to limit which apply. See "Available Repairs" below for details on each pass.

**Note on malformed commands:** Lean's parser silently discards source it cannot parse as a command (e.g., a stray `#fake_command`). Such text is dropped during the initial parse and never reaches `repair_proofs`. The reprinted output will not contain it. This is a property of Lean's parser, not `repair_proofs`.

[Try this example in the web UI](https://axle.axiommath.ai/repair_proofs#data=eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcblxudGhlb3JlbSBwYXJhbGxlbF9nb2Fsc19leHRyYW5lb3VzXG4gICh5IDog4oSCKSAoeCA6IOKEnSkgKGggOiB4IOKJpSAyKSA6XG4gIDcgKiAoMyAqIHkgKyAyKSA9IDIxICogeSArIDE0XG4gIOKIpyB4XjIg4omlIDFcbiAgOj0gYnlcbiAgY29uc3RydWN0b3JcbiAgYWxsX2dvYWxzIHNvcnJ5XG4gIGdyaW5kXG4gIHJmbFxuICBzb3JyeSIsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

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
    Requesting a name not found in the code returns an error.
    When `theorems_only` is `false`, these select over all declarations (not just theorems).

??? "`indices` · list[int] · Theorem indices to process"
    Optional list of theorem indices to process (0-based). Supports negative indices:
    `-1` is the last theorem, `-2` is second-to-last, etc.
    If not specified, all theorems are processed.
    When `theorems_only` is `false`, these select over all declarations (not just theorems).

??? "`theorems_only` · bool · default: `True` · Process theorems/lemmas only"
    If `true` (default), only `theorem`/`lemma` declarations are processed. Set to `false` to process all declaration kinds (`def`/`instance`/`abbrev`/`opaque`/etc). When `false`, `names` and `indices` select over all declarations rather than just theorems.

??? "`repairs` · list[str] · default: `['remove_unknown_options', 'enable_autoImplicit', 'relax_defeq_transparency', 'remove_extraneous_tactics', 'apply_terminal_tactics', 'replace_unsafe_tactics']` · List of repairs to apply"
    If not specified, all repairs are applied. See below for available repairs.

??? "`terminal_tactics` · list[str] · default: `['grind']` · Tactics to try for closing goals"
    Used when 'apply_terminal_tactics' repair is applied. Tactics tried in order; stops on first success. Defaults to 'grind'.

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

??? "`tool_messages` · dict · Messages from repair_proofs tool"
    Messages from the repair_proofs tool with `errors`, `warnings`, and `infos` lists.

    Errors here are failed repairs: a repair was detected as necessary, but no successful change could fix it.

??? "`content` · string · Lean code with repair attempts applied"
    Check `okay` to see if repairs succeeded and the repaired code compiles.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.

??? "`repair_stats` · dict · Count of each repair type applied"
    Maps repair names to counts (e.g., `{"apply_terminal_tactics": 2}`).

??? "`okay` · bool · True if all repairs succeed and the repaired code compiles"
    `True` when all repairs succeed and the repaired code compiles; `False` otherwise. A failed repair is when a repair is detected as necessary but no successful change could fix it — e.g. a `sorry` that no terminal tactic could prove, or a `native_decide` that can't be safely replaced. Failed repairs are reported in `tool_messages.errors`.


## Available Repairs

??? "`remove_unknown_options`"
    Strips `set_option` references with an option name Lean doesn't recognize. Bare `set_option` commands are dropped entirely; `set_option ... in <inner>` gets unwrapped to just `<inner>` so the inner declaration / tactic / term is preserved.

    **Bare command — dropped:**
    ```lean
    import Mathlib

    set_option fake_option true

    theorem foo : 1 = 1 := by rfl
    ```
    becomes
    ```lean
    import Mathlib

    theorem foo : 1 = 1 := by rfl
    ```

    **`set_option ... in <decl>` — unwrapped:**
    ```lean
    import Mathlib

    set_option fake_option true in
    theorem foo : 1 = 1 := by rfl
    ```
    becomes
    ```lean
    import Mathlib

    theorem foo : 1 = 1 := by rfl
    ```

??? "`enable_autoImplicit`"
    When a command fails because it relies on auto-implicit binders but `autoImplicit` is disabled in the current scope, this repair prepends `set_option autoImplicit true in` to the command so it elaborates. Note that `autoImplicit` is already on by default, so this only affects code that explicitly turns it off.

??? "`relax_defeq_transparency`"
    Lean 4.29's `backward.isDefEq.respectTransparency` (default `true`) keeps `isDefEq` from unfolding reducible/instance definitions when unifying implicit arguments, breaking proofs that relied on it. Mathlib turns it off per-theorem. Similarly, this repair prepends `set_option backward.isDefEq.respectTransparency false in` when the fix gets the proof further (all errors resolved, or the first error appears later in the source). On environments without the option, the repair is a no-op.

    **Before:**
    ```lean
    import Mathlib

    open Finset in
    theorem pnat_card_Icc (a b : ℕ+) : #(Icc a b) = b + 1 - a := by
      rw [← Nat.card_Icc, ← PNat.map_subtype_embedding_Icc, card_map]
    ```

    **After (Lean ≥ 4.29):**
    ```lean
    import Mathlib

    set_option backward.isDefEq.respectTransparency false in
    open Finset in
    theorem pnat_card_Icc (a b : ℕ+) : #(Icc a b) = b + 1 - a := by
      rw [← Nat.card_Icc, ← PNat.map_subtype_embedding_Icc, card_map]
    ```

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
axle repair-proofs broken.lean --environment lean-4.31.0
# Repair specific theorems
axle repair-proofs broken.lean --names main_theorem,helper --environment lean-4.31.0
# Apply only specific repairs
axle repair-proofs broken.lean --repairs remove_extraneous_tactics --environment lean-4.31.0
# Pipeline usage
cat broken.lean | axle repair-proofs - --environment lean-4.31.0 | axle check - --environment lean-4.31.0
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
    "remove_unknown_options": 0,
    "enable_autoImplicit": 0,
    "remove_extraneous_tactics": 2,
    "apply_terminal_tactics": 0,
    "replace_unsafe_tactics": 0
  },
  "okay": true
}
```
