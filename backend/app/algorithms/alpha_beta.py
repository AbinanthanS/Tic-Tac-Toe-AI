"""
Minimax with Alpha-Beta Pruning.
Implements optimal play for Hard difficulty and depth-limited search for Medium difficulty.
"""

import math
import time
from app.algorithms.base import AIStrategy
from app.algorithms.metrics import AIMetrics, AIResult
from app.algorithms.minimax import evaluate_terminal
from app.domain.models import Board, Player, WINNING_COMBINATIONS
from app.domain.exceptions import InvalidMoveError


def heuristic_evaluation(board: Board) -> int:
    """
    Static evaluation function for non-terminal states in depth-limited search.
    Scores board potential from the AI's perspective (+ values favor AI, - values favor Human).
    
    Heuristic rules:
    - Line with two AI marks and one open cell: +3
    - Line with two Human marks and one open cell: -3
    - Center cell occupancy bonus: +2 for AI, -2 for Human
    - Corner cell occupancy bonus: +1 for AI, -1 for Human
    """
    score = 0

    # Line evaluation
    for combo in WINNING_COMBINATIONS:
        marks = [board.cells[pos] for pos in combo]
        ai_count = marks.count(Player.AI)
        human_count = marks.count(Player.HUMAN)

        if ai_count == 2 and human_count == 0:
            score += 3
        elif human_count == 2 and ai_count == 0:
            score -= 3
        elif ai_count == 1 and human_count == 0:
            score += 1
        elif human_count == 1 and ai_count == 0:
            score -= 1

    # Center cell positional weighting
    center = board.cells[4]
    if center == Player.AI:
        score += 2
    elif center == Player.HUMAN:
        score -= 2

    return score


class AlphaBetaStrategy(AIStrategy):
    """
    Minimax search enhanced with Alpha-Beta pruning.
    
    Args:
        max_depth: Maximum search depth ply. If None, searches to full completion.
    """

    def __init__(self, max_depth: int | None = None) -> None:
        self.max_depth = max_depth

    def select_move(self, board: Board) -> AIResult:
        available = board.available_moves()
        if not available:
            raise InvalidMoveError("Cannot select move: board has no available moves.")

        metrics = AIMetrics()
        start_ns = time.perf_counter_ns()

        best_score = -math.inf
        best_move = available[0]
        alpha = -math.inf
        beta = math.inf

        for move in available:
            next_board = board.make_move(move, Player.AI)
            score = self._alpha_beta(
                board=next_board,
                depth=1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
                metrics=metrics,
            )
            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        metrics.execution_time_ms = elapsed_ms

        return AIResult(position=best_move, metrics=metrics)

    def _alpha_beta(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        metrics: AIMetrics,
    ) -> int:
        metrics.nodes_explored += 1
        if depth > metrics.max_depth_reached:
            metrics.max_depth_reached = depth

        # 1. Check for exact terminal state
        term_val = evaluate_terminal(board, depth)
        if term_val is not None:
            metrics.terminal_states_evaluated += 1
            return term_val

        # 2. Check depth limit for heuristic evaluation (Medium mode)
        if self.max_depth is not None and depth >= self.max_depth:
            metrics.terminal_states_evaluated += 1
            return heuristic_evaluation(board)

        # 3. Branching
        if is_maximizing:
            max_eval = -math.inf
            for move in board.available_moves():
                next_board = board.make_move(move, Player.AI)
                score = self._alpha_beta(next_board, depth + 1, alpha, beta, False, metrics)
                if score > max_eval:
                    max_eval = score
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    metrics.cutoffs_count += 1
                    break  # Beta cutoff
            return int(max_eval)
        else:
            min_eval = math.inf
            for move in board.available_moves():
                next_board = board.make_move(move, Player.HUMAN)
                score = self._alpha_beta(next_board, depth + 1, alpha, beta, True, metrics)
                if score < min_eval:
                    min_eval = score
                beta = min(beta, min_eval)
                if beta <= alpha:
                    metrics.cutoffs_count += 1
                    break  # Alpha cutoff
            return int(min_eval)
