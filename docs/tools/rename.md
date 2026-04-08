# rename

Rename declarations in Lean code.

[Try this example in the web UI](https://axle.axiommath.ai/rename#data=eyJjb250ZW50IjoidGhlb3JlbSBoZWxwZXIgOiAxICsgMSA9IDIgOj0gYnkgc2ltcFxuZXhhbXBsZSA6IDIgPSAxICsgMSA6PSBoZWxwZXIuc3ltbVxuXG5uYW1lc3BhY2Ugbm1cblxudGhlb3JlbSBoZWxwZXIgOiAxICsgMSA9IDIgOj0gYnkgc2ltcFxudGhlb3JlbSB0aG0gOiAyID0gMSArIDEgOj0gaGVscGVyLnN5bW1cblxuZW5kIG5tIiwiZGVjbGFyYXRpb25zIjp7ImhlbHBlciI6Im91dHNpZGVfaGVscGVyIiwibm0uaGVscGVyIjoibm0uaW5zaWRlX2hlbHBlciIsIm5tLnRobSI6Im5tLmluc2lkZV90aGVvcmVtIn0sImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

## Input Parameters

??? "`content` · str · required · Lean source code"
    The Lean source code to be processed by this tool.

??? "`declarations` · dict · required · Map from old declaration names to new names"
    A dictionary mapping original declaration names to their new names (JSON format).
    All references to renamed declarations are updated throughout the code.

    CLI supports `key=val,key=val` format or `--declarations-file mapping.json`.

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

??? "`tool_messages` · dict · Messages from rename tool"
    Messages from the rename tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · Lean code with renamed declarations"
    The Lean code with renamed declarations. The transformed code with all specified declarations renamed. References are updated throughout.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.rename(
    content="import Mathlib\ntheorem foo : 1 = 1 := rfl\ntheorem baz : 1 = 1 := foo",
    declarations={"foo": "bar"},
    environment="lean-4.28.0",
    timeout_seconds=120,  # Optional
)
print(result.content)  # theorem bar : 1 = 1 := rfl
```

## CLI

**Usage:** `axle rename CONTENT [OPTIONS]`

```bash
# Rename using command-line mapping
axle rename theorem.lean --declarations foo=bar,helper=main_helper --environment lean-4.28.0
# Rename using JSON file
axle rename theorem.lean --declarations-file mapping.json --environment lean-4.28.0
# Save to file
axle rename theorem.lean --declarations foo=bar -o renamed.lean --environment lean-4.28.0
# Pipeline usage
cat theorem.lean | axle rename - --declarations foo=bar --environment lean-4.28.0 | axle check - --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/rename \
    -d '{"content": "import Mathlib\ntheorem foo : 1 = 1 := rfl\ntheorem baz : 1 = 1 := foo", "declarations": {"foo": "bar"}, "environment": "lean-4.28.0"}' | jq
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
  "content": "import Mathlib\n\ntheorem bar : 1 = 1 := rfl\n\ntheorem baz : 1 = 1 := bar",
  "timings": {
    "total_ms": 94,
    "parse_ms": 89
  }
}
```

## Examples

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
    ```
