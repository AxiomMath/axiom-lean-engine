"""Metadata for Axle API endpoints used to generate GUI forms."""

from typing import Any, TypedDict


class InputField(TypedDict, total=False):
    """Definition of an input field for an API endpoint."""

    name: str
    type: str  # "text", "textarea", "textarea_list", "list", "dict", "number", "checkbox"
    description: str
    details: str  # Extended description for documentation (supports markdown)
    required: bool
    default: Any
    placeholder: str
    # CLI-specific fields
    cli_positional: (
        int | bool
    )  # Position in args (1, 2, 3...) or False. If True, uses declaration order
    cli_flag: str  # Override flag name (e.g., "--declarations" instead of "--content")
    cli_stdin_support: bool  # Whether this parameter can accept stdin via "-"
    cli_multiple_files: bool  # Whether this accepts multiple file paths (e.g., merge documents)
    cli_dict_inline: bool  # Whether dict can be specified as key=val,key=val format
    cli_dict_file_flag: str  # Flag name for JSON file input (e.g., "--declarations-file")
    cli_hidden: bool  # Don't show in CLI (for fields always passed by the CLI tool itself)
    cli_list_type: str  # Element type for lists: "str" (default) or "int"


class OutputField(TypedDict, total=False):
    """Definition of an output field from an API endpoint."""

    name: str
    type: str  # "bool", "list", "dict", "string", "number"
    description: str
    details: str  # Extended description for documentation (supports markdown)


# REUSABLE INPUT FIELDS

# Content input (Lean code)
CONTENT_INPUT: InputField = {
    "name": "content",
    "type": "textarea",
    "description": "Lean source code",
    "details": "The Lean source code to be processed by this tool.",
    "required": True,
    "placeholder": "theorem foo : 1 = 1 := rfl",
    "cli_positional": 1,
    "cli_stdin_support": True,
}

# Environment selection
ENVIRONMENT_INPUT: InputField = {
    "name": "environment",
    "type": "text",
    "description": "Lean environment or version",
    "details": """\
The Lean environment to use for evaluation. Each environment includes a specific
Lean version and pre-built dependencies (typically Mathlib).

Available environments: `lean-4.28.0`, `lean-4.27.0`, `lean-4.26.0`, etc.""",
    "required": True,
    "placeholder": "lean-4.28.0",
}

# Timeout setting
TIMEOUT_INPUT: InputField = {
    "name": "timeout_seconds",
    "type": "number",
    "description": "Max execution time in seconds",
    "details": """\
Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead. Additionally, all non-admin requests are subject to an absolute maximum timeout of 300 seconds (5 minutes).""",
    "required": False,
    "default": 120,
    "placeholder": "120",
}

# Import handling
IGNORE_IMPORTS_INPUT: InputField = {
    "name": "ignore_imports",
    "type": "checkbox",
    "description": "Ignore import mismatches",
    "details": """\
Controls import statement handling:

- `false` (default): Validate that imports match the environment. Returns an error if they don't.
- `true`: Ignore the imports in `content` and use the environment's default imports instead. See the troubleshooting page for more details.""",
    "default": False,
}

# Theorem selection by name
NAMES_INPUT: InputField = {
    "name": "names",
    "type": "list",
    "description": "Theorem names to process",
    "details": """\
Optional list of theorem names to process. If not specified, all theorems are processed.
Names not found in the code are silently ignored.""",
    "required": False,
    "placeholder": "foo, bar",
}

# Theorem selection by index
INDICES_INPUT: InputField = {
    "name": "indices",
    "type": "list",
    "description": "Theorem indices to process",
    "details": """\
Optional list of theorem indices to process (0-based). Supports negative indices:
`-1` is the last theorem, `-2` is second-to-last, etc.
If not specified, all theorems are processed.""",
    "required": False,
    "placeholder": "0, 1, -1",
    "cli_list_type": "int",
}

# Mathlib linter toggle
MATHLIB_LINTER_INPUT: InputField = {
    "name": "mathlib_linter",
    "type": "checkbox",
    "description": "Enable Mathlib linters",
    "details": "If true, enables Mathlib's standard linter set. Linter messages appear in `lean_messages.warnings`.",
    "default": False,
}

# REUSABLE OUTPUT FIELDS

LEAN_MESSAGES_OUTPUT: OutputField = {
    "name": "lean_messages",
    "type": "dict",
    "description": "Messages from Lean compiler",
    "details": """\
Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
Errors here indicate invalid Lean code (syntax errors, type errors, etc.).""",
}

TIMINGS_OUTPUT: OutputField = {
    "name": "timings",
    "type": "dict",
    "description": "Execution timing breakdown",
    "details": "Timing information in milliseconds for various stages of processing.",
}

CONTENT_OUTPUT: OutputField = {
    "name": "content",
    "type": "string",
    "description": "Processed Lean code",
    "details": "The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.",
}


def tool_messages_output(tool_name: str) -> OutputField:
    """Generate tool_messages output with tool-specific description."""
    return {
        "name": "tool_messages",
        "type": "dict",
        "description": f"Messages from {tool_name} tool",
        "details": f"""\
Messages from the {tool_name} tool with `errors`, `warnings`, and `infos` lists.
Errors here indicate tool-specific issues (not Lean compilation errors).""",
    }


class CliOutputConfig(TypedDict, total=False):
    """Configuration for CLI output behavior."""

    mode: str  # "json_stdout" | "lean_stdout" | "lean_file" | "multiple_files"
    supports_output_file: bool  # Whether to add -o/--output flag
    supports_output_dir: bool  # Whether to add -o/--output-dir flag
    output_dir_default: str  # Default output directory (for extract_theorems)
    output_file_pattern: str  # Pattern for multiple files (e.g., "theorem_{i}.lean")
    metadata_to_stderr: bool  # Whether to write JSON metadata to stderr
    force_flag: bool  # Whether to add -f/--force flag for overwrite


class EndpointMetadata(TypedDict, total=False):
    """Complete metadata for an API endpoint."""

    title: str
    description: str  # One-line summary (used in CLI)
    details: str  # Full description (used in docs)
    inputs: list[InputField]
    outputs: list[OutputField]
    # CLI-specific fields
    cli_output: CliOutputConfig  # Output behavior configuration
    cli_examples: list[str]  # List of example command lines with comments
    # Documentation fields for complete doc generation
    python_example: str  # Python API example code
    http_example: str  # HTTP API curl example
    example_response: str  # JSON response example
    web_ui_example_data: str  # Base64-encoded example data for web UI link
    # Sections dict determines both content and order:
    # - Custom sections: "Title" -> "markdown content"
    # - Built-in sections: "__inputs__" -> True (placeholder, content auto-generated)
    # - Order follows dict key order
    # - If no __xxx__ keys, custom sections render first, then default built-ins
    sections: dict[str, str | bool]


