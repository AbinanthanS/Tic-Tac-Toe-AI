"""
Search metrics instrumentation for AI algorithms.
"""

from dataclasses import dataclass
import time


@dataclass(slots=True)
class AIMetrics:
    """
    Search telemetry captured during AI move calculation.
    
    Attributes:
        nodes_explored: Total invocations of the search function (Minimax/AlphaBeta).
        cutoffs_count: Total alpha or beta cutoffs triggered.
        terminal_states_evaluated: Number of leaf nodes where a terminal state or depth-limit was evaluated.
        max_depth_reached: Deepest ply reached in the search tree.
        execution_time_ms: Wall-clock execution time in milliseconds.
    """
    nodes_explored: int = 0
    cutoffs_count: int = 0
    terminal_states_evaluated: int = 0
    max_depth_reached: int = 0
    execution_time_ms: float = 0.0


@dataclass(slots=True)
class AIResult:
    """
    Structured response returned by an AI strategy.
    
    Attributes:
        position: The 0-indexed cell chosen by the AI.
        metrics: Search telemetry data.
    """
    position: int
    metrics: AIMetrics
