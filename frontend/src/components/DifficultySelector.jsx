import React from 'react';

const DIFFICULTIES = [
  { id: 'easy', label: 'Easy', desc: 'Random moves', color: 'border-emerald-500/40 text-emerald-400 hover:bg-emerald-950/30' },
  { id: 'medium', label: 'Medium', desc: 'Depth-2 Heuristics', color: 'border-amber-500/40 text-amber-400 hover:bg-amber-950/30' },
  { id: 'hard', label: 'Hard', desc: 'Optimal Alpha-Beta', color: 'border-cyan-500/40 text-cyan-400 hover:bg-cyan-950/30' },
];

export function DifficultySelector({ currentDifficulty, onSelectDifficulty, disabled }) {
  return (
    <div className="flex flex-col sm:flex-row gap-2 justify-center mb-6">
      {DIFFICULTIES.map((diff) => {
        const isActive = currentDifficulty === diff.id;
        return (
          <button
            key={diff.id}
            onClick={() => onSelectDifficulty(diff.id)}
            disabled={disabled}
            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all duration-200 flex flex-col items-center justify-center min-w-[110px] ${
              isActive
                ? 'bg-slate-800 border-cyan-400 text-white shadow-md shadow-cyan-950 ring-2 ring-cyan-500/30'
                : 'bg-slate-900/80 border-slate-700/60 text-slate-400 hover:text-slate-200 hover:border-slate-600'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer active:scale-95'}`}
          >
            <span className="font-semibold">{diff.label}</span>
            <span className="text-[10px] text-slate-400">{diff.desc}</span>
          </button>
        );
      })}
    </div>
  );
}
