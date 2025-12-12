# pandas-flowchart 📊

![pandas-flowchart logo](pandas_flow/imgs/logo.jpg)

A Python library that integrates with pandas to automatically track data transformation operations and generate visual flowcharts using HTML or Mermaid diagrams.

[![Medium](https://img.shields.io/badge/Medium-%23121212.svg?style=for-the-badge&logo=Medium&logoColor=white)](https://medium.com/@rafaelscherer.stm/stop-trying-to-decipher-your-pandas-pipelines-e0bfe56aa3d7) [![PyPI](https://img.shields.io/pypi/v/pandas-flowchart?style=for-the-badge)](https://pypi.org/project/pandas-flowchart/) [![Python](https://img.shields.io/pypi/pyversions/pandas-flowchart?style=for-the-badge)](https://pypi.org/project/pandas-flowchart/) [![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

## Features

- **Automatic Operation Tracking**: Intercepts common pandas operations (merge, filter, assign, drop, groupby, etc.)
- **Structured Metadata Recording**: Captures operation details, row counts, and custom statistics
- **Visual Flowcharts**: Generates Mermaid diagrams with color-coded operation boxes
- **Variable Monitoring**: Track specific variables' unique counts and statistics across the pipeline
- **Mini-Histograms**: ASCII sparkline histograms for numeric variables
- **Multiple Output Formats**: Export to Markdown, HTML, or raw Mermaid syntax

## Example: Healthcare Data Pipeline

This example tracks a realistic analytics workflow for a medical provider: loading patient/exam records, merging them on `patient_id`, filtering for active adults, deriving age groups, deduplicating visits, and 	then branching off into staged summaries before rendering the final Mermaid diagram shown below.

[[image_link](https://raw.githubusercontent.com/rschererstm/pandas-flowchart/refs/heads/main/pandas_flow/imgs/healthcare_pipeline.png)]

![Healthcare Data Pipeline](pandas_flow/imgs/healthcare_pipeline.png)

## Installation

```bash
pip install pandas-flowchart
```

Or install from source:

```bash
git clone https://github.com/rschererstm/pandas-flowchart
cd pandas-flowchart
pip install -e .
```

## Quick Start

```python
import pandas as pd
import pandas_flow

# Setup the tracker with variables to monitor
flow = pandas_flow.setup(
    track_row_count=True,
    track_variables={
        "patient_id": "n_unique",
        "exam_date": "n_unique",
    },
    stats_variable="age",
    stats_types=["min", "max", "mean", "std", "histogram"],
)

# Your pandas operations are automatically tracked
patients = pd.read_csv("patients.csv")
exams = pd.read_csv("exams.csv")

# Merge datasets
combined = patients.merge(exams, on="patient_id", how="inner")

# Filter adults
adults = combined.query("age >= 18")

# Add calculated columns
adults = adults.assign(
    age_group=lambda x: pd.cut(x["age"], bins=[18, 30, 50, 70, 100])
)

# Remove duplicates
clean_data = adults.drop_duplicates(subset=["patient_id", "exam_date"])

# Generate the flowchart
flow.render("pipeline_flowchart.md")
```

This generates a beautiful Mermaid flowchart showing each operation with:

- Operation type and description
- Input/output row counts
- Tracked variable statistics
- Distribution histograms

## Detailed Usage

### Setting Up the Tracker

```python
import pandas_flow

flow = pandas_flow.setup(
    # Track row counts after each operation
    track_row_count=True,
  
    # Variables to monitor (name -> stat_type)
    # stat_type can be: "n_total", "n_non_null", "n_unique"
    track_variables={
        "user_id": "n_unique",
        "transaction_date": "n_unique",
        "product_category": "n_unique",
    },
  
    # Variable for detailed statistics
    stats_variable="amount",
  
    # Which stats to compute for stats_variable
    stats_types=["min", "max", "mean", "std", "top3_freq", "histogram"],
  
    # Auto-intercept pandas operations (default: True)
    auto_intercept=True,
  
    # Visual theme: "default", "dark", or "light"
    theme="default",
)
```

### Tracked Operations

The library automatically intercepts these pandas operations:

| Category                    | Operations                                                    |
| --------------------------- | ------------------------------------------------------------- |
| **Data Loading**      | `read_csv`, `read_excel`, `read_parquet`, `read_json` |
| **Filtering**         | `query`, `loc`, `iloc`, boolean indexing                |
| **Joins**             | `merge`, `join`                                           |
| **Column Operations** | `assign`, `drop`, `rename`                              |
| **Concatenation**     | `concat`                                                    |
| **Groupby**           | `groupby` + `agg`/`transform`                           |
| **Reshape**           | `pivot`, `pivot_table`, `melt`                          |
| **Cleaning**          | `drop_duplicates`, `dropna`, `fillna`                   |
| **Sorting**           | `sort_values`, `sort_index`                               |

### Manual Tracking

For operations that can't be automatically intercepted (like boolean indexing), use manual tracking:

```python
from pandas_flow.interceptors import track_filter

# Before filtering
original_df = df.copy()

# Filter with boolean indexing
df = df[df["status"] == "active"]

# Manually track the operation
track_filter(flow, original_df, df, 'status == "active"')
```

Or use the decorator pattern:

```python
@flow.track("Custom Processing", OperationType.CUSTOM)
def process_data(df):
    # Your custom logic
    return df.pipe(custom_transform)

result = process_data(input_df)
```

### Generating Output

```python
# Markdown with Mermaid code block
flow.render("pipeline.md")

# Standalone HTML page (interactive)
flow.render("pipeline.html")

# Raw Mermaid syntax
flow.render("pipeline.mmd")

# Get Mermaid code as string
mermaid_code = flow.get_mermaid(
    title="My Data Pipeline",
    direction="TB",  # TB, LR, BT, RL
    include_legend=False,
    include_stats=True,
)
```

### Context Manager Usage

```python
with pandas_flow.setup(track_variables={"id": "n_unique"}) as flow:
    df = pd.read_csv("data.csv")
    df = df.query("active == True")
    df = df.drop_duplicates()
  
    flow.render("output.md")
# Interceptors are automatically removed after the context
```

## Output Example

### Box Contents

Each operation box includes:

- **Operation name** (bold header)
- **Description** (what the operation does)
- **Input DataFrames** with source filename and dimensions
- **Output DataFrame** dimensions
- **Row change indicator** (↑ increase / ↓ decrease with percentage)
- **Tracked variable statistics**
- **Distribution histogram** (ASCII sparkline or embedded image with x-axis)

## Color Scheme

Operations are color-coded by type (pastel/less saturated colors):

| Operation Type  | Color                 |
| --------------- | --------------------- |
| Data Loading    | Soft Gray (#9ca3af)   |
| Filtering       | Soft Blue (#7cb3d9)   |
| Joins           | Soft Green (#6dc993)  |
| Column Creation | Soft Orange (#f0a86e) |
| Drop Operations | Soft Red (#e8918a)    |
| Groupby         | Soft Purple (#b99ad1) |
| Concatenation   | Soft Teal (#6bc4ce)   |
| Reshape         | Soft Pink (#f5a3c7)   |
| Sorting         | Soft Yellow (#f5d76e) |

## API Reference

### `pandas_flow.setup()`

Main entry point to create and activate a FlowTracker.

**Parameters:**

- `track_row_count` (bool): Track row counts after each operation. Default: `True`
- `track_variables` (dict): Map of variable names to stat types. Default: `None`
- `stats_variable` (str): Variable for detailed statistics. Default: `None`
- `stats_types` (list): Statistics to compute. Default: `["min", "max", "mean", "std", "top3_freq", "histogram"]`
- `auto_intercept` (bool): Auto-intercept pandas operations. Default: `True`
- `theme` (str): Color theme. Options: `"default"`, `"dark"`, `"light"`

**Returns:** `FlowTracker` instance

### `FlowTracker.render()`

Render the flowchart to a file.

**Parameters:**

- `output_path` (str): Output file path (.md, .html, or .mmd)
- `title` (str): Diagram title. Default: `"Data Flow Pipeline"`
- `direction` (str): Flow direction. Options: `"TB"`, `"LR"`, `"BT"`, `"RL"`
- `include_legend` (bool): Include color legend. Default: `False`
- `include_stats` (bool): Include statistics in boxes. Default: `True`

### `FlowTracker.get_mermaid()`

Get Mermaid code without saving to file.

### `FlowTracker.summary()`

Get a text summary of all recorded operations.

### `FlowTracker.clear()`

Clear all recorded events.

## Architecture

```
pandas_flow/
├── __init__.py          # Public API exports
├── tracker.py           # FlowTracker central class
├── events.py            # Event types and metadata classes
├── interceptors.py      # Pandas operation interceptors
├── stats.py             # Statistics calculator
├── visualization.py     # ASCII art utilities
└── mermaid_renderer.py  # Mermaid diagram generator
```

### Design Principles

1. **Non-invasive**: Intercepts operations without modifying your code
2. **Configurable**: Track only what you need
3. **Extensible**: Easy to add custom operations
4. **Performant**: Minimal overhead during data processing

## Advanced Features

### Multiple DataFrames

The library correctly handles pipelines with multiple DataFrames:

```python
df1 = pd.read_csv("sales.csv")
df2 = pd.read_csv("products.csv")
df3 = pd.read_csv("customers.csv")

# Multiple merges are tracked with proper connections
result = df1.merge(df2, on="product_id").merge(df3, on="customer_id")
```

### Chained Operations

Method chaining is fully supported:

```python
result = (
    pd.read_csv("data.csv")
    .query("status == 'active'")
    .drop_duplicates(subset=["id"])
    .assign(processed=True)
    .sort_values("date")
)
```

### Export to PNG

For PNG export, install the optional dependency:

```bash
pip install pandas-flowchart[png]
```

Then use the Mermaid CLI or a Mermaid renderer service.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.
