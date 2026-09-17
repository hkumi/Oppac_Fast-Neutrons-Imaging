"""
Proton energy spectrum comparison across converter thicknesses.

Reads the "proton_conv" (energy at production, inside/near the
converter) and "proton_gas" (energy once the proton reaches the
sensitive gas volume) 1D histograms - both already booked in
RunAction.cc and filled in SteppingAction.cc - from your converter
thickness sweep files, and compares them across thicknesses.

The point: if thin converters barely degrade the proton energy
(proton_gas spectrum looks like proton_conv) while thick converters
show a strong low-energy shift or depletion (many protons lost or
heavily slowed before reaching the gas), that's the direct mechanistic
evidence for *why* yield/resolution peak where they do - not just
"we observed a peak."

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib

Run this from the directory containing your B4_conv_*um.root files.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Pick the thicknesses you want to compare - the three from the
# suggestion (10, 100, 1000 um) are a good spread: below, at, and
# above the yield/resolution optimum you already found.
# ---------------------------------------------------------------
THICKNESS_UM = [10, 100, 1000]
FILES = {t: f"B4_conv_{t}um.root" for t in THICKNESS_UM}

PRODUCTION_HIST = "proton_conv"   # recoil proton energy at production
GAS_HIST = "proton_gas"           # proton energy once it reaches the gas


def hist_to_arrays(path, hist_name):
    """Returns (bin_centers, values, mean_energy) for a 1D histogram."""
    with uproot.open(path) as f:
        h = f[hist_name]
        values, edges = h.to_numpy()

    centers = 0.5 * (edges[:-1] + edges[1:])
    total = values.sum()
    mean_energy = np.sum(centers * values) / total if total > 0 else np.nan
    return centers, values, mean_energy


def compare_spectra(thicknesses=THICKNESS_UM, files=FILES):
    results = {}
    for t in thicknesses:
        fname = files[t]
        try:
            centers_conv, values_conv, mean_conv = hist_to_arrays(fname, PRODUCTION_HIST)
            centers_gas, values_gas, mean_gas = hist_to_arrays(fname, GAS_HIST)
        except FileNotFoundError:
            print(f"WARNING: {fname} not found, skipping {t}um")
            continue

        retained_fraction = mean_gas / mean_conv if mean_conv > 0 else np.nan
        results[t] = {
            "centers_conv": centers_conv, "values_conv": values_conv, "mean_conv": mean_conv,
            "centers_gas": centers_gas, "values_gas": values_gas, "mean_gas": mean_gas,
            "retained_fraction": retained_fraction,
        }

        print(f"{t:>5} um converter:  "
              f"mean proton energy at production = {mean_conv:.1f} keV,  "
              f"mean energy reaching gas = {mean_gas:.1f} keV  "
              f"(retained {retained_fraction*100:.1f}%)")

    return results


def plot_comparison(results, save_path="proton_spectra_comparison.png"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(results)))

    for color, (t, r) in zip(colors, results.items()):
        # normalize each spectrum to unit area so shapes are directly
        # comparable regardless of how many total protons were produced
        norm_conv = r["values_conv"] / r["values_conv"].sum()
        norm_gas = r["values_gas"] / r["values_gas"].sum()

        axes[0].step(r["centers_conv"], norm_conv, where="mid",
                     label=f"{t} um", color=color)
        axes[1].step(r["centers_gas"], norm_gas, where="mid",
                     label=f"{t} um", color=color)

    axes[0].set_title("Proton energy at production")
    axes[0].set_xlabel("Energy (keV)")
    axes[0].set_ylabel("Normalized counts")
    axes[0].legend(title="Converter")
    axes[0].grid(alpha=0.3)

    axes[1].set_title("Proton energy reaching the gas")
    axes[1].set_xlabel("Energy (keV)")
    axes[1].set_ylabel("Normalized counts")
    axes[1].legend(title="Converter")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"\nSaved plot to {save_path}")
    plt.show()


if __name__ == "__main__":
    results = compare_spectra()
    if results:
        plot_comparison(results)
    else:
        print("No files found - check THICKNESS_UM/FILES at the top of this script.")
