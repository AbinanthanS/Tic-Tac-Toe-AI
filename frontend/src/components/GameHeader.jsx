import React from 'react';

export function GameHeader({ isThinking }) {
  return (
    <header className="text-center mb-6">
      <div className="inline-flex items-center gap-2 px-3 py-1 bg-cyan-950/60 border border-cyan-800/50 rounded-full text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-2">
        <span>Minimax</span>
        <span>•</span>
        <span>Alpha-Beta Pruning</span>
        <span>•</span>
        <span className="text-emerald-400">FastAPI</span>
      </div>
      <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
        Tic-Tac-Toe AI
      </h1>
      <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
        Challenge an optimal adversarial AI powered by depth-limited heuristics and branch pruning.
      </p>
    </header>
  );
}
