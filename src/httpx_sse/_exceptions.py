from __future__ import annotations

from typing import Optional

import httpx


class SSEError(httpx.TransportError):
    """Raised when an SSE stream cannot be established or decoded.

    Attributes:
        response: The underlying HTTPX response, when available. Useful when
            the server returned a non-SSE body (e.g. JSON 401) so callers can
            inspect status, headers and content.
    """

    def __init__(
        self, message: str, *, response: Optional[httpx.Response] = None
    ) -> None:
        super().__init__(message)
        self.response = response
