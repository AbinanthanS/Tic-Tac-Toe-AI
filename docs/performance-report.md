# Performance & Benchmark Report: Minimax vs. Alpha-Beta Pruning

This report presents an empirical, reproducible performance evaluation comparing **Exhaustive Minimax** against **Minimax with Alpha-Beta ($\alpha$-$\beta$) Pruning** across four representative game-tree topologies in Tic-Tac-Toe.

---

## 1. Experimental Methodology

* **Hardware/Environment**: Windows x86_64, Python 3.11.9
* **Measurement Tool**: High-resolution wall-clock timer `time.perf_counter_ns()`
* **Repetitions**: 5 independent runs per board position; **median execution time** reported to eliminate OS scheduling jitter.
* **Invariant**: Both algorithms were executed with identical move ordering and evaluated using the exact same depth-penalized terminal scoring function. Both produced identical, mathematically optimal moves.

---

## 2. Actual Measured Results

The benchmark was executed via `python backend/benchmark.py`. The real, unmanipulated measurements are recorded below:

| Board Position Topology | Plain Minimax (Nodes) | Alpha-Beta (Nodes) | Cutoffs Triggered | Plain Minimax (Median ms) | Alpha-Beta (Median ms) | Search Space Reduction | Wall-Clock Speedup |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Empty Board (Worst Case)**<br>*(9 cells available)* | 549,945 | **20,865** | 7,692 | 2,315.49 ms | **95.73 ms** | **96.2%** | **24.2x** |
| **2. Early Game**<br>*(Human center move 4)* | 55,504 | **2,458** | 965 | 227.65 ms | **11.00 ms** | **95.6%** | **20.7x** |
| **3. Mid Game (Fork Threat)**<br>*(Human corners 0 & 8, AI center 4)* | 1,052 | **355** | 116 | 4.14 ms | **1.53 ms** | **66.3%** | **2.7x** |
| **4. Late Game**<br>*(6 moves played, 3 open cells)* | 11 | **9** | 2 | 0.05 ms | **0.08 ms** | **18.2%** | **0.7x** |

---

## 3. Key Engineering Findings & Architectural Insights

### 3.1 Exponential Pruning Efficiency in Deep Trees
In the early game and empty board states (depth $\ge 8$), Alpha-Beta pruning demonstrated a **96.2% reduction in explored states**, collapsing over half a million recursive function calls down to just 20,865. This directly translated to a **24x wall-clock speedup** (from 2.3 seconds down to under 100 milliseconds).

### 3.2 The Bookkeeping Overhead in Shallow Endgames (Crucial Senior Interview Insight)
In the late game (position 4 with only 3 open cells), plain Minimax visited 11 nodes, while Alpha-Beta visited 9 nodes (pruning 2 branches). However:
- Plain Minimax median time: `0.05 ms`
- Alpha-Beta median time: `0.08 ms`

**Why did Alpha-Beta take slightly longer in the endgame?**
When the remaining search depth is tiny ($< 3$ plies), the constant-factor algorithmic overhead—updating $\alpha$ and $\beta$ variables, passing additional function arguments on the Python call stack, and evaluating conditional cutoff checks ($\beta \le \alpha$)—exceeds the negligible cost of evaluating the 2 pruned leaf nodes.
*Takeaway*: Alpha-Beta pruning provides massive asymptotic gains for deep trees, while in near-terminal shallow states the tree size is so small that both algorithms are instantaneous.

---

## 4. Reproducing the Experiment

To reproduce these exact measurements on your machine:
```powershell
python backend/benchmark.py
```
