import React from 'react';

export function AIThinkingPanel({ metrics, isThinking, difficulty }) {
  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 shadow-lg backdrop-blur mb-6">
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-2 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-base">⚡</span>
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            AI Search Telemetry & Analytics
          </h2>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-400 font-mono">
          Mode: {difficulty.toUpperCase()}
        </span>
      </div>

      {metrics ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Nodes Explored */}
          <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-2.5">
            <div className="text-[11px] text-slate-400">Nodes Explored</div>
            <div className="text-lg font-black text-cyan-400 font-mono mt-0.5">
              {metrics.nodes_explored.toLocaleString()}
            </div>
          </div>

          {/* Cutoffs Count */}
          <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-2.5">
            <div className="text-[11px] text-slate-400">α-β Cutoffs</div>
            <div className="text-lg font-black text-amber-400 font-mono mt-0.5">
              {metrics.cutoffs_count.toLocaleString()}
            </div>
          </div>

          {/* Search Depth */}
          <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-2.5">
            <div className="text-[11px] text-slate-400">Max Depth</div>
            <div className="text-lg font-black text-indigo-400 font-mono mt-0.5">
              {metrics.max_depth_reached} plies
            </div>
          </div>

          {/* Compute Time */}
          <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-2.5">
            <div className="text-[11px] text-slate-400">Execution Time</div>
            <div className="text-lg font-black text-emerald-400 font-mono mt-0.5">
              {metrics.execution_time_ms.toFixed(2)} ms
            </div>
          </div>
        </div>
      ) : isThinking ? (
        <div className="py-4 text-center text-xs text-rose-400 animate-pulse font-mono">
          Searching game tree, scoring heuristics, and evaluating terminal positions...
        </div>
      ) : (
        <div className="py-4 text-center text-xs text-slate-400 font-mono">
          Make a move to view real-time Minimax tree exploration telemetry.
        </div>
      )}
    </div>
  );
}
