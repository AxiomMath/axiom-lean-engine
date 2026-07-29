# extract_theorems

!!! warning "Deprecated"
    `extract_theorems` is deprecated and will be removed in a future release. Use [`extract_decls`](extract_decls.md) instead, which supports all declaration kinds (def, theorem, lemma, abbrev, instance, structure, etc.).

Split a file containing one or more theorems into smaller units, each containing a single theorem along with any required dependencies.

[Try this example in the web UI](https://axle.axiommath.ai/extract_theorems#data=eyJjb250ZW50IjoiZGVmIGRvdWJsZSAobiA6IE5hdCkgOiBOYXQgOj0gMiAqIG5cbnRoZW9yZW0gZG91YmxlX2V2ZW4gOiDiiIAgbiA6IE5hdCwg4oiDIGsgOiBOYXQsIGRvdWJsZSBuID0gMiAqIGsgOj0gYnkgc29ycnlcbnRoZW9yZW0gZG91YmxlX3BvcyA6IOKIgCBuIDogTmF0LCBuID4gMCDihpIgZG91YmxlIG4gPiAwIDo9IGJ5IHNvcnJ5IiwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D)

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

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.); an empty `errors` list means the code compiles.

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`tool_messages` · dict · Messages from extraction tool"
    Messages from the extraction tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

    If the tool allows declaration selection and a `names`/`indices` selection is given, elaboration is skipped for the proofs of unselected declarations, so this field reflects only the selected declarations and is otherwise incomplete.

??? "`documents` · dict · Theorem names mapped to self-contained documents"
    Dictionary mapping theorem names to self-contained Lean code documents. Each key is a theorem name, and the value is a self-contained breakdown of the theorem, including a content field containing that theorem plus all dependencies it needs (imports, definitions, etc.).

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Document Fields

Each document in the `documents` dictionary contains:

??? "`kind` · str · The kind of declaration"
    The kind of the declaration. For `extract_theorems`, this is always `"theorem"`. For `extract_decls`, possible values are: `theorem`, `def`, `abbrev`, `axiom`, `opaque`, `structure`, `class`, `class inductive`, `inductive`, `instance`, `example`, `unknown`.

??? "`declaration` · str · The declaration source code"
    The raw source code of this declaration.

??? "`content` · str · Standalone content including declaration and dependencies"
    Complete, self-contained Lean code that includes the declaration and all its local dependencies. Can be compiled independently.

    **Empty** when the request specifies `names` or `indices`. In that mode only the selected declarations are returned and the unselected ones are *not* elaborated (a large speedup), so their transitive dependencies can no longer be computed. A `tool_messages` warning is emitted; all other fields (`type`, dependency lists, `is_sorry`, etc.) are still populated. Call the tool without `names`/`indices` to get the self-contained `content`.

    Also empty when the request sets `elaborate_proofs=false`.

??? "`tokens` · list[str] · Raw tokens from the declaration"
    The declaration's source code split into tokens.

??? "`signature` · str · Declaration signature (everything before the body)"
    The declaration signature, e.g., `theorem foo (x : Nat) : x = x` or `def bar : Nat`.

??? "`type` · str · Pretty-printed type of the declaration"
    The type of the declaration as pretty-printed by Lean.

??? "`type_hash` · int · Hash of the canonical type expression"
    Hash of the canonical, alpha-invariant type expression. Useful for deduplication.

??? "`unfolded_type_hash` · int · Hash after unfolding local elaboration auxiliaries"
    Hash of the type after unfolding module-local elaboration auxiliaries; useful for deduplication.

??? "`type_depth` · int · Structural depth of the type expression"
    The nesting depth of the declaration's type as a Lean expression. This field maxes out at 255.

??? "`term_depth` · int · Structural depth of the value expression"
    The nesting depth of the declaration's value or proof as a Lean expression, or 0 when the declaration has no value. This field maxes out at 255.

    Always `0` for theorems when `elaborate_proofs=false` — do not use it in that mode.

??? "`is_sorry` · bool · Whether the declaration contains a sorry"
    True if the declaration contains a `sorry`.

    Always `false` for theorems when `elaborate_proofs=false` — do not use it in that mode.

??? "`index` · int · 0-based index in original file"
    Position of this declaration in the original file. Note: indices may not be contiguous (mutual definitions share indices).

??? "`line_pos` · int · 1-based line number where declaration starts"
    Line number where the declaration begins.

??? "`end_line_pos` · int · 1-based line number where declaration ends"
    Line number where the declaration ends.

??? "`proof_length` · int · Approximate number of tactics in proof"
    Rough measure of proof complexity based on tactic count. Only meaningful for theorems/lemmas with tactic proofs.

