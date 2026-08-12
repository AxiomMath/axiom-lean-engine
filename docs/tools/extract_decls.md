# extract_decls

Split a file containing one or more declarations into smaller units, each containing a single declaration along with any required dependencies. This is the replacement for the deprecated [`extract_theorems`](extract_theorems.md) tool, and works for all declaration kinds (def, theorem, lemma, abbrev, instance, structure, etc.).

[Try this example in the web UI](https://axle.axiommath.ai/extract_decls#data=eyJjb250ZW50Ijoic3RydWN0dXJlIFdlaWdodCB3aGVyZVxuICB2YWwgOiBOYXRcbiAgcG9zIDogdmFsID4gMCA6PSBieSBvbWVnYVxuXG5jbGFzcyBXZWlnaHRlZCAozrEgOiBUeXBlKSB3aGVyZVxuICB3ZWlnaHQgOiDOsSDihpIgV2VpZ2h0XG5cbmRlZiB0cml2aWFsV2VpZ2h0IDogV2VpZ2h0IDo9IOKfqDEsIGJ5IG9tZWdh4p+pXG5cbmluc3RhbmNlIDogV2VpZ2h0ZWQgTmF0IHdoZXJlXG4gIHdlaWdodCBfIDo9IHRyaXZpYWxXZWlnaHQiLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjguMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D)

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

??? "`verbosity` · float · default: `0` · Pretty-printer verbosity level (0-2)"
    Preset buckets of pretty-printer options, addressing the ambiguity problem described under `delab_options`:

    - `verbosity=0` (default): Standard pretty-printing options
    - `verbosity=1`: Robust options with additional explicitness
    - `verbosity=2`: Extra robust options with maximum explicitness (e.g. `pp.explicit=true`)

    **Rule of thumb:** If you encounter type inference errors in the output—especially involving coercions, casts, or polymorphic functions—try increasing the verbosity level. Do note that at `verbosity=2`, type signatures may become incredibly complex and unreadable, so it should be used sparingly.

    For finer-grained control over individual pretty-printer options, see `delab_options`, whose overrides apply on top of this preset.

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

??? "`elaborate_proofs` · bool · default: `True` · Elaborate theorem proofs"
    If `true` (default), proofs are fully elaborated. Set to `false` to replace every theorem proof with `sorry` before elaboration (a large speedup on proof-heavy files). Statement-level fields and all fields of non-theorem declarations are unaffected.

    When `false`, emits a `tool_messages` warning and:

    - These fields are empty — do not use them: `content`; for theorems `is_sorry`, `term_depth`, `local_value_dependencies`, `external_value_dependencies`.
    - These fields are incomplete — use with caution: `lean_messages`, `declaration_messages`; for theorems `local_syntactic_dependencies`, `external_syntactic_dependencies`, `wall_ms`, `heartbeats`.

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
result = await axle.extract_decls(
    content="import Mathlib\ndef foo : Nat := 1\ntheorem bar : foo = 1 := rfl",
    environment="lean-4.28.0",
    ignore_imports=True,  # Optional
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
axle extract-decls combined.lean --environment lean-4.31.0
# Extract to custom directory
axle extract-decls combined.lean -o my_decls/ --environment lean-4.31.0
# Force overwrite
axle extract-decls combined.lean -o my_decls/ -f --environment lean-4.31.0
# Pipeline usage
cat combined.lean | axle extract-decls - -o output/ --environment lean-4.31.0
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
      "type_depth": 0,
      "term_depth": 3,
      "is_sorry": false,
      "index": 0,
      "line_pos": 2,
      "end_line_pos": 2,
      "proof_length": 1,
      "tactic_counts": {},
      "wall_ms": 1,
      "heartbeats": 3,
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
      "type_depth": 4,
      "term_depth": 4,
      "is_sorry": false,
      "index": 1,
      "line_pos": 3,
      "end_line_pos": 3,
      "proof_length": 1,
      "tactic_counts": {},
      "wall_ms": 1,
      "heartbeats": 5,
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
