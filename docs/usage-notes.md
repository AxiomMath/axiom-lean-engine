# Usage Notes

Practical notes on understanding AXLE inputs and outputs.

## Understanding Messages

AXLE responses include two message fields: `lean_messages` and `tool_messages`. Both contain `errors`, `warnings`, and `infos` arrays.

### Lean Messages

`lean_messages` contains output from the Lean compiler itself.

AXLE was built to handle certain categories of errors—particularly those restricted to the proof body (e.g., failed tactics). For maximum safety, use AXLE with code that compiles, but most tools will attempt to work on code with errors.

### Tool Messages

`tool_messages` contains AXLE-specific logs and validation results. For most tools, the `errors` array is empty; fatal issues are raised as `user_error` or `internal_error` at the response level.

**Exceptions:**

- `verify_proof` and `check` include declaration-specific messages explaining why a proof might compile but still be invalid by AXLE's standards (e.g., using `native_decide`, proving a different statement, etc.)

### Message Severity

- **errors** — Something is wrong; the result may be unusable
- **warnings** — Something is suspicious but not fatal
- **infos** — Informational output (timing, debug info, etc.)

### Checking Results

If you expect output to compile, check `lean_messages.errors` first. A good rule of thumb: if the input compiles, the output should compile.

```python
result = await axle.rename(content=code, declarations={"old": "new"}, environment="lean-4.28.0")

if result.lean_messages.errors:
    print("Output has compilation errors:")
    for msg in result.lean_messages.errors:
        print(f"  {msg}")
else:
    print(result.content)
```

For **evaluation tools** (`verify_proof`, `check`), `lean_messages.errors` being non-empty is expected—it's diagnostic output for invalid code. Check `result.okay` for pass/fail.

## Limitations

### Header Handling

All requests to AXLE are assumed to have the same header (import statements), which is derived from the `imports` field of the environment. You can discover the expected imports for any environment by querying the [environments endpoint](configuration.md#discovering-available-environments).

By default, if your code includes a different header than the environment expects, AXLE will raise a user error. This strict behavior ensures you are aware of any import mismatches that could lead to unexpected results.

If you want AXLE to automatically replace mismatched imports with the environment's default header, set `ignore_imports=True` in your request. When enabled, AXLE will:

1. Log a warning about the import mismatch
2. Replace your code's import statements with the environment's default imports
3. Return the modified code in the `content` field of the response

Note that behavior may be inconsistent if the header in your code does not match the environment's expected header.

### AXLE Scope

AXLE was designed with simple imports, theorems, and definitions in mind. While we attempt to support other Lean commands and constructs (other declaration types, `open` commands, `section`/`namespace` blocks, etc.), and attempt to fail fast on them with the [`normalize`](tools/normalize.md) tool, we make no guarantees about stability when using AXLE with these constructs.
