"""
Pandas operation interceptors.

This module provides mechanisms to intercept pandas operations and
automatically record them in the FlowTracker.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from .events import OperationType

if TYPE_CHECKING:
    from .tracker import FlowTracker


# Storage for original methods
_original_methods: dict[str, Any] = {}

# Currently active tracker
_tracker: FlowTracker | None = None

# Re-entrancy guard to prevent tracking internal pandas operations
_tracking_active: bool = False


def install(tracker: FlowTracker) -> None:
    """
    Install pandas interceptors.

    Args:
        tracker: FlowTracker instance to record events
    """
    global _tracker
    _tracker = tracker

    # Intercept pandas module-level functions
    _intercept_read_functions()
    _intercept_concat()

    # Intercept DataFrame methods
    _intercept_dataframe_methods()


def uninstall(tracker: FlowTracker) -> None:
    """
    Remove pandas interceptors and restore original methods.

    Args:
        tracker: FlowTracker instance (for verification)
    """
    global _tracker

    # Restore original methods
    for name, original in _original_methods.items():
        if name.startswith("pd."):
            setattr(pd, name[3:], original)
        elif name.startswith("DataFrame."):
            setattr(pd.DataFrame, name[10:], original)

    _original_methods.clear()
    _tracker = None


def _intercept_read_functions() -> None:
    """Intercept pandas read_* functions."""

    # read_csv
    _original_methods["pd.read_csv"] = pd.read_csv

    @functools.wraps(pd.read_csv)
    def tracked_read_csv(*args, **kwargs) -> pd.DataFrame:
        result = _original_methods["pd.read_csv"](*args, **kwargs)

        if _tracker:
            # Get filename
            filepath = args[0] if args else kwargs.get("filepath_or_buffer")
            filename = _extract_filename(filepath)

            _tracker.record_operation(
                operation_type=OperationType.READ_CSV,
                operation_name="Read CSV",
                input_dfs=[],
                output_df=result,
                description=f"Load data from {filename}",
                arguments={"file": filename},
            )

            # Register with source file
            _tracker.register_dataframe(result, name=filename, source_file=str(filepath))

        return result

    pd.read_csv = tracked_read_csv

    # read_excel
    _original_methods["pd.read_excel"] = pd.read_excel

    @functools.wraps(pd.read_excel)
    def tracked_read_excel(*args, **kwargs) -> pd.DataFrame:
        result = _original_methods["pd.read_excel"](*args, **kwargs)

        if _tracker:
            filepath = args[0] if args else kwargs.get("io")
            filename = _extract_filename(filepath)

            _tracker.record_operation(
                operation_type=OperationType.READ_EXCEL,
                operation_name="Read Excel",
                input_dfs=[],
                output_df=result,
                description=f"Load data from {filename}",
                arguments={"file": filename},
            )

            _tracker.register_dataframe(result, name=filename, source_file=str(filepath))

        return result

    pd.read_excel = tracked_read_excel

    # read_parquet
    _original_methods["pd.read_parquet"] = pd.read_parquet

    @functools.wraps(pd.read_parquet)
    def tracked_read_parquet(*args, **kwargs) -> pd.DataFrame:
        result = _original_methods["pd.read_parquet"](*args, **kwargs)

        if _tracker:
            filepath = args[0] if args else kwargs.get("path")
            filename = _extract_filename(filepath)

            _tracker.record_operation(
                operation_type=OperationType.READ_PARQUET,
                operation_name="Read Parquet",
                input_dfs=[],
                output_df=result,
                description=f"Load data from {filename}",
                arguments={"file": filename},
            )

            _tracker.register_dataframe(result, name=filename, source_file=str(filepath))

        return result

    pd.read_parquet = tracked_read_parquet

    # read_json
    _original_methods["pd.read_json"] = pd.read_json

    @functools.wraps(pd.read_json)
    def tracked_read_json(*args, **kwargs) -> pd.DataFrame:
        result = _original_methods["pd.read_json"](*args, **kwargs)

        if _tracker:
            filepath = args[0] if args else kwargs.get("path_or_buf")
            filename = _extract_filename(filepath)

            _tracker.record_operation(
                operation_type=OperationType.READ_JSON,
                operation_name="Read JSON",
                input_dfs=[],
                output_df=result,
                description=f"Load data from {filename}",
                arguments={"file": filename},
            )

            _tracker.register_dataframe(result, name=filename, source_file=str(filepath))

        return result

    pd.read_json = tracked_read_json


def _intercept_concat() -> None:
    """Intercept pd.concat function."""
    _original_methods["pd.concat"] = pd.concat

    @functools.wraps(pd.concat)
    def tracked_concat(objs, *args, **kwargs):
        global _tracking_active

        result = _original_methods["pd.concat"](objs, *args, **kwargs)

        # Skip if tracker not active, if we're inside another tracked operation,
        # or if result is not a DataFrame (could be a Series)
        if _tracker and not _tracking_active and isinstance(result, pd.DataFrame):
            # Get input DataFrames
            input_dfs = [obj for obj in objs if isinstance(obj, pd.DataFrame)]

            # Only track if we have DataFrame inputs
            if input_dfs:
                axis = kwargs.get("axis", 0)
                axis_name = "rows" if axis == 0 else "columns"

                _tracker.record_operation(
                    operation_type=OperationType.CONCAT,
                    operation_name="Concatenate",
                    input_dfs=input_dfs,
                    output_df=result,
                    description=f"Concatenate {len(input_dfs)} DataFrames along {axis_name}",
                    arguments={"n_dataframes": len(input_dfs), "axis": axis},
                )

        return result

    pd.concat = tracked_concat


def _intercept_dataframe_methods() -> None:
    """Intercept DataFrame instance methods."""

    # merge
    _original_methods["DataFrame.merge"] = pd.DataFrame.merge

    @functools.wraps(pd.DataFrame.merge)
    def tracked_merge(self, right, *args, **kwargs) -> pd.DataFrame:
        global _tracking_active

        # Set re-entrancy guard to prevent tracking internal operations
        was_tracking = _tracking_active
        _tracking_active = True

        try:
            result = _original_methods["DataFrame.merge"](self, right, *args, **kwargs)
        finally:
            _tracking_active = was_tracking

        if _tracker and not was_tracking:
            how = kwargs.get("how", "inner")
            on = kwargs.get("on")
            left_on = kwargs.get("left_on")
            right_on = kwargs.get("right_on")

            # Determine join keys
            if on:
                keys = on if isinstance(on, list) else [on]
            elif left_on and right_on:
                keys = [f"{left_on}={right_on}"]
            else:
                keys = ["index"]

            _tracker.record_operation(
                operation_type=OperationType.MERGE,
                operation_name=f"Merge ({how})",
                input_dfs=[self, right],
                output_df=result,
                description=f"{how.upper()} join on {', '.join(str(k) for k in keys)}",
                arguments={"how": how, "on": on, "left_on": left_on, "right_on": right_on},
            )

        return result

    pd.DataFrame.merge = tracked_merge

    # join
    _original_methods["DataFrame.join"] = pd.DataFrame.join

    @functools.wraps(pd.DataFrame.join)
    def tracked_join(self, other, *args, **kwargs) -> pd.DataFrame:
        global _tracking_active

        # Set re-entrancy guard
        was_tracking = _tracking_active
        _tracking_active = True

        try:
            result = _original_methods["DataFrame.join"](self, other, *args, **kwargs)
        finally:
            _tracking_active = was_tracking

        if _tracker and not was_tracking:
            how = kwargs.get("how", "left")
            on = kwargs.get("on")

            input_dfs = [self]
            if isinstance(other, pd.DataFrame):
                input_dfs.append(other)
            elif isinstance(other, list):
                input_dfs.extend([o for o in other if isinstance(o, pd.DataFrame)])

            _tracker.record_operation(
                operation_type=OperationType.JOIN,
                operation_name=f"Join ({how})",
                input_dfs=input_dfs,
                output_df=result,
                description=f"{how.upper()} join",
                arguments={"how": how, "on": on},
            )

        return result

    pd.DataFrame.join = tracked_join

    # assign
    _original_methods["DataFrame.assign"] = pd.DataFrame.assign

    @functools.wraps(pd.DataFrame.assign)
    def tracked_assign(self, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.assign"](self, **kwargs)

        if _tracker:
            new_cols = list(kwargs.keys())

            _tracker.record_operation(
                operation_type=OperationType.ASSIGN,
                operation_name="Assign",
                input_dfs=[self],
                output_df=result,
                description=f"Create column(s): {', '.join(new_cols)}",
                arguments={"columns": new_cols},
            )

        return result

    pd.DataFrame.assign = tracked_assign

    # drop
    _original_methods["DataFrame.drop"] = pd.DataFrame.drop

    @functools.wraps(pd.DataFrame.drop)
    def tracked_drop(self, labels=None, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.drop"](self, labels, *args, **kwargs)

        # Skip if inplace=True (returns None) or if tracker not active
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            axis = kwargs.get("axis", 0)
            columns = kwargs.get("columns")

            if columns:
                dropped = columns if isinstance(columns, list) else [columns]
                desc = f"Drop column(s): {', '.join(str(c) for c in dropped)}"
            elif axis == 1:
                dropped = labels if isinstance(labels, list) else [labels]
                desc = f"Drop column(s): {', '.join(str(c) for c in dropped)}"
            else:
                dropped = labels if isinstance(labels, list) else [labels]
                desc = f"Drop row(s): {len(dropped)} labels"

            _tracker.record_operation(
                operation_type=OperationType.DROP,
                operation_name="Drop",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"labels": labels, "axis": axis, "columns": columns},
            )

        return result

    pd.DataFrame.drop = tracked_drop

    # drop_duplicates
    _original_methods["DataFrame.drop_duplicates"] = pd.DataFrame.drop_duplicates

    @functools.wraps(pd.DataFrame.drop_duplicates)
    def tracked_drop_duplicates(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.drop_duplicates"](self, *args, **kwargs)

        # Skip if inplace=True (returns None)
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            subset = kwargs.get("subset")
            keep = kwargs.get("keep", "first")

            if subset:
                cols = subset if isinstance(subset, list) else [subset]
                desc = f"Remove duplicates on {', '.join(cols)}"
            else:
                desc = "Remove duplicate rows"

            _tracker.record_operation(
                operation_type=OperationType.DROP_DUPLICATES,
                operation_name="Drop Duplicates",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"subset": subset, "keep": keep},
            )

        return result

    pd.DataFrame.drop_duplicates = tracked_drop_duplicates

    # dropna
    _original_methods["DataFrame.dropna"] = pd.DataFrame.dropna

    @functools.wraps(pd.DataFrame.dropna)
    def tracked_dropna(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.dropna"](self, *args, **kwargs)

        # Skip if inplace=True (returns None)
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            subset = kwargs.get("subset")
            how = kwargs.get("how", "any")

            _tracker.record_operation(
                operation_type=OperationType.DROPNA,
                operation_name="Drop NA",
                input_dfs=[self],
                output_df=result,
                description=f"Remove rows with {how} missing values",
                arguments={"subset": subset, "how": how},
            )

        return result

    pd.DataFrame.dropna = tracked_dropna

    # fillna
    _original_methods["DataFrame.fillna"] = pd.DataFrame.fillna

    @functools.wraps(pd.DataFrame.fillna)
    def tracked_fillna(self, value=None, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.fillna"](self, value, *args, **kwargs)

        # Skip if inplace=True (returns None)
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            method = kwargs.get("method")

            if method:
                desc = f"Fill NA using {method}"
            elif isinstance(value, dict):
                desc = f"Fill NA in {len(value)} columns"
            else:
                desc = f"Fill NA with {value}"

            _tracker.record_operation(
                operation_type=OperationType.FILLNA,
                operation_name="Fill NA",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"value": str(value)[:50], "method": method},
            )

        return result

    pd.DataFrame.fillna = tracked_fillna

    # query
    _original_methods["DataFrame.query"] = pd.DataFrame.query

    @functools.wraps(pd.DataFrame.query)
    def tracked_query(self, expr, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.query"](self, expr, *args, **kwargs)

        if _tracker:
            _tracker.record_operation(
                operation_type=OperationType.QUERY,
                operation_name="Query",
                input_dfs=[self],
                output_df=result,
                description=f"Filter: {expr}",
                arguments={"expr": expr},
            )

        return result

    pd.DataFrame.query = tracked_query

    # sort_values
    _original_methods["DataFrame.sort_values"] = pd.DataFrame.sort_values

    @functools.wraps(pd.DataFrame.sort_values)
    def tracked_sort_values(self, by, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.sort_values"](self, by, *args, **kwargs)

        # Skip if inplace=True (returns None)
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            ascending = kwargs.get("ascending", True)
            cols = by if isinstance(by, list) else [by]
            direction = "ascending" if ascending else "descending"

            _tracker.record_operation(
                operation_type=OperationType.SORT_VALUES,
                operation_name="Sort",
                input_dfs=[self],
                output_df=result,
                description=f"Sort by {', '.join(cols)} ({direction})",
                arguments={"by": by, "ascending": ascending},
            )

        return result

    pd.DataFrame.sort_values = tracked_sort_values

    # pivot
    _original_methods["DataFrame.pivot"] = pd.DataFrame.pivot

    @functools.wraps(pd.DataFrame.pivot)
    def tracked_pivot(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.pivot"](self, *args, **kwargs)

        if _tracker:
            index = kwargs.get("index") or (args[0] if args else None)
            columns = kwargs.get("columns") or (args[1] if len(args) > 1 else None)
            values = kwargs.get("values") or (args[2] if len(args) > 2 else None)

            _tracker.record_operation(
                operation_type=OperationType.PIVOT,
                operation_name="Pivot",
                input_dfs=[self],
                output_df=result,
                description=f"Pivot: index={index}, columns={columns}",
                arguments={"index": index, "columns": columns, "values": values},
            )

        return result

    pd.DataFrame.pivot = tracked_pivot

    # pivot_table
    _original_methods["DataFrame.pivot_table"] = pd.DataFrame.pivot_table

    @functools.wraps(pd.DataFrame.pivot_table)
    def tracked_pivot_table(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.pivot_table"](self, *args, **kwargs)

        if _tracker:
            index = kwargs.get("index")
            columns = kwargs.get("columns")
            values = kwargs.get("values")
            aggfunc = kwargs.get("aggfunc", "mean")

            _tracker.record_operation(
                operation_type=OperationType.PIVOT_TABLE,
                operation_name="Pivot Table",
                input_dfs=[self],
                output_df=result,
                description=f"Pivot table with {aggfunc}",
                arguments={
                    "index": index,
                    "columns": columns,
                    "values": values,
                    "aggfunc": str(aggfunc),
                },
            )

        return result

    pd.DataFrame.pivot_table = tracked_pivot_table

    # melt
    _original_methods["DataFrame.melt"] = pd.DataFrame.melt

    @functools.wraps(pd.DataFrame.melt)
    def tracked_melt(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.melt"](self, *args, **kwargs)

        if _tracker:
            id_vars = kwargs.get("id_vars")
            value_vars = kwargs.get("value_vars")

            _tracker.record_operation(
                operation_type=OperationType.MELT,
                operation_name="Melt",
                input_dfs=[self],
                output_df=result,
                description="Unpivot from wide to long format",
                arguments={"id_vars": id_vars, "value_vars": value_vars},
            )

        return result

    pd.DataFrame.melt = tracked_melt

    # rename
    _original_methods["DataFrame.rename"] = pd.DataFrame.rename

    @functools.wraps(pd.DataFrame.rename)
    def tracked_rename(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.rename"](self, *args, **kwargs)

        # Skip if inplace=True (returns None)
        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            columns = kwargs.get("columns", {})

            if columns:
                renames = [f"{k}→{v}" for k, v in columns.items()]
                desc = f"Rename: {', '.join(renames[:3])}"
                if len(renames) > 3:
                    desc += f" (+{len(renames) - 3} more)"
            else:
                desc = "Rename columns/index"

            _tracker.record_operation(
                operation_type=OperationType.RENAME,
                operation_name="Rename",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"columns": columns},
            )

        return result

    pd.DataFrame.rename = tracked_rename

    # astype
    _original_methods["DataFrame.astype"] = pd.DataFrame.astype

    @functools.wraps(pd.DataFrame.astype)
    def tracked_astype(self, dtype, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.astype"](self, dtype, *args, **kwargs)

        if _tracker:
            if isinstance(dtype, dict):
                conversions = [f"{k}→{v}" for k, v in dtype.items()]
                desc = f"Convert types: {', '.join(conversions[:3])}"
            else:
                desc = f"Convert all to {dtype}"

            _tracker.record_operation(
                operation_type=OperationType.ASTYPE,
                operation_name="Convert Types",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"dtype": str(dtype)},
            )

        return result

    pd.DataFrame.astype = tracked_astype

    # reset_index
    _original_methods["DataFrame.reset_index"] = pd.DataFrame.reset_index

    @functools.wraps(pd.DataFrame.reset_index)
    def tracked_reset_index(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.reset_index"](self, *args, **kwargs)

        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            drop = kwargs.get("drop", False)
            desc = "Reset index" + (" (drop)" if drop else " (keep as column)")

            _tracker.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name="Reset Index",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"drop": drop},
            )

        return result

    pd.DataFrame.reset_index = tracked_reset_index

    # set_index
    _original_methods["DataFrame.set_index"] = pd.DataFrame.set_index

    @functools.wraps(pd.DataFrame.set_index)
    def tracked_set_index(self, keys, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.set_index"](self, keys, *args, **kwargs)

        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            key_names = keys if isinstance(keys, list) else [keys]
            desc = f"Set index: {', '.join(str(k) for k in key_names)}"

            _tracker.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name="Set Index",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"keys": key_names},
            )

        return result

    pd.DataFrame.set_index = tracked_set_index

    # sample
    _original_methods["DataFrame.sample"] = pd.DataFrame.sample

    @functools.wraps(pd.DataFrame.sample)
    def tracked_sample(self, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.sample"](self, *args, **kwargs)

        if _tracker:
            n = kwargs.get("n") or (args[0] if args else None)
            frac = kwargs.get("frac")

            if frac:
                desc = f"Sample {frac * 100:.0f}% of rows"
            elif n:
                desc = f"Sample {n} rows"
            else:
                desc = "Sample rows"

            _tracker.record_operation(
                operation_type=OperationType.FILTER,
                operation_name="Sample",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"n": n, "frac": frac},
            )

        return result

    pd.DataFrame.sample = tracked_sample

    # replace
    _original_methods["DataFrame.replace"] = pd.DataFrame.replace

    @functools.wraps(pd.DataFrame.replace)
    def tracked_replace(self, to_replace=None, value=None, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.replace"](self, to_replace, value, *args, **kwargs)

        inplace = kwargs.get("inplace", False)
        if _tracker and result is not None and not inplace:
            if isinstance(to_replace, dict):
                desc = f"Replace values in {len(to_replace)} mappings"
            else:
                desc = f"Replace {to_replace} with {value}"

            _tracker.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name="Replace",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"to_replace": str(to_replace)[:30], "value": str(value)[:30]},
            )

        return result

    pd.DataFrame.replace = tracked_replace

    # stack
    _original_methods["DataFrame.stack"] = pd.DataFrame.stack

    @functools.wraps(pd.DataFrame.stack)
    def tracked_stack(self, *args, **kwargs):
        result = _original_methods["DataFrame.stack"](self, *args, **kwargs)

        if _tracker and isinstance(result, pd.DataFrame):
            _tracker.record_operation(
                operation_type=OperationType.STACK,
                operation_name="Stack",
                input_dfs=[self],
                output_df=result,
                description="Stack columns to rows",
                arguments={},
            )

        return result

    pd.DataFrame.stack = tracked_stack

    # unstack
    _original_methods["DataFrame.unstack"] = pd.DataFrame.unstack

    @functools.wraps(pd.DataFrame.unstack)
    def tracked_unstack(self, *args, **kwargs):
        result = _original_methods["DataFrame.unstack"](self, *args, **kwargs)

        if _tracker and isinstance(result, pd.DataFrame):
            _tracker.record_operation(
                operation_type=OperationType.UNSTACK,
                operation_name="Unstack",
                input_dfs=[self],
                output_df=result,
                description="Unstack rows to columns",
                arguments={},
            )

        return result

    pd.DataFrame.unstack = tracked_unstack

    # explode
    _original_methods["DataFrame.explode"] = pd.DataFrame.explode

    @functools.wraps(pd.DataFrame.explode)
    def tracked_explode(self, column, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.explode"](self, column, *args, **kwargs)

        if _tracker:
            cols = column if isinstance(column, list) else [column]

            _tracker.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name="Explode",
                input_dfs=[self],
                output_df=result,
                description=f"Explode list column(s): {', '.join(str(c) for c in cols)}",
                arguments={"column": cols},
            )

        return result

    pd.DataFrame.explode = tracked_explode

    # clip
    _original_methods["DataFrame.clip"] = pd.DataFrame.clip

    @functools.wraps(pd.DataFrame.clip)
    def tracked_clip(self, lower=None, upper=None, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.clip"](self, lower, upper, *args, **kwargs)

        if _tracker:
            bounds = []
            if lower is not None:
                bounds.append(f"min={lower}")
            if upper is not None:
                bounds.append(f"max={upper}")
            desc = f"Clip values: {', '.join(bounds)}" if bounds else "Clip values"

            _tracker.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name="Clip",
                input_dfs=[self],
                output_df=result,
                description=desc,
                arguments={"lower": lower, "upper": upper},
            )

        return result

    pd.DataFrame.clip = tracked_clip

    # nlargest
    _original_methods["DataFrame.nlargest"] = pd.DataFrame.nlargest

    @functools.wraps(pd.DataFrame.nlargest)
    def tracked_nlargest(self, n, columns, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.nlargest"](self, n, columns, *args, **kwargs)

        if _tracker:
            cols = columns if isinstance(columns, list) else [columns]

            _tracker.record_operation(
                operation_type=OperationType.FILTER,
                operation_name="N Largest",
                input_dfs=[self],
                output_df=result,
                description=f"Top {n} by {', '.join(cols)}",
                arguments={"n": n, "columns": cols},
            )

        return result

    pd.DataFrame.nlargest = tracked_nlargest

    # nsmallest
    _original_methods["DataFrame.nsmallest"] = pd.DataFrame.nsmallest

    @functools.wraps(pd.DataFrame.nsmallest)
    def tracked_nsmallest(self, n, columns, *args, **kwargs) -> pd.DataFrame:
        result = _original_methods["DataFrame.nsmallest"](self, n, columns, *args, **kwargs)

        if _tracker:
            cols = columns if isinstance(columns, list) else [columns]

            _tracker.record_operation(
                operation_type=OperationType.FILTER,
                operation_name="N Smallest",
                input_dfs=[self],
                output_df=result,
                description=f"Bottom {n} by {', '.join(cols)}",
                arguments={"n": n, "columns": cols},
            )

        return result

    pd.DataFrame.nsmallest = tracked_nsmallest


def _extract_filename(filepath: Any) -> str:
    """Extract filename from a filepath."""
    if filepath is None:
        return "unknown"

    try:
        path = Path(str(filepath))
        return path.name
    except Exception:
        return str(filepath)[:50]


# Helper functions for manual tracking


def track_filter(
    tracker: FlowTracker,
    input_df: pd.DataFrame,
    output_df: pd.DataFrame,
    condition: str,
) -> None:
    """
    Manually track a filter operation.

    Args:
        tracker: FlowTracker instance
        input_df: DataFrame before filtering
        output_df: DataFrame after filtering
        condition: String describing the filter condition
    """
    tracker.record_operation(
        operation_type=OperationType.FILTER,
        operation_name="Filter",
        input_dfs=[input_df],
        output_df=output_df,
        description=f"Filter: {condition}",
        arguments={"condition": condition},
    )


def track_loc(
    tracker: FlowTracker,
    input_df: pd.DataFrame,
    output_df: pd.DataFrame,
    selector: str,
) -> None:
    """
    Manually track a loc operation.

    Args:
        tracker: FlowTracker instance
        input_df: DataFrame before selection
        output_df: DataFrame after selection
        selector: String describing the selection
    """
    tracker.record_operation(
        operation_type=OperationType.LOC,
        operation_name="Select (loc)",
        input_dfs=[input_df],
        output_df=output_df,
        description=f"Select: {selector}",
        arguments={"selector": selector},
    )


def track_groupby_agg(
    tracker: FlowTracker,
    input_df: pd.DataFrame,
    output_df: pd.DataFrame,
    group_cols: list[str],
    agg_func: str | dict,
) -> None:
    """
    Manually track a groupby aggregation.

    Args:
        tracker: FlowTracker instance
        input_df: DataFrame before groupby
        output_df: DataFrame after aggregation
        group_cols: Columns used for grouping
        agg_func: Aggregation function(s)
    """
    tracker.record_operation(
        operation_type=OperationType.AGGREGATE,
        operation_name="GroupBy Aggregate",
        input_dfs=[input_df],
        output_df=output_df,
        description=f"Group by {', '.join(group_cols)} with {agg_func}",
        arguments={"group_by": group_cols, "agg_func": str(agg_func)},
    )
