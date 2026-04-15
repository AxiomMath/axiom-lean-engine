"""Response types for AXLE API."""

from dataclasses import dataclass


@dataclass
class Messages:
    errors: list[str]
    warnings: list[str]
    infos: list[str]

    @classmethod
    def from_response(cls, response: dict) -> "Messages":
        return cls(
            errors=response.get("errors", []),
            warnings=response.get("warnings", []),
            infos=response.get("infos", []),
        )


@dataclass
class VerifyProofResponse:
    okay: bool
    content: str
    lean_messages: Messages
    tool_messages: Messages
    failed_declarations: list[str]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "VerifyProofResponse":
        return cls(
            okay=response.get("okay", False),
            content=response.get("content", ""),
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            failed_declarations=response.get("failed_declarations", []),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class Document:
    """A single declaration extracted from Lean code (theorem, def, structure, etc.)."""

    name: str
    kind: str
    declaration: str
    content: str
    tokens: list[str]
    signature: str
    type: str
    type_hash: int
    is_sorry: bool
    index: int
    line_pos: int
    end_line_pos: int
    proof_length: int
    tactic_counts: dict[str, int]
    local_type_dependencies: list[str]
    local_value_dependencies: list[str]
    external_type_dependencies: list[str]
    external_value_dependencies: list[str]
    local_syntactic_dependencies: list[str]
    external_syntactic_dependencies: list[str]
    declaration_messages: Messages
    theorem_messages: Messages  # Deprecated: use declaration_messages instead

    @classmethod
    def from_response(cls, name: str, response: dict) -> "Document":
        return cls(
            name=name,
            kind=response.get("kind", ""),
            declaration=response.get("declaration", ""),
            content=response.get("content", ""),
            tokens=response.get("tokens", []),
            signature=response.get("signature", ""),
            type=response.get("type", ""),
            type_hash=response.get("type_hash", 0),
            is_sorry=response.get("is_sorry", False),
            index=response.get("index", 0),
            line_pos=response.get("line_pos", 0),
            end_line_pos=response.get("end_line_pos", 0),
            proof_length=response.get("proof_length", 0),
            tactic_counts=response.get("tactic_counts", {}),
            local_type_dependencies=response.get("local_type_dependencies", []),
            local_value_dependencies=response.get("local_value_dependencies", []),
            external_type_dependencies=response.get("external_type_dependencies", []),
            external_value_dependencies=response.get("external_value_dependencies", []),
            local_syntactic_dependencies=response.get("local_syntactic_dependencies", []),
            external_syntactic_dependencies=response.get("external_syntactic_dependencies", []),
            declaration_messages=Messages.from_response(response.get("declaration_messages", {})),
            theorem_messages=Messages.from_response(response.get("theorem_messages", {})),
        )


@dataclass
class ExtractTheoremsResponse:
    content: str
    lean_messages: Messages
    tool_messages: Messages
    documents: dict[str, Document]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "ExtractTheoremsResponse":
        return cls(
            content=response.get("content", ""),
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            documents={
                k: Document.from_response(k, v) for k, v in response.get("documents", {}).items()
            },
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class ExtractDeclsResponse:
    content: str
    lean_messages: Messages
    tool_messages: Messages
    documents: dict[str, Document]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "ExtractDeclsResponse":
        return cls(
            content=response.get("content", ""),
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            documents={
                k: Document.from_response(k, v) for k, v in response.get("documents", {}).items()
            },
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class RenameResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "RenameResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class MergeResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "MergeResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class Theorem2SorryResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "Theorem2SorryResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class Theorem2LemmaResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "Theorem2LemmaResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class CheckResponse:
    okay: bool
    content: str
    lean_messages: Messages
    tool_messages: Messages
    failed_declarations: list[str]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "CheckResponse":
        return cls(
            okay=response.get("okay", False),
            content=response.get("content", ""),
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            failed_declarations=response.get("failed_declarations", []),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class SimplifyTheoremsResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    simplification_stats: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "SimplifyTheoremsResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            simplification_stats=response.get("simplification_stats", {}),
            info=response.get("info"),
        )


@dataclass
class RepairProofsResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    repair_stats: dict[str, int]
    info: dict | None
    okay: bool

    @classmethod
    def from_response(cls, response: dict) -> "RepairProofsResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            repair_stats=response.get("repair_stats", {}),
            info=response.get("info"),
            okay=response.get("okay", False),
        )


@dataclass
class Have2LemmaResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    lemma_names: list[str]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "Have2LemmaResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            lemma_names=response.get("lemma_names", []),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class Have2SorryResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "Have2SorryResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class Sorry2LemmaResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    lemma_names: list[str]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "Sorry2LemmaResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            lemma_names=response.get("lemma_names", []),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class DisproveResponse:
    content: str
    lean_messages: Messages
    tool_messages: Messages
    results: dict[str, str]
    disproved_theorems: list[str]
    timings: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "DisproveResponse":
        return cls(
            content=response.get("content", ""),
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            results=response.get("results", {}),
            disproved_theorems=response.get("disproved_theorems", []),
            timings=response.get("timings", {}),
            info=response.get("info"),
        )


@dataclass
class NormalizeResponse:
    lean_messages: Messages
    tool_messages: Messages
    content: str
    timings: dict[str, int]
    normalize_stats: dict[str, int]
    info: dict | None

    @classmethod
    def from_response(cls, response: dict) -> "NormalizeResponse":
        return cls(
            lean_messages=Messages.from_response(response.get("lean_messages", {})),
            tool_messages=Messages.from_response(response.get("tool_messages", {})),
            content=response.get("content", ""),
            timings=response.get("timings", {}),
            normalize_stats=response.get("normalize_stats", {}),
            info=response.get("info"),
        )
