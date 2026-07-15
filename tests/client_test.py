"""Tests for the AXLE client response types."""

import json
from unittest.mock import AsyncMock

import pytest

from axle.client import AxleClient
from axle.exceptions import AxleRuntimeError, LeanResourceExceeded, LeanTimeout
from axle.types import VerifyProofResponse


def test_verify_proof_response(mock_verify_response: dict) -> None:
    response = VerifyProofResponse.from_response(mock_verify_response)
    assert response.okay is True


async def test_run_one_raises_resource_exceeded() -> None:
    client = AxleClient(url="http://test")
    client._call = AsyncMock(  # type: ignore[method-assign]
        return_value=json.dumps(
            {
                "error": "signal: GNU MP: Cannot allocate memory (size=6678118440)",
                "error_type": "LeanResourceExceeded",
            }
        )
    )
    with pytest.raises(LeanResourceExceeded, match="Cannot allocate memory"):
        await client.run_one("disprove", {})


async def test_run_one_raises_timeout() -> None:
    client = AxleClient(url="http://test")
    client._call = AsyncMock(  # type: ignore[method-assign]
        return_value=json.dumps(
            {"error": "lean worker timeout after 60.0s", "error_type": "LeanTimeout"}
        )
    )
    with pytest.raises(LeanTimeout, match="timeout"):
        await client.run_one("disprove", {})


async def test_run_one_untyped_error_still_runtime_error() -> None:
    client = AxleClient(url="http://test")
    client._call = AsyncMock(  # type: ignore[method-assign]
        return_value=json.dumps({"error": "All executors failed after 3 attempt(s)"})
    )
    with pytest.raises(AxleRuntimeError):
        await client.run_one("disprove", {})


def _client_with_environments(envs: list[dict]) -> AxleClient:
    client = AxleClient(url="http://test")
    client.environments = AsyncMock(return_value=envs)  # type: ignore[method-assign]
    return client


async def test_get_latest_environment_picks_highest_basic_lean() -> None:
    client = _client_with_environments(
        [
            {"name": "lean-4.9.0"},
            {"name": "lean-4.28.0"},
            {"name": "lean-4.31.0"},
            {"name": "custom-lib"},
            {"name": "custom-env-4.28.0"},
        ]
    )
    assert await client.get_latest_environment() == {"name": "lean-4.31.0"}


async def test_get_latest_environment_includes_rc_when_it_is_newest() -> None:
    client = _client_with_environments([{"name": "lean-4.31.0"}, {"name": "lean-4.32.0-rc1"}])
    assert await client.get_latest_environment() == {"name": "lean-4.32.0-rc1"}


async def test_get_latest_environment_prefers_release_over_its_rc() -> None:
    client = _client_with_environments(
        [{"name": "lean-4.32.0-rc2"}, {"name": "lean-4.32.0"}, {"name": "lean-4.32.0-rc1"}]
    )
    assert await client.get_latest_environment() == {"name": "lean-4.32.0"}


async def test_get_latest_environment_returns_none_when_no_basic_lean() -> None:
    client = _client_with_environments([{"name": "custom-lib"}, {"name": "custom-env-4.26.0"}])
    assert await client.get_latest_environment() is None
