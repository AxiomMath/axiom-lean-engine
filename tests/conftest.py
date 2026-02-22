"""Pytest configuration and fixtures for AXLE tests."""

import pytest


@pytest.fixture
def mock_verify_response() -> dict:
    """Mock response for verify_proof endpoint."""
    return {
        "okay": True,
        "content": "import Mathlib\n\ntheorem test : 1 = 1 := rfl\n",
        "lean_messages": {"errors": [], "warnings": [], "infos": []},
        "tool_messages": {"errors": [], "warnings": [], "infos": []},
        "failed_declarations": [],
        "timings": {"total": 100},
        "info": None,
    }
