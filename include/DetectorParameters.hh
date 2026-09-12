#ifndef DetectorParameters_h
#define DetectorParameters_h 1

#include "G4SystemOfUnits.hh"
#include "globals.hh"

// Single source of truth for the SiPM array geometry.
// DetectorConstruction.cc, RunAction.cc and SteppingAction.cc all
// #include this file, so if you change a number here it changes
// everywhere consistently. Never hardcode "25", "50", "100" etc.
// again in those three files - always use these names instead.

namespace B4
{
    // SiPMs per side (there are 4 sides -> kNSiPMTotal in the array)
    constexpr G4int kNCellsPerSide = 25;

    // Photo-sensor active area (this is your "1 mm sensor" goal)
    constexpr G4double kSiPMSize = 1.0 * mm;

    // Pitch is fixed so that kNCellsPerSide * kCellSize exactly fills
    // the 100mm side: 25 * 4mm = 100mm (same pitch as the original
    // design). Keeping nCells at 25 means the pitch (and therefore,
    // per the paper's fig. 5, the spatial resolution) does NOT change
    // just because the sensor got smaller - only the collimator wall
    // around each sensor gets thicker (3mm instead of 1mm).
    constexpr G4double kCellSize = 4.0 * mm;

    // Collimator wall thickness = whatever's left after the sensor
    // (derived, not chosen directly, so it can never silently
    // mismatch kCellSize)
    constexpr G4double kCollimatorWall = kCellSize - kSiPMSize;

    // Total number of SiPMs across all 4 sides
    constexpr G4int kNSiPMTotal = 4 * kNCellsPerSide;
}

#endif
