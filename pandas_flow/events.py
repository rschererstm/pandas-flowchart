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


# Color scheme for operation types (Mermaid compatible) - pastel/less saturated colors
OPERATION_COLORS = {
    # Loading - soft gray
    OperationType.READ_CSV: "#9ca3af",
    OperationType.READ_EXCEL: "#9ca3af",
    OperationType.READ_PARQUET: "#9ca3af",
    OperationType.READ_JSON: "#9ca3af",
    OperationType.READ_SQL: "#9ca3af",
    # Filtering - soft blue
    OperationType.FILTER: "#7cb3d9",
    OperationType.LOC: "#7cb3d9",
    OperationType.ILOC: "#7cb3d9",
    OperationType.QUERY: "#7cb3d9",
    # Joins - soft green
    OperationType.MERGE: "#6dc993",
    OperationType.JOIN: "#6dc993",
    # Column operations - soft orange
    OperationType.ASSIGN: "#f0a86e",
    OperationType.RENAME: "#f0a86e",
    # Drop - soft red
    OperationType.DROP: "#e8918a",
    OperationType.DROP_DUPLICATES: "#e8918a",
    OperationType.DROPNA: "#e8918a",
    # Groupby - soft purple
    OperationType.GROUPBY: "#b99ad1",
    OperationType.AGGREGATE: "#b99ad1",
    OperationType.TRANSFORM: "#b99ad1",
    # Concat - soft teal
    OperationType.CONCAT: "#6bc4ce",
    OperationType.APPEND: "#6bc4ce",
    # Reshape - soft pink
    OperationType.PIVOT: "#f5a3c7",
    OperationType.PIVOT_TABLE: "#f5a3c7",
    OperationType.MELT: "#f5a3c7",
    OperationType.STACK: "#f5a3c7",
    OperationType.UNSTACK: "#f5a3c7",
    # Sorting - soft yellow
    OperationType.SORT_VALUES: "#f5d76e",
    OperationType.SORT_INDEX: "#f5d76e",
    # Fill - soft cyan
    OperationType.FILLNA: "#72d5d0",
    # Type conversion - soft brown
    OperationType.ASTYPE: "#c49a72",
    # Custom - medium gray
    OperationType.CUSTOM: "#7b8794",
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
