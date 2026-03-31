import matplotlib.pyplot as plt
from pathlib import Path
from src.parsers import read_convergence, read_surface_data
from src.plots import plot_convergence, plot_surface_cp, plot_force_monitors

OUTPUT_DIR = Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)

print("Generating Cp validation plot...")

cfd = read_surface_data("examples/data/n0012cp_cfl3d_sa.dat", zone=0)
gregory = read_surface_data("examples/data/CP_Gregory_expdata.dat", zone=0)
ladson = read_surface_data("examples/data/CP_Ladson.dat", zone=0)

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

print("Generating convergence plot...")
conv = read_convergence("examples/data/sample_convergence.csv")
plot_convergence(conv, output=str(OUTPUT_DIR / "convergence.png"))

print("Generating force monitor plot...")
plot_force_monitors(conv, output=str(OUTPUT_DIR / "force_monitors.png"))

plt.close("all")
print(f"\nDone. All plots saved to {OUTPUT_DIR}/")
