"""
Game Service Layer.
Coordinates domain logic, AI decision engines, and repository persistence.
"""

from app.domain.models import GameState, GameStatus, Player, Difficulty, Board
from app.domain.exceptions import GameNotFoundError, GameRuleViolationError, InvalidMoveError
from app.algorithms.factory import get_ai_strategy
from app.algorithms.metrics import AIMetrics
from app.repositories.base import GameRepository
from app.schemas.game import GameResponse, AIMetricsSchema


class GameService:
    """Orchestrates game lifecycle and turns."""

    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    def create_game(self, difficulty: Difficulty = Difficulty.HARD) -> GameResponse:
        """Initializes and persists a fresh game session."""
        game = GameState(difficulty=difficulty)
        self.repository.save(game)
        return self._to_response(game)

    def get_game(self, game_id: str) -> GameResponse:
        """Retrieves an existing game session."""
        game = self._find_game_or_raise(game_id)
        return self._to_response(game)

    def reset_game(self, game_id: str) -> GameResponse:
        """Resets the board for an existing session while maintaining difficulty."""
        game = self._find_game_or_raise(game_id)
        game.board = Board()
        game.current_player = Player.HUMAN
        game.status = GameStatus.ACTIVE
        game.winning_line = None
        game.move_history.clear()
        self.repository.update(game)
        return self._to_response(game)

    def process_human_move(self, game_id: str, position: int) -> GameResponse:
        """
        Executes a turn sequence:
        1. Validates session existence.
        2. Applies human move.
        3. If human wins or draws, skips AI and returns terminal state immediately.
        4. If game continues, selects and applies AI move.
        5. Persists and returns updated state.
        """
        game = self._find_game_or_raise(game_id)

        # 1. Apply Human Move
        game.apply_move(position=position, player=Player.HUMAN)

        # 2. Check if Human's move concluded the game
        if game.status != GameStatus.ACTIVE:
            self.repository.update(game)
            return self._to_response(game)

        # 3. Game continues: Invoke AI Strategy
        strategy = get_ai_strategy(game.difficulty)
        ai_result = strategy.select_move(game.board)

        # 4. Apply AI Move
        game.apply_move(position=ai_result.position, player=Player.AI)
        self.repository.update(game)

        return self._to_response(
            game=game,
            ai_metrics=ai_result.metrics,
            last_ai_move=ai_result.position
        )

    def _find_game_or_raise(self, game_id: str) -> GameState:
        game = self.repository.get_by_id(game_id)
        if game is None:
            raise GameNotFoundError(game_id)
        return game

    @staticmethod
    def _to_response(
        game: GameState,
        ai_metrics: AIMetrics | None = None,
        last_ai_move: int | None = None
    ) -> GameResponse:
        metrics_schema = None
        if ai_metrics is not None:
            metrics_schema = AIMetricsSchema(
                nodes_explored=ai_metrics.nodes_explored,
                cutoffs_count=ai_metrics.cutoffs_count,
                terminal_states_evaluated=ai_metrics.terminal_states_evaluated,
                max_depth_reached=ai_metrics.max_depth_reached,
                execution_time_ms=round(ai_metrics.execution_time_ms, 3),
            )

        return GameResponse(
            id=game.id,
            board=game.board.to_list(),
            current_player=game.current_player,
            status=game.status,
            difficulty=game.difficulty,
            winning_line=game.winning_line,
            ai_metrics=metrics_schema,
            last_ai_move=last_ai_move,
            created_at=game.created_at,
            updated_at=game.updated_at,
        )

