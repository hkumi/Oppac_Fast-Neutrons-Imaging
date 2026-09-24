"""
Converter thickness sweep analysis.

Same approach as analyze_collimator_sweep.py, but for the HDPE
converter thickness instead of collimator length. For a recoil-proton
converter, yield vs. thickness usually has a real peak: too thin and
few neutrons convert at all; too thick and protons produced deep in
the converter lose too much energy (or never escape) before reaching
the gas. This script helps you locate that peak for your specific
neutron energy (2.5 MeV) and geometry.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib

Run this from the directory containing your B4_conv_*um.root files.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import csv

# ---------------------------------------------------------------
# Edit if your filenames/thicknesses differ
# ---------------------------------------------------------------
THICKNESS_UM = [10, 50, 100, 200, 500, 1000]
FILES = [f"B4_conv_{t}um_v2.root" for t in THICKNESS_UM]
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


def run_sweep_analysis(thickness_um=THICKNESS_UM, files=FILES):
    results = []
    for thickness, fname in zip(thickness_um, files):
        try:
            entries, mean_x, mean_y, std_x, std_y = analyze_file(fname)
        except FileNotFoundError:
            print(f"WARNING: {fname} not found, skipping")
            continue

        results.append({
            "thickness_um": thickness,
            "entries": entries,
            "mean_x": mean_x,
            "mean_y": mean_y,
            "std_x": std_x,
            "std_y": std_y,
        })

        print(f"thickness={thickness:>5} um  entries={entries:>8.0f}  "
              f"mean=({mean_x:+.3f}, {mean_y:+.3f}) mm  "
              f"std=({std_x:.3f}, {std_y:.3f}) mm")

    return results


def save_csv(results, path="converter_sweep_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved table to {path}")


def plot_sweep(results, save_path="converter_sweep.png"):
    thickness = [r["thickness_um"] for r in results]
    entries = [r["entries"] for r in results]
    resolution = [(r["std_x"] + r["std_y"]) / 2 for r in results]
    entries_err = [np.sqrt(e) if e > 0 else 0 for e in entries]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    axes[0].errorbar(thickness, entries, yerr=entries_err, marker="o",
                      linestyle="-", color="firebrick", capsize=3)
    axes[0].set_xlabel("Converter thickness (um)")
    axes[0].set_ylabel("Valid reconstructed events")
    axes[0].set_title("Yield vs converter thickness")
    axes[0].grid(alpha=0.3)

    axes[1].plot(thickness, resolution, marker="o", linestyle="-")
    axes[1].set_xlabel("Converter thickness (um)")
    axes[1].set_ylabel("Spatial resolution, avg(std x, std y) (mm)")
    axes[1].set_title("Resolution vs converter thickness")
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
        print("No files found - check THICKNESS_UM/FILES paths at the top of this script.")
