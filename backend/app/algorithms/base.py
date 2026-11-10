"""
Abstract Base Class defining the AI Strategy interface.
"""

from abc import ABC, abstractmethod
from app.domain.models import Board
from app.algorithms.metrics import AIResult


class AIStrategy(ABC):
    """
    Interface for all AI decision engines.
    Follows the Strategy Pattern to decouple move selection from game execution.
    """
    @abstractmethod
    def select_move(self, board: Board) -> AIResult:
        """
        Determines the best legal move for the AI given the current board state.
        
        Args:
            board: Current board snapshot.
            
        Returns:
            AIResult containing chosen cell index (0-8) and search metrics.
            
        Raises:
            InvalidMoveError: If the board has no available moves.
        """
        pass
