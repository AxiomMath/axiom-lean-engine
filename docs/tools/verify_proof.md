# verify_proof

Validate a candidate Lean theorem and check that it conforms to the given formal statement.

[Try this example in the web UI](https://axle.axiommath.ai/verify_proof#data=eyJmb3JtYWxfc3RhdGVtZW50IjoiZGVmIEEgOj0gNFxudGhlb3JlbSBtYWluIDogQSA9IDUgOj0gc29ycnkiLCJjb250ZW50IjoiZGVmIEEgOj0gNVxudGhlb3JlbSBtYWluIDogQSA9IDUgOj0gcmZsIiwibWF0aGxpYl9vcHRpb25zIjpmYWxzZSwidXNlX2RlZl9lcSI6dHJ1ZSwiaWdub3JlX2ltcG9ydHMiOnRydWUsImVudmlyb25tZW50IjoibGVhbi00LjI3LjAiLCJ0aW1lb3V0X3NlY29uZHMiOjEyMH0%3D)

## See Also

In the interest of scalability, `verify_proof` trusts the Lean environment to behave correctly. That's usually fine, but a sufficiently creative adversary can exploit this to make invalid proofs appear valid with Lean metaprogramming.

This is a known limitation that we don't expect to address, since the alternatives below cover adversarial use cases.

If you're verifying untrusted code, consider additionally using these other resources which perform a similar check. These run proofs in isolated environments and are less susceptible to known exploits, at the cost of speed:

- [lean4checker](https://github.com/leanprover/lean4checker): Lean FRO-developed .olean verifier
- [Comparator](https://github.com/leanprover/comparator): Lean FRO-developed gold standard for proof judges
- [SafeVerify](https://github.com/GasStationManager/SafeVerify): battle-tested public proof checker

We recommend reading the [Lean4 reference page on this topic](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) for more discussion.

See the corresponding [Github issue](https://github.com/AxiomMath/axiom-lean-engine/issues/2).

## Input Parameters

??? "`formal_statement` · str · required · Sorried theorem to verify against"
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
    contains `def foo := 5`, then `content` must define `foo` with the same value.

??? "`content` · str · required · Candidate proof to verify"
    The Lean source code containing the proof(s) to validate against the formal statement.

??? "`permitted_sorries` · list[str] · Theorems allowed to contain `sorry`"
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

    This option is also useful for enabling tactics like `native_decide`, which introduce extra axioms:

    - **Lean 4.28.0 and below:** include `Lean.trustCompiler`, `Lean.ofReduceBool`, and `Lean.ofReduceNat`.
    - **Lean 4.29.0 and above:** `native_decide` axioms were reworked (see [here](https://github.com/leanprover/lean4/pull/12217)). Use glob patterns, e.g. `<theorem_name>._native.native_decide.*`, to allow all `native_decide`-related axioms for a given theorem.

    **Note:** glob patterns do not defend against an adversary deliberately crafting malicious axioms with matching names, so we don't recommend using them with untrusted code.

??? "`mathlib_options` · bool · default: `False` · Enable Mathlib options"
    If true, enables conventional Mathlib options. This toggle sets `linter.mathlibStandardSet` to true, `autoImplicit` to false, `relaxedAutoImplicit` to false, and `pp.unicode.fun` to true.

??? "`use_def_eq` · bool · default: `True` · Use definitional equality for type comparison"
    When `true`, types are compared using equality after kernel reduction.

    When `false`, types are compared at face value, which is faster but may rarely
    reject valid proofs.

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

??? "`okay` · bool · True if proof passes verification"
    Returns `true` if the candidate proof is valid and matches the formal statement. Check `tool_messages.errors` for details when `false`.

??? "`content` · string · Processed Lean code"
    The Lean code that was actually processed. May differ from input if `ignore_imports=true` caused header injection.

??? "`lean_messages` · dict · Messages from Lean compiler"
    Messages from the Lean compiler with `errors`, `warnings`, and `infos` lists.
    Errors here indicate invalid Lean code (syntax errors, type errors, etc.).

??? "`tool_messages` · dict · Messages from verify_proof tool"
    Messages from the AXLE verification tool with `errors`, `warnings`, and `infos` lists.

    Errors here mean `content` was valid Lean code, but not a satisfactory proof of `formal_statement`.
    Common errors include: "Missing required declaration", "does not match expected signature", "uses sorry".

??? "`failed_declarations` · list · Declaration names that failed validation"
    Declaration names that failed validation

??? "`timings` · dict · Execution timing breakdown"
    Timing information in milliseconds for various stages of processing.


## Verification Error Messages

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
| `Candidate uses banned 'open private' command` | Use of disallowed `open private` command |

## Python API

```python
result = await axle.verify_proof(
    formal_statement="import Mathlib\ntheorem citation_needed : 1 = 1 := by sorry",
    content="import Mathlib\ntheorem citation_needed : 1 = 1 := rfl",
    environment="lean-4.28.0",
    permitted_sorries=["helper"],  # Optional
    mathlib_options=False,          # Optional
    ignore_imports=False,          # Optional
    timeout_seconds=120,           # Optional
)

print(result.okay)  # True if proof is valid
print(result.content)  # The processed Lean code
```

## CLI

**Usage:** `axle verify-proof FORMAL_STATEMENT CONTENT [OPTIONS]`

```bash
# Basic usage
axle verify-proof statement.lean proof.lean --environment lean-4.28.0
# With permitted sorries
axle verify-proof statement.lean proof.lean --permitted-sorries helper1,helper2 --environment lean-4.28.0
# Pipeline usage
cat proof.lean | axle verify-proof statement.lean - --environment lean-4.28.0
# Exit non-zero if proof is invalid
axle verify-proof statement.lean proof.lean --strict --environment lean-4.28.0
# Use in shell conditionals
if axle verify-proof statement.lean proof.lean --strict --environment lean-4.28.0 > /dev/null; then
    echo "Proof valid"
fi
# Specify different environment
axle verify-proof statement.lean proof.lean --environment lean-4.28.0
```

## HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/verify_proof \
    -d '{"content": "import Mathlib\ntheorem citation_needed : 1 = 1 := rfl", "formal_statement": "import Mathlib\ntheorem citation_needed : 1 = 1 := by sorry", "environment": "lean-4.28.0"}' | jq
```

## Example Response

```json
{
  "okay": false,
  "content": "import Mathlib\n\ntheorem foo : 1 = 1 := rfl\n",
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
}
```