# All Axle API endpoints metadata
ENDPOINTS: dict[str, EndpointMetadata] = {
    "verify_proof": {
        "title": "Verify Proof",
        "details": "Validate a candidate Lean theorem and check that it conforms to the given formal statement.",
        "description": "validate a Lean proof against a formal statement",
        "cli_output": {
            "mode": "json_stdout",
            "metadata_to_stderr": False,
        },
        "cli_examples": [
            "# Basic usage\naxle verify-proof statement.lean proof.lean --environment lean-4.28.0",
            "# With permitted sorries\naxle verify-proof statement.lean proof.lean --permitted-sorries helper1,helper2 --environment lean-4.28.0",
            "# Pipeline usage\ncat proof.lean | axle verify-proof statement.lean - --environment lean-4.28.0",
            "# Exit non-zero if proof is invalid\naxle verify-proof statement.lean proof.lean --strict --environment lean-4.28.0",
            '# Use in shell conditionals\nif axle verify-proof statement.lean proof.lean --strict --environment lean-4.28.0 > /dev/null; then\n    echo "Proof valid"\nfi',
            "# Specify different environment\naxle verify-proof statement.lean proof.lean --environment lean-4.25.1",
        ],
        "web_ui_example_data": "eyJmb3JtYWxfc3RhdGVtZW50IjoiZGVmIEEgOj0gNFxudGhlb3JlbSBtYWluIDogQSA9IDUgOj0gc29ycnkiLCJjb250ZW50IjoiZGVmIEEgOj0gNVxudGhlb3JlbSBtYWluIDogQSA9IDUgOj0gcmZsIiwibWF0aGxpYl9saW50ZXIiOmZhbHNlLCJ1c2VfZGVmX2VxIjp0cnVlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "See Also": """\
In the interest of scalability, `verify_proof` trusts the Lean environment to behave correctly. That's usually fine, but a sufficiently creative adversary can exploit this to make invalid proofs appear valid with Lean metaprogramming.

This is a known limitation that we don't expect to address, since the alternatives below cover adversarial use cases.

If you're verifying untrusted code, consider additionally using these other resources which perform a similar check. These run proofs in isolated environments and are less susceptible to known exploits, at the cost of speed:

- [lean4checker](https://github.com/leanprover/lean4checker): Lean FRO-developed .olean verifier
- [Comparator](https://github.com/leanprover/comparator): Lean FRO-developed gold standard for proof judges
- [SafeVerify](https://github.com/GasStationManager/SafeVerify): battle-tested public proof checker

We recommend reading the [Lean4 reference page on this topic](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) for more discussion.

See the corresponding [Github issue](https://github.com/AxiomMath/axiom-lean-engine/issues/2).""",
            "__inputs__": True,
            "__outputs__": True,
            "Verification Error Messages": """\
`tool_messages.errors` will match one of the following patterns:

| Pattern | Meaning |
|---------|---------|
| `Missing required declaration '{name}'` | A symbol in `formal_statement` is missing from `content` |
| `Kind mismatch for '{name}': candidate has {X} but expected {Y}` | Mismatch between definition kinds (e.g., `theorem` vs `def`) |
| `Theorem '{name}' does not match expected signature: expected {X}, got {Y}` | Type of theorem has been changed |
| `Definition '{name}' does not match expected signature: expected {X}, got {Y}` | Type or value of definition has been changed |
| `Unsafe/partial function '{name}' detected` | Use of a disallowed function |
| `In '{name}': Axiom '{axiom}' is not in the allowed set of standard axioms` | Use of a disallowed axiom |
| `Declaration '{name}' uses 'sorry' which is not allowed in a valid proof` | Theorem is not proven |
| `Candidate uses banned 'open private' command` | Use of disallowed `open private` command |""",
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
        },
        "python_example": """\
result = await axle.verify_proof(
    formal_statement="import Mathlib\\ntheorem citation_needed : 1 = 1 := by sorry",
    content="import Mathlib\\ntheorem citation_needed : 1 = 1 := rfl",
    environment="lean-4.28.0",
    permitted_sorries=["helper"],  # Optional
    mathlib_linter=False,          # Optional
    ignore_imports=False,          # Optional
    timeout_seconds=120,           # Optional
)

print(result.okay)  # True if proof is valid
print(result.content)  # The processed Lean code""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/verify_proof \\
    -d '{"content": "import Mathlib\\ntheorem citation_needed : 1 = 1 := rfl", "formal_statement": "import Mathlib\\ntheorem citation_needed : 1 = 1 := by sorry", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
{
  "okay": false,
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := rfl\\n",
  "lean_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "tool_messages": {
    "errors": [
      "Theorem 'foo' does not match expected signature: expected type 2 = 2, got 1 = 1"
    ],
    "warnings": [],
    "infos": []
  },
  "timings": {
    "total_ms": 160,
    "formal_statement_ms": 3,
    "declarations_ms": 0,
    "candidate_ms": 28
  },
  "failed_declarations": ["foo"]
}""",
        "inputs": [
            {
                "name": "formal_statement",
                "type": "textarea",
                "description": "Sorried theorem to verify against",
                "details": """\
The formal statement defines what the proof must satisfy. It should contain
`sorry` placeholders where proofs are expected. AXLE extracts all declarations
from this and checks that `content` provides valid implementations.

```lean
-- formal_statement: defines the theorem signature
import Mathlib
theorem add_comm (a b : Nat) : a + b = b + a := by sorry
```

```lean
-- content: provides the actual proof
import Mathlib
theorem add_comm (a b : Nat) : a + b = b + a := Nat.add_comm a b
```

Definitions and other declarations are also checked—if `formal_statement`
contains `def foo := 5`, then `content` must define `foo` with the same value.""",
                "required": True,
                "placeholder": "theorem foo : 1 = 1 := by sorry",
                "cli_positional": 1,
                "cli_stdin_support": False,
            },
            {
                **CONTENT_INPUT,
                "description": "Candidate proof to verify",
                "details": "The Lean source code containing the proof(s) to validate against the formal statement.",
                "placeholder": "theorem foo : 1 = 1 := rfl",
                "cli_positional": 2,
            },
            {
                "name": "permitted_sorries",
                "type": "list",
                "description": "Theorems allowed to contain `sorry`",
                "details": """\
Use this when your proof relies on helper lemmas you haven't proven yet.
Theorems listed here won't trigger "uses sorry" errors.

```python
result = await axle.verify_proof(
    formal_statement="...",
    content="...",
    permitted_sorries=["helper_lemma"],
)
```

Names not present in the code are silently ignored.

This option is also useful for enabling tactics like `native_decide`. To do so, simply include the axioms `Lean.trustCompiler`, `Lean.ofReduceBool`, and `Lean.ofReduceNat` in this field.""",
                "required": False,
                "placeholder": "helper_lemma, auxiliary_theorem",
            },
            MATHLIB_LINTER_INPUT,
            {
                "name": "use_def_eq",
                "type": "checkbox",
                "description": "Use definitional equality for type comparison",
                "details": """\
When `true`, types are compared using equality after kernel reduction.

When `false`, types are compared at face value, which is faster but may rarely
reject valid proofs.""",
                "default": True,
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            {
                "name": "okay",
                "type": "bool",
                "description": "True if proof passes verification",
                "details": "Returns `true` if the candidate proof is valid and matches the formal statement. Check `tool_messages.errors` for details when `false`.",
            },
            CONTENT_OUTPUT,
            LEAN_MESSAGES_OUTPUT,
            {
                **tool_messages_output("verify_proof"),
                "details": """\
Messages from the AXLE verification tool with `errors`, `warnings`, and `infos` lists.

Errors here mean `content` was valid Lean code, but not a satisfactory proof of `formal_statement`.
Common errors include: "Missing required declaration", "does not match expected signature", "uses sorry".""",
            },
            {
                "name": "failed_declarations",
                "type": "list",
                "description": "Declaration names that failed validation",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "check": {
        "title": "Check",
        "details": "Evaluate Lean code and collect all messages (errors, warnings, and info). Use this to check if code is valid without verification against a formal statement, or to get the output of `#check` / `#eval` statements.",
        "description": "evaluate Lean code and report all messages",
        "cli_output": {
            "mode": "json_stdout",
            "metadata_to_stderr": False,
        },
        "cli_examples": [
            "# Basic usage\naxle check theorem.lean --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle check - --environment lean-4.28.0",
            "# Exit non-zero if code is invalid\naxle check theorem.lean --strict --environment lean-4.28.0",
            '# Use in shell conditionals\nif axle check theorem.lean --strict --environment lean-4.28.0 > /dev/null; then\n    echo "Valid Lean code"\nfi',
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoiI2NoZWNrIE5hdFxuI2NoZWNrIExpc3RcbiNldmFsIDEgKyAxIiwibWF0aGxpYl9saW50ZXIiOmZhbHNlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "See Also": "For interactive compilation feedback without an API, try the [Lean 4 Web Playground](https://live.lean-lang.org).",
        },
        "python_example": """\
result = await axle.check(
    content="import Mathlib\\n#eval 2+2",
    environment="lean-4.28.0",
    mathlib_linter=False,     # Optional
    ignore_imports=False,     # Optional
    timeout_seconds=120,      # Optional
)

print(result.okay)  # True if code is valid
print(result.content)  # The processed Lean code
print(result.lean_messages.infos)  # ["4\\n"]""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/check \\
    -d '{"content": "import Mathlib\\n#eval 2+2", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
{
  "okay": true,
  "content": "import Mathlib\\n\\n#eval 2+2\\n",
  "lean_messages": {
    "errors": [],
    "warnings": [],
    "infos": ["4\\n"]
  },
  "tool_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "timings": {
    "parse_ms": 30,
    "total_ms": 62
  },
  "failed_declarations": []
}""",
        "inputs": [
            CONTENT_INPUT,
            MATHLIB_LINTER_INPUT,
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            {
                "name": "okay",
                "type": "bool",
                "description": "True if the Lean code is valid",
                "details": "Returns `true` if the code compiles without errors. Warnings don't affect this value.",
            },
            CONTENT_OUTPUT,
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("check"),
            {
                "name": "failed_declarations",
                "type": "list",
                "description": "Declaration names that failed validation",
                "details": "List of declaration names that have compilation or validation errors.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "extract_theorems": {
        "title": "Extract Theorems",
        "details": "Split a file containing one or more theorems into smaller units, each containing a single theorem along with any required dependencies.",
        "description": "split file into separate theorems with dependencies",
        "cli_output": {
            "mode": "multiple_files",
            "supports_output_dir": True,
            "output_dir_default": "extract_theorems/",
            "output_file_pattern": "theorem_{i}.lean",
            "metadata_to_stderr": False,
            "force_flag": True,
        },
        "cli_examples": [
            "# Extract to default directory\naxle extract-theorems combined.lean --environment lean-4.28.0",
            "# Extract to custom directory\naxle extract-theorems combined.lean -o my_theorems/ --environment lean-4.28.0",
            "# Force overwrite\naxle extract-theorems combined.lean -o my_theorems/ -f --environment lean-4.28.0",
            "# Pipeline usage\ncat combined.lean | axle extract-theorems - -o output/ --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoiZGVmIGRvdWJsZSAobiA6IE5hdCkgOiBOYXQgOj0gMiAqIG5cbnRoZW9yZW0gZG91YmxlX2V2ZW4gOiDiiIAgbiA6IE5hdCwg4oiDIGsgOiBOYXQsIGRvdWJsZSBuID0gMiAqIGsgOj0gYnkgc29ycnlcbnRoZW9yZW0gZG91YmxlX3BvcyA6IOKIgCBuIDogTmF0LCBuID4gMCDihpIgZG91YmxlIG4gPiAwIDo9IGJ5IHNvcnJ5IiwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D",
        "sections": {
            "__inputs__": True,
            "__outputs__": True,
            "Document Fields": """\
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
    Lean messages (`errors`, `warnings`, `infos`) specific to this theorem declaration.""",
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
        },
        "python_example": """\
result = await axle.extract_theorems(
    content="import Mathlib\\ntheorem foo : 1 = 1 := rfl\\ntheorem bar : 2 = 2 := rfl",
    environment="lean-4.28.0",
    ignore_imports=False,  # Optional
    timeout_seconds=120,   # Optional
)

print(result.content)  # The processed Lean code
for name, doc in result.documents.items():
    print(f"{name}: {doc.signature}")
    print(f"  Dependencies: {doc.local_value_dependencies}")""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/extract_theorems \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 := rfl", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
{
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := rfl\\n",
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
      "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := rfl",
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
}""",
        "inputs": [
            {
                **CONTENT_INPUT,
                "placeholder": "theorem foo : 1 = 1 := rfl\ntheorem bar : 2 = 2 := rfl",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            CONTENT_OUTPUT,
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("extraction"),
            {
                "name": "documents",
                "type": "dict",
                "description": "Theorem names mapped to self-contained documents",
                "details": """\
Dictionary mapping theorem names to self-contained Lean code documents. Each key is a theorem name, and the value is a self-contained breakdown of the theorem, including a content field containing that theorem plus all dependencies it needs (imports, definitions, etc.).""",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "rename": {
        "title": "Rename Declarations",
        "details": "Rename declarations in Lean code.",
        "description": "rename declarations in Lean code",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Rename using command-line mapping\naxle rename theorem.lean --declarations foo=bar,helper=main_helper --environment lean-4.28.0",
            "# Rename using JSON file\naxle rename theorem.lean --declarations-file mapping.json --environment lean-4.28.0",
            "# Save to file\naxle rename theorem.lean --declarations foo=bar -o renamed.lean --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle rename - --declarations foo=bar --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBoZWxwZXIgOiAxICsgMSA9IDIgOj0gYnkgc2ltcFxuZXhhbXBsZSA6IDIgPSAxICsgMSA6PSBoZWxwZXIuc3ltbVxuXG5uYW1lc3BhY2Ugbm1cblxudGhlb3JlbSBoZWxwZXIgOiAxICsgMSA9IDIgOj0gYnkgc2ltcFxudGhlb3JlbSB0aG0gOiAyID0gMSArIDEgOj0gaGVscGVyLnN5bW1cblxuZW5kIG5tIiwiZGVjbGFyYXRpb25zIjp7ImhlbHBlciI6Im91dHNpZGVfaGVscGVyIiwibm0uaGVscGVyIjoibm0uaW5zaWRlX2hlbHBlciIsIm5tLnRobSI6Im5tLmluc2lkZV90aGVvcmVtIn0sImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9",
        "python_example": """\
result = await axle.rename(
    content="import Mathlib\\ntheorem foo : 1 = 1 := rfl\\ntheorem baz : 1 = 1 := foo",
    declarations={"foo": "bar"},
    environment="lean-4.28.0",
    timeout_seconds=120,  # Optional
)
print(result.content)  # theorem bar : 1 = 1 := rfl""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/rename \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 := rfl\\ntheorem baz : 1 = 1 := foo", "declarations": {"foo": "bar"}, "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem bar : 1 = 1 := rfl\\n\\ntheorem baz : 1 = 1 := bar",
  "timings": {
    "total_ms": 94,
    "parse_ms": 89
  }
}""",
        "sections": {
            "__inputs__": True,
            "__outputs__": True,
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
            "Examples": """\
??? "Basic rename with reference updates"
    Renaming `original` → `renamed` also updates all references:

    **Before:**
    ```lean
    theorem original : 1 + 1 = 2 := by simp
    example : 2 = 1 + 1 := original.symm
    ```

    **After:**
    ```lean
    theorem renamed : 1 + 1 = 2 := by simp
    example : 2 = 1 + 1 := renamed.symm
    ```

??? "Namespaced declarations"
    Use fully qualified names (`ns.original`) to rename declarations inside namespaces:

    **Before:**
    ```lean
    namespace ns
    theorem original : 1 + 1 = 2 := by simp
    example : 2 = 1 + 1 := original.symm
    end ns

    example : 2 = 1 + 1 := ns.original.symm
    ```

    **After** (with `{"ns.original": "ns.renamed"}`):
    ```lean
    namespace ns
    theorem renamed : 1 + 1 = 2 := by simp
    example : 2 = 1 + 1 := renamed.symm
    end ns

    example : 2 = 1 + 1 := ns.renamed.symm
    ```

??? "Renaming inductive types"
    Renaming an inductive type also updates constructor references:

    **Before:**
    ```lean
    inductive enum
    | caseA
    | caseB

    example : enum := enum.caseA
    ```

    **After** (with `{"enum": "caseEnum"}`):
    ```lean
    inductive caseEnum
    | caseA
    | caseB

    example : caseEnum := caseEnum.caseA
    ```""",
        },
        "inputs": [
            CONTENT_INPUT,
            {
                "name": "declarations",
                "type": "dict",
                "description": "Map from old declaration names to new names",
                "details": """\
A dictionary mapping original declaration names to their new names (JSON format).
All references to renamed declarations are updated throughout the code.

CLI supports `key=val,key=val` format or `--declarations-file mapping.json`.""",
                "required": True,
                "placeholder": '{"foo": "bar"}',
                "cli_dict_inline": True,
                "cli_dict_file_flag": "--declarations-file",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("rename"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with renamed declarations",
                "details": "The Lean code with renamed declarations. The transformed code with all specified declarations renamed. References are updated throughout.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "theorem2lemma": {
        "title": "Convert Theorem/Lemma",
        "details": "Convert between `theorem` and `lemma` declaration keywords.",
        "description": "convert between theorem and lemma keywords",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Convert all theorems to lemmas\naxle theorem2lemma theorems.lean --environment lean-4.28.0",
            "# Convert specific theorems by name\naxle theorem2lemma theorems.lean --names foo,bar --environment lean-4.28.0",
            "# Convert to theorem instead\naxle theorem2lemma lemmas.lean --target theorem --environment lean-4.28.0",
            "# Convert first and last theorems\naxle theorem2lemma theorems.lean --indices 0,-1 --environment lean-4.28.0",
            "# Pipeline usage\ncat theorems.lean | axle theorem2lemma - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiAxID0gMSA6PSBieSByZmxcbnRoZW9yZW0gbWFpbiA6IDIgPSAyIDo9IGJ5IHNvcnJ5IiwibmFtZXMiOlsiZm9vIl0sImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9",
        "python_example": """\
# Convert all theorems to lemmas
result = await axle.theorem2lemma(content=lean_code, environment="lean-4.28.0")

# Convert specific theorems by name
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    names=["foo", "bar"],
)

# Convert by index
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    indices=[0, -1],  # first and last
)

# Convert to theorem instead
result = await axle.theorem2lemma(
    content=lean_code,
    environment="lean-4.28.0",
    target="theorem",
)""",
        "http_example": """\
# Convert all to lemmas
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2lemma \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 := rfl\\ntheorem bar : 2 = 2 := rfl", "environment": "lean-4.28.0"}' | jq

# Convert specific theorems by index to theorems
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2lemma \\
    -d '{"content": "import Mathlib\\nlemma foo : 1 = 1 := rfl\\nlemma bar : 2 = 2 := rfl", "environment": "lean-4.28.0", "indices": [0], "target": "theorem"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\nlemma foo : 1 = 1 := rfl\\n\\nlemma bar : 2 = 2 := rfl",
  "timings": {
    "total_ms": 106,
    "parse_ms": 100
  }
}""",
        "inputs": [
            CONTENT_INPUT,
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "target",
                "type": "text",
                "description": "Target keyword (lemma or theorem)",
                "details": "The keyword to convert to. Use `lemma` or `theorem`. Defaults to `lemma`.",
                "required": False,
                "default": "lemma",
                "placeholder": "lemma",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("theorem2lemma"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with updated declaration keywords",
                "details": "The code with `theorem` converted to `lemma` (or vice versa) for the specified declarations.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "theorem2sorry": {
        "title": "Convert to Sorry",
        "details": "Strip proofs from theorems, replacing them with `sorry`.",
        "description": "replace theorem proofs with sorry",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Convert all theorems to sorry\naxle theorem2sorry solution.lean -o problem.lean --environment lean-4.28.0",
            "# Convert specific theorems by name\naxle theorem2sorry solution.lean --names main_theorem,helper --environment lean-4.28.0",
            "# Pipeline usage\ncat solution.lean | axle theorem2sorry - --names main_theorem --environment lean-4.28.0 > problem.lean",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiAxID0gMSA6PSBieSByZmxcbnRoZW9yZW0gbWFpbiA6IDIgPSAyIDo9IGJ5IHJmbCIsIm5hbWVzIjpbIm1haW4iXSwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D",
        "python_example": """\
# Convert all theorems
result = await axle.theorem2sorry(content=lean_code, environment="lean-4.28.0")

# Convert specific theorems by name
result = await axle.theorem2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    names=["foo"],
)

# Convert by index (supports negative indices)
result = await axle.theorem2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    indices=[0, -1],  # first and last
)""",
        "http_example": """\
# Convert specific theorems by name
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2sorry \\
    -d '{"content": "import Mathlib\\ntheorem left_as_exercise : 1 = 1 := rfl\\ntheorem the_tricky_one : 2 = 2 := rfl", "environment": "lean-4.28.0", "names": ["left_as_exercise"]}' | jq

# Convert all theorems
curl -s -X POST https://axle.axiommath.ai/api/v1/theorem2sorry \\
    -d '{"content": "import Mathlib\\ntheorem left_as_exercise : 1 = 1 := rfl\\ntheorem the_tricky_one : 2 = 2 := rfl", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem left_as_exercise : 1 = 1 := sorry\\n\\ntheorem the_tricky_one : 2 = 2 := rfl",
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  }
}""",
        "inputs": [
            CONTENT_INPUT,
            NAMES_INPUT,
            INDICES_INPUT,
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("theorem2sorry"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with proof bodies replaced by sorry",
                "details": "Useful for creating problem templates from solutions.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "merge": {
        "title": "Merge Lean Files",
        "details": "Combine multiple Lean files into a single file.",
        "description": "combine multiple Lean files into a single file",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Merge multiple files to stdout\naxle merge theorem1.lean theorem2.lean theorem3.lean --environment lean-4.28.0",
            "# Merge all .lean files in directory\naxle merge *.lean -o combined.lean --environment lean-4.28.0",
            "# Merge and check\naxle merge *.lean --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJkb2N1bWVudHMiOlsidGhlb3JlbSBEIDogKDEgPSAxIOKIpyAyID0gMikg4oinIFRydWUgOj0gc29ycnlcbnRoZW9yZW0gQiA6IDIgPSAyIDo9IHJmbFxudGhlb3JlbSBBIDogMSA9IDEgOj0gc29ycnlcbnRoZW9yZW0gQyA6IDEgPSAxIOKIpyAyID0gMiA6PSDin6hBLCBC4p%2BpIiwidGhlb3JlbSBBIDogMSA9IDEgOj0gcmZsXG50aGVvcmVtIEMgOiAxID0gMSDiiKcgMiA9IDIgOj0g4p%2BoQSwgQeKfqSAtLSBpbmNvcnJlY3RcbnRoZW9yZW0gRCA6ICgxID0gMSDiiKcgMiA9IDIpIOKIpyBUcnVlIDo9IOKfqEMsIHRyaXZpYWzin6lcbnRoZW9yZW0gQiA6IDIgPSAyIDo9IHNvcnJ5Il0sInVzZV9kZWZfZXEiOnRydWUsImluY2x1ZGVfYWx0c19hc19jb21tZW50cyI6ZmFsc2UsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9",
        "python_example": """\
result = await axle.merge(
    documents=[code1, code2, code3],
    environment="lean-4.28.0",
    use_def_eq=True,                  # Optional
    include_alts_as_comments=False,   # Optional
    timeout_seconds=120,              # Optional
)
print(result.content)""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/merge \\
    -d '{"documents": ["import Mathlib\\ntheorem foo : 1 = 1 := rfl", "import Mathlib\\ntheorem bar : 2 = 2 := rfl"], "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := rfl\\n\\ntheorem bar : 2 = 2 := rfl",
  "timings": {
    "total_ms": 105,
    "parse_ms": 95
  }
}""",
        "sections": {
            "__inputs__": True,
            "__outputs__": True,
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
            "Demo": """\
This merge function is intended to be a consolidation of multiple Lean files that performs best-effort deduplication and conflict resolution. As a demonstration, we'll merge the following two files, with descriptions of features along the way.

### File 1
```
import Mathlib

open Lean

theorem D : (1 = 1 ∧ 2 = 2) ∧ True := rfl
theorem A : 2 = 2 := rfl

variable (x : Nat)
theorem E : x = 5 := trivial

theorem B : 1 = 1 := rfl
theorem C2 : 1 = 1 ∧ 2 = 2 := ⟨B, A⟩

set_option maxHeartbeats 0
```

### File 2
```
import Mathlib

open Lean.Elab
set_option maxHeartbeats 200000

theorem A : 4 = 4 := rfl
theorem B : 1 = 1 := rfl
theorem C1 : 1 = 1 ∧ 2 = 2 := ⟨B, A⟩
theorem D : (1 = 1 ∧ 2 = 2) ∧ True := ⟨C1, trivial⟩

variable (x : Nat)
theorem E : x = 5 := sorry
```

### Non-declaration commands are extracted first

Any non-declaration commands (variables, open scopes, options, notations, etc.) will be extracted _first_ from all files. These commands will be placed under a comment label like `----------------------`

Note that this may break files, since many of these commands have global side effects that change how a proof is run, so it is a good idea to normalize your code first, whether manually or by calling [normalize](normalize.md).

This gives us:
```
----------------------
open Lean
variable (x : Nat)
set_option maxHeartbeats 0

----------------------
open Lean.Elab
set_option maxHeartbeats 200000
variable (x : Nat)
```

Pay attention to how we have conflicting commands here: at first, we set `maxHeartbeats` to 0, and then immediately reset it to 200000. Until we figure out a better way to handle this scenario, it is good to keep in mind.

### Declarations are merged respecting dependencies

All remaining commands will be declarations, and will be merged in topological order.

### Conflict resolution via renaming

Notice that both files have a theorem `A`, which assert different things. The merge function will automatically rename one of them to a globally unique identifier. Note that our renaming function is fairly robust as seen in the [rename](rename.md) endpoint.
```
theorem A : 2 = 2 := rfl

theorem A_1 : 4 = 4 := rfl
```

### Deduplication of identical theorems

Theorem `B` exists in both files here, so we merge them into a single theorem.

```
theorem B : 1 = 1 := rfl
```

Note that we also merge non-theorems (e.g., definitions and structures), but these must have the same *value* in addition to having the same type, because they *are* implementation-specific.

### Deduplication merges theorems with different names

Theorem `C` exists in both files, but with different names (`C1` vs. `C2`). Our merge function will automatically detect this equivalence and generate a unique name to use in the merged file.
```
theorem C2_1 : 1 = 1 ∧ 2 = 2 := ⟨B, A⟩
```

### Preference for error-free and sorry-free declarations

Theorem `D` exists in both files, but in the first file, the proof `rfl` completely fails, so we'll prefer the implementation in the second file.

```
theorem D : (1 = 1 ∧ 2 = 2) ∧ True := ⟨C2_1, trivial⟩
```

Notice something interesting here: in the first file, `D` was declared *before* `A, B, C` existed, so there couldn't possibly be a proof of `D` that uses `A, B, C`. However, our dependency tracking figures out that since we should use the implementation in the second file, we need the dependencies from that file, where `A, B, C` *are* defined.

### Unsuccessful attempts are preserved as comments

If no successful proofs exist, we select one arbitrarily, but keep the others as reference. We retain the remaining unsuccessful proofs as comments following the chosen proof, with the signposting `unsuccessful attempt`.

```
theorem E : x = 5 := trivial

/-
-- unsuccessful attempt
theorem E : x = 5 := sorry
-/
```

### Final File
```
import Mathlib

----------------------
open Lean
variable (x : Nat)
set_option maxHeartbeats 0

----------------------
open Lean.Elab
set_option maxHeartbeats 200000
variable (x : Nat)

theorem A : 2 = 2 := rfl

theorem B : 1 = 1 := rfl

theorem C2_1 : 1 = 1 ∧ 2 = 2 := ⟨B, A⟩

theorem A_1 : 4 = 4 := rfl

theorem D : (1 = 1 ∧ 2 = 2) ∧ True := ⟨C2_1, trivial⟩

theorem E : x = 5 := trivial

/-
-- unsuccessful attempt
theorem E : x = 5 := sorry
-/
```
Note that you may get slightly different results due to the possibility of multiple topological orderings of the declarations.""",
        },
        "inputs": [
            {
                "name": "documents",
                "type": "textarea_list",
                "description": "List of Lean code strings to merge",
                "details": "Multiple Lean files to combine into a single file. Duplicate declarations are merged intelligently.",
                "required": True,
                "placeholder": "theorem foo : 1 = 1 := rfl",
                "cli_multiple_files": True,
                "cli_positional": True,
            },
            {
                "name": "use_def_eq",
                "type": "checkbox",
                "description": "Use definitional equality for deduplication",
                "details": """\
When `true`, types are compared using equality after kernel reduction.

When `false`, types are compared at face value, which is faster but may rarely fail to merge semantically identical proofs.

Defaults to true.""",
                "default": True,
            },
            {
                "name": "include_alts_as_comments",
                "type": "checkbox",
                "description": "Preserve alternate versions as comments",
                "details": "When deduplicating, preserves all versions of a merged declaration as comments for reference. Defaults to false.",
                "default": False,
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("merge"),
            {
                "name": "content",
                "type": "string",
                "description": "All input files merged into a single Lean file",
                "details": "Duplicates and dependencies are resolved.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "simplify_theorems": {
        "title": "Simplify Theorems",
        "details": "Simplify theorem proofs by removing unnecessary tactics and cleaning up code.",
        "description": "simplify theorem proofs",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Simplify all theorems\naxle simplify-theorems complex.lean --environment lean-4.28.0",
            "# Simplify specific theorems\naxle simplify-theorems complex.lean --names main_theorem,helper --environment lean-4.28.0",
            "# Apply only specific simplifications\naxle simplify-theorems complex.lean --simplifications remove_unused_tactics --environment lean-4.28.0",
            "# Pipeline usage\ncat complex.lean | axle simplify-theorems - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcblxudGhlb3JlbSBmb28gKGEgYiA6IE5hdCkgOlxuICAgIGEg4omkIGEgKyBiIDo9IGJ5XG4gIGhhdmUgaCA6IGEgKyAwIOKJpCBhICsgYiA6PSBieVxuICAgIGFwcGx5IE5hdC5hZGRfbGVfYWRkX2xlZnQgO1xuICAgIGV4YWN0IE5hdC56ZXJvX2xlIF9cbiAgc2ltcCIsImlnbm9yZV9pbXBvcnRzIjpmYWxzZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "__inputs__": True,
            "__outputs__": True,
            "Available Simplifications": """\
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

-->""",
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
        },
        "python_example": """\
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
print(result.simplification_stats)""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/simplify_theorems \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 := by rfl <;> rfl", "environment": "lean-4.28.0", "names": ["foo"]}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := by rfl",
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  },
  "simplification_stats": {
    "remove_unused_tactics": 1,
    "rename_unused_vars": 0,
    "remove_unused_haves": 0
  }
}""",
        "inputs": [
            {**CONTENT_INPUT, "placeholder": "theorem foo : 1 = 1 := by rfl <;> rfl"},
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "simplifications",
                "type": "list",
                "description": "List of simplifications to apply",
                "details": """If not specified, all simplifications are applied. See below for available simplifications.""",
                "required": False,
                "placeholder": "remove_unused_tactics, rename_unused_vars, remove_unused_haves",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("simplify_theorems"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with simplified theorem proofs",
                "details": "May be shorter and cleaner than input.",
            },
            TIMINGS_OUTPUT,
            {
                "name": "simplification_stats",
                "type": "dict",
                "description": "Count of each simplification type applied",
                "details": 'Maps simplification names to counts (e.g., `{"remove_unused_tactics": 3}`).',
            },
        ],
    },
    "repair_proofs": {
        "title": "Repair Proofs",
        "details": "Attempt to repair broken theorem proofs.",
        "description": "repair broken theorem proofs",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Repair all theorems\naxle repair-proofs broken.lean --environment lean-4.28.0",
            "# Repair specific theorems\naxle repair-proofs broken.lean --names main_theorem,helper --environment lean-4.28.0",
            "# Apply only specific repairs\naxle repair-proofs broken.lean --repairs remove_extraneous_tactics --environment lean-4.28.0",
            "# Pipeline usage\ncat broken.lean | axle repair-proofs - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcblxudGhlb3JlbSBwYXJhbGxlbF9nb2Fsc19leHRyYW5lb3VzXG4gICh5IDog4oSCKSAoeCA6IOKEnSkgKGggOiB4IOKJpSAyKSA6XG4gIDcgKiAoMyAqIHkgKyAyKSA9IDIxICogeSArIDE0XG4gIOKIpyB4XjIg4omlIDFcbiAgOj0gYnlcbiAgY29uc3RydWN0b3JcbiAgYWxsX2dvYWxzIHNvcnJ5XG4gIGdyaW5kXG4gIHJmbFxuICBzb3JyeSIsImlnbm9yZV9pbXBvcnRzIjpmYWxzZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "Known Limitations": """\
- The repair tool does not guarantee that repaired proofs will be semantically correct or complete
- Some repairs may introduce new errors or conflicts
- Complex proofs with multiple goals may require manual intervention
- The tool works best on simple, localized proof issues""",
            "__inputs__": True,
            "__outputs__": True,
            "Available Repairs": """\
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
    ```""",
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
        },
        "python_example": """\
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
print(result.repair_stats)""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/repair_proofs \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 := by\\n  rfl\\n  simp\\n  omega", "environment": "lean-4.28.0", "names": ["foo"]}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := by\\n  rfl",
  "timings": {
    "total_ms": 102,
    "parse_ms": 95
  },
  "repair_stats": {
    "remove_extraneous_tactics": 2,
    "apply_terminal_tactics": 0,
    "replace_unsafe_tactics": 0
  },
  "okay": true
}""",
        "inputs": [
            {**CONTENT_INPUT, "placeholder": "theorem foo : 1 = 1 := by sorry"},
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "repairs",
                "type": "list",
                "description": "List of repairs to apply",
                "details": """If not specified, all repairs are applied. See below for available repairs.""",
                "required": False,
                "placeholder": "remove_extraneous_tactics, apply_terminal_tactics, replace_unsafe_tactics",
            },
            {
                "name": "terminal_tactics",
                "type": "list",
                "description": "Tactics to try for closing goals",
                "details": "Used when 'apply_terminal_tactics' repair is applied. Tactics tried in order; stops on first success. Defaults to 'grind'.",
                "required": False,
                "default": ["grind"],
                "placeholder": "grind, aesop, rfl, simp, decide",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("repair_proofs"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with repair attempts applied",
                "details": "Check `okay` to see if repairs succeeded.",
            },
            TIMINGS_OUTPUT,
            {
                "name": "repair_stats",
                "type": "dict",
                "description": "Count of each repair type applied",
                "details": 'Maps repair names to counts (e.g., `{"apply_terminal_tactics": 2}`).',
            },
            {
                "name": "okay",
                "type": "bool",
                "description": "Whether the proof compiles after repair and all repairs succeed",
                "details": "`True` when the file compiles after repair and all repairs succeed; `False` otherwise.",
            },
        ],
    },
    "have2lemma": {
        "title": "Extract Have Statements to Lemmas",
        "details": "Extract `have` statements from proofs and convert them into standalone lemmas.",
        "description": "extract have statements to standalone lemmas",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Extract all have statements\naxle have2lemma theorem.lean --environment lean-4.28.0",
            "# Extract from specific theorems\naxle have2lemma theorem.lean --names main_proof,helper --environment lean-4.28.0",
            "# Include proof bodies in extracted lemmas\naxle have2lemma theorem.lean --include-have-body --environment lean-4.28.0",
            "# Reconstruct callsites (replace have with lemma call)\naxle have2lemma theorem.lean --reconstruct-callsite --environment lean-4.28.0",
            "# Skip context cleanup\naxle have2lemma theorem.lean --no-include-whole-context --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle have2lemma - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBvdXRlciA6IDEgPSAxIDo9IGJ5XG4gIGhhdmUgaW5uZXIgOiAyID0gMiA6PSBieVxuICAgIGhhdmUgbmVzdGVkIDogMyA9IDMgOj0gYnkgcmZsXG4gICAgcmZsXG4gIHJmbCIsImluY2x1ZGVfaGF2ZV9ib2R5Ijp0cnVlLCJpbmNsdWRlX3dob2xlX2NvbnRleHQiOnRydWUsInJlY29uc3RydWN0X2NhbGxzaXRlIjp0cnVlLCJ2ZXJib3NpdHkiOjAsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9",
        "python_example": """\
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
print(result.lemma_names)  # ["main_theorem.h1", "main_theorem.h2"]""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/have2lemma \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\\n  have h1 : 1 = 1 := by rfl\\n  have h2 : 2 = 2 := by rfl\\n  exact ⟨h1, h2⟩", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\nlemma foo.h1 : 1 = 1 := sorry\\n\\nlemma foo.h2 (h1 : 1 = 1) : 2 = 2 := sorry\\n\\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\\n  have h1 : 1 = 1 := by rfl\\n  have h2 : 2 = 2 := by rfl\\n  exact ⟨h1, h2⟩",
  "lemma_names": ["foo.h1", "foo.h2"],
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}""",
        "sections": {
            "See Also": "This tool is partially powered by [`extract_goal`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/ExtractGoal.html), a Mathlib tactic for extracting goals into standalone declarations.",
            "__inputs__": True,
            "__outputs__": True,
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
            "Demo": """\
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

These configuration options provide some flexibility around usage, at the cost of correctness in some cases. Try to keep this in mind when generating bug reports -- some of these errors aren't fixable without significant effort.""",
        },
        "inputs": [
            {
                **CONTENT_INPUT,
                "placeholder": "theorem foo : 1 = 1 := by\n  have h : 1 = 1 := by rfl\n  exact h",
            },
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "include_have_body",
                "type": "checkbox",
                "description": "Include proof bodies in extracted lemmas",
                "details": "If `true`, extracted lemmas include the original proof. If `false`, they use `sorry` as placeholder. Defaults to false.",
                "default": False,
            },
            {
                "name": "include_whole_context",
                "type": "checkbox",
                "description": "Include whole context when extracting",
                "details": "If `true`, lemmas include all context variables. If `false`, attempts to minimize the context. Defaults to true.",
                "default": True,
            },
            {
                "name": "reconstruct_callsite",
                "type": "checkbox",
                "description": "Replace have statement with lemma call",
                "details": "If `true`, the original `have` is replaced with a call to the extracted lemma. Defaults to false.",
                "default": False,
            },
            {
                "name": "verbosity",
                "type": "number",
                "description": "Pretty-printer verbosity level (0-2)",
                "details": "0=default, 1=robust, 2=extra robust. Higher levels produce more explicit type annotations. Use when default output has ambiguity errors.",
                "required": False,
                "default": 0,
                "placeholder": "0",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("have2lemma"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with have statements extracted as lemmas",
                "details": "The code with `have` statements lifted to top-level lemmas. Original theorems may reference these new lemmas.",
            },
            {
                "name": "lemma_names",
                "type": "list",
                "description": "Names of newly created lemmas",
                "details": "Names are auto-generated based on the parent theorem.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "have2sorry": {
        "title": "Replace Have Statements with Sorry",
        "details": "Replace `have` statements in proofs with `sorry`. Useful for creating problem templates from solutions while keeping the overall proof structure intact.",
        "description": "replace have statements with sorry",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Replace all have statements\naxle have2sorry theorem.lean --environment lean-4.28.0",
            "# Replace from specific theorems\naxle have2sorry theorem.lean --names main_proof,helper --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle have2sorry - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBmb28gOiBUcnVlIDo9IGJ5XG4gIGhhdmUgOiAxID0gMiA6PSByZmxcbiAgdHJpdmlhbCIsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9",
        "python_example": """\
result = await axle.have2sorry(
    content=lean_code,
    environment="lean-4.28.0",
    names=["main_theorem"],  # Optional
)
print(result.content)""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/have2sorry \\
    -d '{"content": "import Mathlib\\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\\n  have h1 : 1 = 1 := by rfl\\n  have h2 : 2 = 2 := by rfl\\n  exact ⟨h1, h2⟩", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 ∧ 2 = 2 := by\\n  have h1 : 1 = 1 := sorry\\n  have h2 : 2 = 2 := sorry\\n  exact ⟨h1, h2⟩",
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}""",
        "inputs": [
            {
                **CONTENT_INPUT,
                "placeholder": "theorem foo : 1 = 1 := by\n  have h : 1 = 1 := by rfl\n  exact h",
            },
            NAMES_INPUT,
            INDICES_INPUT,
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("have2sorry"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with have proof bodies replaced by sorry",
                "details": "The `have` structure is preserved.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "sorry2lemma": {
        "title": "Extract Sorries and Errors to Lemmas",
        "details": "Extract `sorry` placeholders and unsolved goals at error locations from Lean code and lift them into standalone top-level lemmas.",
        "description": "extract sorries and errors to standalone lemmas",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Extract all sorries and errors\naxle sorry2lemma theorem.lean --environment lean-4.28.0",
            "# Extract from specific theorems\naxle sorry2lemma theorem.lean --names main_proof,helper --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle sorry2lemma - --environment lean-4.28.0 | axle check - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBtdWx0aXBsZSAobiA6IE5hdCkgOiAxID0gMSDiiKcgMiA9IDIgOj0gYnkgY29uc3RydWN0b3IgPDs%2BIHNvcnJ5IiwiZXh0cmFjdF9zb3JyaWVzIjp0cnVlLCJleHRyYWN0X2Vycm9ycyI6dHJ1ZSwiaW5jbHVkZV93aG9sZV9jb250ZXh0Ijp0cnVlLCJyZWNvbnN0cnVjdF9jYWxsc2l0ZSI6dHJ1ZSwidmVyYm9zaXR5IjowLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "python_example": """\
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
print(result.lemma_names)  # ["main_theorem.sorried", "main_theorem.unsolved"]""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/sorry2lemma \\
    -d '{"content": "import Mathlib\\ntheorem foo (p q : Prop) : p → q := by\\n  intro hp\\n  sorry", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
{
  "lean_messages": {
    "errors": [],
    "warnings": ["-:3:6: warning: declaration uses 'sorry'\\n", "-:5:8: warning: declaration uses 'sorry'\\n"],
    "infos": []
  },
  "tool_messages": {
    "errors": [],
    "warnings": [],
    "infos": []
  },
  "content": "import Mathlib\\n\\nlemma foo.sorried (p q : Prop) (hp : p) : q := sorry\\n\\ntheorem foo (p q : Prop) : p → q := by\\n  intro hp\\n  sorry",
  "lemma_names": ["foo.sorried"],
  "timings": {
    "total_ms": 95,
    "parse_ms": 88
  }
}""",
        "sections": {
            "See Also": "This tool is partially powered by [`extract_goal`](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/ExtractGoal.html), a Mathlib tactic for extracting goals into standalone declarations.",
            "__inputs__": True,
            "__outputs__": True,
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
            "Demo": """\
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
```""",
        },
        "inputs": [
            {**CONTENT_INPUT, "placeholder": "theorem foo : 1 = 1 := by\n  sorry"},
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "extract_sorries",
                "type": "checkbox",
                "description": "Lift sorries into standalone lemmas",
                "details": "If `true`, `sorry` placeholders are extracted into standalone lemmas. Defaults to true.",
                "default": True,
            },
            {
                "name": "extract_errors",
                "type": "checkbox",
                "description": "Lift errors into standalone lemmas",
                "details": "If `true`, error positions (type mismatches, etc.) are extracted into standalone lemmas. Defaults to true.",
                "default": True,
            },
            {
                "name": "include_whole_context",
                "type": "checkbox",
                "description": "Include whole context when extracting",
                "details": "If `true`, lemmas include all context variables. If `false`, attempts to minimize the context. Defaults to true.",
                "default": True,
            },
            {
                "name": "reconstruct_callsite",
                "type": "checkbox",
                "description": "Replace sorry with lemma call",
                "details": "If `true`, the original `sorry` is replaced with a call to the extracted lemma. Defaults to false.",
                "default": False,
            },
            {
                "name": "verbosity",
                "type": "number",
                "description": "Pretty-printer verbosity level (0-2)",
                "details": "0=default, 1=robust, 2=extra robust. Higher levels produce more explicit type annotations. Use when default output has ambiguity errors.",
                "required": False,
                "default": 0,
                "placeholder": "0",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("sorry2lemma"),
            {
                "name": "content",
                "type": "string",
                "description": "Lean code with sorries/errors extracted as lemmas",
                "details": "The code with `sorry` and error positions lifted to top-level lemmas with their goals as types.",
            },
            {
                "name": "lemma_names",
                "type": "list",
                "description": "Names of newly created lemmas",
                "details": "Names are auto-generated based on the parent theorem and position.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "disprove": {
        "title": "Disprove",
        "details": "Attempt to disprove theorems by proving the negation.",
        "description": "attempt to disprove theorems by proving the negation",
        "cli_output": {
            "mode": "json_stdout",
            "metadata_to_stderr": False,
        },
        "cli_examples": [
            "# Disprove all theorems\naxle disprove theorems.lean --environment lean-4.28.0",
            "# Disprove specific theorems by name\naxle disprove theorems.lean --names main_theorem,helper --environment lean-4.28.0",
            "# Disprove specific theorems by index\naxle disprove theorems.lean --indices 0,-1 --environment lean-4.28.0",
            "# Pipeline usage\ncat theorems.lean | axle disprove - --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoidGhlb3JlbSBmaXJzdCA6IOKIgCBuIDog4oSVLCBuIDwgMTBeMTAwIDo9IHNvcnJ5XG50aGVvcmVtIHNlY29uZCA6IDIgPSAxIDo9IGJ5IHNvcnJ5IiwidGVybWluYWxfdGFjdGljcyI6WyJhZXNvcCJdLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "See Also": "This tool is partially powered by [Plausible](https://github.com/leanprover-community/plausible), a Lean 4 library for property-based testing and counterexample generation.",
        },
        "python_example": """\
result = await axle.disprove(
    content=lean_code,
    environment="lean-4.28.0",
    names=["conjecture1", "conjecture2"],  # Optional
    ignore_imports=False,                   # Optional
)
print(result.disproved_theorems)  # ["conjecture2"]
print(result.results)  # Per-theorem results
print(result.content)  # The processed Lean code""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/disprove \\
    -d '{"content": "import Mathlib\\ntheorem solid_fact : 1 = 1 := rfl\\ntheorem bold_claim : 2 = 3 := rfl", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
{
  "content": "import Mathlib\\n\\ntheorem solid_fact : 1 = 1 := rfl\\ntheorem bold_claim : 2 = 3 := rfl\\n",
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
  "results": {
    "solid_fact": "Disprove: failed to prove negation. Remaining goal: `1 = 1`\\n",
    "bold_claim": "Disprove: goal is false! Proof of negation by plausible.\\n\\n===================\\nFound a counter-example!\\nissue: 2 = 3 does not hold\\n(0 shrinks)\\n-------------------\\n"
  },
  "disproved_theorems": ["bold_claim"],
  "timings": {
    "total_ms": 97,
    "parse_ms": 92
  }
}""",
        "inputs": [
            CONTENT_INPUT,
            NAMES_INPUT,
            INDICES_INPUT,
            {
                "name": "terminal_tactics",
                "type": "list",
                "description": "Tactics to try when attempting to disprove",
                "details": "Tactics tried in order to prove the negation. `grind` often works for false statements. Defaults to 'grind'.",
                "required": False,
                "default": ["grind"],
                "placeholder": "grind, aesop, rfl, simp, decide",
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            CONTENT_OUTPUT,
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("disprove"),
            {
                "name": "results",
                "type": "dict",
                "description": "Map from theorem name to disprove result",
                "details": "Each theorem maps to a string indicating the outcome of the disprove attempt.",
            },
            {
                "name": "disproved_theorems",
                "type": "list",
                "description": "List of theorems that were disproved",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "normalize": {
        "title": "Normalize",
        "details": "Standardize Lean file formatting to prepare for other operations, especially `merge` operations. Use this tool to detect when a file is unusually structured, in which case other Axle operations may behave unexpectedly.",
        "description": "standardize Lean file formatting",
        "cli_output": {
            "mode": "lean_stdout",
            "supports_output_file": True,
            "metadata_to_stderr": True,
        },
        "cli_examples": [
            "# Normalize a file\naxle normalize theorem.lean --environment lean-4.28.0",
            "# Normalize and save to file\naxle normalize theorem.lean -o normalized.lean --environment lean-4.28.0",
            "# Apply only specific normalizations\naxle normalize theorem.lean --normalizations remove_sections,expand_decl_names --environment lean-4.28.0",
            "# Pipeline usage\ncat theorem.lean | axle normalize - --environment lean-4.28.0 | axle merge - other.lean --environment lean-4.28.0",
            "# Disable failsafe to always return normalized output\naxle normalize theorem.lean --no-failsafe --environment lean-4.28.0",
        ],
        "web_ui_example_data": "eyJjb250ZW50IjoiaW1wb3J0IE1hdGhsaWJcbm9wZW4gT3B0aW9uXG5cbm5hbWVzcGFjZSB0ZXN0XG5vcGVuIE9wdGlvblxuXG5sZW1tYSBzb21lX2xlbW1hICjOsSA6IFR5cGUpICh4IDogzrEpIDpcbiAgICBPcHRpb24uZ2V0RCAoc29tZSB4KSB4ID0geCA6PSBieVxuICBzaW1wIFtnZXREXVxuXG5lbmQgdGVzdCIsImZhaWxzYWZlIjp0cnVlLCJpZ25vcmVfaW1wb3J0cyI6dHJ1ZSwiZW52aXJvbm1lbnQiOiJsZWFuLTQuMjcuMCIsInRpbWVvdXRfc2Vjb25kcyI6MTIwfQ%3D%3D",
        "sections": {
            "__inputs__": True,
            "__outputs__": True,
            "Available Normalizations": """\
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
    Converts documentation comments (`/-- ... -/`) into regular block comments (`/- ... -/`). Doc comments are typically attached to declarations to provide API documentation.""",
            "__python__": True,
            "__cli__": True,
            "__http__": True,
            "__response__": True,
        },
        "python_example": """\
result = await axle.normalize(
    content=lean_code,
    environment="lean-4.28.0",
    normalizations=["remove_sections", "expand_decl_names"],  # Optional: specify which normalizations
    failsafe=True,  # Optional: return original if normalization fails
)
print(result.content)
print(result.normalize_stats)""",
        "http_example": """\
curl -s -X POST https://axle.axiommath.ai/api/v1/normalize \\
    -d '{"content": "import Mathlib\\nsection\\ntheorem foo : 1 = 1 := rfl\\nend", "environment": "lean-4.28.0"}' | jq""",
        "example_response": """\
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
  "content": "import Mathlib\\n\\ntheorem foo : 1 = 1 := rfl\\n",
  "timings": {
    "total_ms": 92,
    "parse_ms": 87
  },
  "normalize_stats": {
    "remove_sections": 2
  }
}""",
        "inputs": [
            CONTENT_INPUT,
            {
                "name": "normalizations",
                "type": "list",
                "description": "List of normalizations to apply",
                "details": """Options: remove_sections, expand_decl_names, remove_duplicates, split_open_in_commands, normalize_module_comments, normalize_doc_comments. Default: remove_sections, remove_duplicates, split_open_in_commands.""",
                "required": False,
                "placeholder": "remove_sections, remove_duplicates, split_open_in_commands",
            },
            {
                "name": "failsafe",
                "type": "checkbox",
                "description": "Return original if normalization fails",
                "details": "If true, returns the original content unchanged if normalization introduces errors. Defaults to true.",
                "default": True,
            },
            IGNORE_IMPORTS_INPUT,
            ENVIRONMENT_INPUT,
            TIMEOUT_INPUT,
        ],
        "outputs": [
            LEAN_MESSAGES_OUTPUT,
            tool_messages_output("normalize"),
            {
                "name": "content",
                "type": "string",
                "description": "The normalized Lean code",
                "details": "The standardized code. May be identical to input if `failsafe` triggered.",
            },
            TIMINGS_OUTPUT,
            {
                "name": "normalize_stats",
                "type": "dict",
                "description": "Count of each normalization applied",
                "details": 'Maps normalization names to counts (e.g., `{"remove_sections": 2}`).',
            },
        ],
    },
}
