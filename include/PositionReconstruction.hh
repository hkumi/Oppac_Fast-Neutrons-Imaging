#ifndef PositionReconstruction_h
#define PositionReconstruction_h 1

#include "globals.hh"
#include "DetectorParameters.hh"
#include <array>

namespace B4a
{

// Implements the position-reconstruction algorithm (eq. 3.1) from
// Cortesi, Ayyad & Yurkon, 2018 JINST 13 P10006:
//
//   For each of the 4 SiPM arrays, fit the array's per-event photon-count
//   profile with a Gaussian to get its mean position (P), total detected
//   photons (N), and width (sigma). Then combine the two arrays that face
//   each other for each coordinate, weighted by N/sigma:
//
//       x = (Px1*Nx1/sx1 + Px2*Nx2/sx2) / (Nx1/sx1 + Nx2/sx2)
//
// The Gaussian mean/sigma are computed via weighted moments rather than
// a full non-linear least-squares fit - for a reasonably-sampled peak
// this gives the same mean and sigma as a Gaussian fit would, and is
// cheap enough to run inside the event loop for every event.
class PositionReconstruction
{
  public:
    struct SideFit
    {
        G4bool   valid     = false;
        G4double mean      = 0.;   // P     - fitted mean position (mm)
        G4double amplitude = 0.;   // N     - total detected photons on this side
        G4double sigma     = 0.;   // sigma - width of the light distribution
    };

    struct Position
    {
        G4bool   valid = false;
        G4double x = 0.;
        G4double y = 0.;
    };

    using SideCounts = std::array<G4int, B4::kNCellsPerSide>;
    using AllCounts  = std::array<G4int, B4::kNSiPMTotal>;

    // Sensor index within one side (0..kNCellsPerSide-1) -> physical
    // position in mm. Matches the placement formula used in
    // DetectorConstruction.cc, so reconstructed coordinates line up
    // with the actual geometry.
    static G4double IndexToPosition(G4int idx);

    // Fit one side's photon-count profile.
    static SideFit FitSide(const SideCounts& counts);

    // Combine two opposing arrays' fits into one coordinate (eq. 3.1).
    static G4double CombineTwoSides(const SideFit& a, const SideFit& b);

    // Full reconstruction from the flat 4*kNCellsPerSide hit array
    // (same layout as EventAction's fSiPMHits / the SiPM_* ntuple columns:
    // side = copyNo / kNCellsPerSide, idx = copyNo % kNCellsPerSide).
    static Position Reconstruct(const AllCounts& hits);
};

}

#endif
