"""
Water sphere phantom analysis: radial profile.

Unlike the 5-hole plate (open holes = MORE transmission = bright spots),
a solid water sphere BLOCKS/scatters neutrons - so the reconstructed
image should show a circular DIP in density where the ball sits,
surrounded by a brighter, roughly flat background outside it.

This script computes radius = sqrt(x^2+y^2) for every valid
reconstructed event and histograms counts vs radius, so the dip (or
its absence) is visible directly as a function of distance from center,
independent of any assumption about shape orientation.

Requires: uproot, numpy, matplotlib
    pip install uproot numpy matplotlib
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

FILE = "B4_sphere70_imaging.root"
TREE = "B4"
SPHERE_RADIUS_MM = 35.0  # 70mm diameter / 2


def load_data(path=FILE):
    with uproot.open(path) as f:
        tree = f[TREE]
        arrays = tree.arrays(["X_rec", "Y_rec", "RecValid"], library="np")

    valid = arrays["RecValid"] > 0.5
    x = arrays["X_rec"][valid]
    y = arrays["Y_rec"][valid]
    r = np.sqrt(x**2 + y**2)

    print(f"Total valid reconstructed events: {len(x)}")
    return x, y, r


def plot_2d_and_radial(x, y, r, save_path="sphere70_phantom.png", bins_2d=25, bins_r=30):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    h = axes[0].hist2d(x, y, bins=bins_2d, range=[[-50, 50], [-50, 50]])
    circle = plt.Circle((0, 0), SPHERE_RADIUS_MM, fill=False,
                         edgecolor="orange", linestyle="--", linewidth=2)
    axes[0].add_patch(circle)
    axes[0].set_xlabel("Reconstructed X (mm)")
    axes[0].set_ylabel("Reconstructed Y (mm)")
    axes[0].set_title("Reconstructed image (dashed = true sphere edge)")
    fig.colorbar(h[3], ax=axes[0])

    axes[1].hist(r, bins=bins_r, range=(0, 50), color="steelblue", alpha=0.8)
    axes[1].axvline(SPHERE_RADIUS_MM, color="darkorange", linestyle="--",
                     label=f"sphere radius ({SPHERE_RADIUS_MM}mm)")
    axes[1].set_xlabel("Radius from center (mm)")
    axes[1].set_ylabel("Counts")
    axes[1].set_title("Radial profile - expect a dip below the dashed line")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Saved plot to {save_path}")
    plt.show()


def report_contrast(r, sphere_radius=SPHERE_RADIUS_MM):
    inside = r < sphere_radius
    # annulus just outside the sphere, same radial width, for a fair
    # density (not raw count) comparison - areas differ, so normalize
    outside = (r >= sphere_radius) & (r < sphere_radius * np.sqrt(2))

    n_in = inside.sum()
    n_out = outside.sum()
    area_in = np.pi * sphere_radius**2
    area_out = np.pi * (sphere_radius * np.sqrt(2))**2 - area_in

    density_in = n_in / area_in
    density_out = n_out / area_out

    print(f"\nDensity inside sphere radius:  {density_in:.4f} counts/mm^2 ({n_in} counts)")
    print(f"Density just outside (annulus): {density_out:.4f} counts/mm^2 ({n_out} counts)")
    if density_in > 0:
        print(f"Outside/inside density ratio: {density_out/density_in:.2f}x")
    else:
        print("No counts inside sphere radius - cannot compute ratio")


if __name__ == "__main__":
    x, y, r = load_data()
    if len(x) > 0:
        plot_2d_and_radial(x, y, r)
        report_contrast(r)
    else:
        print("No valid events found.")
