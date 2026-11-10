"""
FastAPI Application Entry Point.
Configures middleware, exception handlers, and API routing.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.games import router as games_router
from app.domain.exceptions import (
    GameNotFoundError,
    GameRuleViolationError,
    InvalidMoveError,
    DomainError,
)

app = FastAPI(
    title="Full-Stack AI Tic-Tac-Toe API",
    description="High-performance FastAPI backend powered by Minimax and Alpha-Beta pruning AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration for local frontend development (Vite default: http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Domain Exception Handlers
@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request: Request, exc: GameNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "GAME_NOT_FOUND",
            "message": str(exc),
            "details": {"game_id": exc.game_id},
        },
    )


@app.exception_handler(GameRuleViolationError)
async def rule_violation_handler(request: Request, exc: GameRuleViolationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "RULE_VIOLATION",
            "message": str(exc),
            "details": None,
        },
    )


@app.exception_handler(InvalidMoveError)
async def invalid_move_handler(request: Request, exc: InvalidMoveError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "INVALID_MOVE",
            "message": str(exc),
            "details": {"position": exc.position},
        },
    )


@app.exception_handler(DomainError)
async def generic_domain_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "DOMAIN_ERROR",
            "message": str(exc),
            "details": None,
        },
    )


# Register versioned API router
app.include_router(games_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Tic-Tac-Toe AI Backend API. Visit /docs for OpenAPI documentation."}
