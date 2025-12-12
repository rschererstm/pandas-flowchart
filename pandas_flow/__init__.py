"""
Pandas Flow - A library for tracking pandas operations and generating visual flowcharts.

This library intercepts pandas operations, records metadata about each transformation,
and generates visual flowcharts using Cytoscape.js (interactive) or Mermaid syntax (static).
"""

from .cytoscape_renderer import CytoscapeRenderer
from .events import FlowEvent, OperationType
from .mermaid_renderer import THEMES, MermaidRenderer
from .stats import StatsCalculator
from .tracker import FlowTracker, setup

__version__ = "0.1.0"
__all__ = [
    "FlowTracker",
    "setup",
    "OperationType",
    "FlowEvent",
    "StatsCalculator",
    "MermaidRenderer",
    "CytoscapeRenderer",
    "THEMES",
]
