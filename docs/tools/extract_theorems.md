# extract_theorems

Split a file containing one or more theorems into smaller units, each containing a single theorem along with any required dependencies.

[Try this example in the web UI](https://axle.axiommath.ai/extract_theorems#data=eyJjb250ZW50IjoiZGVmIGRvdWJsZSAobiA6IE5hdCkgOiBOYXQgOj0gMiAqIG5cbnRoZW9yZW0gZG91YmxlX2V2ZW4gOiDiiIAgbiA6IE5hdCwg4oiDIGsgOiBOYXQsIGRvdWJsZSBuID0gMiAqIGsgOj0gYnkgc29ycnlcbnRoZW9yZW0gZG91YmxlX3BvcyA6IOKIgCBuIDogTmF0LCBuID4gMCDihpIgZG91YmxlIG4gPiAwIDo9IGJ5IHNvcnJ5IiwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D)

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

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

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from extraction tool"
    Messages from the extraction tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`documents` · dict · Theorem names mapped to self-contained documents"
    Dictionary mapping theorem names to self-contained Lean code documents. Each key is a theorem name, and the value is a self-contained breakdown of the theorem, including a content field containing that theorem plus all dependencies it needs (imports, definitions, etc.).

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Document Fields

Each document in the `documents` dictionary contains:

??? "`declaration` · str · The content of this theorem declaration"
    The raw source code of this theorem declaration.

??? "`content` · str · Standalone content including theorem and dependencies"
    Complete, self-contained Lean code that includes the theorem and all its local dependencies. Can be compiled independently.

??? "`tokens` · list[str] · Raw tokens from the theorem"
    The theorem's source code split into tokens.

??? "`signature` · str · Theorem signature (everything before proof body)"
    The theorem signature, e.g., `theorem foo (x : Nat) : x = x`.

??? "`type` · str · Pretty-printed type of the theorem"
    The type of the theorem as pretty-printed by Lean.

??? "`type_hash` · int · Hash of the canonical type expression"
    Hash of the canonical, alpha-invariant type expression. Useful for deduplication.

??? "`is_sorry` · bool · Whether the theorem contains a sorry"
    True if the theorem's proof contains an explicit `sorry`.

??? "`index` · int · 0-based index in original file"
    Position of this theorem in the original file. Note: indices may not be contiguous (mutual definitions share indices).

??? "`line_pos` · int · 1-based line number where theorem starts"
    Line number where the theorem declaration begins.

??? "`end_line_pos` · int · 1-based line number where theorem ends"
    Line number where the theorem declaration ends.

??? "`proof_length` · int · Approximate number of tactics in proof"
    Rough measure of proof complexity based on tactic count.

??? "`tactic_counts` · dict[str, int] · Map of tactic names to occurrence counts"
    Breakdown of which tactics are used and how often.

??? "`local_type_dependencies` · list[str] · Transitive local dependencies of the type"
    Local declarations that the theorem's type depends on (transitively).

??? "`local_value_dependencies` · list[str] · Transitive local dependencies of the proof"
    Local declarations that the theorem's proof depends on (transitively).

??? "`external_type_dependencies` · list[str] · Immediate external dependencies of the type"
    External constants (builtins, imports) that appear in the type.

??? "`external_value_dependencies` · list[str] · Immediate external dependencies of the proof"
    External constants (builtins, imports) that appear in the proof.

??? "`local_syntactic_dependencies` · list[str] · Local constants explicitly written in source"
    Local constants that appear literally in source (not from notation/macro expansion).

??? "`external_syntactic_dependencies` · list[str] · External constants explicitly written in source"
    External constants that appear literally in source (not from notation/macro expansion).

??? "`document_messages` · dict · Messages from standalone document compilation"
    Lean messages (`errors`, `warnings`, `infos`) from compiling the standalone `content`.

??? "`theorem_messages` · dict · Messages specific to this theorem"
    Lean messages (`errors`, `warnings`, `infos`) specific to this theorem declaration.

## Python API

```python
result = await axle.extract_theorems(
    content="import Mathlib\ntheorem foo : 1 = 1 := rfl\ntheorem bar : 2 = 2 := rfl",
    environment="lean-4.28.0",
    ignore_imports=False,  # Optional
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
axle extract-theorems combined.lean --environment lean-4.28.0
# Extract to custom directory
axle extract-theorems combined.lean -o my_theorems/ --environment lean-4.28.0
# Force overwrite
axle extract-theorems combined.lean -o my_theorems/ -f --environment lean-4.28.0
# Pipeline usage
cat combined.lean | axle extract-theorems - -o output/ --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/extract_theorems \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := rfl", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl\n",
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
      "declaration": "theorem foo : 1 = 1 := rfl",
      "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl",
      "tokens": ["theorem", "foo", ":", "1", "=", "1", ":=", "rfl"],
      "signature": "theorem foo : 1 = 1",
      "type": "1 = 1",
      "type_hash": 12345678901234567890,
      "is_sorry": false,
      "index": 0,
      "line_pos": 1,
      "end_line_pos": 1,
      "proof_length": 1,
      "tactic_counts": {},
      "local_value_dependencies": [],
      "local_type_dependencies": [],
      "external_value_dependencies": ["rfl", "Nat", "OfNat.ofNat", "instOfNatNat"],
      "external_type_dependencies": ["Eq", "Nat", "OfNat.ofNat", "instOfNatNat"],
      "local_syntactic_dependencies": [],
      "external_syntactic_dependencies": ["rfl"],
      "document_messages": {"errors": [], "warnings": [], "infos": []},
      "theorem_messages": {"errors": [], "warnings": [], "infos": []}
    }
  }
}
```
