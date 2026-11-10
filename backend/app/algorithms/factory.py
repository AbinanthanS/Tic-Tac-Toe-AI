"""
Factory module for creating AI strategy instances.
"""

from app.algorithms.base import AIStrategy
from app.algorithms.random_ai import RandomAIStrategy
from app.algorithms.alpha_beta import AlphaBetaStrategy
from app.domain.models import Difficulty


def get_ai_strategy(difficulty: Difficulty | str) -> AIStrategy:
    """
    Factory function returning the appropriate AIStrategy implementation.
    
    - EASY: Random legal move selection.
    - MEDIUM: Depth-limited Minimax with Alpha-Beta pruning (depth=2) and heuristic evaluation.
    - HARD: Full Minimax with Alpha-Beta pruning (unbounded depth) for mathematically optimal play.
    """
    diff_enum = Difficulty(difficulty) if isinstance(difficulty, str) else difficulty

    if diff_enum == Difficulty.EASY:
        return RandomAIStrategy()
    elif diff_enum == Difficulty.MEDIUM:
        return AlphaBetaStrategy(max_depth=2)
    elif diff_enum == Difficulty.HARD:
        return AlphaBetaStrategy(max_depth=None)
    else:
        raise ValueError(f"Unsupported difficulty: {difficulty}")

