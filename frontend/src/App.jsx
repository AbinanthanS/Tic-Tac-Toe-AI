import React from 'react';
import { useGame } from './hooks/useGame';
import { GameHeader } from './components/GameHeader';
import { DifficultySelector } from './components/DifficultySelector';
import { ScoreBoard } from './components/ScoreBoard';
import { GameStatus } from './components/GameStatus';
import { GameBoard } from './components/GameBoard';
import { GameControls } from './components/GameControls';
import { AIThinkingPanel } from './components/AIThinkingPanel';

export function App() {
  const {
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
    dismissError,
  } = useGame('hard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between py-8 px-4 sm:px-6">
      <main className="max-w-xl mx-auto w-full">
        <GameHeader isThinking={isThinking} />

        {/* Global Error Banner */}
        {error && (
          <div className="mb-4 bg-rose-950/80 border border-rose-500/70 text-rose-200 px-4 py-3 rounded-xl text-sm flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-2">
              <span className="text-base">⚠️</span>
              <span>{error}</span>
            </div>
            <button
              onClick={dismissError}
              className="text-rose-400 hover:text-rose-100 font-bold ml-3 text-xs underline cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        <DifficultySelector
          currentDifficulty={difficulty}
          onSelectDifficulty={changeDifficulty}
          disabled={isLoading || isThinking}
        />

        <ScoreBoard
          scoreboard={scoreboard}
          onClearScoreboard={clearScoreboard}
        />

        {game && (
          <>
            <GameStatus
              status={game.status}
              currentPlayer={game.current_player}
              isThinking={isThinking}
            />

            <GameBoard
              board={game.board}
              winningLine={game.winning_line}
              lastAIMove={game.last_ai_move}
              disabled={isLoading || isThinking || game.status !== 'active'}
              onCellClick={makeMove}
            />

            <GameControls
              onRestart={restartGame}
              onNewGame={() => startNewGame(difficulty)}
              disabled={isLoading || isThinking}
            />

            <AIThinkingPanel
              metrics={game.ai_metrics}
              isThinking={isThinking}
              difficulty={difficulty}
            />
          </>
        )}

        {isLoading && !game && (
          <div className="py-20 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-cyan-500 border-t-transparent" />
            <p className="mt-3 text-sm text-slate-400 font-mono">Initializing Game Engine...</p>
          </div>
        )}
      </main>

      <footer className="text-center text-xs text-slate-400 mt-8 border-t border-slate-900 pt-4">
        Built with React 18, Vite, Tailwind CSS & FastAPI • Minimax with Alpha-Beta Pruning
      </footer>
    </div>
  );
}

export default App;
