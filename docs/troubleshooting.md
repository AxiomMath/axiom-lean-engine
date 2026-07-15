# Troubleshooting

Common issues when working with AXLE and how to resolve them.

## Reading Error Messages

### Fatal Errors

When a request fails entirely, the response includes an error type at the top level:

| Error Type | Meaning | Action |
|------------|---------|--------|
| `user_error` | Invalid request (missing parameters, bad arguments, import mismatch) | Fix the request—check your inputs |
| `internal_error` | Server bug | [Report it](https://github.com/AxiomMath/axiom-lean-engine/issues) |
| `error` | Runtime failure that exhausted internal retries (executor crash) | Rarely worth retrying—AXLE already retried internally |
| `error` + `error_type: LeanResourceExceeded` | Lean worker hit a resource cap (e.g. memory) for this input | Reduce the problem's memory allocation |
| `error` + `error_type: LeanTimeout` | Lean worker exceeded its time budget for this input | Simplify the input or raise the timeout |

In the Python client, these map to exceptions: `AxleInvalidArgument`, `AxleInternalError`, `AxleRuntimeError`, `LeanResourceExceeded`, and `LeanTimeout`. See [Error Handling](python-api.md#error-handling) for details on catching and handling these exceptions, and for an exhaustive list of all AXLE exceptions, including networking errors.

### Resource Limits

Each request runs in a worker with a default time budget of **120 seconds** and a cap of **16 GB** on allocatable working memory. Exceeding the time budget yields a `LeanTimeout`; exceeding the memory cap yields a `LeanResourceExceeded`. The timeout is configurable per request via the `timeout_seconds` parameter, up to a maximum of 900 seconds (15 minutes).

### Non-Fatal Errors
When troubleshooting, start by examining the messages in the response. AXLE responses include two message fields, each containing `errors`, `warnings`, and `infos` arrays:

| Field | Contents |
|-------|----------|
| `lean_messages` | Output from the Lean compiler itself; an empty `errors` list means the code compiles |
| `tool_messages` | AXLE-specific logs and validation results |

**Message severity:**

- **errors** — Something is wrong; the result may be unusable
- **warnings** — Something is suspicious but not fatal
- **infos** — Informational output (timing, debug info, etc.)

For most tools, `tool_messages.errors` is empty; fatal issues are raised at the response level (see above). The exceptions are `verify_proof`, which uses `tool_messages.errors` to report strict proof verification failures, and `repair_proofs`, which uses it to report failed repairs.

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


### Import Mismatches

**Symptom:** Your code's imports don't match the environment's default header, and you get an info/warning message or unexpectedly slow (or incorrect) results.

**Cause:** Every environment has a default header derived from its `imports` field. AXLE keeps a pre-built environment for that header so requests run fast. When your code's imports differ from it, AXLE's behavior depends on the `ignore_imports` flag.

**Behavior:**

- **`ignore_imports=True` (default):** AXLE ignores the imports in your `content` and substitutes the environment's default header. This reuses the cached environment, so it is fast. The substituted code is returned in the `content` field, and an info message notes the override.

- **`ignore_imports=False`:** AXLE processes your imports exactly as written. This is *significantly slower* because the cached environment cannot be reused, and it may produce **inconsistent or incorrect results** if a required dependency (such as `Mathlib.Tactic`) is missing. AXLE returns a warning in these cases.

**Recommendation:** Leave `ignore_imports` at its default (`True`) unless you specifically need custom imports. To discover the expected imports for an environment, query the [environments endpoint](configuration.md#discovering-available-environments).

### Unsupported Lean Constructs

**Symptom:** Unexpected behavior or errors with certain Lean code patterns.

**Cause:** AXLE was designed with simple imports, theorems, and definitions in mind.

**Potentially unsupported constructs:**

- Non-standard declaration types
- `open` commands
- `section`/`namespace` blocks
- Complex macro usage

**Resolution:** Use the [`normalize`](tools/normalize.md) tool to detect unsupported constructs early. We attempt to support these patterns and fail fast when we can't, but we make no guarantees about stability.

### Interpreting the `okay` Field

For every tool, `okay` is `true` exactly when `lean_messages.errors` is empty (the code compiles) and `tool_messages.errors` is empty (no tool-specific errors). What differs is what each tool reports as a tool error:

- **`check`** — compilation only. It produces no tool errors: validation findings (a declaration that uses `sorry`, a disallowed axiom, or an unsafe definition) are reported as `tool_messages` warnings, with the offending names in `failed_declarations`, and do **not** move `okay`. To treat `check` as a pass/fail for a real proof, require `result.okay and not result.failed_declarations`, or better yet, use `verify_proof`.
- **`verify_proof`** — compilation + strict proof verification. Tool errors are verification failures: the findings above, plus a signature mismatch or a missing declaration. Any of them sets `okay: false`.
- **`repair_proofs`** — compilation + no failed repairs. A failed repair — a repair was detected as necessary, but no successful change could fix it (e.g. a `sorry` that no terminal tactic could prove, or a `native_decide` that can't be safely replaced) — is a tool error and sets `okay: false`.

If you just want a single "is this a complete, valid proof" answer, use `verify_proof`.

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

3. **Request more capacity.** If you need higher rate limits, you can [request more capacity](https://forms.gle/CdLKu45tEsRXtFQ29).

### Slow Requests / Timing Mismatches

**Symptom:** Requests take longer than expected, or reported timings don't match end-to-end latency.

**Cause:** Several server-side factors can affect request duration:

- **Warmup time** — Cold environments need initialization
- **Queue delays** — Requests may wait for available executors or hit rate limits
- **Server load** — Shared infrastructure can experience slowdowns

**Note:** The request timeout does not necessarily correspond to end-to-end delay. Server-reported timings reflect processing time, not total round-trip time including queue wait.

### Tool-Specific Issues

For troubleshooting specific to individual tools, see the documentation for that tool in the [Tools](tools/verify_proof.md) section.

### HTTP 302 to a browser sign-in (`AxleBrowserLoginRequiredError`)
You may be attempting to access a forbidden internal tier.
