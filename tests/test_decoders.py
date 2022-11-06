from typing import Iterator

import httpx

from httpx_sse import iter_sse

# NOTE: the 'whatwg_example*' test cases are inspired by:
# https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation  # noqa: E501


def test_iter_sse_whatwg_example1() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"data: YH00\n"
            yield b"data: +2\n"
            yield b"data: 10\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 1

    assert events[0].event == "message"
    assert events[0].data == "YH00\n+2\n10"
    assert events[0].id == ""
    assert events[0].retry is None


def test_iter_sse_whatwg_example2() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b": test stream\n"
            yield b"\n"
            yield b"data: first event\n"
            yield b"id: 1\n"
            yield b"\n"
            yield b"data: second event\n"
            yield b"id\n"
            yield b"\n"
            yield b"data:  third event\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 3

    assert events[0].event == "message"
    assert events[0].data == "first event"
    assert events[0].id == "1"
    assert events[0].retry is None

    assert events[1].event == "message"
    assert events[1].data == "second event"
    assert events[1].id == ""
    assert events[1].retry is None

    assert events[2].event == "message"
    assert events[2].data == " third event"
    assert events[2].id == ""
    assert events[2].retry is None


def test_iter_sse_whatwg_example3() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"data\n"
            yield b"\n"
            yield b"data\n"
            yield b"data\n"
            yield b"\n"
            yield b"data:\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 2

    assert events[0].event == "message"
    assert events[0].data == ""
    assert events[0].id == ""
    assert events[0].retry is None

    assert events[1].event == "message"
    assert events[1].data == "\n"
    assert events[1].id == ""
    assert events[1].retry is None


def test_iter_sse_whatwg_example4() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"data:test\n"
            yield b"\n"
            yield b"data: test\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 2

    assert events[0].event == "message"
    assert events[0].data == "test"
    assert events[0].id == ""
    assert events[0].retry is None

    assert events[1].event == "message"
    assert events[1].data == "test"
    assert events[1].id == ""
    assert events[1].retry is None


def test_iter_sse_event() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"event: logline\n"
            yield b"data: New user connected\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 1

    assert events[0].event == "logline"
    assert events[0].data == "New user connected"
    assert events[0].id == ""
    assert events[0].retry is None


def test_iter_sse_id_null() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"data: test\n"
            yield b"id: 123\0\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 1

    assert events[0].event == "message"
    assert events[0].data == "test"
    assert events[0].id == ""
    assert events[0].retry is None


def test_iter_sse_id_retry() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"retry: 10000\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 1

    assert events[0].event == "message"
    assert events[0].data == ""
    assert events[0].id == ""
    assert events[0].retry == 10000


def test_iter_sse_id_retry_invalid() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"retry: 1667a\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 0


def test_iter_sse_unknown_field() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b"something: ignore\n"
            yield b"\n"

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        stream=Body(),
    )

    events = list(iter_sse(response))
    assert len(events) == 0
