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
Maximum execution time in seconds. Requests exceeding this limit return a timeout error. Note that end-to-end request latency may exceed this timeout due to queue time and other overhead.""",
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
- `true`: Ignore the imports in `content` and use the environment's default imports instead. See the usage notes page for more details.""",
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
    description: str
    inputs: list[InputField]
    outputs: list[OutputField]
    # CLI-specific fields
    cli_one_line_desc: str  # One-line description for NAME section
    cli_output: CliOutputConfig  # Output behavior configuration
    cli_examples: list[str]  # List of example command lines with comments


# All Axle API endpoints metadata
ENDPOINTS: dict[str, EndpointMetadata] = {
    "verify_proof": {
        "title": "Verify Proof",
        "description": "Validate a candidate Lean theorem and check that it conforms to the given formal statement.",
        "cli_one_line_desc": "validate a Lean proof against a formal statement",
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

Names not present in the code are silently ignored, so you can pass a
static list without checking what's actually in the file.""",
                "required": False,
                "placeholder": "helper_lemma, auxiliary_theorem",
            },
            MATHLIB_LINTER_INPUT,
            {
                "name": "use_def_eq",
                "type": "checkbox",
                "description": "Use definitional equality for type comparison",
                "details": """\
When `true`, types are compared using Lean's definitional equality (equality
after kernel reduction).

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
        "description": "Evaluate Lean code and collect all messages (errors, warnings, and info). Use this if you just want to check if code is valid without verification.",
        "cli_one_line_desc": "evaluate Lean code and report all messages",
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
                "details": "List of declaration names that have compilation or validation errors. Empty if `okay` is `true`.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "extract_theorems": {
        "title": "Extract Theorems",
        "description": "Split a file containing one or more theorems into smaller units, each containing a single theorem with required dependencies.",
        "cli_one_line_desc": "split file into separate theorems with dependencies",
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
        "description": "Rename symbols in Lean code",
        "cli_one_line_desc": "rename declarations in Lean code",
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
        "description": "Convert between theorem and lemma declaration keywords",
        "cli_one_line_desc": "convert between theorem and lemma keywords",
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
        "description": "Strip proofs from theorems by replacing them with sorry",
        "cli_one_line_desc": "replace theorem proofs with sorry",
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
        "description": "Combine multiple Lean files into a single file",
        "cli_one_line_desc": "combine multiple Lean files into a single file",
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
When `true`, types are compared using Lean's definitional equality (equality after kernel reduction).

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
        "description": "Simplify theorem proofs using various simplification techniques",
        "cli_one_line_desc": "simplify theorem proofs",
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
        "description": "Repair broken theorem proofs by attempting various fixes",
        "cli_one_line_desc": "repair broken theorem proofs",
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
                "details": "Check `lean_messages.errors` to see if repairs succeeded.",
            },
            TIMINGS_OUTPUT,
            {
                "name": "repair_stats",
                "type": "dict",
                "description": "Count of each repair type applied",
                "details": 'Maps repair names to counts (e.g., `{"apply_terminal_tactics": 2}`).',
            },
        ],
    },
    "have2lemma": {
        "title": "Extract Have Statements to Lemmas",
        "description": "Extract `have` statements from theorem proofs and convert them into standalone lemmas",
        "cli_one_line_desc": "extract have statements to standalone lemmas",
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
        "description": "Replace `have` statements in theorem proofs with `sorry`. Useful for creating problem templates from solutions.",
        "cli_one_line_desc": "replace have statements with sorry",
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
        "description": "Extract `sorry` placeholders and errors from Lean code and lift them into standalone top-level lemmas",
        "cli_one_line_desc": "extract sorries and errors to standalone lemmas",
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
        "description": "Attempt to disprove theorems by proving the negation",
        "cli_one_line_desc": "attempt to disprove theorems by proving the negation",
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
                "details": "Names of theorems where the negation was successfully proven.",
            },
            TIMINGS_OUTPUT,
        ],
    },
    "normalize": {
        "title": "Normalize",
        "description": "Standardize Lean file formatting to prepare for merge operations.",
        "cli_one_line_desc": "standardize Lean file formatting",
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
