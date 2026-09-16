# Installation

## Requirements

- Python 3.11 or higher
- An internet connection (to reach the AXLE API)

## Install from PyPI

```bash
pip install axiom-axle
```

<!-- Disable homebrew for now (not set up)
## Install CLI via Homebrew (macOS/Linux)

```bash
brew install axle
```
-->

## Install from Source

```bash
git clone https://github.com/AxiomMath/axiom-lean-engine.git
cd axiom-lean-engine
pip install -e .
```
or
```bash
pip install git+ssh://git@github.com/AxiomMath/axiom-lean-engine
```

## Development Installation

For development, install with dev dependencies:

```bash
git clone https://github.com/AxiomMath/axiom-lean-engine.git
cd axiom-lean-engine
make setup-env
```

This will:

- Install all dependencies (including dev tools)
- Set up pre-commit hooks
- Install the package in editable mode

## Verify Installation

```bash
# Check CLI
axle --version

# Check Python package
python -c "from axle import AxleClient; print('OK')"
```

## Next Steps

See the [Quick Start](quickstart.md) tutorial to get started.
