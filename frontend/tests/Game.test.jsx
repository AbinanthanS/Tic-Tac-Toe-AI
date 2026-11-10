import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../src/App';
import { api } from '../src/services/api';

// Mock the API layer
vi.mock('../src/services/api', () => ({
  api: {
    createGame: vi.fn(),
    submitMove: vi.fn(),
    resetGame: vi.fn(),
    checkHealth: vi.fn(),
  },
}));

describe('Tic-Tac-Toe React Application', () => {
  const mockInitialGame = {
    id: 'game-123',
    board: [null, null, null, null, null, null, null, null, null],
    current_player: 'X',
    status: 'active',
    difficulty: 'hard',
    winning_line: null,
    ai_metrics: null,
    last_ai_move: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    api.createGame.mockResolvedValue(mockInitialGame);
  });

  it('renders initial game interface and components', async () => {
    render(<App />);

    // Header
    expect(screen.getByText(/Tic-Tac-Toe AI/i)).toBeInTheDocument();

    // Difficulty buttons
    expect(screen.getByRole('button', { name: /Easy/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Medium/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Hard/i })).toBeInTheDocument();

    // Scoreboard
    expect(screen.getByText(/Human \(X\)/i)).toBeInTheDocument();
    expect(screen.getByText(/AI \(O\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Draws/i)).toBeInTheDocument();

    // 9 Board cells
    await waitFor(() => {
      const cells = screen.getAllByRole('gridcell');
      expect(cells).toHaveLength(9);
    });

    // Control buttons
    expect(screen.getByRole('button', { name: /Restart Board/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /New Game/i })).toBeInTheDocument();
  });

  it('handles human move and renders AI counter-move response', async () => {
    const user = userEvent.setup();
    const updatedGameResponse = {
      ...mockInitialGame,
      board: [null, null, null, null, 'X', null, null, null, 'O'],
      status: 'active',
      last_ai_move: 8,
      ai_metrics: {
        nodes_explored: 120,
        cutoffs_count: 45,
        terminal_states_evaluated: 50,
        max_depth_reached: 4,
        execution_time_ms: 1.25,
      },
    };
    api.submitMove.mockResolvedValue(updatedGameResponse);

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole('gridcell')).toHaveLength(9);
    });

    // Click center cell (position 4)
    const centerCell = screen.getByLabelText(/Cell 4/i);
    await user.click(centerCell);

    expect(api.submitMove).toHaveBeenCalledWith('game-123', 4);

    // AI telemetry metrics rendered
    await waitFor(() => {
      expect(screen.getByText(/120/i)).toBeInTheDocument();
      expect(screen.getByText(/45/i)).toBeInTheDocument();
    });
  });

  it('updates scoreboard only on terminal game states', async () => {
    const user = userEvent.setup();
    const wonGameResponse = {
      ...mockInitialGame,
      board: ['X', 'X', 'X', 'O', 'O', null, null, null, null],
      status: 'won',
      winning_line: [0, 1, 2],
    };
    api.submitMove.mockResolvedValue(wonGameResponse);

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole('gridcell')).toHaveLength(9);
    });

    // Scoreboard starts at 0
    expect(screen.getAllByText('0')).toHaveLength(3);

    // Click cell 2 to win
    const cell2 = screen.getByLabelText(/Cell 2/i);
    await user.click(cell2);

    // Human score increments to 1
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText(/Victory! You won the game!/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully and allows dismissal', async () => {
    const user = userEvent.setup();
    api.submitMove.mockRejectedValue(new Error('Cell 0 is already occupied.'));

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole('gridcell')).toHaveLength(9);
    });

    const cell0 = screen.getByLabelText(/Cell 0/i);
    await user.click(cell0);

    // Error banner appears
    await waitFor(() => {
      expect(screen.getByText(/Cell 0 is already occupied/i)).toBeInTheDocument();
    });

    // Dismiss error
    const dismissBtn = screen.getByRole('button', { name: /Dismiss/i });
    await user.click(dismissBtn);

    expect(screen.queryByText(/Cell 0 is already occupied/i)).not.toBeInTheDocument();
  });

  it('handles restart board action', async () => {
    const user = userEvent.setup();
    const resetGameResponse = {
      ...mockInitialGame,
      board: [null, null, null, null, null, null, null, null, null],
      status: 'active',
    };
    api.resetGame.mockResolvedValue(resetGameResponse);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Restart Board/i })).toBeInTheDocument();
    });

    const restartBtn = screen.getByRole('button', { name: /Restart Board/i });
    await user.click(restartBtn);

    expect(api.resetGame).toHaveBeenCalledWith('game-123');
  });
});
