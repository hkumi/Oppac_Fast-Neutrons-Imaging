"""
Collimator-length sweep analysis.

Reads the "ReconstructedImage" 2D histogram from each sweep ROOT file
(booked in RunAction.cc, filled event-by-event by EventAction via
PositionReconstruction), computes:
  - yield: total number of valid reconstructed events (histogram entries)
  - resolution: std dev of x and y directly from the 2D histogram's
    bin contents (equivalent to the "Std Dev" TBrowser shows you,
    computed here so it can be automated across all 6 files at once)

then plots both against collimator length, same two-panel layout as
Figure 5 in Cortesi, Ayyad & Yurkon, 2018 JINST 13 P10006.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib

Run this from the directory containing your B4_len*mm.root files,
or edit `files` below to give full paths.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import csv

# ---------------------------------------------------------------
# Edit these two lists if your filenames or lengths differ
# ---------------------------------------------------------------
LENGTHS_MM = [5, 10, 15, 20, 25, 30]
FILES = [f"B4_len{L}mm_lowrefl.root" for L in LENGTHS_MM]
HIST_NAME = "ReconstructedImage"


def analyze_file(path, hist_name=HIST_NAME):
    """Returns (entries, mean_x, mean_y, std_x, std_y) for the 2D
    reconstructed-image histogram in one ROOT file."""
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


def run_sweep_analysis(lengths_mm=LENGTHS_MM, files=FILES):
    results = []
    for length, fname in zip(lengths_mm, files):
        try:
            entries, mean_x, mean_y, std_x, std_y = analyze_file(fname)
        except FileNotFoundError:
            print(f"WARNING: {fname} not found, skipping")
            continue

        results.append({
            "length_mm": length,
            "entries": entries,
            "mean_x": mean_x,
            "mean_y": mean_y,
            "std_x": std_x,
            "std_y": std_y,
        })

        print(f"length={length:>3}mm  entries={entries:>8.0f}  "
              f"mean=({mean_x:+.3f}, {mean_y:+.3f}) mm  "
              f"std=({std_x:.3f}, {std_y:.3f}) mm")

    return results


def save_csv(results, path="collimator_sweep_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved table to {path}")


def plot_sweep(results, save_path="collimator_sweep.png"):
    lengths = [r["length_mm"] for r in results]
    entries = [r["entries"] for r in results]
    # average of std_x/std_y as a single "resolution" number, same
    # simplification the paper uses when quoting one FWHM/sigma value
    resolution = [(r["std_x"] + r["std_y"]) / 2 for r in results]
    entries_err = [np.sqrt(e) if e > 0 else 0 for e in entries]  # Poisson

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    axes[0].errorbar(lengths, resolution, marker="o", linestyle="-")
    axes[0].set_xlabel("Collimator length (mm)")
    axes[0].set_ylabel("Spatial resolution, avg(std x, std y) (mm)")
    axes[0].set_title("Resolution vs collimator length")
    axes[0].grid(alpha=0.3)

    axes[1].errorbar(lengths, entries, yerr=entries_err, marker="o",
                      linestyle="-", color="firebrick", capsize=3)
    axes[1].set_xlabel("Collimator length (mm)")
    axes[1].set_ylabel("Valid reconstructed events")
    axes[1].set_title("Yield vs collimator length")
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
        print("No files found - check LENGTHS_MM/FILES paths at the top of this script.")
