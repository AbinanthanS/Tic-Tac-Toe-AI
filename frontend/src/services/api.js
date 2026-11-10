/**
 * API Service for Tic-Tac-Toe Backend Communication.
 * Uses standard Fetch API to interact with versioned /api/v1 endpoints.
 * Supports configurable VITE_API_BASE_URL for production cloud deployments.
 */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE = RAW_BASE ? `${RAW_BASE.replace(/\/$/, '')}/api/v1` : '/api/v1';


async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMessage = data?.message || data?.error || `Request failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.details = data?.details;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Unable to connect to the backend server. Is FastAPI running on port 8000?');
    }
    throw err;
  }
}

export const api = {
  checkHealth: () => request('/health'),

  createGame: (difficulty = 'hard') =>
    request('/games', {
      method: 'POST',
      body: JSON.stringify({ difficulty }),
    }),

  getGame: (gameId) => request(`/games/${gameId}`),

  submitMove: (gameId, position) =>
    request(`/games/${gameId}/moves`, {
      method: 'POST',
      body: JSON.stringify({ position }),
    }),

  resetGame: (gameId) =>
    request(`/games/${gameId}/reset`, {
      method: 'POST',
    }),
};
