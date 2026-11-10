import React from 'react';
import { GameCell } from './GameCell';

export function GameBoard({
  board,
  winningLine,
  lastAIMove,
  disabled,
  onCellClick,
}) {
  return (
    <div
      role="grid"
      aria-label="Tic-Tac-Toe Board"
      className="grid grid-cols-3 gap-3 w-full max-w-[320px] sm:max-w-[360px] mx-auto p-3 bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur mb-6"
    >
      {board.map((cellValue, idx) => (
        <GameCell
          key={idx}
          index={idx}
          value={cellValue}
          isWinningCell={winningLine ? winningLine.includes(idx) : false}
          isLastAIMove={lastAIMove === idx}
          disabled={disabled}
          onClick={onCellClick}
        />
      ))}
    </div>
  );
}
