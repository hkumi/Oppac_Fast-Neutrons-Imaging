"""
Off-axis position sweep analysis (low reflectivity setting).

Reads the ReconstructedImage 2D histogram from each position-sweep file
and plots:
  1. Reconstructed X vs. true X (linearity check) - a perfect detector
     would fall exactly on the y=x line. Deviation from that line at
     each point is the Integral Non-Linearity (INL), same idea as
     Figure 7 in Cortesi, Ayyad & Yurkon, 2018 JINST 13 P10006.
  2. Resolution (std dev of reconstructed x) vs. true position -
     checks whether resolution stays uniform across the detector face
     or degrades near the edges, same idea as Figure 6b in the paper.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib

Run this from the directory containing your B4_x*mm_lowrefl.root files.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import csv

# ---------------------------------------------------------------
# True beam positions and matching filenames
# ---------------------------------------------------------------
TRUE_X_MM = [-40, -30, -20, -10, 0, 10, 20, 30, 40]
LABELS    = ["m40", "m30", "m20", "m10", "0", "10", "20", "30", "40"]
FILES = [f"B4_x{lab}mm_lowrefl.root" for lab in LABELS]
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


def run_sweep_analysis(true_x=TRUE_X_MM, files=FILES):
    results = []
    for tx, fname in zip(true_x, files):
        try:
            entries, mean_x, mean_y, std_x, std_y = analyze_file(fname)
        except FileNotFoundError:
            print(f"WARNING: {fname} not found, skipping true_x={tx}mm")
            continue

        inl = mean_x - tx  # deviation from perfect linearity
        results.append({
            "true_x_mm": tx,
            "entries": entries,
            "mean_x": mean_x,
            "mean_y": mean_y,
            "std_x": std_x,
            "std_y": std_y,
            "inl_mm": inl,
        })

        print(f"true_x={tx:>4}mm  entries={entries:>6.0f}  "
              f"mean_x={mean_x:+7.3f}mm  INL={inl:+6.3f}mm  "
              f"std_x={std_x:.3f}mm  std_y={std_y:.3f}mm")

    return results


def save_csv(results, path="position_sweep_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved table to {path}")


def plot_sweep(results, save_path="position_sweep.png"):
    true_x = [r["true_x_mm"] for r in results]
    mean_x = [r["mean_x"] for r in results]
    std_x = [r["std_x"] for r in results]
    inl = [r["inl_mm"] for r in results]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

    # Panel 1: linearity (reconstructed vs true)
    axes[0].plot([-50, 50], [-50, 50], "k--", alpha=0.4, label="perfect (y=x)")
    axes[0].errorbar(true_x, mean_x, yerr=std_x, marker="o", linestyle="-",
                      capsize=3, label="measured")
    axes[0].set_xlabel("True X position (mm)")
    axes[0].set_ylabel("Reconstructed mean X (mm)")
    axes[0].set_title("Linearity: reconstructed vs true position")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Panel 2: INL (deviation from perfect line)
    axes[1].axhline(0, color="k", linestyle="--", alpha=0.4)
    axes[1].plot(true_x, inl, marker="o", linestyle="-", color="darkorange")
    axes[1].set_xlabel("True X position (mm)")
    axes[1].set_ylabel("INL: reconstructed - true (mm)")
    axes[1].set_title("Integral Non-Linearity")
    axes[1].grid(alpha=0.3)

    # Panel 3: resolution across the face
    axes[2].plot(true_x, std_x, marker="o", linestyle="-", color="seagreen")
    axes[2].set_xlabel("True X position (mm)")
    axes[2].set_ylabel("Std dev of reconstructed X (mm)")
    axes[2].set_title("Resolution across the detector face")
    axes[2].grid(alpha=0.3)

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
        print("No files found - check TRUE_X_MM/LABELS/FILES at the top of this script.")
