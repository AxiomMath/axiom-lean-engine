# extract_decls

Split a file containing one or more declarations into smaller units, each containing a single declaration along with any required dependencies. Unlike extract_theorems, this works for all declaration kinds (def, theorem, lemma, abbrev, instance, structure, etc.).

[Try this example in the web UI](https://axle.axiommath.ai/extract_decls#data=eyJjb250ZW50Ijoic3RydWN0dXJlIFdlaWdodCB3aGVyZVxuICB2YWwgOiBOYXRcbiAgcG9zIDogdmFsID4gMCA6PSBieSBvbWVnYVxuXG5jbGFzcyBXZWlnaHRlZCAozrEgOiBUeXBlKSB3aGVyZVxuICB3ZWlnaHQgOiDOsSDihpIgV2VpZ2h0XG5cbmRlZiB0cml2aWFsV2VpZ2h0IDogV2VpZ2h0IDo9IOKfqDEsIGJ5IG9tZWdh4p+pXG5cbmluc3RhbmNlIDogV2VpZ2h0ZWQgTmF0IHdoZXJlXG4gIHdlaWdodCBfIDo9IHRyaXZpYWxXZWlnaHQiLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjguMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

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
    Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 900 seconds (15 minutes).


## Output Fields

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from extraction tool"
    Messages from the extraction tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`documents` · dict · Declaration names mapped to self-contained documents"
    Dictionary mapping declaration names to self-contained Lean code documents. Each key is a declaration name, and the value is a self-contained breakdown of the declaration, including a content field containing that declaration plus all dependencies it needs (imports, definitions, etc.).

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Document Fields

Each document in the `documents` dictionary contains:

!!! note "Field applicability"
    Not all fields are meaningful for all declaration kinds. For example, `proof_length` and `tactic_counts` are only relevant for theorems/lemmas with tactic proofs. For other declaration kinds (def, abbrev, structure, class, inductive, etc.), these fields may be empty or zero.

??? "`kind` · str · The kind of declaration"
    The kind of the declaration. For `extract_theorems`, this is always `"theorem"`. For `extract_decls`, possible values are: `theorem`, `def`, `abbrev`, `axiom`, `opaque`, `structure`, `class`, `class inductive`, `inductive`, `instance`, `example`, `unknown`.

??? "`declaration` · str · The declaration source code"
    The raw source code of this declaration.

??? "`content` · str · Standalone content including declaration and dependencies"
    Complete, self-contained Lean code that includes the declaration and all its local dependencies. Can be compiled independently.

??? "`tokens` · list[str] · Raw tokens from the declaration"
    The declaration's source code split into tokens.

??? "`signature` · str · Declaration signature (everything before the body)"
    The declaration signature, e.g., `theorem foo (x : Nat) : x = x` or `def bar : Nat`.

??? "`type` · str · Pretty-printed type of the declaration"
    The type of the declaration as pretty-printed by Lean.

??? "`type_hash` · int · Hash of the canonical type expression"
    Hash of the canonical, alpha-invariant type expression. Useful for deduplication.

??? "`is_sorry` · bool · Whether the declaration contains a sorry"
    True if the declaration contains a `sorry`.

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

??? "`local_type_dependencies` · list[str] · Transitive local dependencies of the type"
    Local declarations that the declaration's type depends on (non-transitive).

??? "`local_value_dependencies` · list[str] · Transitive local dependencies of the body"
    Local declarations that the declaration's body/proof depends on (non-transitive).

??? "`external_type_dependencies` · list[str] · Immediate external dependencies of the type"
    External constants (builtins, imports) that appear in the type.

??? "`external_value_dependencies` · list[str] · Immediate external dependencies of the body"
    External constants (builtins, imports) that appear in the body/proof.

??? "`local_syntactic_dependencies` · list[str] · Local constants explicitly written in source"
    Local constants that appear literally in source (not from notation/macro expansion).

??? "`external_syntactic_dependencies` · list[str] · External constants explicitly written in source"
    External constants that appear literally in source (not from notation/macro expansion).

??? "`declaration_messages` · dict · Messages specific to this declaration"
    Lean messages (`errors`, `warnings`, `infos`) specific to this declaration in the original document.

??? "`theorem_messages` · dict · (Deprecated) Messages specific to this declaration"
    Lean messages (`errors`, `warnings`, `infos`) specific to this declaration. For `extract_theorems`, this contains the same data as `declaration_messages`. For `extract_decls`, this is always empty.

    !!! warning "Deprecated"
        This field is deprecated. Use `declaration_messages` instead for new code.

## Python API

```python
result = await axle.extract_decls(
    content="import Mathlib\ndef foo : Nat := 1\ntheorem bar : foo = 1 := rfl",
    environment="lean-4.28.0",
    ignore_imports=False,  # Optional
    timeout_seconds=120,   # Optional
)

print(result.content)  # The processed Lean code
for name, doc in result.documents.items():
    print(f"{name}: {doc.declaration}")
```

## CLI

**Usage:** `axle extract-decls CONTENT [OPTIONS]`

```bash
# Extract to default directory
axle extract-decls combined.lean --environment lean-4.28.0
# Extract to custom directory
axle extract-decls combined.lean -o my_decls/ --environment lean-4.28.0
# Force overwrite
axle extract-decls combined.lean -o my_decls/ -f --environment lean-4.28.0
# Pipeline usage
cat combined.lean | axle extract-decls - -o output/ --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/extract_decls \
    -d '{"content": "import Mathlib\ndef foo : Nat := 1\ntheorem bar : foo = 1 := rfl", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "content": "import Mathlib\ndef foo : Nat := 1\ntheorem bar : foo = 1 := rfl",
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
      "kind": "def",
      "declaration": "def foo : Nat := 1",
      "content": "import Mathlib\n\ndef foo : Nat := 1",
      "tokens": ["def", "foo", ":", "Nat", ":=", "1"],
      "signature": "def foo : Nat",
      "type": "ℕ",
      "type_hash": 421340980,
      "is_sorry": false,
      "index": 0,
      "line_pos": 2,
      "end_line_pos": 2,
      "proof_length": 1,
      "tactic_counts": {},
      "local_value_dependencies": [],
      "local_type_dependencies": [],
      "external_value_dependencies": ["OfNat.ofNat", "Nat", "instOfNatNat"],
      "external_type_dependencies": ["Nat"],
      "local_syntactic_dependencies": [],
      "external_syntactic_dependencies": ["Nat"],
      "theorem_messages": {"errors": [], "warnings": [], "infos": []},
      "declaration_messages": {"errors": [], "warnings": [], "infos": []}
    },
    "bar": {
      "kind": "theorem",
      "declaration": "theorem bar : foo = 1 := rfl",
      "content": "import Mathlib\n\ndef foo : Nat := 1\n\ntheorem bar : foo = 1 := rfl",
      "tokens": ["theorem", "bar", ":", "foo", "=", "1", ":=", "rfl"],
      "signature": "theorem bar : foo = 1",
      "type": "foo = 1",
      "type_hash": 254164366,
      "is_sorry": false,
      "index": 1,
      "line_pos": 3,
      "end_line_pos": 3,
      "proof_length": 1,
      "tactic_counts": {},
      "local_value_dependencies": ["foo"],
      "local_type_dependencies": ["foo"],
      "external_value_dependencies": ["rfl", "Nat"],
      "external_type_dependencies": ["Eq", "Nat", "OfNat.ofNat", "instOfNatNat"],
      "local_syntactic_dependencies": ["foo"],
      "external_syntactic_dependencies": ["rfl"],
      "theorem_messages": {"errors": [], "warnings": [], "infos": []},
      "declaration_messages": {"errors": [], "warnings": [], "infos": []}
    }
  }
}
```
