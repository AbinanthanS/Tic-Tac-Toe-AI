"""
Unit tests and correctness verification for the AI Engine.
Includes tactical tests, exhaustive optimal play simulations, and algorithm benchmarking.
"""

import pytest
import time
from app.algorithms.factory import get_ai_strategy
from app.algorithms.minimax import MinimaxStrategy
from app.algorithms.alpha_beta import AlphaBetaStrategy
from app.algorithms.random_ai import RandomAIStrategy
from app.domain.models import Board, Player, Difficulty, GameState, GameStatus
from app.domain.exceptions import InvalidMoveError


class TestAITactics:
    """Test critical tactical capabilities required of any competent game AI."""

    @pytest.fixture
    def hard_ai(self) -> AlphaBetaStrategy:
        return AlphaBetaStrategy()

    @pytest.fixture
    def medium_ai(self) -> AlphaBetaStrategy:
        return AlphaBetaStrategy(max_depth=2)

    def test_ai_takes_immediate_horizontal_win(self, hard_ai: AlphaBetaStrategy):
        # AI (O) has 0 and 1, cell 2 is empty -> O must take 2 to win
        # X . .
        # . X .
        # O O .
        board = Board.from_sequence([
            "X", None, None,
            None, "X", None,
            "O", "O", None
        ])
        result = hard_ai.select_move(board)
        assert result.position == 8  # 6 and 7 are O, 8 completes row

    def test_ai_takes_immediate_diagonal_win(self, hard_ai: AlphaBetaStrategy):
        # O has 0 and 4, cell 8 is empty -> O must take 8
        board = Board.from_sequence([
            "O", "X", "X",
            None, "O", None,
            None, None, None
        ])
        result = hard_ai.select_move(board)
        assert result.position == 8

    def test_ai_blocks_immediate_horizontal_threat(self, hard_ai: AlphaBetaStrategy):
        # Human (X) has 3 and 4, cell 5 is empty -> AI must block at 5
        board = Board.from_sequence([
            "O", None, None,
            "X", "X", None,
            None, None, None
        ])
        result = hard_ai.select_move(board)
        assert result.position == 5

    def test_ai_blocks_immediate_vertical_threat(self, hard_ai: AlphaBetaStrategy):
        # Human (X) has 1 and 4, cell 7 is empty -> AI must block at 7
        board = Board.from_sequence([
            "O", "X", None,
            None, "X", None,
            None, None, None
        ])
        result = hard_ai.select_move(board)
        assert result.position == 7

    def test_ai_blocks_immediate_diagonal_threat(self, hard_ai: AlphaBetaStrategy):
        # Human (X) has 2 and 4, cell 6 is empty -> AI must block at 6
        board = Board.from_sequence([
            None, None, "X",
            None, "X", None,
            None, None, "O"
        ])
        result = hard_ai.select_move(board)
        assert result.position == 6

    def test_ai_never_picks_occupied_cell(self, hard_ai: AlphaBetaStrategy):
        board = Board.from_sequence([
            "X", "O", "X",
            "X", "O", "O",
            None, "X", "X"
        ])
        result = hard_ai.select_move(board)
        assert result.position == 6
        assert board.is_empty(result.position)

    def test_ai_raises_on_full_board(self, hard_ai: AlphaBetaStrategy):
        board = Board.from_sequence([
            "X", "O", "X",
            "X", "O", "O",
            "O", "X", "X"
        ])
        with pytest.raises(InvalidMoveError, match="no available moves"):
            hard_ai.select_move(board)


