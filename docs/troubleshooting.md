# Troubleshooting

Common issues when working with AXLE and how to resolve them.

## Reading Error Messages

### Fatal Errors

When a request fails entirely, the response includes an error type at the top level:

| Error Type | Meaning | Action |
|------------|---------|--------|
| `user_error` | Invalid request (missing parameters, bad arguments, import mismatch) | Fix the request—check your inputs |
| `internal_error` | Server bug | [Report it](https://github.com/AxiomMath/axiom-lean-engine/issues) |
| `error` | Runtime failure (timeout, OOM, executor crash) | Retry or simplify input |

In the Python client, these map to exceptions: `AxleInvalidArgument`, `AxleInternalError`, and `AxleRuntimeError`. See [Error Handling](python-api.md#error-handling) for details on catching and handling these exceptions, and for an exhaustive list of all AXLE exceptions, including networking errors.

### Non-Fatal Errors
When troubleshooting, start by examining the messages in the response. AXLE responses include two message fields, each containing `errors`, `warnings`, and `infos` arrays:

| Field | Contents |
|-------|----------|
| `lean_messages` | Output from the Lean compiler itself |
| `tool_messages` | AXLE-specific logs and validation results |

**Message severity:**

- **errors** — Something is wrong; the result may be unusable
- **warnings** — Something is suspicious but not fatal
- **infos** — Informational output (timing, debug info, etc.)

For most tools, `tool_messages.errors` is empty; fatal issues are raised at the response level (see above). The exceptions are `verify_proof` and `check`, which use `tool_messages.errors` to report validation failures.

## Common Issues

### Tool Not Working As Expected

**Symptom:** A tool returns unexpected results, fails to transform code correctly, or produces output with errors.

**Cause:** AXLE was built to handle certain categories of errors—particularly those restricted to the proof body (e.g., failed tactics, `sorry`). Errors outside the proof body (malformed declarations, syntax errors, unresolved imports) may cause tools to behave unexpectedly.

**What AXLE handles well:**

- Code that compiles cleanly
- Proofs with localized errors (e.g., a tactic that doesn't close the goal)

**What may cause issues:**

- Syntax errors or malformed declarations
- Unresolved identifiers outside proof bodies
- Unsupported constructs (see [Unsupported Constructs](#unsupported-lean-constructs))

**Rule of thumb:** If the input compiles, the output should compile. For best results, use AXLE with code that already compiles.

```python
result = await axle.rename(content=code, declarations={"old": "new"}, environment="lean-4.28.0")

if result.lean_messages.errors:
    print("Output has compilation errors:")
    for msg in result.lean_messages.errors:
        print(f"  {msg}")
else:
    print(result.content)
```


### Import Mismatch Errors

**Symptom:** AXLE raises a user error about mismatched imports.

**Cause:** Your code's import statements don't match the environment's expected header. All requests to AXLE are assumed to have the same header (import statements), which is derived from the `imports` field of the environment.

**Resolution options:**

1. **Match your imports to the environment.** Query the [environments endpoint](configuration.md#discovering-available-environments) to discover the expected imports.

2. **Set `ignore_imports=True`** to have AXLE automatically replace your imports with the environment's defaults. When enabled, AXLE will:
    - Log a warning about the import mismatch
    - Replace your code's import statements with the environment's default imports
    - Return the modified code in the `content` field

Note that behavior may be inconsistent if your imports don't match the environment's expected header.

### Unsupported Lean Constructs

**Symptom:** Unexpected behavior or errors with certain Lean code patterns.

**Cause:** AXLE was designed with simple imports, theorems, and definitions in mind.

**Potentially unsupported constructs:**

- Non-standard declaration types
- `open` commands
- `section`/`namespace` blocks
- Complex macro usage

**Resolution:** Use the [`normalize`](tools/normalize.md) tool to detect unsupported constructs early. We attempt to support these patterns and fail fast when we can't, but we make no guarantees about stability.

### Proof Validates But `okay` Is False

**Symptom:** Using `verify_proof` or `check`, the code compiles but `result.okay` returns `False`.

**Cause:** These evaluation tools apply stricter validation than the Lean compiler. A proof may compile but still be invalid by AXLE's standards.

**Common reasons for rejection:**

- Using `native_decide` or other disallowed tactics
- The proof proves a different statement than expected
- Other AXLE-specific validation rules

**Resolution:** Check `tool_messages.errors` for declaration-specific messages explaining why the proof was rejected.

### "All Executors Failed After N Attempts"

**Symptom:** Request fails with an error like `all executors failed after N attempts`.

**Cause:** This indicates a runtime error or crash on the server side. The most likely cause is an out-of-memory (OOM) condition, where the server kills runaway Lean processes that exceed memory limits.

**Resolution:** Check your input for patterns that might cause excessive memory usage:

- Very large files or deeply nested expressions
- Proofs that trigger expensive elaboration
- Tactics that generate large proof terms

Try simplifying your input or breaking it into smaller pieces.

### Limited Concurrency

**Symptom:** Requests are being throttled or you're hitting concurrency limits.

**Resolution:**

1. **Get and set an API key.** Authenticated requests have higher rate limits. See [Configuration](configuration.md) for details.

2. **Increase client-side concurrency.** Set the `AXLE_MAX_CONCURRENCY` environment variable to allow more concurrent requests from your client.

### Slow Requests / Timing Mismatches

**Symptom:** Requests take longer than expected, or reported timings don't match end-to-end latency.

**Cause:** Several server-side factors can affect request duration:

- **Warmup time** — Cold environments need initialization
- **Queue delays** — Requests may wait for available executors or hit rate limits
- **Server load** — Shared infrastructure can experience slowdowns

**Note:** The request timeout does not necessarily correspond to end-to-end delay. Server-reported timings reflect processing time, not total round-trip time including queue wait.

### Tool-Specific Issues

For troubleshooting specific to individual tools, see the documentation for that tool in the [Tools](tools/verify_proof.md) section.
