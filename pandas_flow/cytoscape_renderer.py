"""
Cytoscape.js renderer for pandas_flow.

Generates modern, interactive HTML visualizations using Cytoscape.js
with Dagre layout, featuring a sliding side panel for node details.
"""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING, Any

from .events import (
    OPERATION_COLORS,
    FlowEvent,
    OperationType,
    TrackedVariableStats,
)

if TYPE_CHECKING:
    import pandas as pd


# Shape mapping for Cytoscape.js
# Maps operation types to Cytoscape shape names
OPERATION_SHAPES = {
    # Data I/O - barrel/cylinder shape
    OperationType.READ_CSV: "barrel",
    OperationType.READ_EXCEL: "barrel",
    OperationType.READ_PARQUET: "barrel",
    OperationType.READ_JSON: "barrel",
    OperationType.READ_SQL: "barrel",
    # Filter operations - cut-rectangle (decision-like)
    OperationType.FILTER: "cut-rectangle",
    OperationType.LOC: "cut-rectangle",
    OperationType.ILOC: "cut-rectangle",
    OperationType.QUERY: "diamond",
    # Join operations - hexagon
    OperationType.MERGE: "hexagon",
    OperationType.JOIN: "hexagon",
    # Column operations - round-rectangle
    OperationType.ASSIGN: "round-rectangle",
    OperationType.RENAME: "round-rectangle",
    # Drop operations - tag shape
    OperationType.DROP: "tag",
    OperationType.DROP_DUPLICATES: "tag",
    OperationType.DROPNA: "tag",
    # GroupBy operations - rhomboid
    OperationType.GROUPBY: "rhomboid",
    OperationType.AGGREGATE: "rhomboid",
    OperationType.TRANSFORM: "rhomboid",
    # Concat operations - vee
    OperationType.CONCAT: "vee",
    OperationType.APPEND: "vee",
    # Reshape operations - star
    OperationType.PIVOT: "star",
    OperationType.PIVOT_TABLE: "star",
    OperationType.MELT: "star",
    OperationType.STACK: "star",
    OperationType.UNSTACK: "star",
    # Sorting - round-rectangle
    OperationType.SORT_VALUES: "round-rectangle",
    OperationType.SORT_INDEX: "round-rectangle",
    # Fill - ellipse
    OperationType.FILLNA: "ellipse",
    # Type conversion - round-rectangle
    OperationType.ASTYPE: "round-rectangle",
    # Custom - rectangle
    OperationType.CUSTOM: "round-rectangle",
}

# Node type categories for CSS styling
OPERATION_CATEGORIES_MAP = {
    "io": [
        OperationType.READ_CSV,
        OperationType.READ_EXCEL,
        OperationType.READ_PARQUET,
        OperationType.READ_JSON,
        OperationType.READ_SQL,
    ],
    "filter": [
        OperationType.FILTER,
        OperationType.LOC,
        OperationType.ILOC,
        OperationType.QUERY,
    ],
    "merge": [OperationType.MERGE, OperationType.JOIN],
    "column": [OperationType.ASSIGN, OperationType.RENAME],
    "drop": [OperationType.DROP, OperationType.DROP_DUPLICATES, OperationType.DROPNA],
    "groupby": [OperationType.GROUPBY, OperationType.AGGREGATE, OperationType.TRANSFORM],
    "concat": [OperationType.CONCAT, OperationType.APPEND],
    "reshape": [
        OperationType.PIVOT,
        OperationType.PIVOT_TABLE,
        OperationType.MELT,
        OperationType.STACK,
        OperationType.UNSTACK,
    ],
    "sort": [OperationType.SORT_VALUES, OperationType.SORT_INDEX],
    "fill": [OperationType.FILLNA, OperationType.ASTYPE],
    "custom": [OperationType.CUSTOM],
}


def _get_category(op_type: OperationType) -> str:
    """Get the category name for an operation type."""
    for category, types in OPERATION_CATEGORIES_MAP.items():
        if op_type in types:
            return category
    return "custom"


