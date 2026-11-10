"""
FastAPI Dependency Injection Providers.
"""

from app.repositories.base import GameRepository
from app.repositories.memory import InMemoryGameRepository
from app.services.game_service import GameService

# Application-level singleton repository for in-memory session persistence
_repository_instance = InMemoryGameRepository()


def get_game_repository() -> GameRepository:
    """Dependency provider returning the in-memory game repository."""
    return _repository_instance


def get_game_service() -> GameService:
    """Dependency provider returning GameService injected with repository."""
    return GameService(repository=_repository_instance)
