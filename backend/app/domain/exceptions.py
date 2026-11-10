"""
Domain exceptions representing business and game rule violations.
"""

class DomainError(Exception):
    """Base class for all domain-specific errors."""
    pass


class InvalidMoveError(DomainError):
    """Raised when an illegal move is attempted."""
    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position


class GameRuleViolationError(DomainError):
    """Raised when an action violates the lifecycle or rules of a game."""
    pass


class GameNotFoundError(DomainError):
    """Raised when a requested game session does not exist."""
    def __init__(self, game_id: str) -> None:
        super().__init__(f"Game with ID '{game_id}' not found.")
        self.game_id = game_id

