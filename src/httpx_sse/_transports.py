import httpx

from ._exceptions import SSEError


class SSETransport(httpx.BaseTransport):
    def __init__(self, parent: httpx.BaseTransport = None) -> None:
        if parent is None:
            parent = httpx.HTTPTransport()

        self._parent = parent

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        _prepare_request(request)
        response = self._parent.handle_request(request)
        _check_response(response)
        return response


class AsyncSSETransport(httpx.AsyncBaseTransport):
    def __init__(self, parent: httpx.AsyncBaseTransport = None) -> None:
        if parent is None:
            parent = httpx.AsyncHTTPTransport()

        self._parent = parent

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        _prepare_request(request)
        response = await self._parent.handle_async_request(request)
        _check_response(response)
        return response


# See:
# https://html.spec.whatwg.org/multipage/server-sent-events.html#the-eventsource-interface


def _prepare_request(request: httpx.Request) -> None:
    request.headers["Cache-Control"] = "no-store"


def _check_response(response: httpx.Response) -> None:
    content_type, _, _ = response.headers["content-type"].partition(";")

    if content_type != "text/event-stream":
        raise SSEError(
            "Expected response Content-Type to be 'text/event-stream', "
            f"got {content_type!r}"
        )
