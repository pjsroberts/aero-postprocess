import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from pathlib import Path

from . import parsers

# Clean, professional style
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


def plot_convergence(
    df: pd.DataFrame,
    output: str | None = None,
    log_scale: bool = True,
    title: str = "Convergence History",
) -> plt.Figure:
    residual_cols = parsers.get_residual_columns(df)
    if not residual_cols:
        raise ValueError("No residual columns found in DataFrame")

    fig, ax = plt.subplots()

    colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea"]
    for i, col in enumerate(residual_cols):
        label = col.replace("_residual", "").replace("_", " ").title()
        ax.plot(df.index, df[col], label=label, color=colors[i % len(colors)])

    if log_scale:
        ax.set_yscale("log")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Residual")
    ax.set_title(title)
    ax.legend(loc="upper right", framealpha=0.9)

    if output:
        fig.savefig(output)
        print(f"  Saved: {output}")

    return fig


def plot_surface_cp(
    datasets: list[dict],
    output: str | None = None,
    title: str = "Surface Pressure Distribution",
) -> plt.Figure:
    default_colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"]
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, ds in enumerate(datasets):
        color = ds.get("color", default_colors[i % len(default_colors)])
        style = ds.get("style", "-")
        marker_styles = {"o": 4, "s": 3, "^": 4, "D": 3}

        if style in marker_styles:
            ax.plot(
                ds["df"][ds["x_col"]],
                ds["df"][ds["cp_col"]],
                style,
                color=color,
                markersize=marker_styles[style],
                label=ds["label"],
                alpha=0.8,
            )
        else:
            ax.plot(
                ds["df"][ds["x_col"]],
                ds["df"][ds["cp_col"]],
                style,
                color=color,
                linewidth=1.5,
                label=ds["label"],
            )

    ax.invert_yaxis()
    ax.set_xlabel("x/c")
    ax.set_ylabel("Cp")
    ax.set_title(title)
    ax.legend(framealpha=0.9)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

    if output:
        fig.savefig(output)
        print(f"  Saved: {output}")

    return fig


def plot_force_monitors(
    df: pd.DataFrame, output: str | None = None, title: str = "Force Monitor History"
) -> plt.Figure:
    monitor_cols = parsers.get_monitor_columns(df)
    if not monitor_cols:
        raise ValueError("No force/moment columns found in DataFrame")
    n = len(monitor_cols)
    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n), sharex=True)
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, monitor_cols):
        ax.plot(df.index, df[col], color="#2563eb", linewidth=1.5)
        label = col.replace("_", " ").title()
        ax.set_ylabel(label)
        ax.set_title(f"{label} vs Iteration")
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

    if output:
        fig.savefig(output)
        print(f"  Saved: {output}")
    return fig
