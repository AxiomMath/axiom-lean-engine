# AXLE - Axiom Lean Engine

## Proof manipulation as infrastructure, not an afterthought

AXLE is a set of Lean utilities for theorem proving: validating candidate proofs, splitting theorems from larger files, converting proofs to `sorry`, and more. They are written as Lean metaprograms to be robust.

## Features

- **Proof Verification**: Validate proofs against formal statements
- **Code Analysis**: Check Lean code for errors and extract theorems
- **Code Transformation**: Rename declarations, convert keywords, simplify proofs

## Usage Methods

AXLE can be accessed through:

1. **Web Interface** - Interactive UI at [https://axle.axiommath.ai/](https://axle.axiommath.ai/)
2. **Python API** - `pip install axiom-axle` ([Python API Reference](python-api.md))
3. **CLI** - `axle verify-proof`, `axle check`, etc. ([CLI Reference](cli-reference.md))
4. **HTTP API** - Direct REST calls with `curl`

See the [Quick Start](quickstart.md) tutorial for examples of each method.

## Available Tools

| Endpoint | Description |
|----------|-------------|
| `verify_proof` | Validate a proof against a formal statement |
| `check` | Check Lean code for errors |
| `extract_theorems` | Split file into individual theorems with dependencies |
| `extract_decls` | Split file into individual declarations with dependencies |
| `rename` | Rename declarations |
| `theorem2lemma` | Convert between `theorem` and `lemma` keywords |
| `theorem2sorry` | Strip proofs from theorems |
| `merge` | Combine multiple Lean files |
| `simplify_theorems` | Simplify theorem proofs |
| `repair_proofs` | Attempt to repair broken proofs |
| `have2lemma` | Extract `have` statements to standalone lemmas |
| `have2sorry` | Replace `have` statements with `sorry` |
| `sorry2lemma` | Extract `sorry` and errors to standalone lemmas |
| `disprove` | Attempt to disprove theorems |
| `normalize` | Standardize Lean formatting |

See tools documentation for detailed parameters and response fields.

## Links

- [Installation Guide](installation.md)
- [Quick Start Tutorial](quickstart.md)
- [Python API Reference](python-api.md)
- [CLI Reference](cli-reference.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)

## Public Deployments

AXLE's public deployment follows a weekly release schedule:

- **Maintenance Window**: Every Wednesday at 10:00 AM Pacific Time
- **Expected Downtime**: Brief interruption (typically under 5 minutes) during restart
- **Updates**: New features, bug fixes, and improvements deployed weekly

After each deployment, the [changelog](https://github.com/AxiomMath/axiom-lean-engine/blob/main/CHANGELOG.md) is updated with details on what changed.

## Submitting Issues

If you encounter bugs, unexpected behavior, or have feature requests:

<a href="https://github.com/AxiomMath/axiom-lean-engine/issues/new?title=Bug%20report%3A%20AXLE&body=%23%23%23%20Bug%20Description%0A%3C%21--%20Please%20describe%20the%20issue%20you%20encountered%20--%3E%0A%0A%0A%0A%23%23%23%20Expected%20Behavior%0A%3C%21--%20What%20did%20you%20expect%20to%20happen%3F%20--%3E%0A%0A%0A%0A%23%23%23%20Actual%20Behavior%0A%3C%21--%20What%20actually%20happened%3F%20--%3E%0A%0A%0A%0A%23%23%23%20Reproduction%20Details%0A-%20%2A%2ATool%3A%2A%2A%20%0A-%20%2A%2AEnvironment%3A%2A%2A%20%0A-%20%2A%2ALink%3A%2A%2A%20%0A%0A%23%23%23%20Additional%20Context%0A%3C%21--%20Add%20any%20other%20context%20about%20the%20problem%20here%20--%3E%0A" target="_blank" class="file-bug-btn">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
  </svg>
  FILE A BUG
</a>

## Resources

- [Axiom Homepage](https://axiommath.ai/)
- [Lean Homepage](https://lean-lang.org/)
- [Mathlib](https://leanprover-community.github.io) - Mathematics library for Lean 4
- [Lean Zulip](https://leanprover.zulipchat.com/) - Community discussion
- [AXLE on Zulip](https://leanprover.zulipchat.com/#narrow/channel/219941-Machine-Learning-for-Theorem-Proving/topic/Axiom.20Lean.20Engine/with/577859288) - Discussion thread for AXLE
- [axiom-axle-mcp](https://pypi.org/project/axiom-axle-mcp/) - MCP server for AXLE
- [Pantograph](https://github.com/lenianiva/Pantograph) - Machine-to-machine interaction interface for Lean
