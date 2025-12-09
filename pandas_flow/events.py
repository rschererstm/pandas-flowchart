"""
Event classes for tracking pandas operations.

Each operation is recorded as a FlowEvent with standardized metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OperationType(Enum):
    """Types of pandas operations that can be tracked."""

    # Data loading
    READ_CSV = "read_csv"
    READ_EXCEL = "read_excel"
    READ_PARQUET = "read_parquet"
    READ_JSON = "read_json"
    READ_SQL = "read_sql"

    # Filtering
    FILTER = "filter"
    LOC = "loc"
    ILOC = "iloc"
    QUERY = "query"

    # Joins
    MERGE = "merge"
    JOIN = "join"

    # Column operations
    ASSIGN = "assign"
    DROP = "drop"
    RENAME = "rename"

    # Concatenation
    CONCAT = "concat"
    APPEND = "append"

    # Groupby
    GROUPBY = "groupby"
    AGGREGATE = "aggregate"
    TRANSFORM = "transform"

    # Reshape
    PIVOT = "pivot"
    PIVOT_TABLE = "pivot_table"
    MELT = "melt"
    STACK = "stack"
    UNSTACK = "unstack"

    # Sorting
    SORT_VALUES = "sort_values"
    SORT_INDEX = "sort_index"

    # Duplicate handling
    DROP_DUPLICATES = "drop_duplicates"

    # Missing data
    DROPNA = "dropna"
    FILLNA = "fillna"

    # Type conversion
    ASTYPE = "astype"

    # Custom
    CUSTOM = "custom"


# Color scheme for operation types (Mermaid compatible)
OPERATION_COLORS = {
    # Loading - gray
    OperationType.READ_CSV: "#6c757d",
    OperationType.READ_EXCEL: "#6c757d",
    OperationType.READ_PARQUET: "#6c757d",
    OperationType.READ_JSON: "#6c757d",
    OperationType.READ_SQL: "#6c757d",
    # Filtering - blue
    OperationType.FILTER: "#3498db",
    OperationType.LOC: "#3498db",
    OperationType.ILOC: "#3498db",
    OperationType.QUERY: "#3498db",
    # Joins - green
    OperationType.MERGE: "#27ae60",
    OperationType.JOIN: "#27ae60",
    # Column operations - orange
    OperationType.ASSIGN: "#e67e22",
    OperationType.RENAME: "#e67e22",
    # Drop - red
    OperationType.DROP: "#e74c3c",
    OperationType.DROP_DUPLICATES: "#e74c3c",
    OperationType.DROPNA: "#e74c3c",
    # Groupby - purple
    OperationType.GROUPBY: "#9b59b6",
    OperationType.AGGREGATE: "#9b59b6",
    OperationType.TRANSFORM: "#9b59b6",
    # Concat - teal
    OperationType.CONCAT: "#17a2b8",
    OperationType.APPEND: "#17a2b8",
    # Reshape - pink
    OperationType.PIVOT: "#fd79a8",
    OperationType.PIVOT_TABLE: "#fd79a8",
    OperationType.MELT: "#fd79a8",
    OperationType.STACK: "#fd79a8",
    OperationType.UNSTACK: "#fd79a8",
    # Sorting - yellow
    OperationType.SORT_VALUES: "#f1c40f",
    OperationType.SORT_INDEX: "#f1c40f",
    # Fill - cyan
    OperationType.FILLNA: "#00cec9",
    # Type conversion - brown
    OperationType.ASTYPE: "#a0522d",
    # Custom - dark gray
    OperationType.CUSTOM: "#495057",
}

# Category names for legend
OPERATION_CATEGORIES = {
    "Data Loading": [
        OperationType.READ_CSV,
        OperationType.READ_EXCEL,
        OperationType.READ_PARQUET,
        OperationType.READ_JSON,
        OperationType.READ_SQL,
    ],
    "Filtering": [OperationType.FILTER, OperationType.LOC, OperationType.ILOC, OperationType.QUERY],
    "Joins": [OperationType.MERGE, OperationType.JOIN],
    "Column Creation": [OperationType.ASSIGN, OperationType.RENAME],
    "Drop Operations": [OperationType.DROP, OperationType.DROP_DUPLICATES, OperationType.DROPNA],
    "Groupby": [OperationType.GROUPBY, OperationType.AGGREGATE, OperationType.TRANSFORM],
    "Concatenation": [OperationType.CONCAT, OperationType.APPEND],
    "Reshape": [
        OperationType.PIVOT,
        OperationType.PIVOT_TABLE,
        OperationType.MELT,
        OperationType.STACK,
        OperationType.UNSTACK,
    ],
    "Sorting": [OperationType.SORT_VALUES, OperationType.SORT_INDEX],
    "Fill/Transform": [OperationType.FILLNA, OperationType.ASTYPE],
}


@dataclass
class DataFrameInfo:
    """Information about a DataFrame at a point in time."""

    name: str | None = None
    source_file: str | None = None
    n_rows: int = 0
    n_cols: int = 0
    columns: list[str] = field(default_factory=list)
    dtypes: dict[str, str] = field(default_factory=dict)
    memory_usage: int = 0  # bytes


@dataclass
class TrackedVariableStats:
    """Statistics for a tracked variable."""

    name: str
    n_total: int = 0
    n_non_null: int = 0
    n_unique: int = 0

    # Extended stats (for stats_variable)
    min_value: Any = None
    max_value: Any = None
    mean_value: float | None = None
    std_value: float | None = None
    top_values: list[tuple[Any, int, float]] = field(
        default_factory=list
    )  # (value, count, percentage)
    histogram: str = ""  # ASCII histogram


@dataclass
class FlowEvent:
    """
    Represents a single operation in the data flow.

    Attributes:
        event_id: Unique identifier for this event
        timestamp: When the operation occurred
        operation_type: Type of pandas operation
        operation_name: Human-readable name for display
        description: Optional description of what the operation does

        input_dfs: Information about input DataFrame(s)
        output_df: Information about output DataFrame

        arguments: Relevant arguments passed to the operation
        tracked_stats: Statistics for tracked variables after this operation

        parent_events: IDs of events that led to this one (for merge operations)
    """

    event_id: str
    timestamp: datetime
    operation_type: OperationType
    operation_name: str
    description: str = ""

    input_dfs: list[DataFrameInfo] = field(default_factory=list)
    output_df: DataFrameInfo | None = None

    arguments: dict[str, Any] = field(default_factory=dict)
    tracked_stats: list[TrackedVariableStats] = field(default_factory=list)

    parent_events: list[str] = field(default_factory=list)

    def get_color(self) -> str:
        """Get the color associated with this operation type."""
        return OPERATION_COLORS.get(self.operation_type, "#495057")

    def format_row_change(self) -> str:
        """Format the row count change between input and output."""
        if not self.input_dfs or not self.output_df:
            return ""

        input_rows = self.input_dfs[0].n_rows
        output_rows = self.output_df.n_rows

        if input_rows == output_rows:
            return f"{output_rows:,} rows (unchanged)"
        elif output_rows > input_rows:
            diff = output_rows - input_rows
            pct = (diff / input_rows * 100) if input_rows > 0 else 0
            return f"{output_rows:,} rows (+{diff:,}, +{pct:.1f}%)"
        else:
            diff = input_rows - output_rows
            pct = (diff / input_rows * 100) if input_rows > 0 else 0
            return f"{output_rows:,} rows (-{diff:,}, -{pct:.1f}%)"
