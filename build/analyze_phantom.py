"""
Resolution phantom analysis: Y-sliced X projection.

Your 5 holes (2,3,5,8,10mm diameter) all sit at y=0, x=-20,-10,0,10,20mm.
A raw 2D scatter of ReconstructedImage spreads your limited statistics
across the whole face. Since we know the holes are all at y=0, cutting
to a narrow Y band and histogramming only X concentrates the same
statistics where the actual pattern lives - much more sensitive for
spotting the holes with fewer events, same idea as the original
paper's 1D pinhole projections.

Reads X_rec/Y_rec/RecValid directly from the ntuple (not the H2
histogram), so you can freely try different Y cuts without re-running
the simulation.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

FILE = "B4_phantom_100mm_v2_1e8.root"
TREE = "B4"
Y_CUTOFF_MM = 5.0   # keep only |Y_rec| < this value

# True hole positions/sizes, for marking on the plot
HOLE_X = [-20, -10, 0, 10, 20]
HOLE_SIZE = [2.0, 3.0, 5.0, 8.0, 10.0]


def load_and_project(path=FILE, y_cutoff=Y_CUTOFF_MM):
    with uproot.open(path) as f:
        tree = f[TREE]
        arrays = tree.arrays(["X_rec", "Y_rec", "RecValid"], library="np")

    valid = arrays["RecValid"] > 0.5
    x = arrays["X_rec"][valid]
    y = arrays["Y_rec"][valid]

    print(f"Total valid reconstructed events: {len(x)}")

    y_slice = np.abs(y) < y_cutoff
    x_sliced = x[y_slice]

    print(f"Events within |Y_rec| < {y_cutoff}mm: {len(x_sliced)}")
    return x_sliced


def plot_projection(x_sliced, save_path="phantom_x_projection.png", bins=100):
    plt.figure(figsize=(10, 5))
    counts, edges, _ = plt.hist(x_sliced, bins=bins, range=(-50, 50),
                                 color="steelblue", alpha=0.8)

    for hx, hs in zip(HOLE_X, HOLE_SIZE):
        plt.axvline(hx, color="darkorange", linestyle="--", alpha=0.6)
        plt.text(hx, plt.ylim()[1] * 0.95, f"{hs}mm",
                  ha="center", va="top", fontsize=8, color="darkorange")

    plt.xlabel("Reconstructed X (mm)")
    plt.ylabel(f"Counts (|Y_rec| < {Y_CUTOFF_MM}mm)")
    plt.title("Resolution phantom: X projection through the 5 holes")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Saved plot to {save_path}")
    plt.show()


def region_significance(x_sliced, hole_x=HOLE_X, hole_size=HOLE_SIZE):
    """For each hole, count events within its own radius of its true
    center ('signal window'), and compare to the count density in
    nearby background regions (between holes, same total width),
    with Poisson uncertainty on each. This sidesteps bin-alignment
    issues entirely - a real signal should show up here even if the
    histogram plot looks ambiguous."""
    print(f"\n{'Hole (mm)':>10} {'Signal window':>15} {'Signal count':>13} "
          f"{'Bkg density/mm':>15} {'Expected bkg':>13} {'Excess':>10} {'Sigma':>8}")

    # background rate from a region clearly between all holes and the
    # edges - here, the outer quarters of the range, away from any hole
    bkg_mask = (np.abs(x_sliced) > 30)
    bkg_width = 2 * (50 - 30)  # mm of background region used
    bkg_rate = bkg_mask.sum() / bkg_width  # counts per mm

    for hx, hs in zip(hole_x, hole_size):
        r = hs / 2
        sig_mask = (x_sliced > hx - r) & (x_sliced < hx + r)
        signal_count = sig_mask.sum()
        window_width = 2 * r
        expected_bkg = bkg_rate * window_width
        excess = signal_count - expected_bkg
        # Poisson-ish uncertainty on the excess (signal + expected background)
        sigma = np.sqrt(signal_count + expected_bkg) if (signal_count + expected_bkg) > 0 else 1
        significance = excess / sigma

        print(f"{hx:>10} {f'+/-{r:.1f}mm':>15} {signal_count:>13} "
              f"{bkg_rate:>15.3f} {expected_bkg:>13.2f} {excess:>10.2f} {significance:>8.2f}")


if __name__ == "__main__":
    x_sliced = load_and_project()
    if len(x_sliced) > 0:
        plot_projection(x_sliced, bins=25)   # 4mm bins, matching sensor pitch
        region_significance(x_sliced)
    else:
        print("No events survived the Y cut - try a larger Y_CUTOFF_MM "
              "or more statistics.")
