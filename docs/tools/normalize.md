# normalize

Standardize Lean file formatting to prepare for other operations, especially `merge` operations. Use this tool to detect when a file is unusually structured, in which case other Axle operations may behave unexpectedly.

[Try this example in the web UI](https://axle.axiommath.ai/normalize#data=eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcbm9wZW4gT3B0aW9uXG5cbm5hbWVzcGFjZSB0ZXN0XG5vcGVuIE9wdGlvblxuXG5sZW1tYSBzb21lX2xlbW1hICjOsSA6IFR5cGUpICh4IDogzrEpIDpcbiAgICBPcHRpb24uZ2V0RCAoc29tZSB4KSB4ID0geCA6PSBieVxuICBzaW1wIFtnZXREXVxuXG5lbmQgdGVzdCIsImZhaWxzYWZlIjp0cnVlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

??? "`normalizations` · list[str] · List of normalizations to apply"
    Options: remove_sections, expand_decl_names, remove_duplicates, split_open_in_commands, normalize_module_comments, normalize_doc_comments. Default: remove_sections, remove_duplicates, split_open_in_commands.

??? "`failsafe` · bool · default: `True` · Return original if normalization fails"
    If true, returns the original content unchanged if normalization introduces errors. Defaults to true.

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

??? "`tool_messages` · dict · Messages from normalize tool"
    Messages from the normalize tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

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
axle normalize theorem.lean --environment lean-4.28.0
# Normalize and save to file
axle normalize theorem.lean -o normalized.lean --environment lean-4.28.0
# Apply only specific normalizations
axle normalize theorem.lean --normalizations remove_sections,expand_decl_names --environment lean-4.28.0
# Pipeline usage
cat theorem.lean | axle normalize - --environment lean-4.28.0 | axle merge - other.lean --environment lean-4.28.0
# Disable failsafe to always return normalized output
axle normalize theorem.lean --no-failsafe --environment lean-4.28.0
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
