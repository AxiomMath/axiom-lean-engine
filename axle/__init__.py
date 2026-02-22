"""AXLE - Python client for the Axiom Lean Engine API."""

from axle.client import AxleClient
from axle.exceptions import (
    AxleApiError,
    AxleConflictError,
    AxleForbiddenError,
    AxleInternalError,
    AxleInvalidArgument,
    AxleIsUnavailable,
    AxleNotFoundError,
    AxleRateLimitedError,
    AxleRuntimeError,
)
from axle.helpers import (
    inline_lean_messages,
    remove_comments,
)
from axle.types import (
    CheckResponse,
    DisproveResponse,
    Document,
    ExtractTheoremsResponse,
    Have2LemmaResponse,
    Have2SorryResponse,
    MergeResponse,
    NormalizeResponse,
    RenameResponse,
    RepairProofsResponse,
    SimplifyTheoremsResponse,
    Sorry2LemmaResponse,
    Theorem2LemmaResponse,
    Theorem2SorryResponse,
    VerifyProofResponse,
)

__all__ = [
    # Client
    "AxleClient",
    # Exceptions
    "AxleApiError",
    "AxleConflictError",
    "AxleForbiddenError",
    "AxleInternalError",
    "AxleInvalidArgument",
    "AxleIsUnavailable",
    "AxleNotFoundError",
    "AxleRateLimitedError",
    "AxleRuntimeError",
    # Helpers
    "inline_lean_messages",
    "remove_comments",
    # Response types
    "CheckResponse",
    "DisproveResponse",
    "Document",
    "ExtractTheoremsResponse",
    "Have2LemmaResponse",
    "Have2SorryResponse",
    "MergeResponse",
    "NormalizeResponse",
    "RenameResponse",
    "RepairProofsResponse",
    "SimplifyTheoremsResponse",
    "Sorry2LemmaResponse",
    "Theorem2LemmaResponse",
    "Theorem2SorryResponse",
    "VerifyProofResponse",
]

__version__ = "0.1.0"
