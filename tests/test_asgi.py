from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.types import ASGIApp

from httpx_sse import aconnect_sse


@pytest.fixture
def app() -> ASGIApp:
    async def auth_events(request: Request) -> Response:
        async def events() -> AsyncIterator[dict]:
            yield {
                "event": "login",
                "data": '{"user_id": "4135"}',
            }

        return EventSourceResponse(events())

    return Starlette(routes=[Route("/sse/auth/", endpoint=auth_events)])


@pytest_asyncio.fixture
async def client(app: ASGIApp) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app) as client:
        yield client


@pytest.mark.asyncio
async def test_asgi_test(client: httpx.AsyncClient) -> None:
    async with aconnect_sse(
        client, "GET", "http://testserver/sse/auth/"
    ) as event_source:
        events = [sse async for sse in event_source.aiter_sse()]
        (sse,) = events
        assert sse.event == "login"
        assert sse.json() == {"user_id": "4135"}
