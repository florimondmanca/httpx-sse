from httpx_sse import ServerSentEvent


def test_server_sent_event_default() -> None:
    sse = ServerSentEvent()

    assert sse.event == "message"
    assert sse.data == ""
    assert sse.id == ""
    assert sse.retry is None
