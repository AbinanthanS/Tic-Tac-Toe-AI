"""
API Integration Tests using FastAPI TestClient and HTTPX.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_game_repository
from app.domain.models import Player, GameStatus, Board

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_repository():
    """Wipe in-memory repository before each test for test isolation."""
    repo = get_game_repository()
    if hasattr(repo, "clear"):
        repo.clear()


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_create_game_default_hard():
    response = client.post("/api/v1/games", json={"difficulty": "hard"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["difficulty"] == "hard"
    assert data["status"] == "active"
    assert data["current_player"] == "X"
    assert len(data["board"]) == 9
    assert all(c is None for c in data["board"])
    assert data["winning_line"] is None
    assert data["ai_metrics"] is None


@pytest.mark.parametrize("diff", ["easy", "medium", "hard"])
def test_create_game_all_difficulties(diff):
    response = client.post("/api/v1/games", json={"difficulty": diff})
    assert response.status_code == 201
    assert response.json()["difficulty"] == diff


def test_create_game_invalid_difficulty():
    response = client.post("/api/v1/games", json={"difficulty": "impossible"})
    assert response.status_code == 422


def test_get_game_success():
    create_res = client.post("/api/v1/games", json={"difficulty": "medium"})
    game_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/games/{game_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == game_id
    assert get_res.json()["difficulty"] == "medium"


def test_get_game_not_found():
    response = client.get("/api/v1/games/non-existent-uuid")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "GAME_NOT_FOUND"


def test_submit_valid_move_triggers_ai():
    create_res = client.post("/api/v1/games", json={"difficulty": "hard"})
    game_id = create_res.json()["id"]

    # Human plays at center (cell 4)
    move_res = client.post(f"/api/v1/games/{game_id}/moves", json={"position": 4})
    assert move_res.status_code == 200
    data = move_res.json()

    # Human's cell was occupied
    assert data["board"][4] == "X"
    # AI made its counter-move
    assert data["last_ai_move"] is not None
    ai_pos = data["last_ai_move"]
    assert ai_pos != 4
    assert data["board"][ai_pos] == "O"

    # AI search metrics are populated
    assert data["ai_metrics"] is not None
    assert data["ai_metrics"]["nodes_explored"] > 0
    assert data["ai_metrics"]["execution_time_ms"] >= 0.0

    # Turn passes back to human
    assert data["current_player"] == "X"
    assert data["status"] == "active"


def test_submit_move_to_occupied_cell_returns_400():
    create_res = client.post("/api/v1/games", json={"difficulty": "easy"})
    game_id = create_res.json()["id"]

    # Human plays cell 0
    client.post(f"/api/v1/games/{game_id}/moves", json={"position": 0})

    # Human attempts to play cell 0 again
    err_res = client.post(f"/api/v1/games/{game_id}/moves", json={"position": 0})
    assert err_res.status_code == 400
    assert err_res.json()["error"] == "INVALID_MOVE"


@pytest.mark.parametrize("invalid_pos", [-1, 9, 100])
def test_submit_move_out_of_bounds_returns_422(invalid_pos):
    create_res = client.post("/api/v1/games", json={"difficulty": "hard"})
    game_id = create_res.json()["id"]

    res = client.post(f"/api/v1/games/{game_id}/moves", json={"position": invalid_pos})
    assert res.status_code == 422


def test_reset_game():
    create_res = client.post("/api/v1/games", json={"difficulty": "hard"})
    game_id = create_res.json()["id"]

    # Make a move
    client.post(f"/api/v1/games/{game_id}/moves", json={"position": 0})

    # Reset
    reset_res = client.post(f"/api/v1/games/{game_id}/reset")
    assert reset_res.status_code == 200
    data = reset_res.json()
    assert all(c is None for c in data["board"])
    assert data["status"] == "active"
    assert data["current_player"] == "X"
    assert data["difficulty"] == "hard"


def test_human_win_skips_ai():
    """
    If a human move wins the game, the AI must NOT be invoked,
    and game status must immediately be 'won'.
    """
    repo = get_game_repository()
    create_res = client.post("/api/v1/games", json={"difficulty": "easy"})
    game_id = create_res.json()["id"]

    # Setup board directly in repo so human can win in one move:
    # X X .
    # O O .
    # . . .
    # Cell 2 will complete top row for X
    game = repo.get_by_id(game_id)
    game.board = Board.from_sequence([
        "X", "X", None,
        "O", "O", None,
        None, None, None
    ])
    repo.update(game)

    # Human plays winning move at cell 2
    move_res = client.post(f"/api/v1/games/{game_id}/moves", json={"position": 2})
    assert move_res.status_code == 200
    data = move_res.json()

    assert data["status"] == "won"
    assert data["winning_line"] == [0, 1, 2]
    # AI must NOT have made a move
    assert data["last_ai_move"] is None
    assert data["ai_metrics"] is None


def test_move_after_game_over_returns_409():
    """Attempting to make a move on a finished game returns 409 Conflict."""
    repo = get_game_repository()
    create_res = client.post("/api/v1/games", json={"difficulty": "easy"})
    game_id = create_res.json()["id"]

    # Set status to WON
    game = repo.get_by_id(game_id)
    game.status = GameStatus.WON
    repo.update(game)

    move_res = client.post(f"/api/v1/games/{game_id}/moves", json={"position": 0})
    assert move_res.status_code == 409
    assert move_res.json()["error"] == "RULE_VIOLATION"

