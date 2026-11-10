"""
Unit tests for the Core Domain Model (Board, Move, GameState, Win/Draw detection).
"""

import pytest
from app.domain.models import Board, Move, Player, GameState, GameStatus, Difficulty, WINNING_COMBINATIONS
from app.domain.exceptions import InvalidMoveError, GameRuleViolationError


class TestBoard:
    def test_board_initialization_empty(self):
        board = Board()
        assert len(board.cells) == 9
        assert all(cell is None for cell in board.cells)
        assert board.available_moves() == list(range(9))
        assert not board.is_full()
        assert board.winner() is None
        assert board.winning_combination() is None
        assert not board.is_terminal()

    def test_board_invalid_size_raises_error(self):
        with pytest.raises(ValueError, match="exactly 9 cells"):
            Board(cells=(None,) * 8)

    def test_board_immutability_on_make_move(self):
        initial_board = Board()
        new_board = initial_board.make_move(0, Player.HUMAN)

        # Original board remains untouched
        assert initial_board.get(0) is None
        assert len(initial_board.available_moves()) == 9

        # New board reflects move
        assert new_board.get(0) == Player.HUMAN
        assert len(new_board.available_moves()) == 8
        assert 0 not in new_board.available_moves()

    def test_occupied_cell_raises_invalid_move(self):
        board = Board().make_move(4, Player.HUMAN)
        with pytest.raises(InvalidMoveError, match="already occupied"):
            board.make_move(4, Player.AI)

    @pytest.mark.parametrize("invalid_pos", [-1, 9, 100])
    def test_position_out_of_bounds_raises_error(self, invalid_pos):
        board = Board()
        with pytest.raises(InvalidMoveError, match="Position out of range"):
            board.make_move(invalid_pos, Player.HUMAN)

    @pytest.mark.parametrize("combo", WINNING_COMBINATIONS)
    def test_all_winning_combinations_detected(self, combo):
        cells = [None] * 9
        for pos in combo:
            cells[pos] = Player.HUMAN
        board = Board(cells=tuple(cells))
        assert board.winner() == Player.HUMAN
        assert board.winning_combination() == combo
        assert board.is_terminal()

    def test_draw_detected_when_board_is_full_and_no_winner(self):
        # Grid:
        # X O X
        # X O O
        # O X X
        cells = [
            Player.HUMAN, Player.AI, Player.HUMAN,
            Player.HUMAN, Player.AI, Player.AI,
            Player.AI, Player.HUMAN, Player.HUMAN,
        ]
        board = Board(cells=tuple(cells))
        assert board.is_full()
        assert board.winner() is None
        assert board.winning_combination() is None
        assert board.is_terminal()

    def test_from_sequence_factory(self):
        seq = ["X", "O", None, None, "X", None, None, None, "O"]
        board = Board.from_sequence(seq)
        assert board.get(0) == Player.HUMAN
        assert board.get(1) == Player.AI
        assert board.get(2) is None
        assert board.to_list() == seq


class TestMove:
    def test_valid_move(self):
        move = Move(player=Player.HUMAN, position=4)
        assert move.player == Player.HUMAN
        assert move.position == 4

    @pytest.mark.parametrize("invalid_pos", [-1, 9, "4"])
    def test_invalid_move_raises(self, invalid_pos):
        with pytest.raises(InvalidMoveError):
            Move(player=Player.HUMAN, position=invalid_pos)  # type: ignore


class TestGameState:
    def test_initial_state(self):
        game = GameState(difficulty=Difficulty.HARD)
        assert game.status == GameStatus.ACTIVE
        assert game.current_player == Player.HUMAN
        assert len(game.move_history) == 0
        assert game.winning_line is None

    def test_turn_order_enforced(self):
        game = GameState()
        # AI cannot move first
        with pytest.raises(GameRuleViolationError, match="Turn violation"):
            game.apply_move(0, Player.AI)

    def test_alternating_turns(self):
        game = GameState()
        game.apply_move(0, Player.HUMAN)
        assert game.current_player == Player.AI
        assert game.board.get(0) == Player.HUMAN

        game.apply_move(4, Player.AI)
        assert game.current_player == Player.HUMAN
        assert game.board.get(4) == Player.AI

    def test_human_win_lifecycle(self):
        game = GameState()
        # X: 0, 1, 2 (Top row win)
        # O: 3, 4
        game.apply_move(0, Player.HUMAN)
        game.apply_move(3, Player.AI)
        game.apply_move(1, Player.HUMAN)
        game.apply_move(4, Player.AI)
        game.apply_move(2, Player.HUMAN)

        assert game.status == GameStatus.WON
        assert game.winning_line == (0, 1, 2)
        assert game.board.winner() == Player.HUMAN

        # Cannot move after game is won
        with pytest.raises(GameRuleViolationError, match="Cannot make a move in a game with status 'won'"):
            game.apply_move(5, Player.AI)

    def test_ai_win_lifecycle(self):
        game = GameState()
        # O wins diagonal (2, 4, 6)
        game.apply_move(0, Player.HUMAN)
        game.apply_move(2, Player.AI)
        game.apply_move(1, Player.HUMAN)
        game.apply_move(4, Player.AI)
        game.apply_move(8, Player.HUMAN)
        game.apply_move(6, Player.AI)

        assert game.status == GameStatus.LOST
        assert game.winning_line == (2, 4, 6)
        assert game.board.winner() == Player.AI

    def test_draw_lifecycle(self):
        game = GameState()
        # 0: X, 1: O, 2: X
        # 3: X, 4: O, 5: O
        # 6: O, 7: X, 8: X
        moves = [
            (0, Player.HUMAN), (1, Player.AI),
            (2, Player.HUMAN), (4, Player.AI),
            (3, Player.HUMAN), (5, Player.AI),
            (7, Player.HUMAN), (6, Player.AI),
            (8, Player.HUMAN),
        ]
        for pos, player in moves:
            game.apply_move(pos, player)

        assert game.status == GameStatus.DRAW
        assert game.winning_line is None
        assert game.board.is_full()
