import httpx
import pytest

from httpx_sse import SSEError, SSETransport


def test_sse_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        # fmt: off
        text = (
            "data: test\n"
            "\n"
        )
        # fmt: on
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, text=text
        )

    mock_transport = httpx.MockTransport(handler)

    with httpx.Client(transport=SSETransport(mock_transport)) as client:
        with client.stream("GET", "sse://testserver") as response:
            assert response.request.headers["cache-control"] == "no-store"


def test_sse_transport_non_event_stream_received() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/plain"})

    mock_transport = httpx.MockTransport(handler)

    with httpx.Client(transport=SSETransport(mock_transport)) as client:
        with pytest.raises(SSEError, match="text/event-stream"):
            with client.stream("GET", "sse://testserver") as _:
                pass  # pragma: no cover


def test_sse_transport_default_parent() -> None:
    transport = SSETransport()
    assert isinstance(transport._parent, httpx.HTTPTransport)
