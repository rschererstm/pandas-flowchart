"""
Mermaid diagram renderer for pandas_flow.

Generates Mermaid flowchart syntax from FlowEvent sequences,
with styled boxes, statistics, and visual indicators.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import html

from .events import (
    FlowEvent, 
    OperationType, 
    OPERATION_COLORS, 
    OPERATION_CATEGORIES,
    TrackedVariableStats,
)
from .stats import StatsCalculator

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
    },
    "dark": {
        "background": "#1a1a2e",
        "text": "#eaeaea",
        "border": "#4a4a6a",
        "arrow": "#8a8aaa",
        "title_bg": "#16213e",
    },
    "light": {
        "background": "#fafafa",
        "text": "#2d2d2d",
        "border": "#e0e0e0",
        "arrow": "#888888",
        "title_bg": "#f5f5f5",
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
    """
    
    def __init__(self, theme: str = "default"):
        """
        Initialize the renderer.
        
        Args:
            theme: Color theme ("default", "dark", "light")
        """
        self.theme = THEMES.get(theme, THEMES["default"])
        self.theme_name = theme
    
    def render(
        self,
        events: list[FlowEvent],
        title: str = "Data Flow Pipeline",
        direction: str = "TB",
        include_legend: bool = True,
        include_stats: bool = True,
    ) -> str:
        """
        Render events as Mermaid flowchart code.
        
        Args:
            events: List of FlowEvents to render
            title: Diagram title
            direction: Flow direction (TB, LR, BT, RL)
            include_legend: Whether to include operation type legend
            include_stats: Whether to include statistics in boxes
            
        Returns:
            Mermaid flowchart code string
        """
        if not events:
            return self._empty_diagram(title, direction)
        
        lines = [
            f"flowchart {direction}",
            "",
        ]
        
        # Generate node definitions
        lines.append("    %% Node definitions")
        for event in events:
            node_def = self._render_node(event, include_stats)
            lines.append(node_def)
        
        lines.append("")
        
        # Generate connections
        lines.append("    %% Connections")
        connections = self._generate_connections(events)
        lines.extend(connections)
        
        lines.append("")
        
        # Generate styles
        lines.append("    %% Styles")
        styles = self._generate_styles(events)
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
                name = df_info.name or df_info.source_file or f"df_{i+1}"
                name = self._truncate(name, 25)
                content_lines.append(f"📥 {self._escape(name)}: {df_info.n_rows:,}×{df_info.n_cols}")
        
        # Output DataFrame info
        if event.output_df:
            content_lines.append(f"📤 {event.output_df.n_rows:,} rows × {event.output_df.n_cols} cols")
            
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
            lines.append(f"🔑 {self._escape(stat.name)}: {stat.n_unique:,} unique")
        
        # Numeric statistics
        if stat.mean_value is not None:
            mean_str = f"μ={stat.mean_value:.2f}"
            if stat.min_value is not None and stat.max_value is not None:
                mean_str += f" [{stat.min_value:.1f}–{stat.max_value:.1f}]"
            lines.append(mean_str)
        
        # Histogram/sparkline
        if stat.histogram:
            lines.append(f"📊 {stat.histogram}")
        
        # Top values (truncated)
        if stat.top_values:
            top_items = []
            for val, count, pct in stat.top_values[:2]:
                val_str = self._truncate(str(val), 10)
                top_items.append(f"{val_str}:{pct:.0f}%")
            if top_items:
                lines.append(f"top: {', '.join(top_items)}")
        
        return lines
    
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
        if op_type in [OperationType.READ_CSV, OperationType.READ_EXCEL, 
                       OperationType.READ_PARQUET, OperationType.READ_JSON,
                       OperationType.READ_SQL]:
            return "[/", "/]"
        
        # Filter operations - stadium shape
        if op_type in [OperationType.FILTER, OperationType.LOC, 
                       OperationType.ILOC, OperationType.QUERY]:
            return "([", "])"
        
        # Join operations - subroutine (double border)
        if op_type in [OperationType.MERGE, OperationType.JOIN]:
            return "[[", "]]"
        
        # GroupBy operations - hexagon
        if op_type in [OperationType.GROUPBY, OperationType.AGGREGATE,
                       OperationType.TRANSFORM]:
            return "{{", "}}"
        
        # Reshape operations - trapezoid
        if op_type in [OperationType.PIVOT, OperationType.PIVOT_TABLE,
                       OperationType.MELT, OperationType.STACK, 
                       OperationType.UNSTACK]:
            return "[\\", "/]"
        
        # Concat operations - cylinder (database)
        if op_type in [OperationType.CONCAT, OperationType.APPEND]:
            return "[(", ")]"
        
        # Drop operations - asymmetric shape
        if op_type in [OperationType.DROP, OperationType.DROP_DUPLICATES,
                       OperationType.DROPNA]:
            return ">", "]"
        
        # Default - rectangle
        return "[", "]"
    
    def _generate_connections(self, events: list[FlowEvent]) -> list[str]:
        """
        Generate connection arrows between nodes.
        
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
            
            # For merge operations, we might have multiple inputs
            if event.operation_type in [OperationType.MERGE, OperationType.JOIN]:
                if len(event.input_dfs) > 1 and i >= 2:
                    # Connect previous two events if available
                    connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")
                    # Add a note about the merge
                else:
                    connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")
            else:
                connections.append(f"    {prev_event.event_id} {arrow} {event.event_id}")
        
        return connections
    
    def _get_arrow_style(self, op_type: OperationType) -> str:
        """Get arrow style based on operation type."""
        # Thick arrow for joins
        if op_type in [OperationType.MERGE, OperationType.JOIN]:
            return "==>"
        
        # Dotted arrow for filter (some data may be lost)
        if op_type in [OperationType.FILTER, OperationType.LOC, 
                       OperationType.DROPNA, OperationType.DROP_DUPLICATES]:
            return "-.->"
        
        # Default arrow
        return "-->"
    
    def _generate_styles(self, events: list[FlowEvent]) -> list[str]:
        """
        Generate Mermaid style definitions for nodes.
        
        Returns:
            List of style definition strings
        """
        styles = []
        
        for event in events:
            color = event.get_color()
            # Calculate contrasting text color
            text_color = self._get_contrasting_color(color)
            
            style = (
                f"    style {event.event_id} "
                f"fill:{color},stroke:{self._darken_color(color)},color:{text_color}"
            )
            styles.append(style)
        
        return styles
    
    def _generate_legend(self, events: list[FlowEvent]) -> list[str]:
        """
        Generate a legend subgraph showing operation types.
        
        Returns:
            List of Mermaid subgraph lines
        """
        # Get unique operation types used
        used_types = set(event.operation_type for event in events)
        
        # Group by category
        legend_items = []
        for category, op_types in OPERATION_CATEGORIES.items():
            category_ops = [op for op in op_types if op in used_types]
            if category_ops:
                for op in category_ops:
                    color = OPERATION_COLORS.get(op, "#495057")
                    legend_items.append((category, op.value, color))
        
        if not legend_items:
            return []
        
        lines = [
            "    subgraph Legend",
            "        direction LR",
        ]
        
        for i, (category, op_name, color) in enumerate(legend_items[:6]):  # Limit to 6
            node_id = f"legend_{i}"
            lines.append(f'        {node_id}["{op_name}"]')
            text_color = self._get_contrasting_color(color)
            lines.append(f"        style {node_id} fill:{color},stroke:#333,color:{text_color}")
        
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
        return text[:max_len - 3] + "..."
    
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
    
    def wrap_html(self, mermaid_code: str, title: str = "") -> str:
        """
        Wrap Mermaid code in a standalone HTML page.
        
        Args:
            mermaid_code: Raw Mermaid code
            title: Page title
            
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
    <title>{html.escape(title or 'Data Flow Pipeline')}</title>
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
        <h1>{html.escape(title or 'Data Flow Pipeline')}</h1>
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

