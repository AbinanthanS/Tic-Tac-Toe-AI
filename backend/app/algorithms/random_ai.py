"""
Easy Difficulty AI: Random Legal Move Selection.
"""

import random
import time
from app.algorithms.base import AIStrategy
from app.algorithms.metrics import AIMetrics, AIResult
from app.domain.models import Board
from app.domain.exceptions import InvalidMoveError


class RandomAIStrategy(AIStrategy):
    """
    Selects a move uniformly at random among all currently available cells.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def select_move(self, board: Board) -> AIResult:
        start_ns = time.perf_counter_ns()
        available = board.available_moves()

        if not available:
            raise InvalidMoveError("Cannot select move: board has no available moves.")

        chosen_position = self._rng.choice(available)
        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

        metrics = AIMetrics(
            nodes_explored=1,
            cutoffs_count=0,
            terminal_states_evaluated=0,
            max_depth_reached=1,
            execution_time_ms=elapsed_ms,
        )

        return AIResult(position=chosen_position, metrics=metrics)

