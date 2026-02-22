"""Exception hierarchy for AXLE."""


class AxleError(Exception):
    """The root of all evil (in this codebase, anyway)."""

    pass


class AxleIsUnavailable(AxleError):
    """The AXLE API server is not available."""

    def __init__(self, url: str, details: str | None = None):
        self.url = url
        self.details = details or "no details"
        message = f"Retryable error at {url}: {details}"
        if details:
            message += f": {details}"
        super().__init__(message)


class AxleApiError(AxleError):
    """Error returned by the AXLE API."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class AxleInternalError(AxleApiError):
    """Internal server error from AXLE.

    This indicates a bug in the AXLE server. Please report it.
    """

    def __init__(self, message: str):
        super().__init__(
            message
            + "\n\nCongratulations, you found a bug! Please file an issue at https://github.com/AxiomMath/axiom-lean-engine/issues"
        )


class AxleInvalidArgument(AxleApiError):
    """User provided invalid input to the API.

    This indicates the request was malformed or contained invalid parameters.
    Check the error message for details on what was wrong.
    """

    def __init__(self, message: str):
        super().__init__(message + "\n\nPlease check your input and try again.")


class AxleRuntimeError(AxleApiError):
    """Operation couldn't complete due to runtime constraints.

    This indicates the request was valid but the operation failed due to
    factors like timeouts, resource limits, or other runtime issues.
    """

    def __init__(self, message: str):
        super().__init__("Error 40-something: " + message)


class AxleForbiddenError(AxleApiError):
    """Request was blocked by the server (403 Forbidden)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=403)


class AxleNotFoundError(AxleApiError):
    """Requested resource was not found (404 Not Found)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class AxleConflictError(AxleApiError):
    """Request conflicts with current state (409 Conflict)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class AxleRateLimitedError(AxleApiError):
    """Request was rate limited (429 Too Many Requests).

    This is a transient error that should be retried after a delay.
    """

    def __init__(self, message: str):
        super().__init__(message, status_code=429)
