"""
Pandas Flow - A library for tracking pandas operations and generating Mermaid flowcharts.

This library intercepts pandas operations, records metadata about each transformation,
and generates visual flowcharts using Mermaid syntax.
"""

from .tracker import FlowTracker, setup
from .events import OperationType, FlowEvent
from .stats import StatsCalculator
from .mermaid_renderer import MermaidRenderer

__version__ = "0.1.0"
__all__ = [
    "FlowTracker",
    "setup",
    "OperationType",
    "FlowEvent",
    "StatsCalculator",
    "MermaidRenderer",
]

