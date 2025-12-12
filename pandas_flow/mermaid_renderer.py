"""
Mermaid diagram renderer for pandas_flow.

Generates Mermaid flowchart syntax from FlowEvent sequences,
with styled boxes, statistics, and visual indicators.
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

import pandas as pd

from .events import (
    OPERATION_CATEGORIES,
    OPERATION_COLORS,
    FlowEvent,
    OperationType,
    TrackedVariableStats,
)

if TYPE_CHECKING:
    pass


# Theme definitions
THEMES = {
    "default": {
        "background": "#ffffff",
        "text": "#333333",
        "border": "#cccccc",
        "arrow": "#666666",
        "title_bg": "#f0f0f0",
        "use_colors": True,
    },
    "dark": {
        "background": "#1a1a2e",
        "text": "#eaeaea",
        "border": "#4a4a6a",
        "arrow": "#8a8aaa",
        "title_bg": "#16213e",
        "use_colors": True,
    },
    "light": {
        "background": "#fafafa",
        "text": "#2d2d2d",
        "border": "#e0e0e0",
        "arrow": "#888888",
        "title_bg": "#f5f5f5",
        "use_colors": True,
    },
    "minimal": {
        "background": "#ffffff",
        "text": "#333333",
        "border": "#999999",
        "arrow": "#666666",
        "title_bg": "#f0f0f0",
        "use_colors": False,
        "node_fill": "#f5f5f5",
        "node_stroke": "#666666",
    },
    "monochrome": {
        "background": "#ffffff",
        "text": "#000000",
        "border": "#000000",
        "arrow": "#000000",
        "title_bg": "#ffffff",
        "use_colors": False,
        "node_fill": "#ffffff",
        "node_stroke": "#000000",
    },
    "grayscale": {
        "background": "#fafafa",
        "text": "#333333",
        "border": "#888888",
        "arrow": "#555555",
        "title_bg": "#eeeeee",
        "use_colors": False,
        "node_fill": "#e8e8e8",
        "node_stroke": "#888888",
    },
}


class MermaidRenderer:
    """
    Renders FlowEvents as Mermaid flowchart diagrams.

    Features:
    - Color-coded operation boxes
    - Statistics display in each box
    - Connection arrows showing data flow
    - Legend for operation types
    - Multiple output formats (Markdown, HTML)
    - Merge operations show both input DataFrames
    - Filter/Drop operations show removed data
    - Embedded mini histograms in HTML mode
    """

    def __init__(self, theme: str = "default"):
        """
        Initialize the renderer.

        Args:
            theme: Color theme ("default", "dark", "light", "minimal", "monochrome", "grayscale")
        """
        self.theme = THEMES.get(theme, THEMES["default"])
        self.theme_name = theme
        self._html_mode = False
        self._histogram_data: dict[str, Any] = {}  # Store data for histogram generation
        self._hexbin_data: dict[str, tuple[list, list]] = {}  # Store data for scatter generation

    def render(
        self,
        events: list[FlowEvent],
        title: str = "Data Flow Pipeline",
        direction: str = "TB",
        include_legend: bool = False,
        include_stats: bool = True,
        show_removed_data: bool = True,
        show_merge_inputs: bool = True,
        html_mode: bool = False,
        histogram_data: dict[str, pd.Series | list] | None = None,
        hexbin_data: dict[str, tuple[list, list]] | None = None,
    ) -> str:
        """
        Render events as Mermaid flowchart code.

        Args:
            events: List of FlowEvents to render
            title: Diagram title
            direction: Flow direction (TB, LR, BT, RL)
            include_legend: Whether to include operation type legend
            include_stats: Whether to include statistics in boxes
            show_removed_data: Show boxes for data removed by filter/drop operations
            show_merge_inputs: Show both input DataFrames for merge operations
            html_mode: If True, embed mini histogram/hexbin images in node labels
            histogram_data: Dict of {variable_name: data_series} for histogram generation
            hexbin_data: Dict of {name: (x_data, y_data)} for scatter plot generation

        Returns:
            Mermaid flowchart code string
        """
        self._html_mode = html_mode
        self._histogram_data = histogram_data or {}
        self._hexbin_data = hexbin_data or {}

        if not events:
            return self._empty_diagram(title, direction)

        lines = [
            f"flowchart {direction}",
            "",
        ]

        # Build a map of DataFrame sources for merge visualization
        df_source_map = self._build_df_source_map(events)

        # Generate node definitions
        lines.append("    %% Node definitions")
        removed_nodes = []  # Track removed data nodes

        for event in events:
            node_def = self._render_node(event, include_stats)
            lines.append(node_def)

            # Generate removed data node for filter/drop operations
            if show_removed_data and self._is_data_removal_operation(event):
                removed_node = self._render_removed_data_node(event)
                if removed_node:
                    lines.append(removed_node)
                    removed_nodes.append(event.event_id)

        lines.append("")

        # Generate connections
        lines.append("    %% Connections")
        connections = self._generate_connections(
            events,
            df_source_map,
            show_merge_inputs,
            removed_nodes,
        )
        lines.extend(connections)

        lines.append("")

        # Generate styles
        lines.append("    %% Styles")
        styles = self._generate_styles(events, removed_nodes)
        lines.extend(styles)

        # Add legend subgraph
        if include_legend:
            lines.append("")
            legend = self._generate_legend(events)
            lines.extend(legend)

        return "\n".join(lines)

    def _empty_diagram(self, title: str, direction: str) -> str:
        """Generate an empty diagram placeholder."""
        return f"""flowchart {direction}
    empty["No operations recorded"]
    style empty fill:#f9f9f9,stroke:#ccc,stroke-dasharray: 5 5
