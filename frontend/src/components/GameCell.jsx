import React from 'react';

export function GameCell({
  index,
  value,
  isWinningCell,
  isLastAIMove,
  disabled,
  onClick,
}) {
  const isOccupied = value !== null;

  return (
    <button
      type="button"
      role="gridcell"
      aria-label={`Cell ${index}: ${value || 'Empty'}`}
      onClick={() => onClick(index)}
      disabled={disabled || isOccupied}
      className={`relative flex items-center justify-center text-4xl sm:text-5xl font-black rounded-xl transition-all duration-150 aspect-square select-none ${
        isWinningCell
          ? 'winning-cell bg-cyan-950/80 border-2 border-cyan-400 text-cyan-300'
          : isOccupied
          ? 'bg-slate-800/90 border border-slate-700/80'
          : 'bg-slate-800/40 border border-slate-700/50 hover:bg-slate-700/50 hover:border-slate-500 cursor-pointer active:scale-95'
      } ${disabled && !isOccupied ? 'cursor-not-allowed opacity-60' : ''}`}
    >
      {/* Last AI Move Marker */}
      {isLastAIMove && value === 'O' && (
        <span
          title="Last AI move"
          className="absolute top-1 right-1.5 text-[9px] font-extrabold uppercase px-1 py-0.2 bg-rose-950 border border-rose-600/70 text-rose-300 rounded"
        >
          AI
        </span>
      )}

      {/* Symbol Rendering */}
      {value === 'X' && (
        <span className="text-cyan-400 drop-shadow-[0_0_12px_rgba(6,182,212,0.8)] animate-in fade-in zoom-in-75 duration-150">
          X
        </span>
      )}

      {value === 'O' && (
        <span className="text-rose-400 drop-shadow-[0_0_12px_rgba(244,63,94,0.8)] animate-in fade-in zoom-in-75 duration-150">
          O
        </span>
      )}
    </button>
  );
}
