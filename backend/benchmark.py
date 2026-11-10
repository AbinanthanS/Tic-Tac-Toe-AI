"""
Standalone Reproducible Benchmarking Suite.
Compares Plain Minimax vs Alpha-Beta Pruning across representative board states.

Execution:
    python backend/benchmark.py
"""

import statistics
import time
from app.algorithms.minimax import MinimaxStrategy
from app.algorithms.alpha_beta import AlphaBetaStrategy
from app.domain.models import Board, Player


def run_benchmark_for_position(name: str, board: Board, repetitions: int = 5):
    minimax = MinimaxStrategy()
    alphabeta = AlphaBetaStrategy()

    # 1. Plain Minimax measurements
    mm_times = []
    mm_result = None
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        mm_result = minimax.select_move(board)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        mm_times.append(elapsed_ms)

    mm_median_time = statistics.median(mm_times)

    # 2. Alpha-Beta Pruning measurements
    ab_times = []
    ab_result = None
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        ab_result = alphabeta.select_move(board)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        ab_times.append(elapsed_ms)

    ab_median_time = statistics.median(ab_times)

    # Reduction metrics
    node_reduction_pct = (
        (1.0 - (ab_result.metrics.nodes_explored / mm_result.metrics.nodes_explored)) * 100.0
        if mm_result.metrics.nodes_explored > 0 else 0.0
    )
    speedup = mm_median_time / ab_median_time if ab_median_time > 0 else 1.0

    return {
        "position_name": name,
        "mm_move": mm_result.position,
        "ab_move": ab_result.position,
        "mm_nodes": mm_result.metrics.nodes_explored,
        "ab_nodes": ab_result.metrics.nodes_explored,
        "ab_cutoffs": ab_result.metrics.cutoffs_count,
        "mm_median_ms": mm_median_time,
        "ab_median_ms": ab_median_time,
        "node_reduction_pct": node_reduction_pct,
        "speedup": speedup,
    }


def main():
    print("=" * 80)
    print("   TIC-TAC-TOE AI ALGORITHM BENCHMARK: MINIMAX vs ALPHA-BETA PRUNING")
    print("=" * 80)
    print("Running 5 repetitions per position using time.perf_counter_ns()...\n")

    test_positions = [
        (
            "1. Empty Board (9 Open Cells - Worst Case)",
            Board(),
        ),
        (
            "2. Early Game (Human opened Center Cell 4)",
            Board.from_sequence([
                None, None, None,
                None, "X", None,
                None, None, None
            ]),
        ),
        (
            "3. Mid Game (Fork Threat: Human corners 0 and 8, AI center 4)",
            Board.from_sequence([
                "X", None, None,
                None, "O", None,
                None, None, "X"
            ]),
        ),
        (
            "4. Late Game (6 Moves Played - 3 Open Cells)",
            Board.from_sequence([
                "X", "O", "X",
                "X", "O", None,
                "O", None, None
            ]),
        ),
    ]

    results = []
    for name, board in test_positions:
        print(f"Benchmarking: {name}...")
        res = run_benchmark_for_position(name, board, repetitions=5)
        results.append(res)

    print("\n" + "=" * 80)
    print("                           MEASURED BENCHMARK RESULTS")
    print("=" * 80)
    header = f"{'Position':<32} | {'MM Nodes':>10} | {'AB Nodes':>10} | {'Cutoffs':>8} | {'MM (ms)':>9} | {'AB (ms)':>8} | {'Reduction':>10} | {'Speedup':>8}"
    print(header)
    print("-" * len(header))

    for r in results:
        print(
            f"{r['position_name'][:32]:<32} | "
            f"{r['mm_nodes']:>10,d} | "
            f"{r['ab_nodes']:>10,d} | "
            f"{r['ab_cutoffs']:>8,d} | "
            f"{r['mm_median_ms']:>9.2f} | "
            f"{r['ab_median_ms']:>8.2f} | "
            f"{r['node_reduction_pct']:>9.1f}% | "
            f"{r['speedup']:>7.1f}x"
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