"""

    def _build_df_source_map(self, events: list[FlowEvent]) -> dict[str, str]:
        """
        Build a map from DataFrame names/sources to event IDs.

        This helps identify which events produced which DataFrames
        for proper merge visualization.
        """
        df_map = {}

        for event in events:
            # Register output DataFrame by various identifiers
            if event.output_df:
                if event.output_df.name:
                    df_map[event.output_df.name] = event.event_id
                if event.output_df.source_file:
                    df_map[event.output_df.source_file] = event.event_id

            # Also register input DataFrames
            for df_info in event.input_dfs:
                if df_info.name and df_info.name not in df_map:
                    df_map[df_info.name] = event.event_id
                if df_info.source_file and df_info.source_file not in df_map:
                    df_map[df_info.source_file] = event.event_id

        return df_map

    def _is_data_removal_operation(self, event: FlowEvent) -> bool:
        """Check if this operation removes data."""
        if (
            event.operation_type
            in [
                OperationType.FILTER,
                OperationType.LOC,
                OperationType.ILOC,
                OperationType.QUERY,
                OperationType.DROP_DUPLICATES,
                OperationType.DROPNA,
            ]
            and event.input_dfs
            and event.output_df
        ):
            # Check if rows were actually removed
            return event.input_dfs[0].n_rows > event.output_df.n_rows
        return False

    def _render_removed_data_node(self, event: FlowEvent) -> str | None:
        """Render a node showing removed data for filter/drop operations."""
        if not event.input_dfs or not event.output_df:
            return None

        input_rows = event.input_dfs[0].n_rows
        output_rows = event.output_df.n_rows
        removed_rows = input_rows - output_rows

        if removed_rows <= 0:
            return None

        pct = (removed_rows / input_rows * 100) if input_rows > 0 else 0

        content = f"🗑️ Removed<br/>{removed_rows:,} rows<br/>({pct:.1f}%)"
        node_id = f"{event.event_id}_removed"

        return f'    {node_id}[/"{content}"/]'

    def _render_node(self, event: FlowEvent, include_stats: bool = True) -> str:
        """
        Render a single event as a Mermaid node.

        Args:
            event: FlowEvent to render
            include_stats: Whether to include statistics

        Returns:
            Mermaid node definition string
        """
        # Build node content
        content_lines = []

        # Operation name (bold/header)
        content_lines.append(f"<b>{self._escape(event.operation_name)}</b>")

        # Description if present
        if event.description:
            desc = self._truncate(event.description, 50)
            content_lines.append(f"<i>{self._escape(desc)}</i>")

        # Input DataFrames info
        if event.input_dfs:
            for i, df_info in enumerate(event.input_dfs):
                name = df_info.name or df_info.source_file or f"df_{i + 1}"
                name = self._truncate(name, 25)
                content_lines.append(f"➡️ {self._escape(name)}: {df_info.n_rows:,}×{df_info.n_cols}")

        # Output DataFrame info
        if event.output_df:
            content_lines.append(
                f"⬅️ {event.output_df.n_rows:,} rows × {event.output_df.n_cols} cols"
            )

            # Row change indicator
            if event.input_dfs:
                input_rows = event.input_dfs[0].n_rows
                output_rows = event.output_df.n_rows
                if output_rows != input_rows:
                    diff = output_rows - input_rows
                    pct = abs(diff) / input_rows * 100 if input_rows > 0 else 0
                    if diff > 0:
                        content_lines.append(f"↑ +{diff:,} (+{pct:.1f}%)")
                    else:
                        content_lines.append(f"↓ {diff:,} (-{pct:.1f}%)")

        # Tracked statistics
        if include_stats and event.tracked_stats:
            content_lines.append("─" * 20)  # Separator
            for stat in event.tracked_stats:
                stat_lines = self._format_stats(stat)
                content_lines.extend(stat_lines)

        # Scatter plot - only in HTML mode (once per node, not per stat)
        if self._html_mode and self._hexbin_data:
            scatter_img = self._generate_inline_scatter()
            if scatter_img:
                content_lines.append(scatter_img)

        # Join content with line breaks
        content = "<br/>".join(content_lines)

        # Determine node shape based on operation type
        shape_start, shape_end = self._get_node_shape(event.operation_type)

        return f'    {event.event_id}{shape_start}"{content}"{shape_end}'

    def _format_stats(self, stat: TrackedVariableStats) -> list[str]:
        """Format statistics for display in a node."""
        lines = []

        # Variable name with unique count
        if stat.n_unique > 0:
            symbol = "🔑" if stat.mean_value is None else "⭐"

            lines.append(f"{symbol} {self._escape(stat.name)}: {stat.n_unique:,} unique")

        # Numeric statistics
        if stat.mean_value is not None:
            mean_str = f"mean={stat.mean_value:.2f}"
            if stat.min_value is not None and stat.max_value is not None:
                mean_str += f" [{stat.min_value:.1f}–{stat.max_value:.1f}]"
            lines.append(mean_str)

        # Histogram - use embedded image in HTML mode, ASCII sparkline otherwise
        if self._html_mode and stat.name in self._histogram_data:
            hist_img = self._generate_inline_histogram(stat.name)
            if hist_img:
                lines.append(hist_img)
            elif stat.histogram:
                lines.append(f"📊 {stat.histogram}")
        elif stat.histogram:
            lines.append(f"📊 {stat.histogram}")

        # Top values (truncated)
        if stat.top_values:
            top_items = []
            for val, _count, pct in stat.top_values[:2]:
                val_str = self._truncate(str(val), 10)
                top_items.append(f"{val_str}:{pct:.0f}%")
            if top_items:
                lines.append(f"top: {', '.join(top_items)}")

        return lines

    def _generate_inline_histogram(self, var_name: str) -> str | None:
        """Generate an inline histogram image tag for HTML mode."""
        if var_name not in self._histogram_data:
            return None

        try:
            from .html_histogram import generate_histogram_img_tag

            data = self._histogram_data[var_name]
            if data is None or (hasattr(data, "__len__") and len(data) == 0):
                return None

            return generate_histogram_img_tag(
                data,
                alt_text=f"{var_name} distribution",
                width_px=80,
                height_px=25,
            )
        except ImportError:
            return None

    def _generate_inline_scatter(self) -> str | None:
        """Generate an inline scatter plot image tag for HTML mode."""
        if not self._hexbin_data:
            return None

        try:
            from .html_histogram import generate_hexbin_img_tag

            # Get the first (and usually only) hexbin entry
            hexbin_name = next(iter(self._hexbin_data))
            x_data, y_data = self._hexbin_data[hexbin_name]

            if not x_data or not y_data or len(x_data) < 3:
                return None

            return generate_hexbin_img_tag(
                x_data,
                y_data,
                alt_text=hexbin_name.replace("_", " "),
                width_px=80,
                height_px=50,
            )
        except ImportError:
            return None

    def _get_node_shape(self, op_type: OperationType) -> tuple[str, str]:
        """
        Get Mermaid node shape delimiters based on operation type.

        Different shapes help visually distinguish operation types:
        - Rectangle: Default operations
        - Stadium: Filter/selection operations
        - Subroutine: Join operations (double border)
        - Parallelogram: I/O operations
        - Hexagon: GroupBy operations
        - Trapezoid: Reshape operations
        """
        # Loading operations - parallelogram (input)
        if op_type in [
            OperationType.READ_CSV,
            OperationType.READ_EXCEL,
            OperationType.READ_PARQUET,
            OperationType.READ_JSON,
            OperationType.READ_SQL,
        ]:
            return "[/", "/]"

        # Filter operations - stadium shape (except query which is diamond)
        if op_type in [
            OperationType.FILTER,
            OperationType.LOC,
            OperationType.ILOC,
        ]:
            return "([", "])"

        # Query operation - diamond shape
        if op_type == OperationType.QUERY:
            return "{", "}"

        # Join operations - subroutine (double border)
        if op_type in [OperationType.MERGE, OperationType.JOIN]:
            return "[[", "]]"

        # GroupBy operations - hexagon
        if op_type in [OperationType.GROUPBY, OperationType.AGGREGATE, OperationType.TRANSFORM]:
            return "{{", "}}"

        # Reshape operations - trapezoid
        if op_type in [
            OperationType.PIVOT,
            OperationType.PIVOT_TABLE,
            OperationType.MELT,
            OperationType.STACK,
            OperationType.UNSTACK,
        ]:
            return "[\\", "/]"

        # Concat operations - cylinder (database)
        if op_type in [OperationType.CONCAT, OperationType.APPEND]:
            return "[(", ")]"

        # Drop operations - asymmetric shape
        if op_type in [OperationType.DROP, OperationType.DROP_DUPLICATES, OperationType.DROPNA]:
            return ">", "]"

        # Default - rectangle
        return "[", "]"

    def _generate_connections(
        self,
        events: list[FlowEvent],
        df_source_map: dict[str, str],
        show_merge_inputs: bool,
        removed_nodes: list[str],
    ) -> list[str]:
        """
        Generate connection arrows between nodes.

        Args:
            events: List of FlowEvents
            df_source_map: Map from DataFrame names to event IDs
            show_merge_inputs: Whether to show both inputs for merge
            removed_nodes: List of event IDs that have removed data nodes

        Returns:
            List of Mermaid connection strings
        """
        connections = []

        for i, event in enumerate(events):
            if i == 0:
                continue

            prev_event = events[i - 1]

            # Determine arrow style based on operation
            arrow = self._get_arrow_style(event.operation_type)

            # For merge operations, try to connect both source DataFrames
            if show_merge_inputs and event.operation_type in [
                OperationType.MERGE,
                OperationType.JOIN,
            ]:
                merge_connections = self._get_merge_connections(event, events, i, df_source_map)
                if merge_connections:
                    connections.extend(merge_connections)
                else:
                    connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")
            else:
                connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")

            # Add connection to removed data node
            if event.event_id in removed_nodes:
                removed_node_id = f"{event.event_id}_removed"
                connections.append(f"    {event.event_id} -.-> {removed_node_id}")

        return connections

    def _get_merge_connections(
        self,
        event: FlowEvent,
        events: list[FlowEvent],
        current_index: int,
        df_source_map: dict[str, str],
    ) -> list[str]:
        """
        Get connections for merge operations from both input DataFrames.

        Returns list of connection strings, or empty list if can't determine sources.
        """
        connections = []
        arrow = self._get_arrow_style(event.operation_type)

        if len(event.input_dfs) >= 2:
            source_events = []

            for df_info in event.input_dfs:
                source_event_id = None

                # Try to find the source event by DataFrame name
                if df_info.name and df_info.name in df_source_map:
                    source_event_id = df_source_map[df_info.name]
                elif df_info.source_file and df_info.source_file in df_source_map:
                    source_event_id = df_source_map[df_info.source_file]

                if source_event_id:
                    source_events.append(source_event_id)

            # If we found at least 2 sources, connect them both
            if len(source_events) >= 2:
                # Remove duplicates while preserving order
                seen = set()
                unique_sources = []
                for s in source_events:
                    if s not in seen:
                        seen.add(s)
                        unique_sources.append(s)

                for source_id in unique_sources[:2]:  # Max 2 sources
                    connections.append(f"    {source_id} {arrow} {event.event_id}")
            elif len(source_events) == 1:
                # Found one source, also connect previous event
                connections.append(f"    {source_events[0]} {arrow} {event.event_id}")
                if current_index > 0:
                    prev_event = events[current_index - 1]
                    if prev_event.event_id != source_events[0]:
                        connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")

        return connections

    def _get_arrow_style(self, op_type: OperationType) -> str:
        """Get arrow style based on operation type."""
        # Thick arrow for joins
        if op_type in [OperationType.MERGE, OperationType.JOIN]:
            return "==>"

        # Dotted arrow for filter (some data may be lost)
        if op_type in [
            OperationType.FILTER,
            OperationType.LOC,
            OperationType.DROPNA,
            OperationType.DROP_DUPLICATES,
            OperationType.QUERY,
        ]:
            return "-.->"

        # Default arrow
        return "-->"

    def _generate_styles(
        self,
        events: list[FlowEvent],
        removed_nodes: list[str],
    ) -> list[str]:
        """
        Generate Mermaid style definitions for nodes.

        Args:
            events: List of FlowEvents
            removed_nodes: List of event IDs that have removed data nodes

        Returns:
            List of style definition strings
        """
        styles = []
        use_colors = self.theme.get("use_colors", True)

        for event in events:
            if use_colors:
                color = event.get_color()
                text_color = self._get_contrasting_color(color)
                stroke_color = self._darken_color(color)
            else:
                color = str(self.theme.get("node_fill", "#f5f5f5"))
                text_color = str(self.theme.get("text", "#333333"))
                stroke_color = str(self.theme.get("node_stroke", "#666666"))

            style = (
                f"    style {event.event_id} fill:{color},stroke:{stroke_color},color:{text_color}"
            )
            styles.append(style)

            # Style for removed data nodes
            if event.event_id in removed_nodes:
                removed_node_id = f"{event.event_id}_removed"
                styles.append(
                    f"    style {removed_node_id} "
                    f"fill:#ffcccc,stroke:#cc0000,color:#660000,stroke-dasharray: 5 5"
                )

        return styles

    def _generate_legend(self, events: list[FlowEvent]) -> list[str]:
        """
        Generate a legend subgraph showing operation types.

        Returns:
            List of Mermaid subgraph lines
        """
        # Get unique operation types used
        used_types = {event.operation_type for event in events}
        use_colors = self.theme.get("use_colors", True)

        # Group by category
        legend_items = []
        for category, op_types in OPERATION_CATEGORIES.items():
            category_ops = [op for op in op_types if op in used_types]
            if category_ops:
                for op in category_ops:
                    color = (
                        OPERATION_COLORS.get(op, "#495057")
                        if use_colors
                        else self.theme.get("node_fill", "#f5f5f5")
                    )
                    legend_items.append((category, op.value, color))

        if not legend_items:
            return []

        lines = [
            "    subgraph Legend",
            "        direction LR",
        ]

        for i, (_category, op_name, color) in enumerate(legend_items[:6]):  # Limit to 6
            node_id = f"legend_{i}"
            color_str = str(color)
            lines.append(f'        {node_id}["{op_name}"]')
            if use_colors:
                text_color = self._get_contrasting_color(color_str)
                lines.append(
                    f"        style {node_id} fill:{color_str},stroke:#333,color:{text_color}"
                )
            else:
                lines.append(f"        style {node_id} fill:{color_str},stroke:#666,color:#333")

        lines.append("    end")

        return lines

    def _escape(self, text: str) -> str:
        """Escape special characters for Mermaid."""
        if not text:
            return ""
        # Escape HTML entities and Mermaid special chars
        text = html.escape(text)
        text = text.replace('"', "'")
        text = text.replace("\n", " ")
        return text

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def _get_contrasting_color(self, hex_color: str) -> str:
        """Get black or white depending on background brightness."""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Calculate relative luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

            return "#ffffff" if luminance < 0.5 else "#000000"
        except (ValueError, IndexError):
            return "#000000"

    def _darken_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Darken a hex color by a factor."""
        hex_color = hex_color.lstrip("#")

        try:
            r = int(int(hex_color[0:2], 16) * factor)
            g = int(int(hex_color[2:4], 16) * factor)
            b = int(int(hex_color[4:6], 16) * factor)

            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color

    def wrap_markdown(self, mermaid_code: str, title: str = "") -> str:
        """
        Wrap Mermaid code in Markdown format.

        Args:
            mermaid_code: Raw Mermaid code
            title: Optional title

        Returns:
            Markdown string with code block
        """
        lines = []

        if title:
            lines.append(f"# {title}")
            lines.append("")

        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")

        return "\n".join(lines)

    def wrap_html(
        self,
        mermaid_code: str,
        title: str = "",
        histogram_data: dict[str, list] | None = None,
    ) -> str:
        """
        Wrap Mermaid code in a standalone HTML page.

        Note: Histograms are now embedded directly in the Mermaid node labels
        when using render() with html_mode=True. The histogram_data parameter
        is kept for backwards compatibility but the separate section is removed.

        Args:
            mermaid_code: Raw Mermaid code
            title: Page title
            histogram_data: Ignored (kept for compatibility)

        Returns:
            Complete HTML document string
        """
        theme_bg = self.theme["background"]
        theme_text = self.theme["text"]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title or "Data Flow Pipeline")}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: {theme_bg};
            color: {theme_text};
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 300;
            font-size: 2rem;
            letter-spacing: 0.05em;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
            background: {theme_bg};
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            font-size: 0.875rem;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{html.escape(title or "Data Flow Pipeline")}</h1>
        <div class="mermaid">
{mermaid_code}
        </div>
        <div class="footer">
            Generated by pandas_flow
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{"dark" if self.theme_name == "dark" else "default"}',
            maxTextSize: 500000,
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>
"""


def render_events_to_mermaid(
    events: list[FlowEvent],
    **kwargs,
) -> str:
    """
    Convenience function to render events to Mermaid code.

    Args:
        events: List of FlowEvents
        **kwargs: Arguments passed to MermaidRenderer.render()

    Returns:
        Mermaid code string
    """
    renderer = MermaidRenderer()
    return renderer.render(events, **kwargs)
