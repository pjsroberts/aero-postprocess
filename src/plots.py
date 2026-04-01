"""
aero-postprocess.plots
~~~~~~~~~~~~~~~~~~~~~~

Publication-quality engineering plots for CFD/FEA post-processing.
Generates convergence histories, surface pressure distributions,
and force/moment monitor plots from parsed simulation data.

All plots use a consistent visual style suitable for technical
reports, conference papers, and client deliverables.

Usage:
    >>> from src.parsers import read_convergence, read_surface_data
    >>> from src.plots import plot_convergence, plot_surface_cp
    >>>
    >>> conv = read_convergence("convergence.csv")
    >>> plot_convergence(conv, output="convergence.png")
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from pathlib import Path

from . import parsers


# ---------------------------------------------------------------------------
# Global style configuration
# ---------------------------------------------------------------------------

plt.style.use("seaborn-v0_8-whitegrid")
mpl.rcParams.update(
    {
        "figure.figsize": (10, 6),
        "figure.dpi": 150,
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "lines.linewidth": 1.5,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
    }
)

# Colour palette — accessible, visually distinct, print-safe
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"]


# ---------------------------------------------------------------------------
# Convergence plots
# ---------------------------------------------------------------------------


def plot_convergence(
    df: pd.DataFrame,
    output: str | None = None,
    log_scale: bool = True,
    title: str = "Convergence History",
) -> plt.Figure:
    """Plot residual convergence history.

    Automatically identifies residual columns via
    :func:`parsers.get_residual_columns` and plots each on a shared
    axis with a logarithmic y-scale.

    Args:
        df:        DataFrame from :func:`parsers.read_convergence`.
        output:    File path to save the figure. If ``None``, the figure
                   is returned without saving.
        log_scale: Use logarithmic y-axis. Defaults to ``True``.
        title:     Plot title string.

    Returns:
        The generated :class:`matplotlib.figure.Figure`.

    Raises:
        ValueError: If no residual columns are found in *df*.

    Example:
        >>> conv = read_convergence("convergence.csv")
        >>> fig = plot_convergence(conv, output="convergence.png")
    """
    residual_cols = parsers.get_residual_columns(df)
    if not residual_cols:
        raise ValueError("No residual columns found in DataFrame")

    fig, ax = plt.subplots()

    for i, col in enumerate(residual_cols):
        label = col.replace("_residual", "").replace("_", " ").title()
        ax.plot(df.index, df[col], label=label, color=COLORS[i % len(COLORS)])

    if log_scale:
        ax.set_yscale("log")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Residual")
    ax.set_title(title)
    ax.legend(loc="upper right", framealpha=0.9)

    _save(fig, output)
    return fig


# ---------------------------------------------------------------------------
# Surface pressure distribution
# ---------------------------------------------------------------------------


def plot_surface_cp(
    datasets: list[dict],
    output: str | None = None,
    title: str = "Surface Pressure Distribution",
) -> plt.Figure:
    """Plot Cp distributions with multiple datasets overlaid.

    Designed for CFD-vs-experiment validation plots. Each dataset
    can use a different marker or line style and colour.

    Args:
        datasets: List of dictionaries, each containing:

            - ``"df"``     — DataFrame with x-position and Cp columns.
            - ``"x_col"``  — Column name for x-position (e.g. ``"x/c"``).
            - ``"cp_col"`` — Column name for Cp (e.g. ``"cp"``).
            - ``"label"``  — Legend label string.
            - ``"style"``  — Matplotlib line/marker style (``"-"``, ``"o"``, etc.).
            - ``"color"``  — *(optional)* Hex colour string.

        output: File path to save the figure.
        title:  Plot title string.

    Returns:
        The generated :class:`matplotlib.figure.Figure`.

    Example:
        >>> plot_surface_cp([
        ...     {"df": cfd, "x_col": "x", "cp_col": "cp",
        ...      "label": "CFD", "style": "-"},
        ...     {"df": exp, "x_col": "x/c", "cp_col": "cp",
        ...      "label": "Experiment", "style": "o"},
        ... ], output="cp_validation.png")
    """
    # Marker style → point size mapping
    marker_sizes = {"o": 4, "s": 3, "^": 4, "D": 3}

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, ds in enumerate(datasets):
        color = ds.get("color", COLORS[i % len(COLORS)])
        style = ds.get("style", "-")
        x = ds["df"][ds["x_col"]]
        y = ds["df"][ds["cp_col"]]

        if style in marker_sizes:
            ax.plot(
                x,
                y,
                style,
                color=color,
                markersize=marker_sizes[style],
                label=ds["label"],
                alpha=0.8,
            )
        else:
            ax.plot(
                x,
                y,
                style,
                color=color,
                linewidth=1.5,
                label=ds["label"],
            )

    ax.invert_yaxis()  # Aerodynamic convention: negative Cp up
    ax.set_xlabel("x/c")
    ax.set_ylabel("Cp")
    ax.set_title(title)
    ax.legend(framealpha=0.9)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

    _save(fig, output)
    return fig


# ---------------------------------------------------------------------------
# Force / moment monitors
# ---------------------------------------------------------------------------


def plot_force_monitors(
    df: pd.DataFrame,
    output: str | None = None,
    title: str = "Force Monitor History",
) -> plt.Figure:
    """Plot force and moment coefficient convergence.

    Creates a vertically stacked subplot for each monitor column
    (Cl, Cd, Cm, etc.) with a dashed line marking the final
    converged value.

    Args:
        df:     DataFrame from :func:`parsers.read_convergence`.
        output: File path to save the figure.
        title:  Overall figure title.

    Returns:
        The generated :class:`matplotlib.figure.Figure`.

    Raises:
        ValueError: If no monitor columns are found in *df*.

    Example:
        >>> conv = read_convergence("convergence.csv")
        >>> fig = plot_force_monitors(conv, output="force_monitors.png")
    """
    monitor_cols = parsers.get_monitor_columns(df)
    if not monitor_cols:
        raise ValueError("No force/moment columns found in DataFrame")

    n = len(monitor_cols)
    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, monitor_cols):
        ax.plot(df.index, df[col], color=COLORS[0], linewidth=1.5)

        label = col.replace("_", " ").title()
        ax.set_ylabel(label)
        ax.set_title(f"{label} vs Iteration")

        # Annotate the final converged value
        final = df[col].iloc[-1]
        ax.axhline(y=final, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.annotate(
            f"{final:.4f}",
            xy=(df.index[-1], final),
            fontsize=10,
            color="gray",
            ha="right",
            va="bottom",
        )

    axes[-1].set_xlabel("Iteration")
    fig.suptitle(title, y=1.02, fontsize=14)
    fig.tight_layout()

    _save(fig, output)
    return fig


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _save(fig: plt.Figure, output: str | None) -> None:
    """Save a figure to disk if an output path is provided.

    Creates parent directories automatically.

    Args:
        fig:    The figure to save.
        output: Destination file path, or ``None`` to skip saving.
    """
    if output is None:
        return

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    print(f"  Saved: {path}")