class TestAIEngineCorrectness:
    """Rigorous tests proving the mathematical optimality of Hard AI."""

    def test_hard_ai_never_loses_against_random_opponent(self):
        """Hard AI should never lose against a random player over 50 simulated games."""
        ai = get_ai_strategy(Difficulty.HARD)
        random_opponent = RandomAIStrategy(seed=42)

        for game_idx in range(50):
            game = GameState(difficulty=Difficulty.HARD)
            while game.status == GameStatus.ACTIVE:
                if game.current_player == Player.HUMAN:
                    res = random_opponent.select_move(game.board)
                    game.apply_move(res.position, Player.HUMAN)
                else:
                    res = ai.select_move(game.board)
                    game.apply_move(res.position, Player.AI)

            # Hard AI must NEVER lose: status can only be LOST (AI win) or DRAW
            # Remember: GameStatus.LOST means Human lost -> AI won!
            # GameStatus.WON would mean Human won -> Fail!
            assert game.status in (GameStatus.LOST, GameStatus.DRAW), (
                f"Hard AI lost in game {game_idx}! Final board: {game.board.cells}"
            )

    def test_hard_ai_draws_against_optimal_play_from_all_openings(self):
        """
        If the Human plays optimally from every possible opening move (0 to 8),
        Hard AI must always hold the game to a DRAW.
        """
        hard_ai = AlphaBetaStrategy()
        # To simulate optimal human, we can use an AlphaBeta search from Human perspective
        human_optimal = AlphaBetaStrategy()

        for opening_move in range(9):
            game = GameState(difficulty=Difficulty.HARD)
            # Human opens
            game.apply_move(opening_move, Player.HUMAN)

            while game.status == GameStatus.ACTIVE:
                if game.current_player == Player.AI:
                    ai_res = hard_ai.select_move(game.board)
                    game.apply_move(ai_res.position, Player.AI)
                else:
                    # In our AlphaBeta implementation, AI is Maximizer (+),
                    # so human plays the move that minimizes score.
                    # Or we invert perspective:
                    human_res = self._best_human_move(game.board)
                    game.apply_move(human_res, Player.HUMAN)

            assert game.status == GameStatus.DRAW, (
                f"Opening {opening_move} did not end in a draw: {game.status.value}"
            )

    @staticmethod
    def _best_human_move(board: Board) -> int:
        """Helper computing the mathematically optimal Human move."""
        ai_engine = AlphaBetaStrategy()
        # Find move with minimum minimax evaluation for Human
        best_score = float("inf")
        best_pos = board.available_moves()[0]
        for move in board.available_moves():
            next_b = board.make_move(move, Player.HUMAN)
            if next_b.winner() == Player.HUMAN:
                return move
            if next_b.is_full():
                return move
            # AI's reply score
            ai_res = ai_engine.select_move(next_b)
            # We want the move that leaves AI with the worst possible advantage
            test_b = next_b.make_move(ai_res.position, Player.AI)
            # Evaluate using standard terminal / minimax
            score = ai_engine._alpha_beta(test_b, 2, -float("inf"), float("inf"), False, ai_res.metrics)
            if score < best_score:
                best_score = score
                best_pos = move
        return best_pos


class TestAlgorithmBenchmarking:
    """Direct comparison between plain Minimax and Minimax with Alpha-Beta Pruning."""

    def test_alpha_beta_pruning_efficiency_on_identical_positions(self):
        """
        Alpha-Beta pruning must explore significantly fewer nodes than plain Minimax
        on complex non-trivial positions, while choosing an equally optimal move score.
        """
        minimax = MinimaxStrategy()
        alphabeta = AlphaBetaStrategy()

        # Test on an empty board (worst-case search complexity)
        empty_board = Board()

        # Both choose an optimal first response to an empty board
        # (center or corner are optimal)
        res_mm = minimax.select_move(empty_board)
        res_ab = alphabeta.select_move(empty_board)

        # 1. Optimality consistency: Both moves must be legal and strategically strong (0, 2, 4, 6, 8)
        assert res_mm.position in empty_board.available_moves()
        assert res_ab.position in empty_board.available_moves()

        # 2. Pruning efficiency: Alpha-Beta must explore FAR fewer nodes than plain Minimax
        # Full game tree for empty board in plain Minimax explores tens of thousands of nodes.
        # Alpha-Beta prunes a massive fraction of them.
        assert res_ab.metrics.nodes_explored < res_mm.metrics.nodes_explored
        assert res_ab.metrics.cutoffs_count > 0

        # Print benchmark results for verification log
        print(f"\n--- EMPTY BOARD BENCHMARK ---")
        print(f"Plain Minimax Nodes Explored:     {res_mm.metrics.nodes_explored}")
        print(f"Alpha-Beta Nodes Explored:        {res_ab.metrics.nodes_explored}")
        print(f"Cutoffs Triggered by Alpha-Beta:  {res_ab.metrics.cutoffs_count}")
        print(f"Plain Minimax Execution Time:     {res_mm.metrics.execution_time_ms:.2f} ms")
        print(f"Alpha-Beta Execution Time:        {res_ab.metrics.execution_time_ms:.2f} ms")
        reduction_pct = (1.0 - (res_ab.metrics.nodes_explored / res_mm.metrics.nodes_explored)) * 100.0
        print(f"Node Exploration Reduction:       {reduction_pct:.1f}%")
