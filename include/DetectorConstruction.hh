#ifndef B4DetectorConstruction_h
#define B4DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"
#include <memory>
#include "G4SystemOfUnits.hh"
class G4VPhysicalVolume;
class G4LogicalVolume;
class G4GlobalMagFieldMessenger;
class G4GenericMessenger;

namespace B4
{

class DetectorConstruction : public G4VUserDetectorConstruction
{
  public:
    DetectorConstruction();
    ~DetectorConstruction() override = default;

  public:
    G4VPhysicalVolume* Construct() override;
    void ConstructSDandField() override;

    // get methods
    //
    const G4VPhysicalVolume* GetSiPMPV() const;
    const G4VPhysicalVolume* GetSiPM2PV() const;
	G4double GetPitch() const { return pitch; }
	G4double GetSize() const { return size; }

    // NEW: collimator length, settable at runtime via
    // "/detector/setCollimatorLength <value> <unit>" instead of
    // needing a recompile for every value in a sweep.
    G4double GetCellLength() const { return fCellLength; }
    void SetCellLength(G4double value);

    // NEW: converter thickness, settable at runtime via
    // "/detector/setConverterThickness <value> <unit>"
    G4double GetConverterThickness() const { return fConvThickness; }
    void SetConverterThickness(G4double value);

    // NEW: collimator wall reflectivity (dimensionless, 0-1). Currently
    // 0.95 (diffuse Teflon). Testing lower values (~0.05-0.10, matching
    // the paper's ABS collimator) to see if it fixes the center-bias
    // found in the off-axis accuracy test, which collimator length
    // alone did not fix.
    G4double GetCollimatorReflectivity() const { return fCollimatorReflectivity; }
    void SetCollimatorReflectivity(G4double value);

    // NEW: scintillation yield (photons per MeV deposited in the gas).
    // Was hardcoded at 2,500,000/MeV (borrowed from Cortesi et al.'s
    // 5.5 MeV alpha-particle-in-pure-CF4 estimate). A from-first-principles
    // calculation for protons in Ar:CF4 (90/10) at the OPPAC's actual gas
    // parameters gives 35,730,000/MeV instead - settable at runtime so
    // both values (and points in between) can be swept and compared.
    G4double GetScintillationYield() const { return fScintillationYield; }
    void SetScintillationYield(G4double value);

    // NEW: SiPM photon detection efficiency (PDE), dimensionless 0-1.
    // Previously NOT modeled at all - every photon reaching a SiPM was
    // counted, i.e. an implicit, unrealistic 100% PDE. The paper's
    // Hamamatsu VUV-3 MPPC has a real PDE shown only as a graph
    // (Figure 3, blue line) with no explicit numeric value in the text -
    // Defaults to 1.0 (effectively off) until you're ready to use the actual
    // peak value from that figure or the private Hamamatsu data (ref [34]).
    G4double GetPDE() const { return fPDE; }
    void SetPDE(G4double value);

    // NEW: beam X/Y position, settable via "/gun/setBeamX" and
    // "/gun/setBeamY". These just forward to
    // PrimaryGeneratorAction::SetSharedBeamX/Y() - see the comment in
    // PrimaryGeneratorAction.hh for why the command lives here instead
    // of on PrimaryGeneratorAction itself (MT thread-visibility issue).
    void SetBeamX(G4double value);
    void SetBeamY(G4double value);

    // NEW: flood illumination for imaging - see the comment in
    // PrimaryGeneratorAction.hh for what these do.
    void SetBeamSpread(G4double value);
    void SetBeamZ(G4double value);

    // NEW: resolution phantom (5 holes of different sizes in an HDPE
    // plate, upstream of the gas box), off by default. Toggle via
    // "/detector/setPhantomEnabled true|false" (before /run/initialize).
    G4bool GetPhantomEnabled() const { return fPhantomEnabled; }
    void SetPhantomEnabled(G4bool value);

    // NEW: phantom plate thickness, settable via
    // "/detector/setPhantomThickness <value> <unit>"
    G4double GetPhantomThickness() const { return fPhantomThickness; }
    void SetPhantomThickness(G4double value);


  private:
    // methods
    //
    void DefineMaterials();
    G4VPhysicalVolume* DefineVolumes(G4double, G4double);
    void DefineCommands();
    void ConstructResolutionPhantom(G4LogicalVolume* motherLog,
                                     G4double zPosition,
                                     G4double plateThickness);

    // data members
    //
    static G4ThreadLocal G4GlobalMagFieldMessenger*  fMagFieldMessenger;
                                      // magnetic field messenger

    G4VPhysicalVolume* SiPMPV = nullptr; // the absorber physical volume
    G4VPhysicalVolume* SiPM2PV = nullptr;
    G4double pitch;
	G4double size;

    // NEW: collimator length, default matches your working 5mm test.
    // Change via macro command instead of editing this default for
    // a parameter sweep.
    G4double fCellLength = 5.0 * mm;

    // NEW: converter thickness, default matches your current 0.01mm.
    G4double fConvThickness = 0.01 * mm;

    G4double fCollimatorReflectivity = 0.95;

    // photons/MeV, default matches the original (possibly-mismatched)
    // alpha-particle-in-pure-CF4 value - see header comment
    G4double fScintillationYield = 2500000.0;

    // Default 1.0 = PDE effectively off (every photon that geometrically
    // arrives is counted, same as before this parameter existed) - kept
    // this way deliberately so deferring the PDE decision never silently
    // affects results. Set to the real value (once confirmed against the
    // paper's Figure 3 or ref [34]) only when you're ready to use it.
    G4double fPDE = 1.0;

    // Off by default - existing point-source tests are unaffected
    // unless /detector/setPhantomEnabled true is issued.
    G4bool fPhantomEnabled = false;

    // Default 20mm showed no measurable contrast (hole vs solid gave
    // near-identical yield) - settable at runtime to test thicker
    // phantoms without recompiling.
    G4double fPhantomThickness = 20.0 * mm;

    std::unique_ptr<G4GenericMessenger> fMessenger;
    std::unique_ptr<G4GenericMessenger> fGunMessenger;

    G4bool fCheckOverlaps = true; // option to activate checking of volumes overlaps
};

// inline functions

inline const G4VPhysicalVolume* DetectorConstruction::GetSiPMPV() const {
  return SiPMPV;
}

inline const G4VPhysicalVolume* DetectorConstruction::GetSiPM2PV() const {
  return SiPM2PV;
}

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
