"""
Thread-safe in-memory implementation of GameRepository.
"""

import threading
from app.domain.models import GameState
from app.repositories.base import GameRepository


class InMemoryGameRepository(GameRepository):
    """
    In-memory storage for active game sessions.
    Thread-safe via threading.Lock to support concurrent ASGI worker threads.
    """

    def __init__(self) -> None:
        self._storage: dict[str, GameState] = {}
        self._lock = threading.Lock()

    def save(self, game: GameState) -> GameState:
        with self._lock:
            self._storage[game.id] = game
            return game

    def get_by_id(self, game_id: str) -> GameState | None:
        with self._lock:
            return self._storage.get(game_id)

    def update(self, game: GameState) -> GameState:
        with self._lock:
            self._storage[game.id] = game
            return game

    def delete(self, game_id: str) -> bool:
        with self._lock:
            if game_id in self._storage:
                del self._storage[game_id]
                return True
            return False

    def clear(self) -> None:
        """Utility for test suites to wipe state between test runs."""
        with self._lock:
            self._storage.clear()

