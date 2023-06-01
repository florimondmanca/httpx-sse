import json

import pytest

from httpx_sse import ServerSentEvent


def test_sse_default() -> None:
    sse = ServerSentEvent()

    assert sse.event == "message"
    assert sse.data == ""
    assert sse.id == ""
    assert sse.retry is None


def test_sse_json() -> None:
    sse = ServerSentEvent()

    with pytest.raises(json.JSONDecodeError):
        sse.json()

    sse = ServerSentEvent(data='{"key": "value"}')
    assert sse.json() == {"key": "value"}

    sse = ServerSentEvent(data='["item1", "item2"]')
    assert sse.json() == ["item1", "item2"]


def test_sse_repr() -> None:
    sse = ServerSentEvent()
    assert repr(sse) == "ServerSentEvent(event='message')"

    sse = ServerSentEvent(data="data", retry=3, id="id", event="event")
    assert repr(sse) == "ServerSentEvent(event='event', data='data', id='id', retry=3)"
