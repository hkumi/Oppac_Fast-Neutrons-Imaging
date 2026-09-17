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
/// \file B4/B4a/src/PrimaryGeneratorAction.cc
/// \brief Implementation of the B4::PrimaryGeneratorAction class
#include "PrimaryGeneratorAction.hh"

#include "G4RunManager.hh"
#include "G4Event.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4AnalysisManager.hh"

namespace B4
{
    // fBeamX/fBeamY default to (0,0) - same as the original hardcoded
    // center beam. Set at runtime via DetectorConstruction's
    // "/gun/setBeamX" and "/gun/setBeamY" commands (see
    // DetectorConstruction.cc), which call SetSharedBeamX/Y() below.
    G4double PrimaryGeneratorAction::fBeamX = 0.0;
    G4double PrimaryGeneratorAction::fBeamY = 0.0;

    PrimaryGeneratorAction::PrimaryGeneratorAction()
    {
        G4int nofParticles = 1;
        fParticleGun = new G4ParticleGun(nofParticles);

        auto particleDefinition = G4ParticleTable::GetParticleTable()->FindParticle("neutron");
        fParticleGun->SetParticleDefinition(particleDefinition);
        fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.));
    }

    PrimaryGeneratorAction::~PrimaryGeneratorAction()
    {
        delete fParticleGun;
    }

    void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
    {
        auto analysisManager = G4AnalysisManager::Instance();

		// Set gun energy
        fParticleGun->SetParticleEnergy(2.5 * MeV);

		G4double zpos = 0.5 * cm;
        // Beam position - reads the shared static fBeamX/fBeamY, set via
        // /gun/setBeamX and /gun/setBeamY (registered on
        // DetectorConstruction - see the comment in the header for why).
		// TEMPORARY DEBUG: print what this thread actually sees for
		// fBeamX/fBeamY, for the very first few events only (avoid
		// flooding the log for a million-event run). Remove this once
		// the beam-position issue is resolved.
		static thread_local G4int debugPrintCount = 0;
		if (debugPrintCount < 5) {
			G4cout << "DEBUG GeneratePrimaries: fBeamX=" << fBeamX/mm
			       << " mm, fBeamY=" << fBeamY/mm << " mm" << G4endl;
			++debugPrintCount;
		}

		fParticleGun->SetParticlePosition(G4ThreeVector(fBeamX, fBeamY, zpos));

        fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0.0, 0.0, -1.0));

        fParticleGun->GeneratePrimaryVertex(anEvent);
    }

}
