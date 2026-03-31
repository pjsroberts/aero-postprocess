import pandas as pd
import numpy as np
from pathlib import Path


def read_convergence(filepath: str, delimiter: str = ",") -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"No file found at {path}")

    df = pd.read_csv(path, delimiter=delimiter, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Auto-detect iteration column
    iter_cols = [
        c for c in df.columns if c.lower() in ("iteration", "iter", "step", "timestep")
    ]
    if iter_cols:
        df = df.set_index(iter_cols[0])

    return df


def read_surface_data(filepath: str, zone: int = 0) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"No file found at {path}")

    with open(path, "r") as f:
        lines = f.readlines()

    # Extract column names from variables= line
    col_names = None
    for line in lines:
        stripped = line.strip().lower()
        if stripped.startswith("variables"):
            parts = stripped.split("=", 1)[1]
            col_names = [c.strip().strip('"').strip("'") for c in parts.split(",")]
            break
    zones: list[list[str]] = []
    current_zone: list[str] = []

    for line in lines:
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith("#")
            or stripped.lower().startswith("variables")
        ):
            continue
        if stripped.lower().startswith("zone"):
            if current_zone:
                zones.append(current_zone)
            current_zone = []
            continue
        current_zone.append(stripped)

    if current_zone:
        zones.append(current_zone)

    if zone >= len(zones):
        raise IndexError(
            f"Requested zone {zone}, but file only has {len(zones)} zone(s)"
        )

    data = []
    for line in zones[zone]:
        try:
            values = [float(v) for v in line.split()]
            data.append(values)
        except ValueError:
            continue

    df = pd.DataFrame(data, columns=col_names if col_names else None)
    return df


def read_force_report(filepath: str) -> dict:
    results = {}
    path = Path(filepath)

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip().lower().replace(" ", "_")
                try:
                    results[key] = float(value.strip())
                except ValueError:
                    results[key] = value.strip()

    return results


def get_residual_columns(df: pd.DataFrame) -> list[str]:
    keywords = ("residual", "res_", "rms", "error")
    return [c for c in df.columns if any(k in c.lower() for k in keywords)]


def get_monitor_columns(df: pd.DataFrame) -> list[str]:
    keywords = ("cl", "cd", "cm", "lift", "drag", "moment", "force")
    residual_cols = set(get_residual_columns(df))
    return [
        c
        for c in df.columns
        if any(k in c.lower() for k in keywords) and c not in residual_cols
    ]


def list_zones(filepath: str) -> list[str]:
    path = Path(filepath)
    zone_names = []

    with open(path, "r") as f:
        for line in f:
            stripped = line.strip()
            if stripped.lower().startswith("zone"):
                # Extract t="..." if present
                if 't="' in stripped.lower():
                    start = stripped.lower().index('t="') + 3
                    end = stripped.index('"', start)
                    zone_names.append(stripped[start:end])
                else:
                    zone_names.append(f"zone_{len(zone_names)}")

    return zone_names
