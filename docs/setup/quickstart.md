# Quick Start

Try AXLE in your browser with the [interactive demo notebook](https://colab.research.google.com/github/AxiomMath/axiom-lean-engine/blob/main/examples/starting_demo.ipynb).

## MCP Server

The [`axiom-axle-mcp`](https://pypi.org/project/axiom-axle-mcp/) package wraps AXLE as a [Model Context Protocol](https://modelcontextprotocol.io/) server, so an AI agent can call `check`, `verify_proof`, `extract_theorems`, and the rest of AXLE's tools directly.

Supported clients include:

- **Claude Code, Cursor, Windsurf, VS Code, Cline**, and other editors that speak MCP — point them at the `axiom-axle-mcp` package locally.
- **Claude web, desktop, and mobile** — connect to the hosted server at `https://mcp.axiommath.ai/mcp` under Settings > Connectors.

See the [PyPI page](https://pypi.org/project/axiom-axle-mcp/) for detailed installation and config instructions.

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
        # okay means it compiled; failed_declarations catches sorry, disallowed axioms, etc. that leave okay true.
        print(f"Compiles: {result.okay}")
        print(f"Valid proof: {result.okay and not result.failed_declarations}")
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
