from typing import AsyncIterator, Iterator

import httpx
import pytest

from httpx_sse import SSEError, aconnect_sse, connect_sse
from httpx_sse._api import _aiter_sse_lines, _iter_sse_lines


@pytest.mark.parametrize(
    "content_type",
    [
        pytest.param("text/event-stream", id="exact"),
        pytest.param(
            "application/json, text/event-stream; charset=utf-8", id="contains"
        ),
    ],
)
def test_connect_sse(content_type: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/":
            return httpx.Response(200, text="Hello, world!")
        else:
            assert request.url.path == "/sse"
            text = "data: test\n\n"
            return httpx.Response(
                200, headers={"content-type": content_type}, text=text
            )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = client.request("GET", "http://testserver")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        with connect_sse(client, "GET", "http+sse://testserver/sse") as event_source:
            assert event_source.response.request.headers["cache-control"] == "no-store"


def test_connect_sse_non_event_stream_received() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/"
        return httpx.Response(200, text="Hello, world!")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SSEError, match="text/event-stream"):
            with connect_sse(client, "GET", "http://testserver") as event_source:
                for _ in event_source.iter_sse():
                    pass  # pragma: no cover


@pytest.mark.asyncio
async def test_aconnect_sse() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/":
            return httpx.Response(200, text="Hello, world!")
        else:
            assert request.url.path == "/sse"
            text = "data: test\n\n"
            return httpx.Response(
                200, headers={"content-type": "text/event-stream"}, text=text
            )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        response = await client.request("GET", "http://testserver")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        async with aconnect_sse(
            client, "GET", "http+sse://testserver/sse"
        ) as event_source:
            assert event_source.response.request.headers["cache-control"] == "no-store"


def test_iter_sse_lines_basic() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"line1\nli"
            yield b"ne2\n"

    response = httpx.Response(200, stream=Body())
    lines = list(_iter_sse_lines(response))
    assert lines == ["line1", "line2"]


def test_iter_sse_lines_with_flush() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"line1\npartial"

    response = httpx.Response(200, stream=Body())
    lines = list(_iter_sse_lines(response))
    assert lines == ["line1", "partial"]  # flush gets the partial line


@pytest.mark.asyncio
async def test_aiter_sse_lines_with_flush() -> None:
    class AsyncBody(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"line1\nno_newline"

    response = httpx.Response(200, stream=AsyncBody())
    lines = [line async for line in _aiter_sse_lines(response)]
    assert lines == ["line1", "no_newline"]  # flush gets the partial line
