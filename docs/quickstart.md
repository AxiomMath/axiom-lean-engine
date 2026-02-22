# Quick Start

Try AXLE in your browser with the [interactive demo notebook](https://colab.research.google.com/github/AxiomMath/axiom-lean-engine/blob/main/examples/starting_demo.ipynb).

## Prerequisites

Before using AXLE, set your API key:

```bash
export AXLE_API_KEY=your-api-key
```

See [Configuration](configuration.md#authentication) for more details.

## Basic Usage

### Check Lean Code

The simplest operation is checking if Lean code is valid:

#### Python

```python
import asyncio
from axle import AxleClient

async def main():
    async with AxleClient() as client:
        result = await client.check(
            content="import Mathlib\ntheorem citation_needed : 1 + 1 = 2 := by decide",
            environment="lean-4.28.0",
        )
        print(f"Valid: {result.okay}")
        if result.lean_messages.errors:
            print("Errors:", result.lean_messages.errors)

asyncio.run(main())
```

#### CLI

```bash
# From file
axle check mytheorem.lean --environment lean-4.28.0

# From stdin
echo "def meaning_of_life := 42\n#print meaning_of_life" | axle check - --environment lean-4.28.0
```

#### HTTP API

```bash
curl -s -X POST https://axle.axiommath.ai/api/v1/check \
    -H "Authorization: Bearer $AXLE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"content": "import Mathlib\ntheorem citation_needed : 1 + 1 = 2 := by decide", "environment": "lean-4.28.0"}' | jq
```

## Next Steps

- [Python API Reference](python-api.md) - Full API documentation
- [CLI Reference](cli-reference.md) - All CLI commands
- [Configuration](configuration.md) - Environment variables and options
