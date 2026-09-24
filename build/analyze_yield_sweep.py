"""
Scintillation yield sweep analysis.

Tests Jan's hypothesis directly: if the old value (2.5e6 photons/MeV,
borrowed from an alpha-particle/pure-CF4 estimate) was simply
statistics-starved, resolution should keep improving as yield increases
and then flatten out (saturate) once there's "enough" light per event -
telling you whether the corrected value (35.73e6) is already past that
saturation point, right at it, or if even more would help further.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import csv

YIELD_VALUES = [2_500_000, 5_000_000, 10_000_000, 20_000_000, 35_730_000, 50_000_000]
LABELS = ["2p5e6", "5e6", "10e6", "20e6", "35p73e6", "50e6"]
FILES = [f"B4_yield_{lab}.root" for lab in LABELS]
HIST_NAME = "ReconstructedImage"


def analyze_file(path, hist_name=HIST_NAME):
    with uproot.open(path) as f:
        h = f[hist_name]
        values, xedges, yedges = h.to_numpy()

    entries = float(values.sum())
    if entries <= 0:
        return entries, np.nan, np.nan, np.nan, np.nan

    xcenters = 0.5 * (xedges[:-1] + xedges[1:])
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])
    X, Y = np.meshgrid(xcenters, ycenters, indexing="ij")

    mean_x = np.sum(X * values) / entries
    mean_y = np.sum(Y * values) / entries
    std_x = np.sqrt(np.sum(values * (X - mean_x) ** 2) / entries)
    std_y = np.sqrt(np.sum(values * (Y - mean_y) ** 2) / entries)

    return entries, mean_x, mean_y, std_x, std_y


def run_sweep_analysis(yield_values=YIELD_VALUES, files=FILES):
    results = []
    for yld, fname in zip(yield_values, files):
        try:
            entries, mean_x, mean_y, std_x, std_y = analyze_file(fname)
        except FileNotFoundError:
            print(f"WARNING: {fname} not found, skipping yield={yld}")
            continue

        results.append({
            "yield_photons_per_MeV": yld,
            "entries": entries,
            "mean_x": mean_x,
            "mean_y": mean_y,
            "std_x": std_x,
            "std_y": std_y,
        })

        print(f"yield={yld:>12,}/MeV  entries={entries:>7.0f}  "
              f"mean=({mean_x:+.3f}, {mean_y:+.3f}) mm  "
              f"std=({std_x:.3f}, {std_y:.3f}) mm")

    return results


def save_csv(results, path="yield_sweep_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved table to {path}")


def plot_sweep(results, save_path="yield_sweep.png"):
    yields = [r["yield_photons_per_MeV"] for r in results]
    entries = [r["entries"] for r in results]
    resolution = [(r["std_x"] + r["std_y"]) / 2 for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    axes[0].plot(yields, resolution, marker="o", linestyle="-", color="steelblue")
    axes[0].axvline(2_500_000, color="gray", linestyle="--", alpha=0.5, label="old (alpha/pure-CF4)")
    axes[0].axvline(35_730_000, color="darkorange", linestyle="--", alpha=0.5, label="corrected (proton/Ar:CF4)")
    axes[0].set_xlabel("Scintillation yield (photons/MeV)")
    axes[0].set_ylabel("Resolution, avg(std x, std y) (mm)")
    axes[0].set_title("Resolution vs scintillation yield")
    axes[0].set_xscale("log")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[1].plot(yields, entries, marker="o", linestyle="-", color="firebrick")
    axes[1].set_xlabel("Scintillation yield (photons/MeV)")
    axes[1].set_ylabel("Valid reconstructed events")
    axes[1].set_title("Yield-of-events vs scintillation yield")
    axes[1].set_xscale("log")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Saved plot to {save_path}")
    plt.show()


if __name__ == "__main__":
    results = run_sweep_analysis()
    if results:
        save_csv(results)
        plot_sweep(results)
    else:
        print("No files found - check YIELD_VALUES/LABELS/FILES at the top of this script.")
