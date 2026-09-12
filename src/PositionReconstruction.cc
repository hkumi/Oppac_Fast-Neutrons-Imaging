#include "PositionReconstruction.hh"
#include <cmath>

namespace B4a
{

using B4::kNCellsPerSide;
using B4::kCellSize;

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4double PositionReconstruction::IndexToPosition(G4int idx)
{
    // Same formula DetectorConstruction.cc uses to place each cell/SiPM:
    //   pos = (-nCells/2 + j + 0.5) * cellSize
    return (idx - kNCellsPerSide / 2.0 + 0.5) * kCellSize;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PositionReconstruction::SideFit PositionReconstruction::FitSide(const SideCounts& counts)
{
    SideFit result;   // valid = false by default

    G4double total = 0.;
    for (G4int c : counts) total += c;

    if (total <= 0.) {
        return result;   // no photons on this side this event
    }

    // weighted mean position
    G4double meanPos = 0.;
    for (G4int i = 0; i < kNCellsPerSide; ++i) {
        meanPos += counts[i] * IndexToPosition(i);
    }
    meanPos /= total;

    // weighted standard deviation (equivalent to the Gaussian fit's sigma)
    G4double variance = 0.;
    for (G4int i = 0; i < kNCellsPerSide; ++i) {
        G4double d = IndexToPosition(i) - meanPos;
        variance += counts[i] * d * d;
    }
    variance /= total;
    G4double sigma = std::sqrt(variance);

    if (sigma < 1.0e-6) {
        // Only one sensor fired (or all photons landed in the same
        // bin) - can't estimate a sub-pixel sigma from a single point,
        // but we still know roughly where the hit was: somewhere
        // within this sensor's footprint. Falling back to a default
        // sigma (rather than discarding the side) matters a lot at
        // low light levels, where most events only light up one or
        // two sensors per side - discarding those throws away almost
        // every event.
        sigma = kCellSize / 2.0;
    }

    result.valid     = true;
    result.mean      = meanPos;
    result.amplitude = total;
    result.sigma     = sigma;
    return result;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4double PositionReconstruction::CombineTwoSides(const SideFit& a, const SideFit& b)
{
    if (!a.valid && !b.valid) return 0.;
    if (!a.valid) return b.mean;
    if (!b.valid) return a.mean;

    G4double wa = a.amplitude / a.sigma;
    G4double wb = b.amplitude / b.sigma;
    return (a.mean * wa + b.mean * wb) / (wa + wb);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PositionReconstruction::Position PositionReconstruction::Reconstruct(const AllCounts& hits)
{
    Position pos;   // valid = false by default

    // split the flat 200-entry array into the 4 sides of 50
    std::array<SideCounts, 4> sideCounts{};
    for (G4int side = 0; side < 4; ++side) {
        for (G4int i = 0; i < kNCellsPerSide; ++i) {
            sideCounts[side][i] = hits[side * kNCellsPerSide + i];
        }
    }

    // side 0,2 -> Y arrays ; side 1,3 -> X arrays
    // (this matches the i=0,2 / i=1,3 split in
    //  DetectorConstruction::DefineVolumes, where i=0,2 place cells
    //  varying in Y and i=1,3 place cells varying in X)
    SideFit y1 = FitSide(sideCounts[0]);
    SideFit y2 = FitSide(sideCounts[2]);
    SideFit x1 = FitSide(sideCounts[1]);
    SideFit x2 = FitSide(sideCounts[3]);

    if (!(y1.valid || y2.valid) || !(x1.valid || x2.valid)) {
        return pos;   // not enough light to reconstruct this event
    }

    pos.valid = true;
    pos.y = CombineTwoSides(y1, y2);
    pos.x = CombineTwoSides(x1, x2);
    return pos;
}

}
