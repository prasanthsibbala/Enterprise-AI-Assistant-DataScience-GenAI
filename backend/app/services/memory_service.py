from collections import defaultdict, deque
from threading import Lock


class MemoryService:
    """Small in-memory conversation buffer for local development."""

    def __init__(self, max_messages: int = 12) -> None:
        self.max_messages = max_messages
        self._messages: dict[str, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )
        self._lock = Lock()

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._messages[session_id].append({"role": role, "content": content})

    def get_messages(self, session_id: str) -> list[dict[str, str]]:
        with self._lock:
            return list(self._messages.get(session_id, []))

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._messages.pop(session_id, None)


memory_service = MemoryService()
