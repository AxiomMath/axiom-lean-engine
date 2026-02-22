.DEFAULT_GOAL := help

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  make all          Run setup-env, lint, and build"
	@echo ""
	@echo "Setup:"
	@echo "  make setup-env    Install dependencies, pre-commit hooks, and package"
	@echo ""
	@echo "Development:"
	@echo "  make lint         Run all linting checks (ruff, mypy, etc.)"
	@echo "  make test         Run test suite"
	@echo "  make test-v       Run test suite with verbose output"
	@echo ""
	@echo "Build:"
	@echo "  make build        Build package (sdist and wheel)"
	@echo "  make clean        Remove build artifacts"

.PHONY: all setup-env lint test test-v build clean

all: setup-env lint build

setup-env:
	uv sync
	uv run pre-commit install
	uv pip install -e .

lint: setup-env
	@uv run pre-commit run --all-files

test: setup-env
	uv run pytest tests/

test-v: setup-env
	uv run pytest -vvv tests/

build: setup-env
	uv run python -m build

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
