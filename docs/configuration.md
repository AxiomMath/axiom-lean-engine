# Configuration

AXLE can be configured via environment variables or constructor arguments.

## Authentication

AXLE uses API key authentication for active request rate limiting. Requests without an API key are limited to 10 concurrent active requests.

To obtain an API key, visit [axle.axiommath.ai/app/console](https://axle.axiommath.ai/app/console)

### Setting Your API Key

The recommended way to configure your API key is via the `AXLE_API_KEY` environment variable:

```bash
export AXLE_API_KEY=your-api-key
```

You can also pass it directly when creating the client (see [Python Configuration](#python-configuration) below).


## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AXLE_API_KEY` | — | API key for authentication |
| `AXLE_API_URL` | `https://axle.axiommath.ai` | API server URL |
| `AXLE_TIMEOUT_SECONDS` | `1_800` | Base timeout in seconds for retry window if service is temporarily unavailable |
| `AXLE_MAX_CONCURRENCY` | `20` | Max concurrent requests |

### Example

```bash
export AXLE_API_KEY=your-api-key
export AXLE_API_URL=https://axle.axiommath.ai
export AXLE_TIMEOUT_SECONDS=600
export AXLE_MAX_CONCURRENCY=50
```

## Python Configuration

### Constructor Arguments

```python
from axle import AxleClient

# API key from environment variable (recommended)
client = AxleClient()

# Explicit API key
client = AxleClient(api_key="your-api-key")

# Custom URL, timeout, and concurrency
client = AxleClient(
    api_key="your-api-key",
    url=AxleClient.DEFAULT_URL,
    base_timeout_seconds=600,
    max_concurrency=50,
)
```

All constructor arguments fall back to environment variables if not provided.

## CLI Configuration

The CLI reads the `AXLE_API_KEY` environment variable automatically. Set it before running CLI commands:

```bash
export AXLE_API_KEY=your-api-key
```

### Global Options

```bash
# Custom API URL
axle --url https://axle.axiommath.ai check file.lean --environment lean-4.28.0

# JSON output
axle --json check file.lean --environment lean-4.28.0

# Output to file
axle theorem2sorry input.lean --environment lean-4.28.0 -o output.lean
```


## Lean Environments

AXLE supports multiple Lean environments, each containing a specific Lean version and set of dependencies (e.g., Mathlib). Every API request requires an `environment` parameter specifying which environment to use. To get started, we recommend using the latest Lean + Mathlib version, which at the time of writing is packaged in `lean-4.28.0`.

### Discovering Available Environments

You can query the available environments using any access method:

#### Python

```python
import asyncio
from axle import AxleClient

async def main():
    async with AxleClient() as client:
        environments = await client.environments()
        for env in environments:
            print(f"{env.name}: {env.description}")

asyncio.run(main())
```

#### CLI

```bash
axle environments
```

#### HTTP API

```bash
curl -s https://axle.axiommath.ai/v1/environments | jq
```

### Environment Response Format

Each environment includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Environment identifier to use in requests (e.g., `"lean-4.28.0"`) |
| `lean_toolchain` | `str` | Lean toolchain version (e.g., `"leanprover/lean4:v4.26.0"`) |
| `repo_url` | `str | null` | Git repository URL for custom environments |
| `revision` | `str | null` | Git revision/commit hash for custom environments |
| `subdir` | `str | null` | Subdirectory within the repository |
| `imports` | `str` | Default imports available (e.g., `"import Mathlib"`) |
| `description` | `str` | Human-readable description |

### Example Environments

```json
[
  {
    "name": "lean-4.21.0",
    "lean_toolchain": "leanprover/lean4:v4.21.0",
    "imports": "import Mathlib",
    "description": "Lean 4.21.0 with Mathlib"
  },
  {
    "name": "pnt-4.26.0",
    "lean_toolchain": "leanprover/lean4:v4.26.0",
    "repo_url": "https://github.com/AlexKontorovich/PrimeNumberTheoremAnd",
    "revision": "d24e98e2384cd191486517bfca980576772f6c17",
    "imports": "import Mathlib\nimport PrimeNumberTheoremAnd",
    "description": "Lean + Mathlib version 4.26.0 with Terence Tao's Prime Number Theorem Project"
  }
]
```

See [Header Handling](usage-notes.md#header-handling) for important notes on how AXLE handles import statements.
