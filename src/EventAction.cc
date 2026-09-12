//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
/// \file B4/B4a/src/EventAction.cc
/// \brief Implementation of the B4a::EventAction class

#include "EventAction.hh"
#include "RunAction.hh"
#include "DetectorParameters.hh"
#include "PositionReconstruction.hh"

#include "G4AnalysisManager.hh"
#include "G4RunManager.hh"
#include "G4Event.hh"
#include "G4UnitsTable.hh"

#include "Randomize.hh"
#include <iomanip>
#include <algorithm>

namespace B4a
{

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void EventAction::BeginOfEventAction(const G4Event* /*event*/)
{
  // initialisation per event
  fEnergySiPM = 0.;
  fEnergySiPM2 = 0.;

  // clear the raw per-sensor hit counts for the new event
  std::fill(fSiPMHits.begin(), fSiPMHits.end(), 0);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void EventAction::EndOfEventAction(const G4Event* event)
{
  auto analysisManager = G4AnalysisManager::Instance();

  // ----------------------------------------------------------------
  // Position reconstruction (eq. 3.1), done entirely in C++ now.
  // fSiPMHits is filled during the event by SteppingAction, one
  // increment per photon that hits a SiPM (see AddSiPMHit()).
  // ----------------------------------------------------------------
  PositionReconstruction::AllCounts hits;
  std::copy(fSiPMHits.begin(), fSiPMHits.end(), hits.begin());

  PositionReconstruction::Position pos = PositionReconstruction::Reconstruct(hits);

  if (pos.valid) {
      analysisManager->FillH2(0, pos.x, pos.y);   // live image, H2 index 0
  }

  analysisManager->FillNtupleDColumn(3, pos.x);
  analysisManager->FillNtupleDColumn(4, pos.y);
  analysisManager->FillNtupleDColumn(5, pos.valid ? 1. : 0.);

  // raw per-sensor profile, kept for offline cross-checking
  for (G4int s = 0; s < B4::kNSiPMTotal; ++s) {
      analysisManager->FillNtupleDColumn(6 + s, fSiPMHits[s]);
  }
  analysisManager->AddNtupleRow();

  G4int nPrimaries = event->GetNumberOfPrimaryVertex();

  for (G4int iVertex = 0; iVertex < nPrimaries; ++iVertex) {
      G4PrimaryVertex* vertex = event->GetPrimaryVertex(iVertex);
      G4PrimaryParticle* primary = vertex->GetPrimary();

      if (primary->GetPDGcode() == 2112) { // neutron=2112; gamma=22
          auto eventID = event->GetEventID();
          auto printModulo = G4RunManager::GetRunManager()->GetPrintProgress();
      }
  }
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo.....

}
