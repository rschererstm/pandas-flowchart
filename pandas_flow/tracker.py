"""
FlowTracker - Central object for tracking pandas operations.

This module provides the main interface for tracking DataFrame operations
and generating flow diagrams.
"""

from __future__ import annotations

import weakref
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import pandas as pd

from .cytoscape_renderer import CytoscapeRenderer
from .events import DataFrameInfo, FlowEvent, OperationType
from .mermaid_renderer import MermaidRenderer
from .stats import StatsCalculator

# Global tracker instance
_active_tracker: FlowTracker | None = None


def get_active_tracker() -> FlowTracker | None:
    """Get the currently active FlowTracker instance."""
    return _active_tracker


def setup(
    track_row_count: bool = True,
    track_variables: dict[str, str] | None = None,
    stats_variable: str | None = None,
    stats_types: list[str] | None = None,
    scatter_variables: tuple[str, str] | None = None,
    auto_intercept: bool = True,
    theme: str = "default",
    modern: bool = True,
) -> FlowTracker:
    """
    Set up a new FlowTracker and activate it.

    Args:
        track_row_count: Whether to track row counts after each operation
        track_variables: Dict mapping variable names to stat types
                        ("n_total", "n_non_null", "n_unique")
        stats_variable: Variable for detailed statistics (min, max, mean, etc.)
        stats_types: List of stat types for stats_variable
                    Options: "min", "max", "mean", "std", "top3_freq", "histogram"
        scatter_variables: Tuple of (x_column, y_column) for scatter plot
                         Only rendered in HTML mode
        auto_intercept: Whether to automatically intercept pandas operations
        theme: Color theme for the flowchart ("default", "dark", "light")
        modern: Use modern Cytoscape.js renderer (True) or classic Mermaid (False)
                True - Interactive graph with Cytoscape.js, TailwindCSS, side panel
                False - Classic Mermaid-based static diagram

    Returns:
        Configured FlowTracker instance

    Example:
        >>> flow = pandas_flow.setup(
        ...     track_row_count=True,
        ...     track_variables={
        ...         "patient_id": "n_unique",
        ...         "exam_date": "n_unique",
        ...     },
        ...     stats_variable="age",
        ...     stats_types=["min", "max", "mean", "std", "histogram"],
        ...     scatter_variables=("age", "result_value"),
        ...     modern=True,
        ... )
    """
    global _active_tracker

    tracker = FlowTracker(
        track_row_count=track_row_count,
        track_variables=track_variables,
        stats_variable=stats_variable,
        stats_types=stats_types,
        scatter_variables=scatter_variables,
        theme=theme,
        modern=modern,
    )

    if auto_intercept:
        tracker.install_interceptors()

    _active_tracker = tracker
    return tracker