class CytoscapeRenderer:
    """
    Renders FlowEvents as interactive Cytoscape.js diagrams.

    Features:
    - Modern, clean visual design with soft shadows
    - Variable node shapes based on operation type
    - Sliding side panel for detailed node information
    - Native drag, pan, and zoom support
    - Responsive layout with Dagre algorithm
    """

    def __init__(self, theme: str = "default"):
        """
        Initialize the renderer.

        Args:
            theme: Color theme ("default", "dark")
        """
        self.theme = theme
        self._histogram_data: dict[str, Any] = {}
        self._hexbin_data: dict[str, tuple[list, list]] = {}

    def render(
        self,
        events: list[FlowEvent],
        title: str = "Data Flow Pipeline",
        direction: str = "TB",
        include_stats: bool = True,
        show_removed_data: bool = True,
        show_merge_inputs: bool = True,
        histogram_data: dict[str, Any] | None = None,
        hexbin_data: dict[str, tuple[list, list]] | None = None,
    ) -> str:
        """
        Render events as a standalone HTML page with Cytoscape.js.

        Args:
            events: List of FlowEvents to render
            title: Diagram title
            direction: Flow direction (TB, LR, BT, RL)
            include_stats: Whether to include statistics in nodes
            show_removed_data: Show nodes for removed data
            show_merge_inputs: Show both inputs for merge operations
            histogram_data: Dict of variable_name -> data for histograms
            hexbin_data: Dict of name -> (x_data, y_data) for scatter plots

        Returns:
            Complete HTML document string
        """
        self._histogram_data = histogram_data or {}
        self._hexbin_data = hexbin_data or {}

        # Build graph data
        nodes, edges = self._build_graph_data(
            events, include_stats, show_removed_data, show_merge_inputs
        )

        # Convert to JSON for embedding
        graph_data = {"nodes": nodes, "edges": edges}
        graph_json = json.dumps(graph_data, indent=2, default=str)

        # Map direction to Dagre rankDir
        rank_dir_map = {"TB": "TB", "LR": "LR", "BT": "BT", "RL": "RL"}
        rank_dir = rank_dir_map.get(direction, "TB")

        return self._generate_html(title, graph_json, rank_dir)

    def _build_graph_data(
        self,
        events: list[FlowEvent],
        include_stats: bool,
        show_removed_data: bool,
        show_merge_inputs: bool,
    ) -> tuple[list[dict], list[dict]]:
        """Build Cytoscape nodes and edges from events."""
        nodes = []
        edges = []
        df_source_map = self._build_df_source_map(events)

        for i, event in enumerate(events):
            # Create main node
            node = self._create_node(event, include_stats)
            nodes.append(node)

            # Create removed data node if applicable
            if show_removed_data and self._is_data_removal_operation(event):
                removed_node = self._create_removed_node(event)
                if removed_node:
                    nodes.append(removed_node)
                    edges.append(
                        {
                            "data": {
                                "id": f"{event.event_id}_to_removed",
                                "source": event.event_id,
                                "target": f"{event.event_id}_removed",
                                "type": "removed",
                            }
                        }
                    )

            # Create edges
            if i > 0:
                event_edges = self._create_edges(
                    event, events, i, df_source_map, show_merge_inputs
                )
                edges.extend(event_edges)

        return nodes, edges

    def _create_node(self, event: FlowEvent, include_stats: bool) -> dict:
        """Create a Cytoscape node from a FlowEvent."""
        op_type = event.operation_type
        category = _get_category(op_type)
        shape = OPERATION_SHAPES.get(op_type, "round-rectangle")
        color = OPERATION_COLORS.get(op_type, "#6b7280")

        # Build label (short version for the graph)
        label = event.operation_name
        if event.output_df:
            label += f"\n{event.output_df.n_rows:,} × {event.output_df.n_cols}"

        # Build detailed data for side panel
        details = self._build_node_details(event, include_stats)

        return {
            "data": {
                "id": event.event_id,
                "label": label,
                "type": category,
                "shape": shape,
                "color": color,
                "operationType": op_type.value,
                "operationName": event.operation_name,
                "description": event.description,
                "details": details,
            }
        }

    def _build_node_details(self, event: FlowEvent, include_stats: bool) -> dict:
        """Build detailed information for the side panel."""
        details: dict[str, Any] = {
            "operation": event.operation_name,
            "type": event.operation_type.value,
            "description": event.description,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

        # Input DataFrames info
        if event.input_dfs:
            details["inputs"] = []
            for df_info in event.input_dfs:
                name = df_info.name or df_info.source_file or "DataFrame"
                details["inputs"].append(
                    {
                        "name": name,
                        "rows": df_info.n_rows,
                        "cols": df_info.n_cols,
                        "columns": df_info.columns[:20],  # Limit columns shown
                    }
                )

        # Output DataFrame info
        if event.output_df:
            details["output"] = {
                "rows": event.output_df.n_rows,
                "cols": event.output_df.n_cols,
                "columns": event.output_df.columns[:20],
            }

            # Row change
            if event.input_dfs:
                input_rows = event.input_dfs[0].n_rows
                output_rows = event.output_df.n_rows
                diff = output_rows - input_rows
                if input_rows > 0:
                    pct = abs(diff) / input_rows * 100
                    details["rowChange"] = {
                        "diff": diff,
                        "percentage": round(pct, 1),
                        "direction": "increase" if diff > 0 else "decrease" if diff < 0 else "unchanged",
                    }

        # Arguments
        if event.arguments:
            details["arguments"] = event.arguments

        # Statistics
        if include_stats and event.tracked_stats:
            details["stats"] = []
            for stat in event.tracked_stats:
                stat_data = self._format_stat_for_details(stat)
                details["stats"].append(stat_data)

        # Histogram data
        if self._histogram_data:
            details["histogramData"] = {}
            for var_name, data in self._histogram_data.items():
                if data is not None and len(data) > 0:
                    # Sample data for histogram (limit to 1000 points)
                    sampled = data[:1000] if len(data) > 1000 else data
                    details["histogramData"][var_name] = sampled

        # Scatter data
        if self._hexbin_data:
            details["scatterData"] = {}
            for name, (x_data, y_data) in self._hexbin_data.items():
                if x_data and y_data and len(x_data) >= 3:
                    # Sample data (limit to 500 points)
                    sample_size = min(500, len(x_data))
                    step = max(1, len(x_data) // sample_size)
                    details["scatterData"][name] = {
                        "x": x_data[::step][:sample_size],
                        "y": y_data[::step][:sample_size],
                    }

        return details

    def _format_stat_for_details(self, stat: TrackedVariableStats) -> dict:
        """Format statistics for the side panel."""
        stat_data: dict[str, Any] = {
            "name": stat.name,
            "total": stat.n_total,
            "nonNull": stat.n_non_null,
            "unique": stat.n_unique,
        }

        if stat.min_value is not None:
            stat_data["min"] = stat.min_value
        if stat.max_value is not None:
            stat_data["max"] = stat.max_value
        if stat.mean_value is not None:
            stat_data["mean"] = round(stat.mean_value, 2)
        if stat.std_value is not None:
            stat_data["std"] = round(stat.std_value, 2)

        if stat.top_values:
            stat_data["topValues"] = [
                {"value": str(val), "count": count, "percentage": round(pct, 1)}
                for val, count, pct in stat.top_values[:5]
            ]

        # Note: ASCII histogram removed - using Chart.js instead

        return stat_data

    def _create_removed_node(self, event: FlowEvent) -> dict | None:
        """Create a node representing removed data."""
        if not event.input_dfs or not event.output_df:
            return None

        input_rows = event.input_dfs[0].n_rows
        output_rows = event.output_df.n_rows
        removed_rows = input_rows - output_rows

        if removed_rows <= 0:
            return None

        pct = (removed_rows / input_rows * 100) if input_rows > 0 else 0

        return {
            "data": {
                "id": f"{event.event_id}_removed",
                "label": f"Removed\n{removed_rows:,} rows\n({pct:.1f}%)",
                "type": "removed",
                "shape": "round-rectangle",
                "color": "#ef4444",
                "details": {
                    "operation": "Data Removed",
                    "rows": removed_rows,
                    "percentage": round(pct, 1),
                    "source": event.operation_name,
                },
            }
        }

    def _create_edges(
        self,
        event: FlowEvent,
        events: list[FlowEvent],
        current_index: int,
        df_source_map: dict[str, str],
        show_merge_inputs: bool,
    ) -> list[dict]:
        """Create edges connecting to this event."""
        edges = []
        prev_event = events[current_index - 1]
        edge_type = self._get_edge_type(event.operation_type)

        # Handle merge operations
        if show_merge_inputs and event.operation_type in [
            OperationType.MERGE,
            OperationType.JOIN,
        ]:
            merge_sources = self._get_merge_sources(event, events, current_index, df_source_map)
            if len(merge_sources) >= 2:
                for source_id in merge_sources[:2]:
                    edges.append(
                        {
                            "data": {
                                "id": f"{source_id}_to_{event.event_id}",
                                "source": source_id,
                                "target": event.event_id,
                                "type": "merge",
                            }
                        }
                    )
                return edges

        # Default connection to previous event
        edges.append(
            {
                "data": {
                    "id": f"{prev_event.event_id}_to_{event.event_id}",
                    "source": prev_event.event_id,
                    "target": event.event_id,
                    "type": edge_type,
                }
            }
        )

        return edges

    def _get_merge_sources(
        self,
        event: FlowEvent,
        events: list[FlowEvent],
        current_index: int,
        df_source_map: dict[str, str],
    ) -> list[str]:
        """Get source event IDs for merge operations."""
        sources = []

        if len(event.input_dfs) >= 2:
            for df_info in event.input_dfs:
                source_id = None
                if df_info.name and df_info.name in df_source_map:
                    source_id = df_source_map[df_info.name]
                elif df_info.source_file and df_info.source_file in df_source_map:
                    source_id = df_source_map[df_info.source_file]
                if source_id:
                    sources.append(source_id)

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for s in sources:
            if s not in seen:
                seen.add(s)
                unique.append(s)

        return unique

    def _get_edge_type(self, op_type: OperationType) -> str:
        """Get edge type based on operation."""
        if op_type in [OperationType.MERGE, OperationType.JOIN]:
            return "merge"
        if op_type in [
            OperationType.FILTER,
            OperationType.LOC,
            OperationType.ILOC,
            OperationType.QUERY,
            OperationType.DROPNA,
            OperationType.DROP_DUPLICATES,
        ]:
            return "filter"
        return "default"

    def _build_df_source_map(self, events: list[FlowEvent]) -> dict[str, str]:
        """Build a map from DataFrame names to event IDs."""
        df_map = {}
        for event in events:
            if event.output_df:
                if event.output_df.name:
                    df_map[event.output_df.name] = event.event_id
                if event.output_df.source_file:
                    df_map[event.output_df.source_file] = event.event_id
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
            return event.input_dfs[0].n_rows > event.output_df.n_rows
        return False

    def _generate_html(self, title: str, graph_json: str, rank_dir: str) -> str:
        """Generate the complete HTML document."""
        escaped_title = html.escape(title)
        is_dark = self.theme == "dark"

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title}</title>
    
    <!-- TailwindCSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Cytoscape.js -->
    <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
    
    <!-- Dagre layout -->
    <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
    <script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
    
    <!-- Chart.js for histograms -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                    }},
                    colors: {{
                        surface: {{
                            50: '#fafafa',
                            100: '#f4f4f5',
                            200: '#e4e4e7',
                            800: '#27272a',
                            900: '#18181b',
                            950: '#09090b',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', system-ui, sans-serif;
            overflow: hidden;
        }}
        
        #cy {{
            width: 100%;
            height: 100vh;
        }}
        
        .mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
        
        /* Custom scrollbar */
        .custom-scrollbar::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .custom-scrollbar::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        .custom-scrollbar::-webkit-scrollbar-thumb {{
            background: #d1d5db;
            border-radius: 3px;
        }}
        
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {{
            background: #4b5563;
        }}
        
        /* Slide panel animation */
        .slide-panel {{
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .slide-panel.open {{
            transform: translateX(0);
        }}
        
        /* Stat card hover effect */
        .stat-card {{
            transition: all 0.2s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .dark .stat-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
    </style>
</head>
<body class="{"dark bg-surface-950" if is_dark else "bg-surface-50"}">
    <!-- Main Container -->
    <div class="flex h-screen">
        <!-- Graph Container -->
        <div class="flex-1 relative">
            <!-- Header -->
            <div class="absolute top-0 left-0 right-0 z-10 p-4 {"bg-gradient-to-b from-surface-950/90 to-transparent" if is_dark else "bg-gradient-to-b from-white/90 to-transparent"}">
                <div class="flex items-center justify-between">
                    <div>
                        <h1 class="text-2xl font-semibold {"text-white" if is_dark else "text-gray-900"}">{escaped_title}</h1>
                        <p class="text-sm {"text-gray-400" if is_dark else "text-gray-500"} mt-1">Click a node to view details</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <button id="fit-btn" class="px-3 py-1.5 text-sm font-medium {"bg-surface-800 text-white hover:bg-surface-700" if is_dark else "bg-white text-gray-700 hover:bg-gray-50"} rounded-lg shadow-sm border {"border-surface-700" if is_dark else "border-gray-200"} transition-colors">
                            Fit View
                        </button>
                        <button id="theme-toggle" class="p-2 {"bg-surface-800 text-white hover:bg-surface-700" if is_dark else "bg-white text-gray-700 hover:bg-gray-50"} rounded-lg shadow-sm border {"border-surface-700" if is_dark else "border-gray-200"} transition-colors">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Cytoscape Container -->
            <div id="cy" class="{"bg-surface-950" if is_dark else "bg-surface-50"}"></div>
            
            <!-- Legend -->
            <div class="absolute bottom-4 left-4 {"bg-surface-900/90 border-surface-700" if is_dark else "bg-white/90 border-gray-200"} backdrop-blur-sm rounded-xl border p-4 shadow-lg">
                <h3 class="text-xs font-semibold {"text-gray-400" if is_dark else "text-gray-500"} uppercase tracking-wider mb-3">Node Types</h3>
                <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-gray-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">Data I/O</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-sky-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">Filter</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-emerald-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">Merge/Join</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-amber-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">Column Ops</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-rose-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">Drop</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-sm bg-violet-400"></span>
                        <span class="{"text-gray-300" if is_dark else "text-gray-600"}">GroupBy</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Side Panel -->
        <div id="side-panel" class="slide-panel fixed right-0 top-0 bottom-0 w-96 {"bg-surface-900 border-surface-700" if is_dark else "bg-white border-gray-200"} border-l shadow-2xl z-20 flex flex-col">
            <!-- Panel Header -->
            <div class="flex items-center justify-between p-4 border-b {"border-surface-700" if is_dark else "border-gray-200"}">
                <h2 id="panel-title" class="font-semibold {"text-white" if is_dark else "text-gray-900"} truncate">Node Details</h2>
                <button id="close-panel" class="p-1 {"text-gray-400 hover:text-white hover:bg-surface-800" if is_dark else "text-gray-500 hover:text-gray-700 hover:bg-gray-100"} rounded-lg transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <!-- Panel Content -->
            <div id="panel-content" class="flex-1 overflow-y-auto custom-scrollbar p-4">
                <!-- Content injected by JavaScript -->
            </div>
        </div>
    </div>
    
    <script>
        // Graph data
        const graphData = {graph_json};
        
        // Theme state
        let isDark = {"true" if is_dark else "false"};
        
        // Initialize Cytoscape
        cytoscape.use(cytoscapeDagre);
        
        const cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: graphData,
            style: getCytoscapeStyles(isDark),
            layout: {{
                name: 'dagre',
                rankDir: '{rank_dir}',
                nodeSep: 60,
                rankSep: 80,
                edgeSep: 30,
                ranker: 'tight-tree',
                align: 'UL',
                acyclicer: 'greedy',
                animate: true,
                animationDuration: 400,
                animationEasing: 'ease-out',
                fit: true,
                padding: 50,
            }},
            minZoom: 0.2,
            maxZoom: 3,
            wheelSensitivity: 0.3,
            boxSelectionEnabled: false,
        }});
        
        // Cytoscape styles function
        function getCytoscapeStyles(dark) {{
            const bgColor = dark ? '#09090b' : '#fafafa';
            const textColor = dark ? '#ffffff' : '#1f2937';
            const edgeColor = dark ? '#4b5563' : '#9ca3af';
            
            return [
                // Node base styles
                {{
                    selector: 'node',
                    style: {{
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-family': 'Inter, system-ui, sans-serif',
                        'font-size': '12px',
                        'font-weight': '500',
                        'color': '#ffffff',
                        'text-wrap': 'wrap',
                        'text-max-width': '120px',
                        'width': '140px',
                        'height': '70px',
                        'background-color': 'data(color)',
                        'border-width': '2px',
                        'border-color': 'data(color)',
                        'border-opacity': 0.8,
                        'shadow-blur': '12px',
                        'shadow-color': 'data(color)',
                        'shadow-opacity': 0.3,
                        'shadow-offset-x': '0px',
                        'shadow-offset-y': '4px',
                        'text-outline-width': '2px',
                        'text-outline-color': 'data(color)',
                    }}
                }},
                
                // Shape-specific styles
                {{
                    selector: 'node[shape="barrel"]',
                    style: {{
                        'shape': 'barrel',
                        'width': '130px',
                        'height': '80px',
                    }}
                }},
                {{
                    selector: 'node[shape="diamond"]',
                    style: {{
                        'shape': 'diamond',
                        'width': '130px',
                        'height': '90px',
                    }}
                }},
                {{
                    selector: 'node[shape="hexagon"]',
                    style: {{
                        'shape': 'hexagon',
                        'width': '150px',
                        'height': '85px',
                    }}
                }},
                {{
                    selector: 'node[shape="cut-rectangle"]',
                    style: {{
                        'shape': 'cut-rectangle',
                        'corner-radius': '8px',
                    }}
                }},
                {{
                    selector: 'node[shape="round-rectangle"]',
                    style: {{
                        'shape': 'round-rectangle',
                        'corner-radius': '12px',
                    }}
                }},
                {{
                    selector: 'node[shape="rhomboid"]',
                    style: {{
                        'shape': 'rhomboid',
                        'width': '150px',
                    }}
                }},
                {{
                    selector: 'node[shape="tag"]',
                    style: {{
                        'shape': 'tag',
                        'width': '140px',
                    }}
                }},
                {{
                    selector: 'node[shape="vee"]',
                    style: {{
                        'shape': 'vee',
                        'width': '130px',
                        'height': '80px',
                    }}
                }},
                {{
                    selector: 'node[shape="star"]',
                    style: {{
                        'shape': 'star',
                        'width': '100px',
                        'height': '100px',
                    }}
                }},
                {{
                    selector: 'node[shape="ellipse"]',
                    style: {{
                        'shape': 'ellipse',
                    }}
                }},
                
                // Removed node style
                {{
                    selector: 'node[type="removed"]',
                    style: {{
                        'background-color': '#fecaca',
                        'border-color': '#ef4444',
                        'border-style': 'dashed',
                        'border-width': '2px',
                        'color': '#991b1b',
                        'text-outline-color': '#fecaca',
                        'shadow-color': '#ef4444',
                        'shadow-opacity': 0.2,
                        'font-size': '11px',
                        'width': '100px',
                        'height': '60px',
                    }}
                }},
                
                // Hover state
                {{
                    selector: 'node:active',
                    style: {{
                        'overlay-opacity': 0.1,
                        'overlay-color': '#ffffff',
                    }}
                }},
                
                // Selected state
                {{
                    selector: 'node:selected',
                    style: {{
                        'border-width': '3px',
                        'border-color': '#3b82f6',
                        'shadow-color': '#3b82f6',
                        'shadow-opacity': 0.5,
                        'shadow-blur': '20px',
                    }}
                }},
                
                // Edge styles
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': edgeColor,
                        'target-arrow-color': edgeColor,
                        'target-arrow-shape': 'triangle-backcurve',
                        'curve-style': 'taxi',
                        'taxi-direction': 'downward',
                        'taxi-turn': '50%',
                        'arrow-scale': 1.0,
                        'source-endpoint': 'outside-to-node',
                        'target-endpoint': 'outside-to-node',
                    }}
                }},
                
                // Merge edge style
                {{
                    selector: 'edge[type="merge"]',
                    style: {{
                        'width': 2.5,
                        'line-color': '#10b981',
                        'target-arrow-color': '#10b981',
                    }}
                }},
                
                // Filter edge style
                {{
                    selector: 'edge[type="filter"]',
                    style: {{
                        'line-style': 'dashed',
                        'line-dash-pattern': [6, 3],
                        'line-color': '#60a5fa',
                        'target-arrow-color': '#60a5fa',
                    }}
                }},
                
                // Removed data edge
                {{
                    selector: 'edge[type="removed"]',
                    style: {{
                        'line-style': 'dotted',
                        'line-dash-pattern': [2, 4],
                        'line-color': '#f87171',
                        'target-arrow-color': '#f87171',
                        'target-arrow-shape': 'none',
                        'opacity': 0.6,
                    }}
                }},
            ];
        }}
        
        // Panel management
        const panel = document.getElementById('side-panel');
        const panelTitle = document.getElementById('panel-title');
        const panelContent = document.getElementById('panel-content');
        const closeBtn = document.getElementById('close-panel');
        const fitBtn = document.getElementById('fit-btn');
        const themeToggle = document.getElementById('theme-toggle');
        
        // Node click handler
        cy.on('tap', 'node', function(evt) {{
            const node = evt.target;
            const data = node.data();
            
            if (data.type === 'removed') {{
                showRemovedPanel(data);
            }} else {{
                showNodePanel(data);
            }}
            
            panel.classList.add('open');
            cy.nodes().unselect();
            node.select();
        }});
        
        // Close panel handlers
        closeBtn.addEventListener('click', () => {{
            panel.classList.remove('open');
            cy.nodes().unselect();
        }});
        
        cy.on('tap', function(evt) {{
            if (evt.target === cy) {{
                panel.classList.remove('open');
                cy.nodes().unselect();
            }}
        }});
        
        // Fit button
        fitBtn.addEventListener('click', () => {{
            cy.fit(null, 60);
        }});
        
        // Theme toggle
        themeToggle.addEventListener('click', () => {{
            isDark = !isDark;
            document.body.classList.toggle('dark');
            document.body.classList.toggle('bg-surface-950');
            document.body.classList.toggle('bg-surface-50');
            cy.style(getCytoscapeStyles(isDark));
            
            // Update UI elements would go here (simplified for this example)
            location.reload();
        }});
        
        // Show node details panel
        function showNodePanel(data) {{
            const details = data.details || {{}};
            panelTitle.textContent = data.operationName || 'Node Details';
            
            let html = '';
            
            // Operation badge
            html += `
                <div class="mb-6">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium" 
                          style="background-color: ${{data.color}}20; color: ${{data.color}}; border: 1px solid ${{data.color}}40;">
                        ${{data.operationType || 'operation'}}
                    </span>
                </div>
            `;
            
            // Description
            if (details.description) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-2">Description</h3>
                        <p class="${{isDark ? 'text-gray-200' : 'text-gray-700'}}">${{escapeHtml(details.description)}}</p>
                    </div>
                `;
            }}
            
            // Row change card
            if (details.rowChange) {{
                const rc = details.rowChange;
                const isIncrease = rc.direction === 'increase';
                const isDecrease = rc.direction === 'decrease';
                const color = isIncrease ? 'emerald' : isDecrease ? 'rose' : 'gray';
                const icon = isIncrease ? '↑' : isDecrease ? '↓' : '→';
                
                html += `
                    <div class="stat-card mb-4 p-4 rounded-xl ${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                        <div class="flex items-center justify-between">
                            <span class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-sm">Row Change</span>
                            <span class="text-${{color}}-500 font-mono font-semibold">
                                ${{icon}} ${{rc.diff > 0 ? '+' : ''}}${{rc.diff.toLocaleString()}} (${{rc.percentage}}%)
                            </span>
                        </div>
                    </div>
                `;
            }}
            
            // Input/Output summary
            if (details.output) {{
                html += `
                    <div class="grid grid-cols-2 gap-3 mb-6">
                        ${{details.inputs && details.inputs[0] ? `
                            <div class="stat-card p-3 rounded-xl ${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                                <div class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs mb-1">Input</div>
                                <div class="font-mono text-lg ${{isDark ? 'text-white' : 'text-gray-900'}}">${{details.inputs[0].rows.toLocaleString()}}</div>
                                <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}} text-xs">rows × ${{details.inputs[0].cols}} cols</div>
                            </div>
                        ` : ''}}
                        <div class="stat-card p-3 rounded-xl ${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                            <div class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs mb-1">Output</div>
                            <div class="font-mono text-lg ${{isDark ? 'text-white' : 'text-gray-900'}}">${{details.output.rows.toLocaleString()}}</div>
                            <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}} text-xs">rows × ${{details.output.cols}} cols</div>
                        </div>
                    </div>
                `;
            }}
            
            // Statistics
            if (details.stats && details.stats.length > 0) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-3">Statistics</h3>
                        <div class="space-y-3">
                `;
                
                for (const stat of details.stats) {{
                    html += `
                        <div class="stat-card p-4 rounded-xl ${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                            <div class="flex items-center justify-between mb-2">
                                <span class="font-medium ${{isDark ? 'text-white' : 'text-gray-900'}}">${{escapeHtml(stat.name)}}</span>
                                <span class="text-xs font-mono ${{isDark ? 'text-gray-400' : 'text-gray-500'}}">${{stat.unique?.toLocaleString() || 0}} unique</span>
                            </div>
                    `;
                    
                    // Numeric stats
                    if (stat.mean !== undefined) {{
                        html += `
                            <div class="grid grid-cols-4 gap-2 text-xs mb-2">
                                <div class="text-center p-1.5 rounded ${{isDark ? 'bg-surface-900' : 'bg-white'}}">
                                    <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}}">Min</div>
                                    <div class="font-mono ${{isDark ? 'text-gray-200' : 'text-gray-700'}}">${{typeof stat.min === 'number' ? stat.min.toFixed(1) : stat.min}}</div>
                                </div>
                                <div class="text-center p-1.5 rounded ${{isDark ? 'bg-surface-900' : 'bg-white'}}">
                                    <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}}">Max</div>
                                    <div class="font-mono ${{isDark ? 'text-gray-200' : 'text-gray-700'}}">${{typeof stat.max === 'number' ? stat.max.toFixed(1) : stat.max}}</div>
                                </div>
                                <div class="text-center p-1.5 rounded ${{isDark ? 'bg-surface-900' : 'bg-white'}}">
                                    <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}}">Mean</div>
                                    <div class="font-mono ${{isDark ? 'text-gray-200' : 'text-gray-700'}}">${{stat.mean.toFixed(1)}}</div>
                                </div>
                                <div class="text-center p-1.5 rounded ${{isDark ? 'bg-surface-900' : 'bg-white'}}">
                                    <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}}">Std</div>
                                    <div class="font-mono ${{isDark ? 'text-gray-200' : 'text-gray-700'}}">${{stat.std?.toFixed(1) || '-'}}</div>
                                </div>
                            </div>
                        `;
                    }}
                    
                    // Top values
                    if (stat.topValues && stat.topValues.length > 0) {{
                        html += `
                            <div class="mt-2">
                                <div class="${{isDark ? 'text-gray-500' : 'text-gray-400'}} text-xs mb-1">Top Values</div>
                                <div class="space-y-1">
                        `;
                        for (const tv of stat.topValues.slice(0, 3)) {{
                            const width = Math.min(100, tv.percentage * 2);
                            html += `
                                <div class="flex items-center gap-2">
                                    <div class="w-20 truncate font-mono text-xs ${{isDark ? 'text-gray-300' : 'text-gray-600'}}">${{escapeHtml(tv.value)}}</div>
                                    <div class="flex-1 h-1.5 ${{isDark ? 'bg-surface-900' : 'bg-gray-200'}} rounded-full overflow-hidden">
                                        <div class="h-full bg-blue-500 rounded-full" style="width: ${{width}}%"></div>
                                    </div>
                                    <div class="text-xs ${{isDark ? 'text-gray-400' : 'text-gray-500'}} w-12 text-right">${{tv.percentage}}%</div>
                                </div>
                            `;
                        }}
                        html += '</div></div>';
                    }}
                    
                    html += '</div>';
                }}
                
                html += '</div></div>';
            }}
            
            // Histogram chart container
            if (details.histogramData && Object.keys(details.histogramData).length > 0) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-3">Distribution</h3>
                        <div class="${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} rounded-xl p-4 border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                            <canvas id="histogram-chart" height="150"></canvas>
                        </div>
                    </div>
                `;
            }}
            
            // Scatter plot container
            if (details.scatterData && Object.keys(details.scatterData).length > 0) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-3">Scatter Plot</h3>
                        <div class="${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} rounded-xl p-4 border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                            <canvas id="scatter-chart" height="200"></canvas>
                        </div>
                    </div>
                `;
            }}
            
            // Columns list
            if (details.output && details.output.columns && details.output.columns.length > 0) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-3">Columns (${{details.output.columns.length}})</h3>
                        <div class="flex flex-wrap gap-1.5">
                `;
                for (const col of details.output.columns) {{
                    html += `<span class="px-2 py-0.5 text-xs font-mono ${{isDark ? 'bg-surface-800 text-gray-300' : 'bg-gray-100 text-gray-600'}} rounded">${{escapeHtml(col)}}</span>`;
                }}
                html += '</div></div>';
            }}
            
            // Arguments
            if (details.arguments && Object.keys(details.arguments).length > 0) {{
                html += `
                    <div class="mb-6">
                        <h3 class="${{isDark ? 'text-gray-400' : 'text-gray-500'}} text-xs font-semibold uppercase tracking-wider mb-3">Arguments</h3>
                        <div class="${{isDark ? 'bg-surface-800' : 'bg-gray-50'}} rounded-xl p-3 border ${{isDark ? 'border-surface-700' : 'border-gray-200'}}">
                            <pre class="text-xs font-mono ${{isDark ? 'text-gray-300' : 'text-gray-600'}} whitespace-pre-wrap">${{escapeHtml(JSON.stringify(details.arguments, null, 2))}}</pre>
                        </div>
                    </div>
                `;
            }}
            
            panelContent.innerHTML = html;
            
            // Render charts after DOM update
            setTimeout(() => {{
                if (details.histogramData) {{
                    renderHistogram(details.histogramData);
                }}
                if (details.scatterData) {{
                    renderScatter(details.scatterData);
                }}
            }}, 100);
        }}
        
        // Show removed data panel
        function showRemovedPanel(data) {{
            const details = data.details || {{}};
            panelTitle.textContent = 'Removed Data';
            
            panelContent.innerHTML = `
                <div class="text-center py-8">
                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rose-100 text-rose-500 mb-4">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </div>
                    <h3 class="text-2xl font-bold ${{isDark ? 'text-white' : 'text-gray-900'}} mb-2">${{(details.rows || 0).toLocaleString()}} rows</h3>
                    <p class="${{isDark ? 'text-gray-400' : 'text-gray-500'}}">removed (${{details.percentage || 0}}%)</p>
                    <p class="${{isDark ? 'text-gray-500' : 'text-gray-400'}} text-sm mt-4">From: ${{escapeHtml(details.source || 'Unknown operation')}}</p>
                </div>
            `;
        }}
        
        // Render histogram chart
        function renderHistogram(histogramData) {{
            const canvas = document.getElementById('histogram-chart');
            if (!canvas) return;
            
            const firstKey = Object.keys(histogramData)[0];
            const data = histogramData[firstKey];
            if (!data || data.length === 0) return;
            
            // Create histogram bins
            const numBins = 20;
            const min = Math.min(...data);
            const max = Math.max(...data);
            const binWidth = (max - min) / numBins;
            const bins = new Array(numBins).fill(0);
            const labels = [];
            
            for (let i = 0; i < numBins; i++) {{
                const binStart = min + i * binWidth;
                labels.push(binStart.toFixed(1));
            }}
            
            for (const value of data) {{
                const binIndex = Math.min(numBins - 1, Math.floor((value - min) / binWidth));
                bins[binIndex]++;
            }}
            
            new Chart(canvas, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: bins,
                        backgroundColor: isDark ? 'rgba(96, 165, 250, 0.6)' : 'rgba(59, 130, 246, 0.6)',
                        borderColor: isDark ? 'rgba(96, 165, 250, 1)' : 'rgba(59, 130, 246, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: isDark ? '#27272a' : '#ffffff',
                            titleColor: isDark ? '#ffffff' : '#1f2937',
                            bodyColor: isDark ? '#d1d5db' : '#4b5563',
                            borderColor: isDark ? '#3f3f46' : '#e5e7eb',
                            borderWidth: 1,
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{ display: false }},
                            ticks: {{
                                color: isDark ? '#9ca3af' : '#6b7280',
                                maxTicksLimit: 6,
                                font: {{ size: 10 }}
                            }}
                        }},
                        y: {{
                            display: true,
                            grid: {{
                                color: isDark ? '#27272a' : '#f3f4f6',
                            }},
                            ticks: {{
                                color: isDark ? '#9ca3af' : '#6b7280',
                                font: {{ size: 10 }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Render scatter chart
        function renderScatter(scatterData) {{
            const canvas = document.getElementById('scatter-chart');
            if (!canvas) return;
            
            const firstKey = Object.keys(scatterData)[0];
            const data = scatterData[firstKey];
            if (!data || !data.x || !data.y) return;
            
            const points = data.x.map((x, i) => ({{ x, y: data.y[i] }}));
            
            new Chart(canvas, {{
                type: 'scatter',
                data: {{
                    datasets: [{{
                        data: points,
                        backgroundColor: isDark ? 'rgba(167, 139, 250, 0.5)' : 'rgba(139, 92, 246, 0.5)',
                        borderColor: isDark ? 'rgba(167, 139, 250, 1)' : 'rgba(139, 92, 246, 1)',
                        pointRadius: 3,
                        pointHoverRadius: 5,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: isDark ? '#27272a' : '#ffffff',
                            titleColor: isDark ? '#ffffff' : '#1f2937',
                            bodyColor: isDark ? '#d1d5db' : '#4b5563',
                            borderColor: isDark ? '#3f3f46' : '#e5e7eb',
                            borderWidth: 1,
                            callbacks: {{
                                label: (ctx) => `(${{ctx.parsed.x.toFixed(2)}}, ${{ctx.parsed.y.toFixed(2)}})`
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{
                                color: isDark ? '#27272a' : '#f3f4f6',
                            }},
                            ticks: {{
                                color: isDark ? '#9ca3af' : '#6b7280',
                                font: {{ size: 10 }}
                            }},
                            title: {{
                                display: true,
                                text: firstKey.split('_vs_')[0],
                                color: isDark ? '#9ca3af' : '#6b7280',
                                font: {{ size: 11 }}
                            }}
                        }},
                        y: {{
                            display: true,
                            grid: {{
                                color: isDark ? '#27272a' : '#f3f4f6',
                            }},
                            ticks: {{
                                color: isDark ? '#9ca3af' : '#6b7280',
                                font: {{ size: 10 }}
                            }},
                            title: {{
                                display: true,
                                text: firstKey.split('_vs_')[1],
                                color: isDark ? '#9ca3af' : '#6b7280',
                                font: {{ size: 11 }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Utility function
        function escapeHtml(str) {{
            if (!str) return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }}
        
        // Initial fit
        cy.ready(() => {{
            setTimeout(() => cy.fit(null, 60), 100);
        }});
    </script>
</body>
</html>
'''

