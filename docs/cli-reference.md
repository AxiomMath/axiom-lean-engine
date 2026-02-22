# CLI Reference

## Global Options

```
axle [OPTIONS] COMMAND [ARGS]

Options:
  --version          Show version and exit
  --url URL          API server URL
  --json             Force JSON output
```

## Common Patterns

All commands require `--environment` (e.g., `--environment lean-4.28.0`).

Most commands accept a file path or `-` for stdin:

```bash
axle check file.lean --environment lean-4.28.0
cat file.lean | axle check - --environment lean-4.28.0
```

Many commands support `-o/--output` for writing to a file:

```bash
axle theorem2sorry solution.lean -o problem.lean --environment lean-4.28.0
```

### Parameter Formats

**List parameters** use comma-separated values:

```bash
axle theorem2sorry file.lean --names foo,bar,baz --environment lean-4.28.0
axle verify-proof statement.lean proof.lean --permitted-sorries helper1,helper2 --environment lean-4.28.0
```

**Dict parameters** use `key=value` pairs or a JSON file:

```bash
axle rename file.lean --declarations foo=bar,old_name=new_name --environment lean-4.28.0
axle rename file.lean --declarations '{"foo": "bar"}' --environment lean-4.28.0
```

**Boolean flags** that default to `true` use `--no-` prefix to disable:

```bash
axle verify-proof statement.lean proof.lean --no-use-def-eq --environment lean-4.28.0
axle normalize file.lean --no-failsafe --environment lean-4.28.0
```

## Exit Codes

- `0` - Success (operation completed without errors)
- `1` - Failure (general error)
- `2` - File exists error (use -f to overwrite)
- `3` - Validation failed (when using --strict flag)
- `130` - Interrupted (Ctrl+C)