class FlowTracker:
    """
    Central tracker for pandas operations.

    Maintains a log of all DataFrame operations and their metadata,
    and provides methods to generate visualizations.
    """

    def __init__(
        self,
        track_row_count: bool = True,
        track_variables: dict[str, str] | None = None,
        stats_variable: str | None = None,
        stats_types: list[str] | None = None,
        scatter_variables: tuple[str, str] | None = None,
        theme: str = "default",
        modern: bool = True,
    ):
        """
        Initialize the FlowTracker.

        Args:
            track_row_count: Whether to track row counts
            track_variables: Dict of variable_name -> stat_type
            stats_variable: Variable for detailed stats
            stats_types: Stat types for stats_variable
            scatter_variables: Tuple of (x_col, y_col) for scatter plot (HTML only)
            theme: Color theme
            modern: Use modern Cytoscape.js renderer (True) or Mermaid (False)
        """
        self.track_row_count = track_row_count
        self.track_variables = track_variables or {}
        self.stats_variable = stats_variable
        self.stats_types = stats_types or ["min", "max", "mean", "std", "top3_freq", "histogram"]
        self.scatter_variables = scatter_variables
        self.theme = theme
        self.modern = modern

        # Event storage
        self.events: list[FlowEvent] = []
        self._event_counter = 0

        # DataFrame tracking
        self._df_registry: dict[int, DataFrameInfo] = {}  # id(df) -> info
        self._df_names: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

        # Stats calculator
        self.stats_calculator = StatsCalculator(
            track_variables=track_variables,
            stats_variable=stats_variable,
            stats_types=stats_types,
        )

        # Histogram data storage (for HTML output)
        self._histogram_data: dict[str, pd.Series | list] = {}

        # Hexbin data storage (for HTML output)
        self._hexbin_data: dict[str, tuple[list, list]] = {}  # name -> (x_data, y_data)

        # Interceptor state
        self._interceptors_installed = False
        self._original_methods: dict[str, Any] = {}

        # Renderers
        self.renderer = MermaidRenderer(theme=theme)
        self.cytoscape_renderer = CytoscapeRenderer(theme=theme)

    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        self._event_counter += 1
        return f"op_{self._event_counter}"

    def register_dataframe(
        self,
        df: pd.DataFrame,
        name: str | None = None,
        source_file: str | None = None,
    ) -> None:
        """
        Register a DataFrame with a name and/or source file.

        Args:
            df: DataFrame to register
            name: Human-readable name for the DataFrame
            source_file: Source file path (for read operations)
        """
        info = self._get_df_info(df)
        info.name = name
        info.source_file = source_file
        self._df_registry[id(df)] = info

    def _get_df_info(self, df: pd.DataFrame) -> DataFrameInfo:
        """Get or create DataFrameInfo for a DataFrame."""
        df_id = id(df)

        if df_id in self._df_registry:
            info = self._df_registry[df_id]
            # Update with current state
            info.n_rows = len(df)
            info.n_cols = len(df.columns)
            info.columns = list(df.columns)
            return info

        return DataFrameInfo(
            n_rows=len(df),
            n_cols=len(df.columns),
            columns=list(df.columns),
            dtypes={str(col): str(dtype) for col, dtype in df.dtypes.items()},
            memory_usage=df.memory_usage(deep=True).sum(),
        )

    def _find_df_name(self, df: pd.DataFrame) -> str | None:
        """Try to find the variable name for a DataFrame."""
        df_id = id(df)
        if df_id in self._df_registry:
            return self._df_registry[df_id].name
        return None

    def record_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        input_dfs: list[pd.DataFrame],
        output_df: pd.DataFrame,
        description: str = "",
        arguments: dict[str, Any] | None = None,
        parent_events: list[str] | None = None,
    ) -> FlowEvent:
        """
        Record a pandas operation.

        Args:
            operation_type: Type of operation
            operation_name: Human-readable name
            input_dfs: Input DataFrame(s)
            output_df: Output DataFrame
            description: Optional description
            arguments: Relevant operation arguments
            parent_events: IDs of parent events (for merges)

        Returns:
            Created FlowEvent
        """
        event_id = self._generate_event_id()

        # Get DataFrame info
        input_infos = [self._get_df_info(df) for df in input_dfs]
        output_info = self._get_df_info(output_df)

        # Compute tracked stats
        tracked_stats = self.stats_calculator.compute_stats(output_df)

        # Store histogram data for stats_variable (for HTML output)
        if self.stats_variable and self.stats_variable in output_df.columns:
            self._histogram_data[self.stats_variable] = (
                output_df[self.stats_variable].dropna().tolist()
            )

        # Store hexbin data (for HTML output)
        if self.scatter_variables:
            x_col, y_col = self.scatter_variables
            if x_col in output_df.columns and y_col in output_df.columns:
                # Get aligned non-null data
                valid_mask = output_df[x_col].notna() & output_df[y_col].notna()
                x_data = output_df.loc[valid_mask, x_col].tolist()
                y_data = output_df.loc[valid_mask, y_col].tolist()
                hexbin_name = f"{x_col}_vs_{y_col}"
                self._hexbin_data[hexbin_name] = (x_data, y_data)

        # Create event
        event = FlowEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            operation_type=operation_type,
            operation_name=operation_name,
            description=description,
            input_dfs=input_infos,
            output_df=output_info,
            arguments=arguments or {},
            tracked_stats=tracked_stats,
            parent_events=parent_events or [],
        )

        self.events.append(event)

        # Register output DataFrame
        self._df_registry[id(output_df)] = output_info

        return event

    def track(
        self,
        operation_name: str,
        operation_type: OperationType = OperationType.CUSTOM,
        description: str = "",
    ) -> Callable:
        """
        Decorator to track a custom operation.

        Args:
            operation_name: Name for the operation
            operation_type: Type of operation
            description: Description of what the operation does

        Returns:
            Decorator function

        Example:
            >>> @flow.track("Clean Data", OperationType.CUSTOM)
            ... def clean_data(df):
            ...     return df.dropna().reset_index(drop=True)
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Get input DataFrame (assume first arg)
                input_df = args[0] if args else None

                # Call the function
                result = func(*args, **kwargs)

                # Record if we got DataFrames
                if isinstance(input_df, pd.DataFrame) and isinstance(result, pd.DataFrame):
                    self.record_operation(
                        operation_type=operation_type,
                        operation_name=operation_name,
                        input_dfs=[input_df],
                        output_df=result,
                        description=description,
                    )

                return result

            return wrapper

        return decorator

    @contextmanager
    def operation(
        self,
        operation_name: str,
        operation_type: OperationType = OperationType.CUSTOM,
        description: str = "",
    ):
        """
        Context manager for tracking an operation.

        Args:
            operation_name: Name for the operation
            operation_type: Type of operation
            description: Description

        Example:
            >>> with flow.operation("Filter Adults", OperationType.FILTER):
            ...     df = df[df["age"] >= 18]
        """
        # This context manager approach is limited - prefer explicit tracking
        yield

    def install_interceptors(self) -> None:
        """Install pandas method interceptors."""
        if self._interceptors_installed:
            return

        from . import interceptors

        interceptors.install(self)
        self._interceptors_installed = True

    def uninstall_interceptors(self) -> None:
        """Remove pandas method interceptors."""
        if not self._interceptors_installed:
            return

        from . import interceptors

        interceptors.uninstall(self)
        self._interceptors_installed = False

    def clear(self) -> None:
        """Clear all recorded events."""
        self.events.clear()
        self._event_counter = 0
        self._df_registry.clear()

    def render(
        self,
        output_path: str,
        title: str = "Data Flow Pipeline",
        direction: str = "TB",
        include_legend: bool = False,
        include_stats: bool = True,
        show_removed_data: bool = True,
        show_merge_inputs: bool = True,
    ) -> str:
        """
        Render the flow diagram to a file.

        Args:
            output_path: Output file path (.md, .html, or .mmd)
            title: Diagram title
            direction: Flow direction ("TB", "LR", "BT", "RL")
            include_legend: Whether to include a color legend
            include_stats: Whether to include statistics in boxes
            show_removed_data: Show boxes for data removed by filter/drop operations
            show_merge_inputs: Show both input DataFrames for merge operations

        Returns:
            Generated content (Mermaid code for .md/.mmd, HTML for .html)
        """
        # Determine if HTML mode
        is_html = output_path.endswith(".html")

        # Use Cytoscape renderer for HTML if modern mode is enabled
        if is_html and self.modern:
            content = self.cytoscape_renderer.render(
                events=self.events,
                title=title,
                direction=direction,
                include_stats=include_stats,
                show_removed_data=show_removed_data,
                show_merge_inputs=show_merge_inputs,
                histogram_data=self._histogram_data if self._histogram_data else None,
                hexbin_data=self._hexbin_data if self._hexbin_data else None,
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return content

        # Use Mermaid renderer for other formats or if explicitly configured
        mermaid_code = self.renderer.render(
            events=self.events,
            title=title,
            direction=direction,
            include_legend=include_legend,
            include_stats=include_stats,
            show_removed_data=show_removed_data,
            show_merge_inputs=show_merge_inputs,
            html_mode=is_html,
            histogram_data=self._histogram_data if is_html and self._histogram_data else None,
            hexbin_data=self._hexbin_data if is_html and self._hexbin_data else None,
        )

        # Determine output format
        if is_html:
            content = self.renderer.wrap_html(mermaid_code, title)
        elif output_path.endswith(".mmd"):
            content = mermaid_code
        else:  # Default to markdown
            content = self.renderer.wrap_markdown(mermaid_code, title)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return mermaid_code

    def get_mermaid(
        self,
        title: str = "Data Flow Pipeline",
        direction: str = "TB",
        include_legend: bool = True,
        include_stats: bool = True,
        show_removed_data: bool = True,
        show_merge_inputs: bool = True,
    ) -> str:
        """
        Get the Mermaid diagram code without saving.

        Args:
            title: Diagram title
            direction: Flow direction
            include_legend: Whether to include legend
            include_stats: Whether to include stats
            show_removed_data: Show boxes for data removed by filter/drop operations
            show_merge_inputs: Show both input DataFrames for merge operations

        Returns:
            Mermaid code string
        """
        return self.renderer.render(
            events=self.events,
            title=title,
            direction=direction,
            include_legend=include_legend,
            include_stats=include_stats,
            show_removed_data=show_removed_data,
            show_merge_inputs=show_merge_inputs,
        )

    def summary(self) -> str:
        """
        Get a text summary of all recorded operations.

        Returns:
            Formatted summary string
        """
        lines = [
            "=" * 60,
            "PANDAS FLOW SUMMARY",
            "=" * 60,
            f"Total operations: {len(self.events)}",
            "",
        ]

        for i, event in enumerate(self.events, 1):
            lines.append(f"{i}. {event.operation_name} ({event.operation_type.value})")
            if event.output_df:
                lines.append(
                    f"   → {event.output_df.n_rows:,} rows × {event.output_df.n_cols} cols"
                )
            for stat in event.tracked_stats:
                if stat.n_unique > 0:
                    lines.append(f"   • {stat.name}: {stat.n_unique:,} unique")
            lines.append("")

        return "\n".join(lines)

    def __enter__(self) -> FlowTracker:
        """Enter context - activate this tracker."""
        global _active_tracker
        self._previous_tracker = _active_tracker
        _active_tracker = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context - restore previous tracker."""
        global _active_tracker
        _active_tracker = self._previous_tracker
        self.uninstall_interceptors()

    def __repr__(self) -> str:
        return f"FlowTracker(events={len(self.events)}, interceptors={'on' if self._interceptors_installed else 'off'})"
