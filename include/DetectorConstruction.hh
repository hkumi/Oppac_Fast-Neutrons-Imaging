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

    std::unique_ptr<G4GenericMessenger> fMessenger;

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
