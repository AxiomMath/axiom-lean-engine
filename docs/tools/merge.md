# merge

Combine multiple Lean files into a single file.

[Try this example in the web UI](https://axle.axiommath.ai/merge#data=eyJkb2N1bWVudHMiOlsidGhlb3JlbSBEIDogKDEgPSAxIOKIpyAyID0gMikg4oinIFRydWUgOj0gc29ycnlcbnRoZW9yZW0gQiA6IDIgPSAyIDo9IHJmbFxudGhlb3JlbSBBIDogMSA9IDEgOj0gc29ycnlcbnRoZW9yZW0gQyA6IDEgPSAxIOKIpyAyID0gMiA6PSDin6hBLCBC4p%2BpIiwidGhlb3JlbSBBIDogMSA9IDEgOj0gcmZsXG50aGVvcmVtIEMgOiAxID0gMSDiiKcgMiA9IDIgOj0g4p%2BoQSwgQeKfqSAtLSBpbmNvcnJlY3RcbnRoZW9yZW0gRCA6ICgxID0gMSDiiKcgMiA9IDIpIOKIpyBUcnVlIDo9IOKfqEMsIHRyaXZpYWzin6lcbnRoZW9yZW0gQiA6IDIgPSAyIDo9IHNvcnJ5Il0sInVzZV9kZWZfZXEiOnRydWUsImluY2x1ZGVfYWx0c19hc19jb21tZW50cyI6ZmFsc2UsImlnbm9yZV9pbXBvcnRzIjp0cnVlLCJlbnZpcm9ubWVudCI6ImxlYW4tNC4yNy4wIiwidGltZW91dF9zZWNvbmRzIjoxMjB9)

## Input Parameters

??? "`documents` · list[str] · required · List of Lean code strings to merge"
    Multiple Lean files to combine into a single file. Duplicate declarations are merged intelligently.

??? "`use_def_eq` · bool · default: `True` · Use definitional equality for deduplication"
    When `true`, types are compared using equality after kernel reduction.

    When `false`, types are compared at face value, which is faster but may rarely fail to merge semantically identical proofs.

    Defaults to true.

??? "`include_alts_as_comments` · bool · default: `False` · Preserve alternate versions as comments"
    When deduplicating, preserves all versions of a merged declaration as comments for reference. Defaults to false.

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

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from merge tool"
    Messages from the merge tool with `errors`, `warnings`, and `infos` lists.
    Errors here indicate tool-specific issues (not Lean compilation errors).

??? "`content` · string · All input files merged into a single Lean file"
    Duplicates and dependencies are resolved.

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Python API

```python
result = await axle.merge(
    documents=[code1, code2, code3],
    environment="lean-4.28.0",
    use_def_eq=True,                  # Optional
    include_alts_as_comments=False,   # Optional
    timeout_seconds=120,              # Optional
)
print(result.content)
```

## CLI

**Usage:** `axle merge FILE1 FILE2 ... [OPTIONS]`

```bash
# Merge multiple files to stdout
axle merge theorem1.lean theorem2.lean theorem3.lean --environment lean-4.28.0
# Merge all .lean files in directory
axle merge *.lean -o combined.lean --environment lean-4.28.0
# Merge and check
axle merge *.lean --environment lean-4.28.0 | axle check - --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/merge \
    -d '{"documents": ["import Mathlib\ntheorem foo : 1 = 1 := rfl", "import Mathlib\ntheorem bar : 2 = 2 := rfl"], "environment": "lean-4.28.0"}' | jq
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
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl\n\ntheorem bar : 2 = 2 := rfl",
  "timings": {
    "total_ms": 105,
    "parse_ms": 95
  }
}
```

## Demo

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
Note that you may get slightly different results due to the possibility of multiple topological orderings of the declarations.
