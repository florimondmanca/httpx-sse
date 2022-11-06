import json
from typing import Any, Optional


class ServerSentEvent:
    def __init__(
        self, event: str = None, data: str = None, id: str = None, retry: int = None
    ) -> None:
        if not event:
            event = "message"

        if data is None:
            data = ""

        if id is None:
            id = ""

        self._event = event
        self._data = data
        self._id = id
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

    def json(self) -> Any:
        return json.loads(self.data)
