# API Specification (REST / OpenAPI)

Base URL: `/api/v1`

---

## 1. Overview

The backend exposes a versioned REST API adhering to JSON over HTTP standards.
- Authoritative game state is maintained exclusively on the server.
- The client only submits atomic player moves (`position: int`).
- Responses return complete game state snapshots along with AI search telemetry.

---

## 2. Endpoints

### 2.1 Health Check
* **Method**: `GET`
* **Path**: `/api/v1/health`
* **Description**: Confirms API operational readiness.
* **Success Response (`200 OK`)**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2.2 Create Game Session
* **Method**: `POST`
* **Path**: `/api/v1/games`
* **Description**: Initializes a fresh game session.
* **Request Body**:
```json
{
  "difficulty": "hard"
}
```
*Field options*: `"easy"`, `"medium"`, `"hard"`. Defaults to `"hard"`.

* **Success Response (`201 Created`)**:
```json
{
  "id": "e6745199-e93d-4c3e-8c3b-55c3c0ef2ff3",
  "board": [null, null, null, null, null, null, null, null, null],
  "current_player": "X",
  "status": "active",
  "difficulty": "hard",
  "winning_line": null,
  "ai_metrics": null,
  "last_ai_move": null,
  "created_at": "2026-11-10T05:30:00Z",
  "updated_at": "2026-11-10T05:30:00Z"
}
```

---

### 2.3 Retrieve Game State
* **Method**: `GET`
* **Path**: `/api/v1/games/{game_id}`
* **Description**: Fetches current snapshot of a game session.
* **Path Parameters**:
  * `game_id` (string, UUID): The game session identifier.
* **Success Response (`200 OK`)**:
  Returns standard `GameResponse`.
* **Error Response (`404 Not Found`)**:
```json
{
  "error": "GAME_NOT_FOUND",
  "message": "Game with ID 'invalid-id' not found.",
  "details": { "game_id": "invalid-id" }
}
```

---

### 2.4 Submit Human Move
* **Method**: `POST`
* **Path**: `/api/v1/games/{game_id}/moves`
* **Description**: Applies the human's move and automatically executes the AI counter-move if the game continues.
* **Request Body**:
```json
{
  "position": 4
}
```
*Constraint*: `0 <= position <= 8`.

* **Success Response (`200 OK`)**:
```json
{
  "id": "e6745199-e93d-4c3e-8c3b-55c3c0ef2ff3",
  "board": ["O", null, null, null, "X", null, null, null, null],
  "current_player": "X",
  "status": "active",
  "difficulty": "hard",
  "winning_line": null,
  "ai_metrics": {
    "nodes_explored": 1445,
    "cutoffs_count": 512,
    "terminal_states_evaluated": 620,
    "max_depth_reached": 8,
    "execution_time_ms": 4.12
  },
  "last_ai_move": 0,
  "created_at": "2026-11-10T05:30:00Z",
  "updated_at": "2026-11-10T05:30:01Z"
}
```

* **Error Responses**:
  * `400 Bad Request`: Cell is already occupied (`INVALID_MOVE`).
  * `404 Not Found`: Game does not exist (`GAME_NOT_FOUND`).
  * `409 Conflict`: Attempted move on already completed game (`RULE_VIOLATION`).
  * `422 Unprocessable Entity`: Position out of bounds (`< 0` or `> 8`) or invalid payload type.

---

### 2.5 Reset Game Board
* **Method**: `POST`
* **Path**: `/api/v1/games/{game_id}/reset`
* **Description**: Clears the board to start fresh while retaining the existing game ID and chosen difficulty.
* **Success Response (`200 OK`)**:
  Returns fresh `GameResponse` with empty board and `status: "active"`.

---

## 3. Standard Error Format
All application errors follow this structure:
```json
{
  "error": "ERROR_CODE",
  "message": "Descriptive human-readable explanation",
  "details": {}
}
```
