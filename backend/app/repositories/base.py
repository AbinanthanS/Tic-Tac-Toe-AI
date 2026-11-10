"""
Abstract Game Repository Interface.
"""

from abc import ABC, abstractmethod
from app.domain.models import GameState


class GameRepository(ABC):
    """Abstract interface defining storage operations for GameState."""

    @abstractmethod
    def save(self, game: GameState) -> GameState:
        """Persist a new game session."""
        pass

    @abstractmethod
    def get_by_id(self, game_id: str) -> GameState | None:
        """Retrieve a game session by its ID. Returns None if not found."""
        pass

    @abstractmethod
    def update(self, game: GameState) -> GameState:
        """Update an existing game session."""
        pass

    @abstractmethod
    def delete(self, game_id: str) -> bool:
        """Delete a game session. Returns True if deleted, False if not found."""
        pass
