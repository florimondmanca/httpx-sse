from typing import AsyncIterator

import httpx
import pytest

from httpx_sse import aiter_sse


@pytest.mark.asyncio
async def test_aiter_sse() -> None:
    class AsyncBody(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data: YH00\n"
            yield b"data: +2\n"
            yield b"data: 10\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=AsyncBody(),
    )

    events = [sse async for sse in aiter_sse(response)]
    assert len(events) == 1

    assert events[0].event == "message"
    assert events[0].data == "YH00\n+2\n10"
    assert events[0].id == ""
    assert events[0].retry is None
