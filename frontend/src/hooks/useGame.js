import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';

/**
 * Custom React hook managing complete game state, server synchronization,
 * and session scoreboard.
 */
export function useGame(initialDifficulty = 'hard') {
  const [game, setGame] = useState(null);
  const [difficulty, setDifficulty] = useState(initialDifficulty);
  const [isLoading, setIsLoading] = useState(true);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState(null);

  // Session scoreboard: increments strictly on active -> terminal transition
  const [scoreboard, setScoreboard] = useState({
    humanWins: 0,
    aiWins: 0,
    draws: 0,
  });

  const lastProcessedStatusRef = useRef('active');

  const updateScoreboardOnTerminal = useCallback((newStatus) => {
    if (lastProcessedStatusRef.current === 'active' && newStatus !== 'active') {
      setScoreboard((prev) => {
        if (newStatus === 'won') return { ...prev, humanWins: prev.humanWins + 1 };
        if (newStatus === 'lost') return { ...prev, aiWins: prev.aiWins + 1 };
        if (newStatus === 'draw') return { ...prev, draws: prev.draws + 1 };
        return prev;
      });
    }
    lastProcessedStatusRef.current = newStatus;
  }, []);

  // Initialize fresh game session
  const startNewGame = useCallback(
    async (targetDifficulty = difficulty) => {
      setIsLoading(true);
      setError(null);
      try {
        const newGame = await api.createGame(targetDifficulty);
        setGame(newGame);
        setDifficulty(targetDifficulty);
        lastProcessedStatusRef.current = 'active';
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    },
    [difficulty]
  );

  // Reset the current board while preserving session and difficulty
  const restartGame = useCallback(async () => {
    if (!game?.id) {
      return startNewGame(difficulty);
    }
    setIsLoading(true);
    setError(null);
    try {
      const resetGameData = await api.resetGame(game.id);
      setGame(resetGameData);
      lastProcessedStatusRef.current = 'active';
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [game?.id, difficulty, startNewGame]);

  // Execute a human player move
  const makeMove = useCallback(
    async (position) => {
      if (!game?.id || isThinking || isLoading) return;
      if (game.status !== 'active') return;
      if (game.board[position] !== null) return;

      setError(null);
      setIsThinking(true);

      // Optimistic update: instantly place 'X' on human's grid for zero-latency feel
      const optimisticBoard = [...game.board];
      optimisticBoard[position] = 'X';
      setGame((prev) => ({
        ...prev,
        board: optimisticBoard,
        current_player: 'O',
      }));

      try {
        const updatedGame = await api.submitMove(game.id, position);
        setGame(updatedGame);
        updateScoreboardOnTerminal(updatedGame.status);
      } catch (err) {
        // Rollback optimistic update on error
        setGame(game);
        setError(err.message);
      } finally {
        setIsThinking(false);
      }
    },
    [game, isThinking, isLoading, updateScoreboardOnTerminal]
  );

  // Change difficulty setting (starts fresh session)
  const changeDifficulty = useCallback(
    (newDiff) => {
      if (newDiff === difficulty) return;
      startNewGame(newDiff);
    },
    [difficulty, startNewGame]
  );

  // Clear scoreboard counters
  const clearScoreboard = useCallback(() => {
    setScoreboard({ humanWins: 0, aiWins: 0, draws: 0 });
  }, []);

  // Initialize on mount
  useEffect(() => {
    startNewGame(initialDifficulty);
  }, []); // Run once on mount

  return {
    game,
    difficulty,
    isLoading,
    isThinking,
    error,
    scoreboard,
    makeMove,
    startNewGame,
    restartGame,
    changeDifficulty,
    clearScoreboard,
    dismissError: () => setError(null),
  };
}
