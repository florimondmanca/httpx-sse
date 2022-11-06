# httpx-sse

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.httpx-sse?branchName=master)](https://dev.azure.com/florimondmanca/public/_build?definitionId=19)
[![Coverage](https://codecov.io/gh/florimondmanca/httpx-sse/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/httpx-sse)
[![Package version](https://badge.fury.io/py/httpx-sse.svg)](https://pypi.org/project/httpx-sse)

Consume [Server-Sent Event (SSE)](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events) messages with [HTTPX](https://www.python-httpx.org).

**Table of contents**

- [Installation](#installation)
- [Quickstart](#quickstart)
- [How-To](#how-to)
- [API Reference](#api-reference)

## Installation

**NOTE**: This is alpha software. Please be sure to pin your dependencies.

```bash
# --Unreleased--
pip install git+https://github.com/florimondmanca/httpx-sse.git
```

## Quickstart

To consume Server-Sent Event streams with `httpx-sse`, you must do two things:

1. Make your HTTPX client use [`SSETransport`](#ssetransport) (or [`AsyncSSETransport`](#asyncssetransport)).
2. Consume events with [`iter_sse`](#iter_sse) (or [`aiter_sse`](#aiter_sse)).

Example usage:

```python
import httpx
from httpx_sse import SSETransport, iter_sse

with httpx.Client(transport=SSETransport()) as client:
    with httpx.stream("GET", "http://localhost:8000/sse") as response:
        for sse in iter_sse(response):
            print(sse.event, sse.data, sse.id, sse.retry)
```

You can try this against this example Starlette server ([credit](https://sysid.github.io/sse/)):

```python
# Requirements: pip install uvicorn starlette sse-starlette
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse

async def numbers(minimum, maximum):
    for i in range(minimum, maximum + 1):
        await asyncio.sleep(0.9)
        yield dict(data=i)

async def sse(request):
    generator = numbers(1, 5)
    return EventSourceResponse(generator)

routes = [
    Route("/sse", endpoint=sse)
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(app)
```

## How-To

### Handling reconnections

_(Advanced)_

`SSETransport` and `AsyncSSETransport` don't have reconnection built-in. This is because how to perform retries is generally dependent on your use case. As a result, if the connection breaks while attempting to read from the server, you will get an `httpx.ReadError` from `iter_sse()` (or `aiter_sse()`).

However, `httpx-sse` does allow implementing reconnection by using the `Last-Event-ID` and reconnection time (in milliseconds), exposed as `sse.id` and `sse.retry` respectively.

Here's how you might achieve this using [`stamina`](https://github.com/hynek/stamina)...

```python
import time
from typing import Iterator

import httpx
from httpx_sse import iter_sse, ServerSentEvent
from stamina import retry

def iter_sse_retrying(client, url):
    last_event_id = ""
    reconnection_delay = 0.0

    # `stamina` will apply jitter and exponential backoff on top of
    # the `retry` reconnection delay sent by the server.
    @retry(on=httpx.ReadError)
    def _fetch_events():
        nonlocal last_event_id, reconnection_delay

        time.sleep(reconnection_delay)

        headers = {"Last-Event-ID": last_event_id} if last_event_id else {}

        with client.stream("GET", url, headers=headers) as response:
            for sse in iter_sse(response):
                last_event_id = sse.id

                if sse.retry is not None:
                    reconnection_delay = sse.retry / 1000

                yield sse

    return _fetch_events()
```

Usage:

```python
with httpx.Client(transport=SSETransport()) as client:
    for sse in iter_sse_retrying(client, "http://localhost:8000/sse"):
        print(sse.event, sse.data)
```

## API Reference

### `SSETransport`

```python
__init__(parent: httpx.BaseTransport=None)
```

An HTTPX [transport](https://www.python-httpx.org/advanced/#custom-transports) for SSE requests.

This transport sets `Cache-Control: no-store` on the request, as per the SSE spec.

If the response `Content-Type` is not `text/event-stream`, the transport will raise an [`SSEError`](#sseerror).

### `AsyncSSETransport`

```python
__init__(parent: httpx.AsyncBaseTransport=None)
```

An async equivalent to `SSETransport`, for use with `httpx.AsyncClient`.

### `iter_sse`

`(response: httpx.Response) -> Iterator[ServerSentEvent]`

Consume response content as server-sent events.

```python
for sse in iter_sse(response):
    ...
```

### `aiter_sse`

`(response: httpx.Response) -> AsyncIterator[ServerSentEvent]`

Consume async response content as server-sent events.

```python
async for sse in aiter_sse(response):
    ...
```

### `ServerSentEvent`

Represents a server-sent event.

* `event: str` - Defaults to `"message"`.
* `data: str` - Defaults to `""`.
* `id: str` - Defaults to `""`.
* `retry: str | None` - Defaults to `None`.

### `SSEError`

An error that occurred while making a request to an SSE endpoint.

Parents:

* `httpx.TransportError`

## License

MIT
