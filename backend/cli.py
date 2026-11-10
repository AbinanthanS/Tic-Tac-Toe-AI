"""
Interactive CLI Runner for Tic-Tac-Toe AI.
Demonstrates decoupled, headless execution of the AI Engine and Domain Model.

Execution:
    python backend/cli.py
"""

from app.domain.models import GameState, GameStatus, Player, Difficulty
from app.algorithms.factory import get_ai_strategy


def print_board(game: GameState) -> None:
    symbols = []
    for idx, cell in enumerate(game.board.cells):
        if cell is not None:
            symbols.append(cell.value)
        else:
            symbols.append(str(idx))

    print()
    print(f" {symbols[0]} | {symbols[1]} | {symbols[2]} ")
    print("---+---+---")
    print(f" {symbols[3]} | {symbols[4]} | {symbols[5]} ")
    print("---+---+---")
    print(f" {symbols[6]} | {symbols[7]} | {symbols[8]} ")
    print()


def main():
    print("=" * 50)
    print("       TIC-TAC-TOE AI — TERMINAL INTERACTION")
    print("=" * 50)
    print("Difficulty Levels:")
    print("  1. Easy   (Random AI)")
    print("  2. Medium (Depth-2 Heuristic Minimax)")
    print("  3. Hard   (Optimal Alpha-Beta Pruning)")

    diff_choice = input("\nSelect difficulty [1-3, default 3]: ").strip()
    diff_map = {"1": Difficulty.EASY, "2": Difficulty.MEDIUM, "3": Difficulty.HARD}
    difficulty = diff_map.get(diff_choice, Difficulty.HARD)
    print(f"Starting game on {difficulty.value.upper()} mode!\n")

    game = GameState(difficulty=difficulty)
    ai_strategy = get_ai_strategy(difficulty)

    while game.status == GameStatus.ACTIVE:
        print_board(game)

        if game.current_player == Player.HUMAN:
            valid_moves = game.board.available_moves()
            while True:
                user_input = input(f"Your turn (X). Choose cell {valid_moves}: ").strip()
                if user_input.isdigit() and int(user_input) in valid_moves:
                    pos = int(user_input)
                    break
                print("Invalid input. Please choose an available cell number.")

            game.apply_move(pos, Player.HUMAN)
        else:
            print("AI is calculating optimal move...")
            ai_res = ai_strategy.select_move(game.board)
            print(f"AI chose cell {ai_res.position} in {ai_res.metrics.execution_time_ms:.2f} ms")
            print(f"(Nodes visited: {ai_res.metrics.nodes_explored}, Cutoffs: {ai_res.metrics.cutoffs_count})")
            game.apply_move(ai_res.position, Player.AI)

    print_board(game)

    if game.status == GameStatus.WON:
        print("🏆 Congratulations! You won!")
    elif game.status == GameStatus.LOST:
        print("🤖 Game Over. The AI won!")
    elif game.status == GameStatus.DRAW:
        print("🤝 It's a Draw! Well played!")


if __name__ == "__main__":
    main()
