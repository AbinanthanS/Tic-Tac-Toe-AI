import React from 'react';

export function GameStatus({ status, currentPlayer, isThinking }) {
  if (status === 'won') {
    return (
      <div className="bg-emerald-950/70 border border-emerald-500/60 text-emerald-300 rounded-lg py-2.5 px-4 text-center font-bold text-sm shadow-md shadow-emerald-950/50 flex items-center justify-center gap-2 mb-4 animate-bounce">
        <span>🏆</span>
        <span>Victory! You won the game!</span>
      </div>
    );
  }

  if (status === 'lost') {
    return (
      <div className="bg-rose-950/70 border border-rose-500/60 text-rose-300 rounded-lg py-2.5 px-4 text-center font-bold text-sm shadow-md shadow-rose-950/50 flex items-center justify-center gap-2 mb-4">
        <span>🤖</span>
        <span>AI Victory. The algorithm played optimally!</span>
      </div>
    );
  }

  if (status === 'draw') {
    return (
      <div className="bg-amber-950/70 border border-amber-500/60 text-amber-300 rounded-lg py-2.5 px-4 text-center font-bold text-sm shadow-md shadow-amber-950/50 flex items-center justify-center gap-2 mb-4">
        <span>🤝</span>
        <span>It's a Draw! Both sides played effectively.</span>
      </div>
    );
  }

  // Active status
  return (
    <div className="bg-slate-800/80 border border-slate-700 rounded-lg py-2 px-4 text-center text-sm font-medium mb-4 flex items-center justify-center gap-2">
      {isThinking ? (
        <span className="flex items-center gap-2 text-rose-400">
          <svg className="animate-spin h-4 w-4 text-rose-400" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>AI is computing minimax tree...</span>
        </span>
      ) : (
        <span className="text-cyan-400 font-semibold flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Your Turn (X) — Select any vacant cell</span>
        </span>
      )}
    </div>
  );
}
