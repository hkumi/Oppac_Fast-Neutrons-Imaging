# O-PPAC Fast-Neutron Imaging Detector — Geant4 Simulation

PhD thesis project: a Geant4 simulation of an Optical Parallel-Plate Avalanche
Counter (O-PPAC) for fast-neutron imaging, following Cortesi, Ayyad & Yurkon,
2018 JINST 13 P10006, with the SiPM sensor size reduced to 1mm (from the
paper's 3.16mm) and the paper's position-reconstruction algorithm (eq. 3.1)
implemented natively in C++ inside the simulation.

**Status:** Fast-neutron characterization and imaging demonstration complete.
Thermal-neutron imaging (a separate converter design) is planned as a
follow-on phase. See `docs/development-log.pdf` for the full, honest
development history — including two software defects found and corrected
along the way — and `docs/thesis-chapter.docx` for the write-up.

## Detection principle

A fast neutron enters an HDPE converter foil, produces a recoil proton via
elastic scattering, the proton crosses a thin CF4 (Ar:CF4 90/10) gas gap
producing electroluminescence photons, and 4 collimated SiPM arrays (25
sensors/side, 1mm each, one array per side) record the light. Position is
reconstructed from the relative light distribution across the 4 arrays.

## Key results

- **Collimator wall reflectivity, not collimator length, governs off-axis
  reconstruction linearity** — a diffuse (Teflon) collimator biases every
  reconstruction toward the array center regardless of length; an absorptive
  (ABS-like) collimator fixes this.
- **Scintillation yield correction**: the originally-used value was borrowed
  from an alpha-particle/pure-CF4 estimate mismatched to this detector's
  actual proton/Ar:CF4 conditions. A first-principles recalculation gave a
  value 14.3x higher, confirmed via a saturation sweep, giving a 2.3x
  resolution improvement (4.09mm → 1.76mm).
- **Confirmed optimum configuration**: 5mm collimator length, 100μm HDPE
  converter, 0.05 collimator reflectivity, 35,730,000 photons/MeV
  scintillation yield. Average resolution ≈ 1.6-1.8mm (position-dependent).
- **Imaging demonstrated** on two independent test objects: a 5-hole
  resolution phantom (resolves ≥5mm features at >5σ) and a 70mm water sphere
  (2.25x density contrast, consistent with transmission-radiography physics).

## Repository structure

```
├── src/                        # Geant4 C++ source
│   ├── DetectorParameters.hh   # Shared geometry constants (single source of truth)
│   ├── DetectorConstruction.hh/.cc   # Geometry, materials, optical surfaces, runtime UI commands
│   ├── PrimaryGeneratorAction.hh/.cc # Neutron gun, runtime beam-position commands
│   ├── PositionReconstruction.hh/.cc # C++ implementation of the paper's eq. 3.1
│   ├── EventAction.hh/.cc
│   ├── SteppingAction.cc       # Per-event hit recording, PDE cut
│   └── RunAction.cc            # Histogram/ntuple booking
├── macros/                     # One .mac file per sweep/test point
│   ├── sweep_*.mac              # Collimator/converter/yield sweeps
│   ├── test_x*.mac              # Off-axis position sweep points
│   ├── *phantom*.mac            # Resolution-phantom and sphere imaging runs
│   └── *contrast*.mac           # Quick contrast-check runs (cheap, before committing to full runs)
├── analysis/                   # Python analysis scripts (uproot/numpy/matplotlib)
│   ├── analyze_collimator_sweep.py
│   ├── analyze_converter_sweep.py
│   ├── analyze_position_sweep.py
│   ├── analyze_yield_sweep.py
│   ├── analyze_phantom.py
│   └── analyze_sphere_phantom.py
├── docs/
│   ├── development-log.pdf      # Full session-by-session development log (source of truth)
│   ├── thesis-chapter.docx      # Draft PhD thesis chapter (fast-neutron part)
│   └── figures/                 # Generated plots (.png), referenced by both docs above
├── CMakeLists.txt
└── README.md
```



## Reproducing a result

Every runtime parameter is set via Geant4 UI commands **before**
`/run/initialize`, inside a macro — this project's build does not support
changing geometry parameters after initialization (`GeometryHasBeenModified()`
does not trigger a rebuild in this Geant4 version's MT backend). Each macro in
`macros/` is self-contained and states which parameters it sets. Example:

```bash
./exampleB4a -m macros/sweep_100mm_v2.mac
python3 analysis/analyze_position_sweep.py
```

## Runtime-adjustable parameters

| Command | Purpose |
|---|---|
| `/detector/setCollimatorLength <value> <unit>` | Collimator tube length |
| `/detector/setConverterThickness <value> <unit>` | HDPE converter thickness |
| `/detector/setCollimatorReflectivity <0-1>` | Collimator wall reflectivity |
| `/detector/setScintillationYield <photons/MeV>` | Gas scintillation yield |
| `/detector/setPDE <0-1>` | SiPM photon detection efficiency (default 1.0 = off, pending confirmation of the real value — see thesis chapter §11.2) |
| `/detector/setPhantomEnabled <1\|0>` | Phantom on/off (use `1`/`0`, **not** `true`/`false` — see known issues below) |
| `/detector/setPhantomType <0\|1>` | 0 = 5-hole plate, 1 = water sphere |
| `/detector/setPhantomThickness <value> <unit>` | Hole-plate thickness |
| `/detector/setSpherePhantomDiameter <value> <unit>` | Sphere diameter |
| `/gun/setBeamX`, `/gun/setBeamY`, `/gun/setBeamZ` | Beam position |
| `/gun/setBeamSpread <value> <unit>` | Flood-illumination spread (0 = point beam) |

## Known issues / gotchas (read before extending this code)

1. **Geant4's UI parser does not reliably accept `true`/`false` for boolean
   commands.** Use `1`/`0`. Using `true` silently defaults to `false` with no
   error — this caused every early phantom test to run with no phantom
   physically present (see development log, "Bugs Found During Imaging
   Development").
2. **All `/detector/...` and `/gun/...` commands must be issued before
   `/run/initialize`** in the same macro invocation.
3. **PDE is currently a placeholder (1.0, off).** The reference paper only
   shows the Hamamatsu VUV-3 MPPC's PDE graphically (its Figure 3); confirm
   the real peak value before treating any resolution figure as final.
4. The position-dependent resolution asymmetry (better toward +x) found in
   the full position sweep is real (confirmed independently in two separate
   measurements) and unexplained — see thesis chapter §11.1.

## Reference

M. Cortesi, J. J. Ayyad, and J. Yurkon, "A novel Optical readout Parallel-
Plate Avalanche Counter (O-PPAC) for high-resolution neutron imaging,"
*Journal of Instrumentation*, vol. 13, P10006, 2018.
