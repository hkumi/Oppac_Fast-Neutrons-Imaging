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

    // NEW: beam X/Y position, settable via "/gun/setBeamX" and
    // "/gun/setBeamY". These just forward to
    // PrimaryGeneratorAction::SetSharedBeamX/Y() - see the comment in
    // PrimaryGeneratorAction.hh for why the command lives here instead
    // of on PrimaryGeneratorAction itself (MT thread-visibility issue).
    void SetBeamX(G4double value);
    void SetBeamY(G4double value);


  private:
    // methods
    //
    void DefineMaterials();
    G4VPhysicalVolume* DefineVolumes(G4double, G4double);
    void DefineCommands();

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
