"""
Core Domain Models for Tic-Tac-Toe.

These models are completely decoupled from FastAPI, databases, or external frameworks.
They encapsulate the core rules, invariants, and game state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Sequence

from app.domain.exceptions import InvalidMoveError, GameRuleViolationError


class Player(str, Enum):
    """
    Representation of game participants.
    By project requirement:
    - Human is always 'X'
    - AI is always 'O'
    """
    HUMAN = "X"
    AI = "O"

    @property
    def opponent(self) -> Player:
        """Returns the opposing player."""
        return Player.AI if self == Player.HUMAN else Player.HUMAN


class GameStatus(str, Enum):
    """
    Status of the game lifecycle.
    - ACTIVE: Game in progress.
    - WON: Human player won.
    - LOST: AI player won (Human lost).
    - DRAW: Game completed with no winner.
    """
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    DRAW = "draw"


class Difficulty(str, Enum):
    """AI difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# The 8 winning combinations on a 3x3 grid (represented as 0-indexed 1D array indices)
WINNING_COMBINATIONS: tuple[tuple[int, int, int], ...] = (
    # Rows
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    # Columns
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    # Diagonals
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True, slots=True)
class Move:
    """
    Represents an atomic move made by a player.
    Frozen dataclass ensures immutability.
    """
    player: Player
    position: int

    def __post_init__(self) -> None:
        if not isinstance(self.position, int):
            raise InvalidMoveError(f"Move position must be an integer, got {type(self.position).__name__}.")
        if self.position < 0 or self.position > 8:
            raise InvalidMoveError(
                f"Move position must be between 0 and 8 (inclusive), got {self.position}.",
                position=self.position
            )


@dataclass(frozen=True, slots=True)
class Board:
    """
    Represents an immutable 3x3 Tic-Tac-Toe board.
    Internally backed by a 9-element tuple of Player | None.
    
    Immutability guarantees that states cannot be mutated accidentally
    during game play or tree search (Minimax).
    """
    cells: tuple[Player | None, ...] = field(default_factory=lambda: (None,) * 9)

    def __post_init__(self) -> None:
        if len(self.cells) != 9:
            raise ValueError(f"Board must have exactly 9 cells, got {len(self.cells)}.")

    @classmethod
    def from_sequence(cls, sequence: Sequence[str | None]) -> Board:
        """Factory method to construct a Board from an arbitrary sequence of strings or None."""
        if len(sequence) != 9:
            raise ValueError(f"Sequence must contain exactly 9 elements, got {len(sequence)}.")
        parsed_cells = tuple(Player(val) if val is not None else None for val in sequence)
        return cls(cells=parsed_cells)

    def get(self, position: int) -> Player | None:
        """Retrieve cell content at the specified index [0-8]."""
        self._validate_position_bounds(position)
        return self.cells[position]

    def is_empty(self, position: int) -> bool:
        """Check if a cell is unoccupied."""
        return self.get(position) is None

    def available_moves(self) -> list[int]:
        """Returns sorted indices of all unoccupied cells."""
        return [idx for idx, cell in enumerate(self.cells) if cell is None]

    def make_move(self, position: int, player: Player) -> Board:
        """
        Applies a move and returns a NEW Board instance.
        Validates bounds and cell vacancy.
        """
        self._validate_position_bounds(position)
        if not self.is_empty(position):
            raise InvalidMoveError(f"Cell {position} is already occupied.", position=position)

        new_cells = list(self.cells)
        new_cells[position] = player
        return Board(cells=tuple(new_cells))

    def is_full(self) -> bool:
        """Returns True if no empty cells remain."""
        return all(cell is not None for cell in self.cells)

    def winning_combination(self) -> tuple[int, int, int] | None:
        """
        Returns the winning 3-tuple index combination if a player has aligned 3 marks,
        or None if there is no winner.
        """
        for combo in WINNING_COMBINATIONS:
            p0, p1, p2 = combo
            c0, c1, c2 = self.cells[p0], self.cells[p1], self.cells[p2]
            if c0 is not None and c0 == c1 == c2:
                return combo
        return None

    def winner(self) -> Player | None:
        """Returns the winning Player ('X' or 'O'), or None if no winner."""
        combo = self.winning_combination()
        if combo is not None:
            return self.cells[combo[0]]
        return None

    def is_terminal(self) -> bool:
        """A board is terminal if a player has won or all cells are filled."""
        return self.winner() is not None or self.is_full()

    @staticmethod
    def _validate_position_bounds(position: int) -> None:
        if not isinstance(position, int) or position < 0 or position > 8:
            raise InvalidMoveError(
                f"Position out of range: must be an integer between 0 and 8, got {position}.",
                position=position if isinstance(position, int) else None
            )

    def to_list(self) -> list[str | None]:
        """Serializes the board cells to a list of 'X', 'O', or None for JSON responses."""
        return [cell.value if cell is not None else None for cell in self.cells]


@dataclass
class GameState:
    """
    Encapsulates the state of an ongoing or completed Tic-Tac-Toe session.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    board: Board = field(default_factory=Board)
    current_player: Player = Player.HUMAN
    status: GameStatus = GameStatus.ACTIVE
    difficulty: Difficulty = Difficulty.HARD
    winning_line: tuple[int, int, int] | None = None
    move_history: list[Move] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def apply_move(self, position: int, player: Player) -> GameState:
        """
        Validates game lifecycle and turn rules, applies the move to the board,
        updates the game status, and advances current player.
        """
        if self.status != GameStatus.ACTIVE:
            raise GameRuleViolationError(
                f"Cannot make a move in a game with status '{self.status.value}'."
            )

        if self.current_player != player:
            raise GameRuleViolationError(
                f"Turn violation: expected player '{self.current_player.value}', got '{player.value}'."
            )

        new_board = self.board.make_move(position, player)
        winning_combo = new_board.winning_combination()
        new_status = self.status

        if winning_combo is not None:
            new_status = GameStatus.WON if player == Player.HUMAN else GameStatus.LOST
        elif new_board.is_full():
            new_status = GameStatus.DRAW

        self.board = new_board
        self.winning_line = winning_combo
        self.status = new_status
        self.move_history.append(Move(player=player, position=position))
        self.current_player = player.opponent
        self.updated_at = datetime.now(timezone.utc)
        return self