??? "`tactic_counts` · dict[str, int] · Map of tactic names to occurrence counts"
    Breakdown of which tactics are used and how often. Only meaningful for theorems/lemmas with tactic proofs.

??? "`wall_ms` · int · Wall-clock milliseconds to elaborate the command"
    How long this command took to elaborate. This field reports wall-clock time, so it can vary from run to run.

    Incomplete for theorems when `elaborate_proofs=false` — use with caution.

??? "`heartbeats` · int · Heartbeats consumed elaborating the command"
    Lean heartbeats consumed while elaborating this command.

    Incomplete for theorems when `elaborate_proofs=false` — use with caution.

??? "`local_type_dependencies` · list[str] · Local dependencies of the type"
    Local declarations that the declaration's type depends on (non-transitive).

??? "`local_value_dependencies` · list[str] · Local dependencies of the body"
    Local declarations that the declaration's body/proof depends on (non-transitive).

    Empty for theorems when `elaborate_proofs=false` — do not use it in that mode.

??? "`external_type_dependencies` · list[str] · Immediate external dependencies of the type"
    External constants (builtins, imports) that appear in the type.

??? "`external_value_dependencies` · list[str] · Immediate external dependencies of the body"
    External constants (builtins, imports) that appear in the body/proof.

    Empty for theorems when `elaborate_proofs=false` — do not use it in that mode.

??? "`local_syntactic_dependencies` · list[str] · Local constants explicitly written in source"
    Local constants that appear literally in source (not from notation/macro expansion).

    Incomplete for theorems when `elaborate_proofs=false` — use with caution.

??? "`external_syntactic_dependencies` · list[str] · External constants explicitly written in source"
    External constants that appear literally in source (not from notation/macro expansion).

    Incomplete for theorems when `elaborate_proofs=false` — use with caution.

??? "`declaration_messages` · dict · Messages specific to this declaration"
    Lean messages (`errors`, `warnings`, `infos`) specific to this declaration in the original document.

    Incomplete for theorems when `elaborate_proofs=false` — use with caution.

??? "`theorem_messages` · dict · (Deprecated) Messages specific to this declaration"
    Lean messages (`errors`, `warnings`, `infos`) specific to this declaration. For `extract_theorems`, this contains the same data as `declaration_messages`. For `extract_decls`, this is always empty.

    !!! warning "Deprecated"
        This field is deprecated. Use `declaration_messages` instead for new code.

## Python API

```python
result = await axle.extract_theorems(
    content="import Mathlib\ntheorem foo : 1 = 1 := rfl\ntheorem bar : 2 = 2 := rfl",
    environment="lean-4.28.0",
    ignore_imports=True,  # Optional
    timeout_seconds=120,   # Optional
)

print(result.content)  # The processed Lean code
for name, doc in result.documents.items():
    print(f"{name}: {doc.signature}")
    print(f"  Dependencies: {doc.local_value_dependencies}")
```

## CLI

**Usage:** `axle extract-theorems CONTENT [OPTIONS]`

```bash
# Extract to default directory
axle extract-theorems combined.lean --environment lean-4.31.0
# Extract to custom directory
axle extract-theorems combined.lean -o my_theorems/ --environment lean-4.31.0
# Force overwrite
axle extract-theorems combined.lean -o my_theorems/ -f --environment lean-4.31.0
# Pipeline usage
cat combined.lean | axle extract-theorems - -o output/ --environment lean-4.31.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/extract_theorems \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := rfl", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "content": "import Mathlib\ntheorem foo : 1 = 1 := rfl",
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
    "total_ms": 92,
    "parse_ms": 87
  },
  "documents": {
    "foo": {
      "kind": "theorem",
      "declaration": "theorem foo : 1 = 1 := rfl",
      "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl",
      "tokens": ["theorem", "foo", ":", "1", "=", "1", ":=", "rfl"],
      "signature": "theorem foo : 1 = 1",
      "type": "1 = 1",
      "type_hash": 1326858781,
      "type_depth": 5,
      "term_depth": 4,
      "is_sorry": false,
      "index": 0,
      "line_pos": 2,
      "end_line_pos": 2,
      "proof_length": 1,
      "tactic_counts": {},
      "wall_ms": 1,
      "heartbeats": 4,
      "local_value_dependencies": [],
      "local_type_dependencies": [],
      "external_value_dependencies": ["rfl", "Nat", "OfNat.ofNat", "instOfNatNat"],
      "external_type_dependencies": ["Eq", "Nat", "OfNat.ofNat", "instOfNatNat"],
      "local_syntactic_dependencies": [],
      "external_syntactic_dependencies": ["rfl"],
      "theorem_messages": {"errors": [], "warnings": [], "infos": []},
      "declaration_messages": {"errors": [], "warnings": [], "infos": []}
    }
  }
}
```
