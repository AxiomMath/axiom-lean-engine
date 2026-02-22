# Python API Reference

## Axle Client

The main client for interacting with the AXLE API.

### Basic Usage

```python
import asyncio
from axle import AxleClient

async def main():
    async with AxleClient() as client:
        result = await client.check(content="import Mathlib\ndef x := 1", environment="lean-4.28.0")
        print(f"Valid: {result.okay}")

asyncio.run(main())
```

### Constructor

```python
AxleClient(
    api_key: str | None = None,          # default: AXLE_API_KEY env var
    url: str | None = None,              # default: AXLE_API_URL env var
    max_concurrency: int | None = None,  # default: AXLE_MAX_CONCURRENCY env var
    base_timeout_seconds: float | None = None,  # default: AXLE_TIMEOUT_SECONDS env var
)
```

All arguments fall back to their corresponding environment variables if not provided. See [Configuration](configuration.md#environment-variables) for details.

## Error Handling

All errors raise exceptions. Use try/except to handle them:

```python
from axle.exceptions import (
    AxleIsUnavailable,
    AxleRuntimeError,
    AxleInternalError,
    AxleInvalidArgument,
    AxleRateLimitedError,
    AxleForbiddenError,
    AxleNotFoundError,
    AxleConflictError,
)

try:
    result = await axle.check(content=code, environment="lean-4.28.0")
except AxleIsUnavailable as e:
    print(f"API unavailable at {e.url}: {e.details}")
except AxleInvalidArgument as e:
    print(f"Invalid request: {e}")
except AxleInternalError as e:
    print(f"Server error: {e}")
except AxleRuntimeError as e:
    print(f"Operation failed: {e}")
```

| Exception | HTTP Status | Cause | Action |
|-----------|-------------|-------|--------|
| `AxleIsUnavailable` | 503 | Cannot reach API server (connection refused, DNS failure, service unavailable, service upgrade) | Automatically retried; check network if persistent |
| `AxleRateLimitedError` | 429 | Too many requests | Automatically retried with backoff |
| `AxleInvalidArgument` | 400 | Malformed request (missing parameters, invalid arguments) | Fix the request |
| `AxleForbiddenError` | 403 | Access denied | Check credentials/permissions |
| `AxleNotFoundError` | 404 | Resource not found | Check the endpoint or resource ID |
| `AxleConflictError` | 409 | Request conflicts with current state | Resolve the conflict |
| `AxleInternalError` | 500 | Server bug | [Report it](https://github.com/AxiomMath/axiom-lean-engine/issues) |
| `AxleRuntimeError` | — | Operation couldn't complete (timeout, resource limits) | Retry or adjust parameters |

### Automatic Retries

The client automatically retries transient errors with exponential backoff:

- `AxleIsUnavailable` (503, connection errors)
- `AxleRateLimitedError` (429)

Non-retryable errors like `AxleInternalError` (500) and client errors (4xx) are raised immediately.

To catch all API errors at once, use the base class `AxleApiError`.
