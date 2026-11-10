"""
Minimax Algorithm without pruning.
Used for optimal move selection and algorithm benchmarking.
"""

import math
import time
from app.algorithms.base import AIStrategy
from app.algorithms.metrics import AIMetrics, AIResult
from app.domain.models import Board, Player
from app.domain.exceptions import InvalidMoveError


def evaluate_terminal(board: Board, depth: int) -> int | None:
    """
    Evaluates terminal board states per the project specification:
    - AI win:    +10 - depth
    - Human win: depth - 10
    - Draw:      0
    - Non-terminal: None
    """
    winner = board.winner()
    if winner == Player.AI:
        return 10 - depth
    if winner == Player.HUMAN:
        return depth - 10
    if board.is_full():
        return 0
    return None


class MinimaxStrategy(AIStrategy):
    """
    Exhaustive Minimax search without pruning.
    Explores the entire game subtree to compute the minimax value.
    """

    def select_move(self, board: Board) -> AIResult:
        available = board.available_moves()
        if not available:
            raise InvalidMoveError("Cannot select move: board has no available moves.")

        metrics = AIMetrics()
        start_ns = time.perf_counter_ns()

        best_score = -math.inf
        best_move = available[0]

        for move in available:
            next_board = board.make_move(move, Player.AI)
            score = self._minimax(
                board=next_board,
                depth=1,
                is_maximizing=False,
                metrics=metrics,
            )
            if score > best_score:
                best_score = score
                best_move = move

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        metrics.execution_time_ms = elapsed_ms

        return AIResult(position=best_move, metrics=metrics)

    def _minimax(
        self,
        board: Board,
        depth: int,
        is_maximizing: bool,
        metrics: AIMetrics,
    ) -> int:
        metrics.nodes_explored += 1
        if depth > metrics.max_depth_reached:
            metrics.max_depth_reached = depth

        term_val = evaluate_terminal(board, depth)
        if term_val is not None:
            metrics.terminal_states_evaluated += 1
            return term_val

        if is_maximizing:
            max_eval = -math.inf
            for move in board.available_moves():
                next_board = board.make_move(move, Player.AI)
                score = self._minimax(next_board, depth + 1, False, metrics)
                if score > max_eval:
                    max_eval = score
            return int(max_eval)
        else:
            min_eval = math.inf
            for move in board.available_moves():
                next_board = board.make_move(move, Player.HUMAN)
                score = self._minimax(next_board, depth + 1, True, metrics)
                if score < min_eval:
                    min_eval = score
            return int(min_eval)

