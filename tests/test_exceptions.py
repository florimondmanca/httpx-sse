import httpx

from httpx_sse import SSEError


def test_sse_error() -> None:
    assert issubclass(SSEError, httpx.TransportError)
