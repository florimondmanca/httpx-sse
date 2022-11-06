from typing import Optional


class ServerSentEvent:
    def __init__(
        self, event: str = None, data: str = None, id: str = None, retry: int = None
    ) -> None:
        self._event = "message" if event is None else event
        self._data = "" if data is None else data
        self._id = "" if id is None else id
        self._retry = retry

    @property
    def event(self) -> str:
        return self._event

    @property
    def data(self) -> str:
        return self._data

    @property
    def id(self) -> str:
        return self._id

    @property
    def retry(self) -> Optional[int]:
        return self._retry
