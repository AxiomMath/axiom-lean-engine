"""Tests for the AXLE client response types."""

from axle.types import VerifyProofResponse


def test_verify_proof_response(mock_verify_response: dict) -> None:
    response = VerifyProofResponse.from_response(mock_verify_response)
    assert response.okay is True
