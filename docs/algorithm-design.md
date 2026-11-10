# Algorithm Design & Complexity Analysis

This document provides a comprehensive technical breakdown of the game-playing algorithms implemented in the project:
1. **Plain Minimax**
2. **Minimax with Alpha-Beta ($\alpha$-$\beta$) Pruning**
3. **Depth-Limited Heuristic Search**
4. **Empirical Benchmarks & Comparative Performance**

---

## 1. The Game Tree & Minimax Theory

Tic-Tac-Toe is a **zero-sum, finite, perfect-information game** between two players:
- **Maximizer ($+$)**: The AI (`Player.AI`, `"O"`), which aims to reach states with maximum score.
- **Minimizer ($-$)**: The Human (`Player.HUMAN`, `"X"`), which aims to reach states with minimum score.

### 1.1 Terminal Scoring Function
To make the AI select the fastest path to victory (and resist defeat as long as possible when losing), the terminal evaluation function incorporates search depth $d$:

$$\text{Score}(s, d) = \begin{cases} +10 - d & \text{if AI wins at depth } d \\ d - 10 & \text{if Human wins at depth } d \\ 0 & \text{if Draw} \end{cases}$$

*Example*: An AI win at ply $d=1$ scores $+9$, whereas an AI win at ply $d=3$ scores $+7$. Since $+9 > +7$, the AI prioritizes the immediate one-ply strike.

---

## 2. Alpha-Beta ($\alpha$-$\beta$) Pruning

Alpha-Beta pruning is an adversarial search optimization that guarantees identical output to Minimax while skipping subtrees that cannot influence the final decision.

### 2.1 The Invariants
- $\alpha$: The highest value that the Maximizer is guaranteed to achieve along the current path.
- $\beta$: The lowest value that the Minimizer is guaranteed to achieve along the current path.

At the root: $\alpha = -\infty$, $\beta = +\infty$.

### 2.2 Cutoff Conditions
1. **Beta Cutoff (Maximizing Node)**:
   When evaluating children at a maximizing node, if:
   $$\alpha \ge \beta$$
   The parent minimizing node already has a guaranteed path that is better for the Minimizer ($\le \beta$). Therefore, the Minimizer will never allow play to reach this branch. We immediately stop searching further sibling moves (**cutoff**).

2. **Alpha Cutoff (Minimizing Node)**:
   When evaluating children at a minimizing node, if:
   $$\beta \le \alpha$$
   The parent maximizing node already has a guaranteed alternative yielding at least $\alpha$. Thus, the Maximizer will never choose to enter this branch. We prune the remaining children (**cutoff**).

---

## 3. Depth-Limited Minimax with Static Heuristics (Medium Mode)

When depth $d$ reaches `max_depth = 2` without a game conclusion, the algorithm evaluates board positional control using a static heuristic function $H(s)$:

$$H(s) = 3 \times (\text{AI 2-in-a-rows with 3rd open}) - 3 \times (\text{Human 2-in-a-rows with 3rd open}) + C_{\text{pos}}$$

Where positional weighting $C_{\text{pos}}$ awards:
- $+2$ for AI controlling center (cell 4), $-2$ for Human.
- $+1$ for AI controlling corners ($0, 2, 6, 8$), $-1$ for Human.

This makes Medium AI play defensively and tactically competent, while remaining vulnerable to multi-ply tactical forks that require looking 3 or more steps ahead.

---

## 4. Empirical Benchmark: Minimax vs. Alpha-Beta

Both algorithms were executed on an empty board (worst-case search tree size). Measurements were captured on Python 3.11 using `time.perf_counter_ns()`.

| Metric | Plain Minimax | Alpha-Beta Pruning | Optimization Impact |
| :--- | :--- | :--- | :--- |
| **Move Selected** | Cell 0 (or symmetric) | Cell 0 (or symmetric) | Identical decision quality |
| **Nodes Explored** | **549,945** | **20,865** | **96.2% reduction in search space** |
| **Cutoffs Triggered** | 0 (Exhaustive) | **7,692** | 7,692 subtrees pruned |
| **Execution Time** | **1,507 ms** | **59 ms** | **~25x speedup** |
| **Max Depth Reached** | 9 | 9 | Complete depth coverage |

### Complexity Analysis:
- **Plain Minimax**: $O(b^d)$, where $b$ is the effective branching factor and $d$ is depth. On an empty board, $9! = 362,880$ terminal leaves, resulting in $> 540,000$ recursive node visits.
- **Alpha-Beta Pruning**: In optimal move ordering, complexity is reduced to $O(b^{d/2})$, effectively doubling the searchable depth in equivalent time.

