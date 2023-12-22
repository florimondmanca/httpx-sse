import httpx
import pytest

from httpx_sse import SSEError, aconnect_sse, connect_sse


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
