import tomllib
from pathlib import Path

import axle


def test_version_matches_pyproject() -> None:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        assert axle.__version__ == tomllib.load(f)["project"]["version"]
