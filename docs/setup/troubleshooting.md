# Service Troubleshooting

Common issues with the AXLE service — capacity, connectivity, and auth — and how to resolve them. For issues with tool behavior and Lean output, see [Tool Troubleshooting](../tools/troubleshooting.md).

## Common Issues

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

2. **Increase client-side concurrency.** Set the `AXLE_MAX_CONCURRENCY` environment variable to allow more concurrent requests from your client. See [Configuration](configuration.md) for details.

3. **Request more capacity.** If you need higher rate limits, you can [request more capacity](https://forms.gle/CdLKu45tEsRXtFQ29).

### Slow Requests / Timing Mismatches

**Symptom:** Requests take longer than expected, or reported timings don't match end-to-end latency.

**Cause:** Several server-side factors can affect request duration:

- **Warmup time** — Cold environments need initialization
- **Queue delays** — Requests may wait for available executors or hit rate limits
- **Server load** — Shared infrastructure can experience slowdowns

**Note:** The request timeout does not necessarily correspond to end-to-end delay. Server-reported timings reflect processing time, not total round-trip time including queue wait.

If Lean execution time itself is too slow, see [Slow Lean Execution](../tools/troubleshooting.md#slow-lean-execution).

### HTTP 302 to a browser sign-in (`AxleBrowserLoginRequiredError`)
You may be attempting to access a forbidden internal tier.
