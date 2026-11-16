import httpx

from httpx_sse import SSEError


def test_sse_error() -> None:
    assert issubclass(SSEError, httpx.TransportError)


def test_sse_error_without_response_preserves_request() -> None:
    request = httpx.Request("GET", "https://example.org/events")
    error = SSEError("not an event stream", request=request)

    assert str(error) == "not an event stream"
    assert error.args == ("not an event stream",)
    assert error.request is request
    assert error.response is None
