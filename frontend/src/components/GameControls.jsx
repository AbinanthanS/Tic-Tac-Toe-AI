import React from 'react';

export function GameControls({ onRestart, onNewGame, disabled }) {
  return (
    <div className="flex gap-3 justify-center mb-6">
      <button
        onClick={onRestart}
        disabled={disabled}
        className="px-4 py-2.5 rounded-lg font-semibold text-sm bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all duration-150 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-md cursor-pointer flex items-center gap-1.5"
      >
        <span>🔄</span>
        <span>Restart Board</span>
      </button>

      <button
        onClick={onNewGame}
        disabled={disabled}
        className="px-4 py-2.5 rounded-lg font-semibold text-sm bg-cyan-600 hover:bg-cyan-500 text-white transition-all duration-150 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-900/50 cursor-pointer flex items-center gap-1.5"
      >
        <span>✨</span>
        <span>New Game</span>
      </button>
    </div>
  );
}
