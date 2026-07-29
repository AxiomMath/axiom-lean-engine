"""AXLE - Python client for the Axiom Lean Engine API."""

from axle.client import AxleClient
from axle.exceptions import (
    AxleApiError,
    AxleBrowserLoginRequiredError,
    AxleConflictError,
    AxleForbiddenError,
    AxleInternalError,
    AxleInvalidArgument,
    AxleIsUnavailable,
    AxleNotFoundError,
    AxleRateLimitedError,
    AxleRuntimeError,
    LeanResourceExceeded,
    LeanTimeout,
)
from axle.helpers import (
    inline_lean_messages,
    remove_comments,
)
from axle.types import (
    CheckResponse,
    DisproveResponse,
    Document,
    ExtractDeclsResponse,
    ExtractProofStatesResponse,
    ExtractTheoremsResponse,
    Have2LemmaResponse,
    Have2SorryResponse,
    MergeResponse,
    NormalizeResponse,
    ProofState,
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
    "AxleBrowserLoginRequiredError",
    "AxleConflictError",
    "AxleForbiddenError",
    "AxleInternalError",
    "AxleInvalidArgument",
    "AxleIsUnavailable",
    "AxleNotFoundError",
    "AxleRateLimitedError",
    "AxleRuntimeError",
    "LeanResourceExceeded",
    "LeanTimeout",
    # Helpers
    "inline_lean_messages",
    "remove_comments",
    # Response types
    "CheckResponse",
    "DisproveResponse",
    "Document",
    "ExtractDeclsResponse",
    "ExtractProofStatesResponse",
    "ExtractTheoremsResponse",
    "Have2LemmaResponse",
    "Have2SorryResponse",
    "MergeResponse",
    "NormalizeResponse",
    "ProofState",
    "RenameResponse",
    "RepairProofsResponse",
    "SimplifyTheoremsResponse",
    "Sorry2LemmaResponse",
    "Theorem2LemmaResponse",
    "Theorem2SorryResponse",
    "VerifyProofResponse",
]

__version__ = "0.1.0"
