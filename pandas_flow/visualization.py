"""
Visualization utilities for pandas_flow.

Contains helpers for generating ASCII art, sparklines,
and other visual elements.
"""

from collections.abc import Sequence

import numpy as np

# Box drawing characters
BOX_CHARS = {
    "horizontal": "─",
    "vertical": "│",
    "top_left": "┌",
    "top_right": "┐",
    "bottom_left": "└",
    "bottom_right": "┘",
    "t_down": "┬",
    "t_up": "┴",
    "t_right": "├",
    "t_left": "┤",
    "cross": "┼",
}

# Sparkline characters (8 levels)
SPARK_CHARS = "▁▂▃▄▅▆▇█"

# Bar chart characters
BAR_CHARS = {
    "full": "█",
    "seven_eighths": "▉",
    "three_quarters": "▊",
    "five_eighths": "▋",
    "half": "▌",
    "three_eighths": "▍",
    "quarter": "▎",
    "eighth": "▏",
    "empty": " ",
}

# Progress/percentage characters
PROGRESS_CHARS = ["░", "▒", "▓", "█"]


def sparkline(
    values: Sequence[float],
    width: int | None = None,
    min_val: float | None = None,
    max_val: float | None = None,
) -> str:
    """
    Generate an ASCII sparkline from numeric values.

    Args:
        values: Sequence of numeric values
        width: Target width (resamples if different from len(values))
        min_val: Minimum value for scaling (auto if None)
        max_val: Maximum value for scaling (auto if None)

    Returns:
        String of sparkline characters
    """
    if not values:
        return ""

    values = list(values)

    # Resample if needed
    if width is not None and width != len(values):
        values = _resample(values, width)

    # Get bounds
    if min_val is None:
        min_val = min(values)
    if max_val is None:
        max_val = max(values)

    # Handle constant values
    if max_val == min_val:
        return SPARK_CHARS[4] * len(values)

    # Generate sparkline
    result = ""
    for val in values:
        # Clamp value
        val = max(min_val, min(max_val, val))
        # Normalize to [0, 1]
        normalized = (val - min_val) / (max_val - min_val)
        # Map to character index
        idx = int(normalized * (len(SPARK_CHARS) - 1))
        result += SPARK_CHARS[idx]

    return result


def horizontal_bar(
    value: float,
    max_value: float,
    width: int = 10,
    show_percentage: bool = False,
) -> str:
    """
    Generate a horizontal bar chart element.

    Args:
        value: Current value
        max_value: Maximum value (for scaling)
        width: Total width in characters
        show_percentage: Whether to append percentage

    Returns:
        ASCII bar string
    """
    if max_value <= 0:
        return BAR_CHARS["empty"] * width

    ratio = min(1.0, value / max_value)
    filled = int(ratio * width)

    bar = BAR_CHARS["full"] * filled + BAR_CHARS["empty"] * (width - filled)

    if show_percentage:
        bar += f" {ratio * 100:.0f}%"

    return bar


def vertical_bars(
    values: Sequence[float],
    height: int = 5,
    width: int | None = None,
) -> list[str]:
    """
    Generate vertical bar chart as list of strings (rows).

    Args:
        values: Sequence of values
        height: Number of rows
        width: If provided, resample values to this width

    Returns:
        List of strings, top to bottom
    """
    if not values:
        return [""] * height

    values = list(values)
    if width is not None and width != len(values):
        values = _resample(values, width)

    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        # All same value - half height bars
        mid_height = height // 2
        rows = []
        for row in range(height):
            if row >= height - mid_height:
                rows.append("█" * len(values))
            else:
                rows.append(" " * len(values))
        return rows

    rows = []
    for row in range(height):
        threshold = (height - row - 1) / (height - 1)
        line = ""
        for val in values:
            normalized = (val - min_val) / (max_val - min_val)
            if normalized >= threshold:
                line += "█"
            elif normalized >= threshold - 0.125:
                line += "▄"
            else:
                line += " "
        rows.append(line)

    return rows


def progress_bar(
    current: int,
    total: int,
    width: int = 20,
    show_count: bool = True,
) -> str:
    """
    Generate a progress bar.

    Args:
        current: Current count
        total: Total count
        width: Bar width in characters
        show_count: Whether to show count after bar

    Returns:
        Progress bar string
    """
    ratio = 0 if total <= 0 else min(1.0, current / total)

    filled = int(ratio * width)
    empty = width - filled

    bar = f"[{'█' * filled}{'░' * empty}]"

    if show_count:
        bar += f" {current:,}/{total:,}"

    return bar


def text_box(
    lines: Sequence[str],
    title: str | None = None,
    width: int | None = None,
    padding: int = 1,
) -> list[str]:
    """
    Draw a text box around content.

    Args:
        lines: Content lines
        title: Optional title for the box
        width: Fixed width (auto if None)
        padding: Horizontal padding inside box

    Returns:
        List of strings forming the box
    """
    if width is None:
        content_widths = [len(line) for line in lines]
        if title:
            content_widths.append(len(title) + 4)
        width = max(content_widths) + padding * 2 + 2 if content_widths else padding * 2 + 2

    inner_width = width - 2
    result = []

    # Top border
    if title:
        title_part = f" {title} "
        remaining = inner_width - len(title_part)
        left_border = remaining // 2
        right_border = remaining - left_border
        top = (
            BOX_CHARS["top_left"]
            + BOX_CHARS["horizontal"] * left_border
            + title_part
            + BOX_CHARS["horizontal"] * right_border
            + BOX_CHARS["top_right"]
        )
    else:
        top = BOX_CHARS["top_left"] + BOX_CHARS["horizontal"] * inner_width + BOX_CHARS["top_right"]
    result.append(top)

    # Content lines
    for line in lines:
        padded = line.ljust(inner_width - padding * 2)
        result.append(
            BOX_CHARS["vertical"] + " " * padding + padded + " " * padding + BOX_CHARS["vertical"]
        )

    # Bottom border
    bottom = (
        BOX_CHARS["bottom_left"] + BOX_CHARS["horizontal"] * inner_width + BOX_CHARS["bottom_right"]
    )
    result.append(bottom)

    return result


def format_number(value: float | int, precision: int = 2) -> str:
    """
    Format a number for display with appropriate precision.

    Args:
        value: Number to format
        precision: Decimal places for floats

    Returns:
        Formatted string
    """
    if isinstance(value, int):
        return f"{value:,}"
    elif abs(value) >= 1000:
        return f"{value:,.0f}"
    elif abs(value) >= 1:
        return f"{value:,.{precision}f}"
    else:
        return f"{value:.{precision}g}"


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def _resample(values: list[float], target_size: int) -> list[float]:
    """Resample a list of values to a target size."""
    if len(values) == target_size:
        return values

    indices = np.linspace(0, len(values) - 1, target_size)
    return [values[int(i)] for i in indices]
