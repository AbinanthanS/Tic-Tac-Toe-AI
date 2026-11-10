import React from 'react';

export function ScoreBoard({ scoreboard, onClearScoreboard }) {
  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 mb-6 shadow-lg backdrop-blur">
      <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2 px-1">
        <span>Session Scoreboard</span>
        <button
          onClick={onClearScoreboard}
          title="Reset score counters"
          className="hover:text-rose-400 transition-colors text-[11px] underline cursor-pointer"
        >
          Reset Scores
        </button>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        {/* Human Score */}
        <div className="bg-slate-900/70 border border-cyan-900/50 rounded-lg p-2">
          <div className="text-xs text-cyan-400 font-bold uppercase tracking-wider">Human (X)</div>
          <div className="text-2xl font-black text-cyan-300 mt-0.5">{scoreboard.humanWins}</div>
        </div>

        {/* Draws */}
        <div className="bg-slate-900/70 border border-slate-700/50 rounded-lg p-2">
          <div className="text-xs text-slate-400 font-bold uppercase tracking-wider">Draws</div>
          <div className="text-2xl font-black text-slate-300 mt-0.5">{scoreboard.draws}</div>
        </div>

        {/* AI Score */}
        <div className="bg-slate-900/70 border border-rose-900/50 rounded-lg p-2">
          <div className="text-xs text-rose-400 font-bold uppercase tracking-wider">AI (O)</div>
          <div className="text-2xl font-black text-rose-300 mt-0.5">{scoreboard.aiWins}</div>
        </div>
      </div>
    </div>
  );
}
