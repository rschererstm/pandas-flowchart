"""
Statistics calculation module for tracked variables.

Computes various statistics including counts, unique values,
distribution metrics, and ASCII histograms.
"""

from typing import Any

import numpy as np
import pandas as pd

from .events import TrackedVariableStats

# ASCII characters for sparklines/histograms (from lowest to highest)
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"


class StatsCalculator:
    """
    Calculator for DataFrame statistics.

    Computes statistics for tracked variables and generates
    ASCII visualizations.
    """

    def __init__(
        self,
        track_variables: dict[str, str] | None = None,
        stats_variable: str | None = None,
        stats_types: list[str] | None = None,
        histogram_bins: int = 8,
    ):
        """
        Initialize the stats calculator.

        Args:
            track_variables: Dict of variable_name -> stat_type
                            ("n_total", "n_non_null", "n_unique")
            stats_variable: Variable for detailed statistics
            stats_types: List of stat types for stats_variable
                        (min, max, mean, std, top3_freq, histogram)
            histogram_bins: Number of bins for histogram
        """
        self.track_variables = track_variables or {}
        self.stats_variable = stats_variable
        self.stats_types = stats_types or ["min", "max", "mean", "std", "top3_freq", "histogram"]
        self.histogram_bins = histogram_bins

    def compute_stats(self, df: pd.DataFrame) -> list[TrackedVariableStats]:
        """
        Compute statistics for all tracked variables.

        Args:
            df: DataFrame to compute statistics for

        Returns:
            List of TrackedVariableStats for each tracked variable
        """
        stats_list = []

        # Compute stats for tracked variables
        for var_name, stat_type in self.track_variables.items():
            stats = self._compute_variable_stats(df, var_name, stat_type)
            if stats:
                stats_list.append(stats)

        # Compute extended stats for stats_variable
        if self.stats_variable and self.stats_variable in df.columns:
            stats = self._compute_extended_stats(df, self.stats_variable)
            if stats:
                stats_list.append(stats)

        return stats_list

    def _compute_variable_stats(
        self, df: pd.DataFrame, var_name: str, stat_type: str
    ) -> TrackedVariableStats | None:
        """Compute basic stats for a tracked variable."""
        if var_name not in df.columns:
            return None

        series = df[var_name]

        return TrackedVariableStats(
            name=var_name,
            n_total=len(series),
            n_non_null=series.notna().sum(),
            n_unique=series.nunique(),
        )

    def _compute_extended_stats(
        self, df: pd.DataFrame, var_name: str
    ) -> TrackedVariableStats | None:
        """Compute extended statistics for the stats_variable."""
        if var_name not in df.columns:
            return None

        series = df[var_name]

        stats = TrackedVariableStats(
            name=var_name,
            n_total=len(series),
            n_non_null=series.notna().sum(),
            n_unique=series.nunique(),
        )

        # Numeric stats
        if pd.api.types.is_numeric_dtype(series):
            if "min" in self.stats_types:
                stats.min_value = series.min()
            if "max" in self.stats_types:
                stats.max_value = series.max()
            if "mean" in self.stats_types:
                stats.mean_value = series.mean()
            if "std" in self.stats_types:
                stats.std_value = series.std()
            if "histogram" in self.stats_types:
                stats.histogram = self._generate_histogram(series)

        # Top frequent values
        if "top3_freq" in self.stats_types:
            stats.top_values = self._get_top_values(series, n=3)

        return stats

    def _generate_histogram(self, series: pd.Series, width: int = 8) -> str:
        """
        Generate an ASCII histogram/sparkline for a numeric series.

        Args:
            series: Numeric pandas Series
            width: Number of bins/characters

        Returns:
            ASCII sparkline string
        """
        # Drop NA values
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return "░" * width

        try:
            # Compute histogram
            counts, _ = np.histogram(clean_series, bins=width)

            if counts.max() == 0:
                return "░" * width

            # Normalize to sparkline characters
            normalized = counts / counts.max()

            # Map to characters
            sparkline = ""
            for val in normalized:
                idx = int(val * (len(SPARKLINE_CHARS) - 1))
                sparkline += SPARKLINE_CHARS[idx]

            return sparkline

        except (ValueError, TypeError):
            return "░" * width

    def _get_top_values(self, series: pd.Series, n: int = 3) -> list[tuple[Any, int, float]]:
        """
        Get the top N most frequent values.

        Args:
            series: Pandas Series
            n: Number of top values to return

        Returns:
            List of (value, count, percentage) tuples
        """
        value_counts = series.value_counts().head(n)
        total = len(series)

        return [
            (value, count, count / total * 100 if total > 0 else 0)
            for value, count in value_counts.items()
        ]

    @staticmethod
    def format_stats_for_display(stats: TrackedVariableStats) -> list[str]:
        """
        Format statistics for display in a flowchart box.

        Args:
            stats: TrackedVariableStats object

        Returns:
            List of formatted strings for display
        """
        lines = []

        # Basic count info
        if stats.n_unique > 0:
            lines.append(f"{stats.name}: {stats.n_unique:,} unique")
        else:
            lines.append(f"{stats.name}: {stats.n_non_null:,} values")

        # Numeric stats
        if stats.mean_value is not None:
            mean_str = f"mean={stats.mean_value:.2f}"
            if stats.min_value is not None and stats.max_value is not None:
                mean_str += f" [{stats.min_value:.1f}, {stats.max_value:.1f}]"
            lines.append(mean_str)

        # Histogram
        if stats.histogram:
            lines.append(f"dist: {stats.histogram}")

        # Top values
        if stats.top_values:
            top_str = "top: " + ", ".join(f"{v}({p:.0f}%)" for v, _, p in stats.top_values[:3])
            if len(top_str) > 40:
                top_str = top_str[:37] + "..."
            lines.append(top_str)

        return lines


def generate_sparkline(values: list[float], width: int = 8) -> str:
    """
    Generate a sparkline from a list of values.

    Args:
        values: List of numeric values
        width: Desired width (will resample if needed)

    Returns:
        ASCII sparkline string
    """
    if not values:
        return "░" * width

    # Resample if needed
    if len(values) != width:
        # Simple resampling
        indices = np.linspace(0, len(values) - 1, width).astype(int)
        values = [values[i] for i in indices]

    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return SPARKLINE_CHARS[4] * width

    sparkline = ""
    for val in values:
        normalized = (val - min_val) / (max_val - min_val)
        idx = int(normalized * (len(SPARKLINE_CHARS) - 1))
        sparkline += SPARKLINE_CHARS[idx]

    return sparkline
