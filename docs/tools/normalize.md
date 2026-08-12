# normalize

Standardize Lean file formatting to prepare for other operations, especially `merge` operations. Use this tool to detect when a file is unusually structured, in which case other Axle operations may behave unexpectedly.

[Try this example in the web UI](https://axle.axiommath.ai/normalize#data=eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcbm9wZW4gT3B0aW9uXG5cbm5hbWVzcGFjZSB0ZXN0XG5vcGVuIE9wdGlvblxuXG5sZW1tYSBzb21lX2xlbW1hICjOsSA6IFR5cGUpICh4IDogzrEpIDpcbiAgICBPcHRpb24uZ2V0RCAoc29tZSB4KSB4ID0geCA6PSBieVxuICBzaW1wIFtnZXREXVxuXG5lbmQgdGVzdCIsImZhaWxzYWZlIjp0cnVlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

??? "`normalizations` · list[str] · List of normalizations to apply"
    Options: remove_sections, remove_opens, expand_decl_names, expand_scoped_notations, remove_duplicates, split_open_in_commands, normalize_module_comments, normalize_doc_comments. Default: remove_sections, remove_duplicates, split_open_in_commands.

??? "`failsafe` · bool · default: `True` · Return original if normalization fails"
    If true, returns the original content unchanged if normalization introduces errors. Defaults to true.

??? "`delab_options` · dict · Pretty-printer option overrides"
    A dictionary of Lean pretty-printer options (JSON format), applied on top of the options this tool pretty-prints with. Only `pp.*` options are accepted.

    **Why override pretty-printer options?** Pretty-printed output can be ambiguous: the printed form loses information and fails to re-elaborate. Consider this example involving coercions:
    ```
    theorem explicit_coercion_test (n : ℕ) (hn : n > 0) : True := by
      have h : (∑ i : Fin n, (1 : ℝ) / (i.val + 1)) ≤ (harmonic n : ℝ) + 1 := by
        sorry
      trivial
    ```

    With default options, the coercion `(harmonic n : ℝ)` may be pretty-printed as `Rat.cast (harmonic n)`, losing the target type `ℝ`. This causes Lean to fail with errors like "failed to synthesize RatCast ℕ" because it can't infer the correct target type for the coercion. Setting `{"pp.explicit": true}` preserves the target type information and produces valid output.

    This is a known limitation of the Lean pretty-printer (for more details, see [this Zulip thread](https://leanprover.zulipchat.com/#narrow/stream/113488-general/topic/RFC.3A.20printing.20coercions.20with.20type.20ascriptions)).

    For preset buckets of suggested options, see the `verbosity` field (available on some tools).

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

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.); an empty `errors` list means the code compiles.

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`tool_messages` · dict · Messages from normalize tool"
    Messages from the normalize tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`content` · string · The normalized Lean code"
    The standardized code. May be identical to input if `failsafe` triggered.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.

??? "`normalize_stats` · dict · Count of each normalization applied"
    Maps normalization names to counts (e.g., `{"remove_sections": 2}`).


## Available Normalizations

??? "`remove_sections`"
    Removes `section`, `namespace`, and `end` commands. Declaration names are fully qualified to preserve semantics. If a `noncomputable section` is removed, `noncomputable section` is re-inserted at the top of the file to preserve semantics.

    **Before:**
    ```lean
    namespace MyNamespace
    noncomputable section MySection

    theorem foo : 1 = 1 := rfl

    end MySection
    end MyNamespace
    ```

    **After:**
    ```lean
    noncomputable section
    theorem MyNamespace.foo : 1 = 1 := rfl
    ```

??? "`remove_opens`"
    Removes `open` commands, both standalone commands and `open ... in` prefixes (including nested chains like `open A in open B in ...`). An `open` that sits behind a non-`open` command (e.g. `def foo := 1 in open A`) is kept unchanged, with a tool warning.

    Removing `open` commands changes how names and notations resolve, so combine this with `expand_decl_names` and `expand_scoped_notations`; a tool warning is emitted when either is missing.

    **Before:**
    ```lean
    open Nat
    theorem foo : Nat.succ 0 = 1 := rfl

    open List in
    theorem bar : List.isEmpty ([] : List Nat) = Bool.true := rfl
    ```

    **After:**
    ```lean
    theorem foo : Nat.succ 0 = 1 := rfl

    theorem bar : List.isEmpty ([] : List Nat) = Bool.true := rfl
    ```

??? "`expand_decl_names`"
    Fully qualifies declaration names by prepending all enclosing namespaces. Useful for making declarations unambiguous without relying on namespace context.

    **Before:**
    ```lean
    open Option
    example (α : Type) (x : α) :
        Option.getD (some x) x = x := by
      simp [getD]
    ```

    **After:**
    ```lean
    open Option
    example (α : Type) (x : α) :
        Option.getD (Option.some x) x = x := by
      simp [Option.getD]
    ```

??? "`expand_scoped_notations`"
    Expands scoped notations (those brought in by `open`) into their underlying applications. This runs Lean's delaborator with notations disabled, so the expanded form uses function application. Combined with `expand_decl_names`, constant names in the output are fully qualified.

    Note: inside an expanded notation, all nested notations are stripped — including globals like +. This expander can be over-aggressive for notations whose body contains other, non-scoped notations.

    Note: the delaborator isn't guaranteed to round-trip cleanly — coercions, universe annotations, and a few other constructs are known trouble spots and may produce output that doesn't re-elaborate. Uncommon in practice, but keep `failsafe` on if correctness matters.

    **Before:**
    ```lean
    namespace MyNS
    scoped infix:65 " ⊹ " => HAdd.hAdd
    end MyNS

    open MyNS

    def x : Nat := (1 ⊹ 2) + 3
    ```

    **After:**
    ```lean
    namespace MyNS
    scoped infix:65 " ⊹ " => HAdd.hAdd
    end MyNS

    open MyNS

    def x : Nat := ( HAdd.hAdd  1  2 ) + 3
    ```

??? "`remove_duplicates`"
    Removes duplicate commands, such as repeated `open` statements for the same module.

    **Before:**
    ```lean
    open Nat
    open Nat
    open List
    ```

    **After:**
    ```lean
    open Nat
    open List
    ```

??? "`split_open_in_commands`"
    Splits `open [modules] in [decl]` syntax into separate `open` and declaration commands. This makes the structure more explicit and easier to process.

    **Before:**
    ```lean
    open Nat in
    theorem foo : succ 0 = 1 := rfl
    ```

    **After:**
    ```lean
    open Nat
    theorem foo : succ 0 = 1 := rfl
    ```

??? "`normalize_module_comments`"
    Converts module documentation comments (`/-! ... -/`) into regular block comments (`/- ... -/`). Module comments are typically used for file-level documentation.

??? "`normalize_doc_comments`"
    Converts documentation comments (`/-- ... -/`) into regular block comments (`/- ... -/`). Doc comments are typically attached to declarations to provide API documentation.

## Python API

```python
result = await axle.normalize(
    content=lean_code,
    environment="lean-4.28.0",
    normalizations=["remove_sections", "expand_decl_names"],  # Optional: specify which normalizations
    failsafe=True,  # Optional: return original if normalization fails
)
print(result.content)
print(result.normalize_stats)
```

## CLI

**Usage:** `axle normalize CONTENT [OPTIONS]`

```bash
# Normalize a file
axle normalize theorem.lean --environment lean-4.31.0
# Normalize and save to file
axle normalize theorem.lean -o normalized.lean --environment lean-4.31.0
# Apply only specific normalizations
axle normalize theorem.lean --normalizations remove_sections,expand_decl_names --environment lean-4.31.0
# Pipeline usage
cat theorem.lean | axle normalize - --environment lean-4.31.0 | axle merge - other.lean --environment lean-4.31.0
# Disable failsafe to always return normalized output
axle normalize theorem.lean --no-failsafe --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/normalize \
    -d '{"content": "import Mathlib\nsection\ntheorem foo : 1 = 1 := rfl\nend", "environment": "lean-4.28.0"}' | jq
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
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl\n",
  "timings": {
    "total_ms": 92,
    "parse_ms": 87
  },
  "normalize_stats": {
    "remove_sections": 2
  }
}
```
