import httpx
import pytest

from httpx_sse import AsyncSSETransport


@pytest.mark.asyncio
async def test_async_sse_transport() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
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

    async with httpx.AsyncClient(transport=AsyncSSETransport(mock_transport)) as client:
        async with client.stream("GET", "sse://testserver") as response:
            assert response.request.headers["cache-control"] == "no-store"


def test_async_sse_transport_default_parent() -> None:
    transport = AsyncSSETransport()
    assert isinstance(transport._parent, httpx.AsyncHTTPTransport)
