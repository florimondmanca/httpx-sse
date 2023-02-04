from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Iterator

import httpx

from ._decoders import SSEDecoder
from ._exceptions import SSEError
from ._models import ServerSentEvent


class EventSource:
    def __init__(self, response: httpx.Response) -> None:
        content_type, _, _ = response.headers["content-type"].partition(";")

        if content_type != "text/event-stream":
            raise SSEError(
                "Expected response Content-Type to be 'text/event-stream', "
                f"got {content_type!r}"
            )

        self._response = response

    @property
    def response(self) -> httpx.Response:
        return self._response

    def iter_sse(self) -> Iterator[ServerSentEvent]:
        decoder = SSEDecoder()
        for line in self._response.iter_lines():
            line = line.rstrip("\n")
            sse = decoder.decode(line)
            if sse is not None:
                yield sse

    async def aiter_sse(self) -> AsyncIterator[ServerSentEvent]:
        decoder = SSEDecoder()
        async for line in self._response.aiter_lines():
            line = line.rstrip("\n")
            sse = decoder.decode(line)
            if sse is not None:
                yield sse


@contextmanager
def connect_sse(client: httpx.Client, url: str, **kwargs: Any) -> Iterator[EventSource]:
    headers = kwargs.pop("headers", {})
    headers["Accept"] = "text/event-stream"
    headers["Cache-Control"] = "no-store"

    with client.stream("GET", url, headers=headers, **kwargs) as response:
        yield EventSource(response)


@asynccontextmanager
async def aconnect_sse(
    client: httpx.AsyncClient,
    url: str,
    **kwargs: Any,
) -> AsyncIterator[EventSource]:
    headers = kwargs.pop("headers", {})
    headers["Accept"] = "text/event-stream"
    headers["Cache-Control"] = "no-store"

    async with client.stream("GET", url, headers=headers, **kwargs) as response:
        yield EventSource(response)
