"""
Pydantic Schemas for Request and Response validation.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator
from app.domain.models import Difficulty, GameStatus, Player


class CreateGameRequest(BaseModel):
    """Payload to initialize a new game session."""
    difficulty: Difficulty = Field(
        default=Difficulty.HARD,
        description="AI opponent difficulty: easy, medium, or hard."
    )


class MoveRequest(BaseModel):
    """Payload to submit a player move."""
    position: int = Field(
        ...,
        ge=0,
        le=8,
        description="Zero-indexed cell index on the 3x3 board (0 to 8)."
    )


class AIMetricsSchema(BaseModel):
    """Search telemetry details returned by the AI engine."""
    nodes_explored: int = Field(..., description="Total recursive nodes visited during search.")
    cutoffs_count: int = Field(..., description="Number of alpha/beta branch cutoffs.")
    terminal_states_evaluated: int = Field(..., description="Leaf evaluations performed.")
    max_depth_reached: int = Field(..., description="Maximum ply reached in the search tree.")
    execution_time_ms: float = Field(..., description="Wall-clock search duration in milliseconds.")


class GameResponse(BaseModel):
    """Authoritative snapshot of the game session."""
    id: str = Field(..., description="Unique game session UUID.")
    board: list[str | None] = Field(..., description="9-element array representing the 3x3 grid.")
    current_player: Player = Field(..., description="Player whose turn is next ('X' or 'O').")
    status: GameStatus = Field(..., description="Current status: active, won, lost, or draw.")
    difficulty: Difficulty = Field(..., description="AI difficulty.")
    winning_line: tuple[int, int, int] | None = Field(
        default=None,
        description="The 3 cell indices forming the winning line, or None."
    )
    ai_metrics: AIMetricsSchema | None = Field(
        default=None,
        description="Search telemetry from the AI's most recent counter-move."
    )
    last_ai_move: int | None = Field(
        default=None,
        description="Position of the AI's most recent counter-move."
    )
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    """API health status response."""
    status: Literal["healthy"] = "healthy"
    version: str = "1.0.0"


class ErrorDetail(BaseModel):
    """Standardized error response body."""
    error: str = Field(..., description="Error category / code.")
    message: str = Field(..., description="Human-readable explanation.")
    details: dict | None = Field(default=None, description="Optional metadata or context.")
