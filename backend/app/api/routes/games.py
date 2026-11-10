"""
FastAPI Route Handlers for the Tic-Tac-Toe Game API.
"""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_game_service
from app.services.game_service import GameService
from app.schemas.game import (
    CreateGameRequest,
    MoveRequest,
    GameResponse,
    HealthResponse,
    ErrorDetail,
)

router = APIRouter(tags=["Games"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
def health_check() -> HealthResponse:
    """Returns service health status."""
    return HealthResponse()


@router.post(
    "/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new game session",
)
def create_game(
    payload: CreateGameRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    """Initializes a new game session with chosen difficulty."""
    return service.create_game(difficulty=payload.difficulty)


@router.get(
    "/games/{game_id}",
    response_model=GameResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorDetail, "description": "Game not found"},
    },
    summary="Retrieve game session state",
)
def get_game(
    game_id: str,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    """Retrieves full state of the specified game session."""
    return service.get_game(game_id)


@router.post(
    "/games/{game_id}/moves",
    response_model=GameResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorDetail, "description": "Invalid move (occupied or out of bounds)"},
        404: {"model": ErrorDetail, "description": "Game not found"},
        409: {"model": ErrorDetail, "description": "Conflicting game state or turn violation"},
        422: {"model": ErrorDetail, "description": "Unprocessable request entity"},
    },
    summary="Play a move",
)
def submit_move(
    game_id: str,
    payload: MoveRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    """Applies human move and triggers AI counter-move."""
    return service.process_human_move(game_id=game_id, position=payload.position)


@router.post(
    "/games/{game_id}/reset",
    response_model=GameResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorDetail, "description": "Game not found"},
    },
    summary="Reset game board",
)
def reset_game(
    game_id: str,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    """Resets the board for the current game while preserving settings."""
    return service.reset_game(game_id)

