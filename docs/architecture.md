# System Architecture & Technical Design

This document details the software architecture, design patterns, and engineering decisions implemented in the Full-Stack AI Tic-Tac-Toe application.

---

## 1. High-Level Architecture Overview

The system adopts a **Layered Monolithic Architecture** with strict dependency boundaries. The domain models and AI search algorithms operate as pure, decoupled engines with zero dependencies on web frameworks or storage systems.

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React + Vite)"]
        UI["UI Components\n(GameBoard, ScoreBoard, AIThinkingPanel)"]
        Hook["useGame() Custom Hook"]
        APIClient["API Service (Fetch API)"]
        UI --> Hook --> APIClient
    end

    subgraph Server ["Backend Layer (FastAPI)"]
        Router["API Route Handlers (/api/v1)"]
        Pydantic["Pydantic V2 Validation\n(Request & Response Schemas)"]
        Service["GameService (Orchestrator)"]
        
        Router --> Pydantic
        Router --> Service
    end

    subgraph Core ["Domain & AI Engine (Pure Python)"]
        Domain["Game Domain\n(Board, Move, GameState, Rules)"]
        AI["AI Engine (Strategy Pattern)\n(Random, Depth-Limited, Alpha-Beta)"]
    end

    subgraph Persistence ["Persistence Layer"]
        Repo["InMemoryGameRepository\n(Thread-Safe Storage)"]
    end

    APIClient -- HTTP / JSON --> Router
    Service --> Domain
    Service --> AI
    Service --> Repo
```

---

## 2. Component Responsibilities

| Layer / Component | Primary Responsibility | Key Files |
| :--- | :--- | :--- |
| **Frontend Presentation** | Renders UI, provides visual feedback, manages responsive styling. | `App.jsx`, `GameBoard.jsx`, `ScoreBoard.jsx`, `AIThinkingPanel.jsx` |
| **Frontend State & API** | Orchestrates optimistic UI updates, handles session scoreboard, communicates via `fetch`. | `useGame.js`, `api.js` |
| **API Layer** | Request routing, CORS configuration, schema validation, HTTP status code translation. | `main.py`, `games.py`, `schemas/game.py` |
| **Game Service** | Coordinates human move execution, terminal checks, AI move calculation, and persistence. | `services/game_service.py` |
| **Game Domain** | Enforces game invariants, board representation, win/draw detection, turn switching. | `domain/models.py`, `domain/exceptions.py` |
| **AI Engine** | Game tree traversal, heuristic scoring, $\alpha$-$\beta$ branch pruning, search telemetry. | `algorithms/minimax.py`, `algorithms/alpha_beta.py`, `algorithms/factory.py` |
| **Repository** | Thread-safe in-memory session management. Decoupled via Abstract Base Class (`GameRepository`). | `repositories/base.py`, `repositories/memory.py` |

---

## 3. Data Flow: Processing a Human Move

When the human clicks cell 4 on the grid:

```mermaid
sequenceDiagram
    autonumber
    actor Human as User (Browser)
    participant UI as React (useGame)
    participant API as FastAPI Router
    participant Svc as GameService
    participant Repo as InMemoryRepo
    participant AI as AlphaBetaStrategy

    Human->>UI: Clicks Cell 4
    UI->>UI: Optimistic Update: Render 'X' instantly
    UI->>API: POST /api/v1/games/{id}/moves {"position": 4}
    API->>Svc: process_human_move(id, 4)
    Svc->>Repo: get_by_id(id)
    Repo-->>Svc: GameState
    Svc->>Svc: Validate turn order & cell availability
    Svc->>Svc: Apply Move 4 (Human 'X')
    alt Human Win or Draw
        Svc->>Repo: update(GameState)
        Svc-->>API: GameResponse (ai_metrics=None)
    else Game Continues
        Svc->>AI: select_move(board)
        AI-->>Svc: AIResult (position=0, metrics={nodes, cutoffs, time})
        Svc->>Svc: Apply Move 0 (AI 'O')
        Svc->>Repo: update(GameState)
        Svc-->>API: GameResponse (board, ai_metrics)
    end
    API-->>UI: 200 OK (Authoritative State)
    UI->>UI: Update Board, Telemetry & Scoreboard
```

---

## 4. Key Architectural Patterns

1. **Authoritative Server**: The client never determines win status or modifies board arrays directly. The backend validates and returns authoritative state.
2. **Strategy Pattern**: All AI difficulty levels implement the common `AIStrategy` interface, allowing plug-and-play AI engines without modifying game logic.
3. **Repository Pattern with Dependency Injection**: In-memory storage is decoupled through `GameRepository(ABC)` and injected into FastAPI routes via `Depends(get_game_service)`.
4. **Optimistic UI with Rollback**: Instant responsiveness on user click with rollback safety if the backend request fails.
