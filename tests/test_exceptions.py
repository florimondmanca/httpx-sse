import httpx
import pytest

from httpx_sse import SSEError


def test_sse_error() -> None:
    assert issubclass(SSEError, httpx.TransportError)


def test_sse_error_carries_response() -> None:
    response = httpx.Response(401, headers={"content-type": "application/json"})
    err = SSEError("boom", response=response)
    assert err.response is response
