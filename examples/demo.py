"""
aero-postprocess demo
~~~~~~~~~~~~~~~~~~~~~

Generates all portfolio plots from NASA Turbulence Modeling Resource
validation data. Produces three figures:

    1. **Cp validation** — CFL3D (SA model) vs Gregory and Ladson
       experimental data for the NACA 0012 at α = 0°.
    2. **Convergence history** — residual decay over solver iterations.
    3. **Force monitors** — Cl and Cd convergence to steady state.

Usage:
    PYTHONPATH=. python examples/demo.py

Output:
    images/cp_validation.png
    images/convergence.png
    images/force_monitors.png
"""

import matplotlib.pyplot as plt
from pathlib import Path

from src.parsers import read_convergence, read_surface_data
from src.plots import plot_convergence, plot_surface_cp, plot_force_monitors


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("images")

DATA_DIR = Path("examples/data")

# NASA TMR data files (NACA 0012, α = 0°)
CFL3D_FILE = DATA_DIR / "n0012cp_cfl3d_sa.dat"
GREGORY_FILE = DATA_DIR / "CP_Gregory_expdata.dat"
LADSON_FILE = DATA_DIR / "CP_Ladson.dat"

# Solver convergence sample
CONVERGENCE_FILE = DATA_DIR / "sample_convergence.csv"


# ---------------------------------------------------------------------------
# Plot generation
# ---------------------------------------------------------------------------


def generate_cp_validation() -> None:
    """CFD vs experiment surface pressure comparison.

    Overlays the CFL3D SA-model solution against two independent
    experimental datasets to demonstrate validation workflow.
    """
    print("Generating Cp validation plot...")

    cfd = read_surface_data(str(CFL3D_FILE), zone=0)
    gregory = read_surface_data(str(GREGORY_FILE), zone=0)
    ladson = read_surface_data(str(LADSON_FILE), zone=0)

    plot_surface_cp(
        datasets=[
            {
                "df": cfd,
                "x_col": "x",
                "cp_col": "cp",
                "label": "CFL3D (SA model)",
                "style": "-",
                "color": "#2563eb",
            },
            {
                "df": gregory,
                "x_col": "x/c",
                "cp_col": "cp",
                "label": "Gregory (exp.)",
                "style": "o",
                "color": "#dc2626",
            },
            {
                "df": ladson,
                "x_col": "x/c",
                "cp_col": "cp",
                "label": "Ladson (exp.)",
                "style": "s",
                "color": "#16a34a",
            },
        ],
        output=str(OUTPUT_DIR / "cp_validation.png"),
        title="NACA 0012 Surface Pressure — CFD vs Experiment, α = 0°",
    )


def generate_convergence() -> None:
    """Residual convergence history from sample solver output."""
    print("Generating convergence plot...")
    conv = read_convergence(str(CONVERGENCE_FILE))
    plot_convergence(conv, output=str(OUTPUT_DIR / "convergence.png"))


def generate_force_monitors() -> None:
    """Force coefficient convergence (Cl, Cd) to steady state."""
    print("Generating force monitor plot...")
    conv = read_convergence(str(CONVERGENCE_FILE))
    plot_force_monitors(conv, output=str(OUTPUT_DIR / "force_monitors.png"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate all demo plots and save to the images directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    generate_cp_validation()
    generate_convergence()
    generate_force_monitors()

    plt.close("all")
    print(f"\nDone. All plots saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
