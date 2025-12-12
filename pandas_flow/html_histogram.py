"""
HTML histogram generation module for pandas_flow.

Provides minimalist image-based histograms using matplotlib
for embedding directly in Mermaid node labels (HTML mode).
"""

from __future__ import annotations

import base64
import io

import numpy as np
import pandas as pd

# Try to import visualization libraries
try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def check_visualization_support() -> dict[str, bool]:
    """Check which visualization libraries are available."""
    return {
        "matplotlib": HAS_MATPLOTLIB,
    }


def generate_mini_histogram(
    data: pd.Series | np.ndarray | list,
    width: float = 1.2,
    height: float = 0.5,
    color: str = "#3498db",
    bins: int = 15,
) -> str | None:
    """
    Generate a minimalist histogram as a base64-encoded PNG.

    Style: Line plot with filled area below, minimal x-axis, very compact.
    Designed to fit inside Mermaid node labels.

    Args:
        data: Numeric data to plot
        width: Figure width in inches (small for inline display)
        height: Figure height in inches (small for inline display)
        color: Fill color
        bins: Number of bins

    Returns:
        Base64-encoded PNG string, or None if not available
    """
    if not HAS_MATPLOTLIB:
        return None

    # Clean data
    if isinstance(data, pd.Series):
        clean_data = data.dropna().values
    elif isinstance(data, list):
        clean_data = np.array([x for x in data if x is not None and not np.isnan(x)])
    else:
        clean_data = data[~np.isnan(data)]

    if len(clean_data) == 0:
        return None

    # Calculate histogram
    counts, bin_edges = np.histogram(clean_data, bins=bins)

    # Get bin centers for line plot
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Create figure with transparent background
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Plot as filled area (line with shadow below)
    ax.fill_between(bin_centers, counts, alpha=0.3, color=color)
    ax.plot(bin_centers, counts, color=color, linewidth=1.5)

    # Minimal styling - show only x-axis with min/max labels
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_visible(False)

    # Format x-axis ticks to show only min and max values
    x_min, x_max = clean_data.min(), clean_data.max()
    ax.set_xticks([x_min, x_max])
    ax.set_xticklabels([f"{x_min:.0f}", f"{x_max:.0f}"], fontsize=6, color="#666666")
    ax.tick_params(axis="x", length=2, pad=1, colors="#999999")
    ax.spines["bottom"].set_color("#999999")
    ax.spines["bottom"].set_linewidth(0.5)

    # Tight layout with space for x-axis
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.25)

    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=80,
        bbox_inches="tight",
        pad_inches=0.02,
        transparent=True,
    )
    buf.seek(0)
    base64_str = base64.b64encode(buf.read()).decode("utf-8")

    plt.close(fig)

    return base64_str


def generate_mini_scatter(
    x_data: pd.Series | np.ndarray | list,
    y_data: pd.Series | np.ndarray | list,
    width: float = 1.2,
    height: float = 0.8,
    color: str = "#3498db",
    point_size: int = 8,
) -> str | None:
    """
    Generate a minimalist scatter plot as a base64-encoded PNG.

    Style: Simple scatter with blue dots, no axes, very compact.
    Designed to fit inside Mermaid node labels.

    Args:
        x_data: X-axis data
        y_data: Y-axis data
        width: Figure width in inches
        height: Figure height in inches
        color: Point color (same blue as histogram)
        point_size: Size of scatter points

    Returns:
        Base64-encoded PNG string, or None if not available
    """
    if not HAS_MATPLOTLIB:
        return None

    # Clean data
    def clean(data: pd.Series | np.ndarray | list) -> np.ndarray:
        if isinstance(data, pd.Series):
            return data.dropna().values
        elif isinstance(data, list):
            return np.array([x for x in data if x is not None and not np.isnan(x)])
        else:
            return data[~np.isnan(data)]

    x_clean = clean(x_data)
    y_clean = clean(y_data)

    # Ensure same length
    min_len = min(len(x_clean), len(y_clean))
    if min_len < 3:
        return None

    x_clean = x_clean[:min_len]
    y_clean = y_clean[:min_len]

    # Create figure with transparent background
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Plot scatter with blue dots
    ax.scatter(x_clean, y_clean, c=color, s=point_size, alpha=0.6, edgecolors="none")

    # Remove all axes, spines, ticks
    ax.set_axis_off()

    # Tight layout
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=80,
        bbox_inches="tight",
        pad_inches=0.02,
        transparent=True,
    )
    buf.seek(0)
    base64_str = base64.b64encode(buf.read()).decode("utf-8")

    plt.close(fig)

    return base64_str


# Keep backward compatibility alias
def generate_mini_hexbin(
    x_data: pd.Series | np.ndarray | list,
    y_data: pd.Series | np.ndarray | list,
    **kwargs,
) -> str | None:
    """Backward compatibility alias for generate_mini_scatter."""
    return generate_mini_scatter(x_data, y_data, **kwargs)


def generate_histogram_img_tag(
    data: pd.Series | np.ndarray | list,
    alt_text: str = "histogram",
    width_px: int = 80,
    height_px: int = 25,
    **kwargs,
) -> str:
    """
    Generate an HTML img tag with embedded mini histogram.

    Designed for inline display in Mermaid node labels.

    Args:
        data: Numeric data to plot
        alt_text: Alt text for the image
        width_px: Display width in pixels
        height_px: Display height in pixels
        **kwargs: Arguments passed to generate_mini_histogram

    Returns:
        HTML img tag string, or empty string if not available
    """
    base64_str = generate_mini_histogram(data, **kwargs)

    if base64_str:
        return (
            f'<img src="data:image/png;base64,{base64_str}" '
            f'alt="{alt_text}" '
            f'style="width:{width_px}px;height:{height_px}px;vertical-align:middle;" />'
        )

    return ""


