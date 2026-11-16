from typing import Optional

import httpx


class SSEError(httpx.TransportError):
    def __init__(
        self,
        message: str,
        *,
        request: Optional[httpx.Request] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message, request=request)
        self.response = response