def generate_hexbin_img_tag(
    x_data: pd.Series | np.ndarray | list,
    y_data: pd.Series | np.ndarray | list,
    alt_text: str = "scatter",
    width_px: int = 80,
    height_px: int = 50,
    **kwargs,
) -> str:
    """
    Generate an HTML img tag with embedded mini hexbin scatter.

    Designed for inline display in Mermaid node labels.

    Args:
        x_data: X-axis data
        y_data: Y-axis data
        alt_text: Alt text for the image
        width_px: Display width in pixels
        height_px: Display height in pixels
        **kwargs: Arguments passed to generate_mini_hexbin

    Returns:
        HTML img tag string, or empty string if not available
    """
    base64_str = generate_mini_hexbin(x_data, y_data, **kwargs)

    if base64_str:
        return (
            f'<img src="data:image/png;base64,{base64_str}" '
            f'alt="{alt_text}" '
            f'style="width:{width_px}px;height:{height_px}px;vertical-align:middle;" />'
        )

    return ""


# Keep backward compatibility functions
def generate_histogram_base64(
    data: pd.Series | np.ndarray | list,
    width: float = 3,
    height: float = 1.5,
    color: str = "#3498db",
    bins: int = 20,
    use_kde: bool = False,  # Ignored, kept for compatibility
) -> str | None:
    """
    Generate a histogram as a base64-encoded PNG image.

    This is the larger version for standalone display.

    Args:
        data: Numeric data to plot
        width: Figure width in inches
        height: Figure height in inches
        color: Fill color
        bins: Number of bins
        use_kde: Ignored (kept for compatibility)

    Returns:
        Base64-encoded PNG string, or None if not available
    """
    if not HAS_MATPLOTLIB:
        return None

    # Clean data
    if isinstance(data, pd.Series):
        clean_data = data.dropna().values
    elif isinstance(data, list):
        clean_data = np.array([x for x in data if x is not None and not np.isnan(x)])
    else:
        clean_data = data[~np.isnan(data)]

    if len(clean_data) == 0:
        return None

    # Calculate histogram
    counts, bin_edges = np.histogram(clean_data, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Create figure
    fig, ax = plt.subplots(figsize=(width, height))

    # Plot as filled area with line
    ax.fill_between(bin_centers, counts, alpha=0.3, color=color)
    ax.plot(bin_centers, counts, color=color, linewidth=2)

    # Minimal styling - only show x-axis
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_visible(False)
    ax.tick_params(axis="x", which="both", labelsize=8)
    ax.set_xlabel("")

    plt.tight_layout()

    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=100, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    buf.seek(0)
    base64_str = base64.b64encode(buf.read()).decode("utf-8")

    plt.close(fig)

    return base64_str


def generate_histogram_html(
    data: pd.Series | np.ndarray | list,
    alt_text: str = "histogram",
    **kwargs,
) -> str:
    """
    Generate an HTML img tag with embedded histogram (larger version).

    Args:
        data: Numeric data to plot
        alt_text: Alt text for the image
        **kwargs: Arguments passed to generate_histogram_base64

    Returns:
        HTML img tag string, or empty string if not available
    """
    base64_str = generate_histogram_base64(data, **kwargs)

    if base64_str:
        return (
            f'<img src="data:image/png;base64,{base64_str}" '
            f'alt="{alt_text}" style="max-width:100%;border-radius:4px;" />'
        )

    return ""


def generate_stats_card_html(
    name: str,
    data: pd.Series | np.ndarray | list,
    color: str = "#3498db",
) -> str:
    """
    Generate an HTML card with statistics and histogram.

    Args:
        name: Variable name
        data: Numeric data
        color: Theme color

    Returns:
        HTML string for the stats card
    """
    clean_data = data.dropna() if isinstance(data, pd.Series) else pd.Series(data).dropna()

    if len(clean_data) == 0:
        return ""

    # Calculate statistics
    stats = {
        "count": len(clean_data),
        "mean": clean_data.mean(),
        "std": clean_data.std(),
        "min": clean_data.min(),
        "max": clean_data.max(),
        "median": clean_data.median(),
    }

    # Generate histogram
    hist_html = generate_histogram_html(clean_data, alt_text=f"{name} distribution", color=color)

    return f"""
    <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:12px;margin:8px 0;">
        <div style="font-weight:bold;color:{color};margin-bottom:8px;">📊 {name}</div>
        {hist_html}
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px;font-size:11px;">
            <div style="text-align:center;">
                <div style="color:{color};font-weight:bold;">{stats["mean"]:.2f}</div>
                <div style="opacity:0.7;">Mean</div>
            </div>
            <div style="text-align:center;">
                <div style="color:{color};font-weight:bold;">{stats["std"]:.2f}</div>
                <div style="opacity:0.7;">Std</div>
            </div>
            <div style="text-align:center;">
                <div style="color:{color};font-weight:bold;">{stats["min"]:.1f} - {stats["max"]:.1f}</div>
                <div style="opacity:0.7;">Range</div>
            </div>
        </div>
    </div>
    """
