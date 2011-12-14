#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/GlobalElectronVeto.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/MakeTH.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/GenParticleAnalysis.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"
#include "Math/GenVector/VectorUtil.h"
#include <string>
#include "TH1F.h"
#include "TH2F.h"

namespace HPlus {
  GlobalElectronVeto::Data::Data(const GlobalElectronVeto *globalElectronVeto, bool passedEvent):
    fGlobalElectronVeto(globalElectronVeto), fPassedEvent(passedEvent) {}
  GlobalElectronVeto::Data::~Data() {}
  
  GlobalElectronVeto::GlobalElectronVeto(const edm::ParameterSet& iConfig, EventCounter& eventCounter, EventWeight& eventWeight):
    fElecCollectionName(iConfig.getUntrackedParameter<edm::InputTag>("ElectronCollectionName")),
    fElecSelection(iConfig.getUntrackedParameter<std::string>("ElectronSelection")),
    fElecPtCut(iConfig.getUntrackedParameter<double>("ElectronPtCut")),
    fElecEtaCut(iConfig.getUntrackedParameter<double>("ElectronEtaCut")),
    fGlobalElectronVetoCounter(eventCounter.addSubCounter("GlobalElectron Selection","GlobalElectronVeto")),
    fElecSelectionSubCountElectronPresent(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Present")),
    fElecSelectionSubCountElectronHasGsfTrkOrTrk(eventCounter.addSubCounter("GlobalElectron Selection", "Electron has gsfTrack or track")),
    fElecSelectionSubCountPtCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Pt " )),
    fElecSelectionSubCountEtaCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Eta")),
    fElecSelectionSubCountFiducialVolumeCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron fiducial volume")),
    fElecSelectionSubCountMatchingMCelectron(eventCounter.addSubCounter("GlobalElectron Selection","Electron matching MC electron")),
    fElecSelectionSubCountMatchingMCelectronFromW(eventCounter.addSubCounter("GlobalElectron Selection","Electron matching MC electron From W")),
    fElecSelectionSubCountElectronSelection(eventCounter.addSubCounter("GlobalElectron Selection", fElecSelection)),
    fElecSelectionSubCountNLostHitsInTrkerCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Num of Lost Hits In Trker")),
    fElecSelectionSubCountmyElectronDeltaCotThetaCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Delta Cot(Theta)")),
    fElecSelectionSubCountmyElectronDistanceCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Distance (r-phi)")),
    fElecSelectionSubCountTransvImpactParCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Transverse Impact Parameter")),
    fElecSelectionSubCountDeltaRFromGlobalOrTrkerMuonCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron DeltaR From Global OrTrker Muon")),
    fElecSelectionSubCountRelIsolationR03Cut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron RelIsolationR03")),
    fElecIDSubCountAllElectronCandidates(eventCounter.addSubCounter("GlobalElectron ID", "All Electron Candidates")),
    fElecIDSubCountElecIDLoose(eventCounter.addSubCounter("GlobalElectron ID", "eidLoose")),
    fElecIDSubCountElecIDRobustLoose(eventCounter.addSubCounter("GlobalElectron ID", "eidRobustLoose")),
    fElecIDSubCountElecIDTight(eventCounter.addSubCounter("GlobalElectron ID", "eidTight")),
    fElecIDSubCountElecIDRobustTight(eventCounter.addSubCounter("GlobalElectron ID", "eidRobustTight")),
    fElecIDSubCountElecIDRobustHighEnergy(eventCounter.addSubCounter("GlobalElectron ID", "eidRobustHighEnergy")),
    fElecIDSubCountSimpleEleId95relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId95relIso")),
    fElecIDSubCountSimpleEleId90relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId90relIso")),
    fElecIDSubCountSimpleEleId85relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId85relIso")),
    fElecIDSubCountSimpleEleId80relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId80relIso")),
    fElecIDSubCountSimpleEleId70relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId70relIso")),
    fElecIDSubCountSimpleEleId60relIso(eventCounter.addSubCounter("GlobalElectron ID", "SimpleEleId60relIso")),
    fEventWeight(eventWeight)
  {
    edm::Service<TFileService> fs;
    TFileDirectory myDir = fs->mkdir("GlobalElectronVeto");
    
    hElectronPt  = makeTH<TH1F>(myDir, "GlobalElectronPt", "GlobalElectronPt;isolated electron p_{T}, GeV/c;N_{electrons} / 5 GeV/c", 400, 0.0, 400.0);
    hElectronEta = makeTH<TH1F>(myDir, "GlobalElectronEta", "GlobalElectronEta;isolated electron #eta;N_{electrons} / 0.1", 300, -3.0, 3.0);
    hElectronEta_identified = makeTH<TH1F>(myDir, "GlobalElectronEta_identified", "GlobalElectronEta_identified;isolated electron #eta;N_{electrons} / 0.1", 300, -3.0, 3.0);
    hElectronPt_identified_eta  = makeTH<TH1F>(myDir, "GlobalElectronPt_identified_eta", "GlobalElectronPt;isolated electron p_{T}, GeV/c;N_{electrons} / 5 GeV/c", 400, 0.0, 400.0);

    hElectronPt_matchingMCelectron  = makeTH<TH1F>(myDir, "GlobalElectronPt_matchingMCelectron", "GlobalElectronPt_matchingMCelectron", 400, 0.0, 400.0);
    hElectronEta_matchingMCelectron = makeTH<TH1F>(myDir, "GlobalElectronEta_matchingMCelectron", "GlobalElectronEta_matchingMCelectron", 400, -3.0, 3.0);
    hElectronPt_matchingMCelectronFromW  = makeTH<TH1F>(myDir, "GlobalElectronPt_matchingMCelectronFromW", "GlobalElectronPt_matchingMCelectronFromW", 400, 0.0, 400.0);
    hElectronEta_matchingMCelectronFromW = makeTH<TH1F>(myDir, "GlobalElectronEta_matchingMCelectronFromW", "GlobalElectronEta_matchingMCelectronFromW", 400, -3.0, 3.0);
    hElectronPt_gsfTrack  = makeTH<TH1F>(myDir, "GlobalElectronPt_gsfTrack", "GlobalElectronPt_gsfTrack", 400, 0.0, 400.0);
    hElectronEta_gsfTrack = makeTH<TH1F>(myDir, "GlobalElectronEta_gsfTrack", "GlobalElectronEta_gsfTrack", 300, -3.0, 3.0);
    hElectronEta_superCluster = makeTH<TH1F>(myDir, "GlobalElectronEta_superCluster", "GlobalElectronEta_superCluster", 60, -3.0, 3.0);
    hElectronPt_AfterSelection = makeTH<TH1F>(myDir, "GlobalElectronPt_AfterSelection", "GlobalElectronPt_AfterSelection", 100, 0.0, 200.0);
    hElectronEta_AfterSelection = makeTH<TH1F>(myDir, "GlobalElectronPt_AfterSelection", "GlobalElectronEta_AfterSelection", 60, -3.0, 3.0);
    hElectronPt_gsfTrack_AfterSelection = makeTH<TH1F>(myDir, "GlobalElectronPt_gsfTrack_AfterSelection", "GlobalElectronPt_gsfTrack_AfterSelection", 100, 0.0, 200.0);
    hElectronEta_gsfTrack_AfterSelection = makeTH<TH1F>(myDir, "GlobalElectronPt_gsfTrack_AfterSelection", "GlobalElectronPt_gsTrack_AfterSelection", 60, -3.0, 3.0);
    hElectronImpactParameter = makeTH<TH1F>(myDir, "ElectronImpactParameter", "ElectronImpactParameter", 100, 0.0, 0.1);

    bUseLooseID = false;
    bUseRobustLooseID = false;
    bUseTightID = false;
    bUseRobustTightID = false;
    bUseRobustHighEnergyID = false;
    bUseSimpleEleId95relIsoID = false;
    bUseSimpleEleId90relIsoID = false;
    bUseSimpleEleId85relIsoID = false;
    bUseSimpleEleId80relIsoID = false;
    bUseSimpleEleId70relIsoID = false;
    bUseSimpleEleId60relIsoID = false;
    bUseCustomElectronID = false;

    // Check Whether official eID will be applied
    if( fElecSelection == "eidLoose") bUseLooseID = true;
    else if( fElecSelection == "eidRobustLoose") bUseRobustLooseID = true;
    else if( fElecSelection == "eidTight") bUseTightID = true;
    else if( fElecSelection == "eidRobustTight") bUseRobustTightID = true;
    else if( fElecSelection == "eidRobustHighEnergy") bUseRobustHighEnergyID = true;
    else if( fElecSelection == "simpleEleId95relIso") bUseSimpleEleId95relIsoID = true;
    else if( fElecSelection == "simpleEleId90relIso") bUseSimpleEleId90relIsoID = true;
    else if( fElecSelection == "simpleEleId85relIso") bUseSimpleEleId85relIsoID= true;
    else if( fElecSelection == "simpleEleId80relIso") bUseSimpleEleId80relIsoID= true;
    else if( fElecSelection == "simpleEleId70relIso") bUseSimpleEleId70relIsoID= true;
    else if( fElecSelection == "simpleEleId60relIso") bUseSimpleEleId60relIsoID= true;
    else if( fElecSelection == "CustomElectronID") bUseCustomElectronID= true;
    else{
      throw cms::Exception("Error") << "The ElectronSelection \"" << fElecSelection << "\" used as input in the python config file is invalid!\nPlease choose one of the following valid options:\n***** Official electron ID ***** \n\"eidLoose\", \"eidRobustLoose\", \"eidTight\", \"eidRobustTight\", \"eidRobustHighEnergy\",\n\"simpleEleId95relIso\", \"simpleEleId90relIso\", \"simpleEleId85relIso\", \"simpleEleId80relIso\", \"simpleEleId70relIso\", \"simpleEleId60relIso\".\n***** Custom electron ID ***** \n\"CustomElectronID\" \nNOTE: If you want use a custom Electron ID, use the function: \n\"GlobalElectronVeto::Data GlobalElectronVeto::analyzeCustomElecID(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"\ninstead of the default one, which is:\n\"GlobalElectronVeto::Data GlobalElectronVeto::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"" << std::endl;
    }
  }

  GlobalElectronVeto::~GlobalElectronVeto() {}

  GlobalElectronVeto::Data GlobalElectronVeto::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
    // Reset data variables
    fSelectedElectronPt = -1.0;
    fSelectedElectronPtBeforePtCut = -1.0;
    fSelectedElectronEta = -999.99;
    fSelectedElectrons.clear();

    if(!bUseCustomElectronID) return Data(this, ElectronSelection(iEvent,iSetup));
    else{
      throw cms::Exception("Error") << "The ElectronSelection \"" << fElecSelection << "\" cannot be called with the function:\n\"GlobalElectronVeto::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"\nFor this selection you must call the function:\n\"GlobalElectronVeto::analyzeCustomElecID(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"" << std::endl;      
      return Data(this, false);
    }
  }
  
  GlobalElectronVeto::Data GlobalElectronVeto::analyzeCustomElecID(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
    // Reset data variables
    fSelectedElectronPt = -1.0;
    fSelectedElectronPtBeforePtCut = -1.0;
    fSelectedElectronEta = -999.99;
    fSelectedElectrons.clear();
    
    if(bUseCustomElectronID) return Data(this, CustomElectronSelection(iEvent,iSetup));
    else{
      throw cms::Exception("Error") << "The ElectronSelection \"" << fElecSelection << "\" cannot be called with the function:\n\"GlobalElectronVeto::analyzeCustomElecID(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"\nFor this selection you must call the function:\n\"GlobalElectronVeto::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)\"" << std::endl;
      return Data(this, false);
    }
  }

  bool GlobalElectronVeto::ElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){
    // Create and attach handle to Electron Collection
    edm::Handle<edm::View<pat::Electron> > myElectronHandle;
    iEvent.getByLabel(fElecCollectionName, myElectronHandle);
    edm::PtrVector<pat::Electron> electrons = myElectronHandle->ptrVector();

    // In the case where the Electron Collection handle is empty...
    if ( !myElectronHandle->size() ) return true;

    edm::Handle <reco::GenParticleCollection> genParticles;
    iEvent.getByLabel("genParticles", genParticles);
    
    // Reset/initialise variables
    float myHighestElecPt = -1.0;
    float myHighestElecPtBeforePtCut = -1.0;
    float myHighestElecEta = -999.99;
    // 
    bool bElecPresent = false;
    bool bElecHasGsfTrkOrTrk = false;
    bool bElecPtCut = false;
    bool bElecEtaCut = false;
    bool bElecFiducialVolumeCut  = false;
    bool bElecMatchingMCelectron = false;
    bool bElecMatchingMCelectronFromW = false;
    bool bPassedElecID = false;

    // Loop over all Electrons
    for(edm::PtrVector<pat::Electron>::const_iterator iElectron = electrons.begin(); iElectron != electrons.end(); ++iElectron) {

      // keep track of the electrons analyzed
      bElecPresent = true;
      increment(fElecIDSubCountAllElectronCandidates);

      //  Keep track of the ElectronID's. Just for my information
      bool bElecIDIsLoose = false;
      bool bElecIDIsRobustLoose = false;
      bool bElecIDIsTight = false;
      bool bElecIDIsRobustTight = false;
      bool bElecIDIsRobustHighEnergy = false;

      // Simple Electron ID's return 1 or 0 (true or false)
      if( (*iElectron)->electronID("eidLoose") ) bElecIDIsLoose = true;
      if( (*iElectron)->electronID("eidRobustLoose") ) bElecIDIsRobustLoose = true;
      if( (*iElectron)->electronID("eidTight") ) bElecIDIsTight = true;
      if( (*iElectron)->electronID("eidRobustTight") ) bElecIDIsRobustTight = true;
      if( (*iElectron)->electronID("eidRobustHighEnergy") ) bElecIDIsRobustHighEnergy = true;
      // Electron ID's with working points return 0,1,2,3,4,5,6,7.
      // Note: 0=fails, 1=passes eID , 2=passes eIsolation , 3=passes eID and eIsolation, 4=passes conversion rejection
      // 5=passes conversion rejection and eID, 6=passes conversion rejection and eIsolation, 7=passes the whole selection
      float fElecIDSimpleEleId95relIso =  (*iElectron)->electronID("simpleEleId95relIso");
      float fElecIDSimpleEleId90relIso =  (*iElectron)->electronID("simpleEleId90relIso");
      float fElecIDSimpleEleId85relIso =  (*iElectron)->electronID("simpleEleId85relIso"); 
      float fElecIDSimpleEleId80relIso =  (*iElectron)->electronID("simpleEleId80relIso");
      float fElecIDSimpleEleId70relIso =  (*iElectron)->electronID("simpleEleId70relIso");
      float fElecIDSimpleEleId60relIso =  (*iElectron)->electronID("simpleEleId60relIso");

      // Take care of the Simple Electron ID counters
      if( bElecIDIsLoose) increment(fElecIDSubCountElecIDLoose);
      if( bElecIDIsRobustLoose ) increment(fElecIDSubCountElecIDRobustLoose); 
      if( bElecIDIsTight ) increment(fElecIDSubCountElecIDTight);
      if( bElecIDIsRobustTight ) increment(fElecIDSubCountElecIDRobustTight);
      if( bElecIDIsRobustHighEnergy) increment(fElecIDSubCountElecIDRobustHighEnergy);
      // Take care of the Electron ID counters (working points)
      if( fElecIDSimpleEleId95relIso == 7) increment(fElecIDSubCountSimpleEleId95relIso);
      if( fElecIDSimpleEleId90relIso == 7) increment(fElecIDSubCountSimpleEleId90relIso);
      if( fElecIDSimpleEleId85relIso == 7) increment(fElecIDSubCountSimpleEleId85relIso);
      if( fElecIDSimpleEleId80relIso == 7) increment(fElecIDSubCountSimpleEleId80relIso);
      if( fElecIDSimpleEleId70relIso == 7) increment(fElecIDSubCountSimpleEleId70relIso);
      if( fElecIDSimpleEleId60relIso == 7) increment(fElecIDSubCountSimpleEleId60relIso);

      // Obtain reference to an Electron track
      reco::GsfTrackRef myGsfTrackRef = (*iElectron)->gsfTrack(); // gsfElecs were selected to create the current PatTuples
      
      // Check that track was found
      if (myGsfTrackRef.isNull()) continue;
      bElecHasGsfTrkOrTrk = true;
      
      // Electron Variables (Pt, Eta etc..)
      float myElectronPt  = (*iElectron)->pt();
      float myElectronEta = (*iElectron)->eta();
      // float myElectronPhi = (*iElectron)->phi();

      // Fill histos with all-Electrons Pt and Eta
      hElectronPt->Fill(myElectronPt, fEventWeight.getWeight());
      hElectronEta->Fill(myElectronEta, fEventWeight.getWeight());
      hElectronPt_gsfTrack->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_gsfTrack->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());

      // Apply electron fiducial volume cut
      // Obtain reference to the superCluster
      reco::SuperClusterRef mySuperClusterRef = (*iElectron)->superCluster(); 
      
      // Check that superCluster was found
      if ( mySuperClusterRef.isNull()) continue;

      hElectronEta_superCluster->Fill(mySuperClusterRef->eta(), fEventWeight.getWeight());
     
      if ( fabs(mySuperClusterRef->eta()) > 1.4442 && fabs(mySuperClusterRef->eta()) < 1.566) continue;
      bElecFiducialVolumeCut = true;


      bElecHasGsfTrkOrTrk = true;   
      // 1) Apply Electron ID (choose low efficiency => High Purity)
      bool thisPassedID = false;
      if( (bUseLooseID) && (bElecIDIsLoose) ) thisPassedID = true;
      else if( (bUseRobustLooseID ) && (bElecIDIsRobustLoose) ) thisPassedID = true;
      else if( (bUseTightID) && (bElecIDIsTight) ) thisPassedID = true;
      else if( (bUseRobustTightID)         && (bElecIDIsRobustTight) ) thisPassedID = true;
      else if( (bUseRobustHighEnergyID)    && (bElecIDIsRobustHighEnergy) ) thisPassedID = true;
      else if( (bUseSimpleEleId95relIsoID) && (fElecIDSimpleEleId95relIso == 7) ) thisPassedID = true;
      else if( (bUseSimpleEleId90relIsoID) && (fElecIDSimpleEleId90relIso == 7) ) thisPassedID = true;
      else if( (bUseSimpleEleId85relIsoID) && (fElecIDSimpleEleId85relIso == 7) ) thisPassedID = true;
      else if( (bUseSimpleEleId80relIsoID) && (fElecIDSimpleEleId80relIso == 7) ) thisPassedID = true;
      else if( (bUseSimpleEleId70relIsoID) && (fElecIDSimpleEleId70relIso == 7) ) thisPassedID = true;
      else if( (bUseSimpleEleId60relIsoID) && (fElecIDSimpleEleId60relIso == 7) ) thisPassedID = true;
      
      if(!thisPassedID) continue;
      fSelectedElectrons.push_back(*iElectron);
      bPassedElecID = true;

      hElectronEta_identified->Fill(myElectronEta);

      if(std::abs(myElectronEta) < fElecEtaCut) {
        myHighestElecPtBeforePtCut = std::max(myHighestElecPtBeforePtCut, myElectronPt);
      hElectronPt_identified_eta->Fill(myElectronPt);
      }

      // 2) Apply Pt cut requirement
      if (myElectronPt < fElecPtCut) continue;
      bElecPtCut = true;


      // 3) Apply Eta cut requirement      
      if (std::abs(myElectronEta) >= fElecEtaCut) continue;
      bElecEtaCut = true;



      // If Electron survives all cuts (1->3) then it is considered an isolated Electron. Now find the max Electron Pt.
	if (thisPassedID && myElectronPt > myHighestElecPt) {
	  myHighestElecPt = myElectronPt;
	  myHighestElecEta = myElectronEta;
	}
      
      // Fill histos after Selection
      hElectronPt_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_AfterSelection->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());
      hElectronPt_gsfTrack_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_gsfTrack_AfterSelection->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());
      
      // Selection purity from MC
      if(!iEvent.isRealData()) {
        for (size_t i=0; i < genParticles->size(); ++i){  
          const reco::Candidate & p = (*genParticles)[i];
          const reco::Candidate & electron = (**iElectron);
          int status = p.status();
          double deltaR = ROOT::Math::VectorUtil::DeltaR( p.p4() , electron.p4() );
          if ( deltaR > 0.05 || status != 1) continue;
          bElecMatchingMCelectron = true;
          hElectronPt_matchingMCelectron->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
          hElectronEta_matchingMCelectron->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());
          int id = p.pdgId();
          if ( abs(id) == 11 ) {
            int numberOfTauMothers = p.numberOfMothers(); 
            for (int im=0; im < numberOfTauMothers; ++im){  
              const reco::GenParticle* dparticle = dynamic_cast<const reco::GenParticle*>(p.mother(im));
              if ( !dparticle) continue;
              int idmother = dparticle->pdgId();
              if ( abs(idmother) == 24 ) {
                bElecMatchingMCelectronFromW = true;
                hElectronPt_matchingMCelectronFromW->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
                hElectronEta_matchingMCelectronFromW->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());
              }
            }
          }
        }
      }
     


      
    }//eof: for(pat::ElectronCollection::const_iterator iElectron = myElectronHandle->begin(); iElectron != myElectronHandle->end(); ++iElectron) {
    
    if(bElecPresent) {
      increment(fElecSelectionSubCountElectronPresent);
      if(bElecHasGsfTrkOrTrk) { 
        increment(fElecSelectionSubCountElectronHasGsfTrkOrTrk);
        if(bElecPtCut) { 
          increment(fElecSelectionSubCountPtCut);
          if(bElecEtaCut) {
            increment(fElecSelectionSubCountEtaCut);
	    if(bElecFiducialVolumeCut) {
	      increment(fElecSelectionSubCountFiducialVolumeCut);
	      if(bPassedElecID) {
		increment(fElecSelectionSubCountElectronSelection);
		if(bElecMatchingMCelectron) {
		  increment(fElecSelectionSubCountMatchingMCelectron);
		  if(bElecMatchingMCelectronFromW) {
		    increment(fElecSelectionSubCountMatchingMCelectronFromW);
		  }
		}
	      }
            }
          }
        }
      }
    }

    // Make a boolean that describes whether a Global Electron (passing all selection criteria) is found.
    bool bDecision = bElecPresent*bElecHasGsfTrkOrTrk*bElecPtCut*bElecEtaCut*bPassedElecID*bElecFiducialVolumeCut;

    // Now store the highest Electron Pt and Eta
    fSelectedElectronPt = myHighestElecPt;
    fSelectedElectronEta = myHighestElecEta;
    
    // If a Global Electron (passing all selection criteria) is found, do not increment counter. Return false.
    if(bDecision)
      return false;
    // Otherwise increment counter and return true.
    else 
      increment(fGlobalElectronVetoCounter);
    return true;
    
  }//eof: bool GlobalElectronVeto::ElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){

  bool GlobalElectronVeto::CustomElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){
    
    // Create and attach handle to Electron Collection
    edm::Handle<std::vector<pat::Electron> > myElectronHandle;
    iEvent.getByLabel(fElecCollectionName, myElectronHandle);

    // Create and attach handle to All Tracks collection
    edm::Handle<reco::TrackCollection> myTracksHandle;
    iEvent.getByLabel("generalTracks", myTracksHandle);

    // Create and attach handle to Muon Collection [Needed for Selection of Electrons - Requirement 5) ]
    edm::Handle<std::vector<pat::Muon> > myMuonHandle;
    iEvent.getByLabel("selectedPatMuons", myMuonHandle); // Select muon id as GlobalMuonPromptTight?

    // Get the Magnetic Field 
    // FIXME: Use scale Current<->BField scale factor. see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/ConversionBackgroundRejection
    edm::ESHandle<MagneticField> myMagneticFieldESHandle;
    iSetup.get<IdealMagneticFieldRecord>().get(myMagneticFieldESHandle);
    double myBFieldInZAtZeroZeroZero = myMagneticFieldESHandle->inTesla(GlobalPoint(0.0,0.0,0.0)).z();
    // double myBFieldInZAtOneOneOne = myMagneticFieldESHandle->inTesla(GlobalPoint(1.0,1.0,1.0)).z();

    /* FIX ME
    // Get beam spot
    edm::Handle<reco::BeamSpot> BeamSpotHandle;
    iEvent.getByLabel("offlineBeamSpot", BeamSpotHandle);
    const reco::BeamSpot *myBeamSpot = BeamSpotHandle.product();
    const math::XYZPoint myBeamSpotPosition = myBeamSpot->position();
    // float impactParameter = fabs( (*iElectron)->gsfTrack()->dxy(myBeamSpotPosition) );
    FIX ME */
    
    // In the case where the Electron Collection handle is empty...
    if ( !myElectronHandle->size() ){
      // std::cout << "WARNING: Electron handle for '" << fElecCollectionName << " is empty! Skipping rest of selection and returning true ..." << std::endl;
      return true;
    }
    // In the case where the GeneralTracks Collection handle is empty...
    if ( !myTracksHandle->size() ){
      std::cout << "WARNING: GeneralTracks handle for \"generalTrackss\" Collection empty! This Collection is required for \"Photon Conversion Rejection\". Skipping rest of selection and returning true..." << std::endl;
      return true;
    }
    // In the case where the Muon Collection handle is empty...
    if ( !myMuonHandle->size() ){
      // std::cout << "WARNING: Muon handle for \"selectedPatMuons\" Collection is empty! This Collection is required for calculating \" DeltaR between the Electron candidate and Global or Tracker Muon\" ". << std::endl;
      // return true;
    }
    

    // Reset/initialise variables
    float myHighestElecPt = -1.0;
    float myHighestElecEta = -999.99;
    //
    bool bElecPresent = false;
    bool bElecHasGsfTrkOrTrk = false;
    bool bElecPtCut = false;
    bool bElecEtaCut = false;
    bool bElecNLostHitsInTrkerCut = false;
    bool bElecElectronDeltaCotThetaCut = false;
    bool bElecElectronDistanceCut = false;
    bool bElecRelIsolationR03Cut = false;
    bool bElecTransvImpactParCut = false;
    bool bElecDeltaRFromGlobalOrTrkerMuonCut = false;
    
    // Loop over all Electrons
    for(pat::ElectronCollection::const_iterator iElectron = myElectronHandle->begin(); iElectron != myElectronHandle->end(); ++iElectron) {

      // For Photon Conversion Rejection (Searching for the partner conversion track in the GeneralTrack Collection
      ConversionFinder convFinder;
      ConversionInfo convInfo = convFinder.getConversionInfo(*iElectron, myTracksHandle, myBFieldInZAtZeroZeroZero );
      // Define the minimal distance in r-phi plane between the electron and its closest opposite sign track. DeltaR > 0.02
      double myElectronDistance = convInfo.dist();
      // Define the minimal distance between the electron and its closest opposite sign track |Delta cot(Theta) | > 0.02
      double myElectronDeltaCotTheta = convInfo.dcot();
      // double convradius = convInfo.radiusOfConversion(); // not used in code
      math::XYZPoint convPoint = convInfo.pointOfConversion();
      
      // keep track of the electrons analyzed
      bElecPresent = true;
      increment(fElecIDSubCountAllElectronCandidates);

      // Uncomment the piece of code below to cout all eID and result on current electron candidate
      /* 
      const std::vector<pat::Electron::IdPair>& myElectronIDs = (*iElectron).electronIDs();
      int myPairs = myElectronIDs.size();
      // Loop over all tags to see which ones were satisfied
      for (int i = 0; i < myPairs; ++i) {
	std::string myElecIDtag = myElectronIDs[i].first;
	float myElecIDresult = myElectronIDs[i].second;
	std::cout << "idtag=" << myElecIDtag << ", result=" << myElecIDresult << std::endl;
      }//eof: for (int i = 0; i < myPairs; ++i) {
      */

      //  Keep track of the ElectronID's. Just for my information
      bool bElecIDIsLoose = false;
      bool bElecIDIsRobustLoose = false;
      bool bElecIDIsTight = false;
      bool bElecIDIsRobustTight = false;
      bool bElecIDIsRobustHighEnergy = false;
      bool bElecNoSimpleID = false;
      bool bElecAllSimpleIDs = false;

      if( (*iElectron).electronID("eidLoose") ) bElecIDIsLoose = true;
      if( (*iElectron).electronID("eidRobustLoose") ) bElecIDIsRobustLoose = true;
      if( (*iElectron).electronID("eidTight") ) bElecIDIsTight = true;
      if( (*iElectron).electronID("eidRobustTight") ) bElecIDIsRobustTight = true;
      if( (*iElectron).electronID("eidRobustHighEnergy") ) bElecIDIsRobustHighEnergy = true;
      else{
	// std::cout << "Other electron ID found..." << std::endl;
      }
      // Now take care of eID counters
      if( (!bElecIDIsLoose) && (!bElecIDIsRobustLoose) && (!bElecIDIsTight) && (!bElecIDIsRobustTight) && (!bElecIDIsRobustHighEnergy) ){
	bElecNoSimpleID = true;}
      else if( (bElecIDIsLoose) && (bElecIDIsRobustLoose) && (bElecIDIsTight) && (bElecIDIsRobustTight) && (bElecIDIsRobustHighEnergy) ){
	bElecAllSimpleIDs = true;}
      else if( (bElecIDIsLoose) && (!bElecIDIsRobustLoose) && (!bElecIDIsTight) && (!bElecIDIsRobustTight) && (!bElecIDIsRobustHighEnergy) ){
	increment(fElecIDSubCountElecIDLoose);}
      else if( (!bElecIDIsLoose) && (bElecIDIsRobustLoose) && (!bElecIDIsTight) && (!bElecIDIsRobustTight) && (!bElecIDIsRobustHighEnergy) ){
	increment(fElecIDSubCountElecIDRobustLoose);}
      else if( (!bElecIDIsLoose) && (!bElecIDIsRobustLoose) && (bElecIDIsTight) && (!bElecIDIsRobustTight) && (!bElecIDIsRobustHighEnergy) ){
	increment(fElecIDSubCountElecIDTight);}
      else if( (!bElecIDIsLoose) && (!bElecIDIsRobustLoose) && (!bElecIDIsTight) && (bElecIDIsRobustTight) && (!bElecIDIsRobustHighEnergy) ){
	increment(fElecIDSubCountElecIDRobustTight);}
      else if( (!bElecIDIsLoose) && (!bElecIDIsRobustLoose) && (!bElecIDIsTight) && (!bElecIDIsRobustTight) && (bElecIDIsRobustHighEnergy) ){
	increment(fElecIDSubCountElecIDRobustHighEnergy);}
      else {
	// std::cout << "\n You forgot something !" << std::endl;
      }

      // Obtain reference to an Electron track
      // reco::TrackRef myTrackRef = (*iElectron).track(); // not in the pattuples 
      reco::GsfTrackRef myGsfTrackRef = (*iElectron).gsfTrack(); // gsfElecs were selected to create the current PatTuples
      
      // Check that track was found
      if (myGsfTrackRef.isNull()){
	// std::cout << "myGsfTrackRef.isNull()" << std::endl;
	continue;
      }
      bElecHasGsfTrkOrTrk = true;
      
      // Electron Variables (Pt, Eta etc..)
      // float myElectronPt = myGsfTrackRef->pt();  // float myElectronPt = (*iElectron).p4().Pt();
      // float myElectronEta = myGsfTrackRef->eta();
      // float myElectronPhi = myGsfTrackRef->phi();
      float myElectronPt  = (*iElectron).pt();  // float myElectronPt = (*iElectron).p4().Pt();
      float myElectronEta = (*iElectron).eta();
      float myElectronPhi = (*iElectron).phi();
      float myTrackIso =  (*iElectron).dr03TkSumPt();
      float myEcalIso  =  (*iElectron).dr03EcalRecHitSumEt();
      float myHcalIso  =  (*iElectron).dr03HcalTowerSumEt();
      int iNLostHitsInTrker = myGsfTrackRef->hitPattern().numberOfLostHits();
      // float impactParameter = fabs( (*iElectron).gsfTrack()->dxy(myBeamSpotPosition) ); // FIX ME?
      // float myTransverseImpactPar = fabs( (*iElectron).gsfTrack()->dxy() ); // FIX ME?
      float myTransverseImpactPar = fabs( (*iElectron).dB() );  // This is the transverse IP w.r.t to beamline.
      float myRelativeIsolation = (myTrackIso + myEcalIso + myHcalIso)/(myElectronPt); // isolation cones are dR=0.3 

      // Fill histos with all-Electrons Pt and Eta
      hElectronPt->Fill(myElectronPt, fEventWeight.getWeight());
      hElectronEta->Fill(myElectronEta, fEventWeight.getWeight());
      hElectronPt_gsfTrack->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_gsfTrack->Fill(myGsfTrackRef->eta(), fEventWeight.getWeight());

      // 1) Apply Pt and Eta cut requirements
      if (myElectronPt < fElecPtCut) continue;
      bElecPtCut = true;
      
      if (myElectronPt < fElecPtCut) continue;
      bElecEtaCut = true;
      
      // 2) Validation of simple cut based eID (choose low efficiency => High Purity)
      // Not implemented.

      // 3) Photon conversion rejection (gamma->e+e-)
      // If an electron has: |dist| < 0.02 && |delta cot(theta)| < 0.02 then it is regarded as coming from a conversion, and rejected
      // a) Number of lost hits in the tracker
      if(iNLostHitsInTrker > 2) continue;
      bElecNLostHitsInTrkerCut = true;
      // b) Minimal distance between the electron and its closest opposite sign track (|Delta cos(theta)|)
      if(myElectronDeltaCotTheta < 0.02) continue;
      bElecElectronDeltaCotThetaCut = true;
      // c) Minimal distance between the electron and its closest opposite sign track in r-phi plane
      if( myElectronDistance < 0.02) continue;
      bElecElectronDistanceCut = true;

      // 4) Transverse Impact Parameter wrt BeamSpot, applied on the gsfTrack of the Electron candidate
      hElectronImpactParameter->Fill(myTransverseImpactPar,fEventWeight.getWeight()); 
      if(myTransverseImpactPar > 0.04) continue;
      bElecTransvImpactParCut = true;
      
      // 5) DeltaR between Electron candidate and any Global or Tracker Muonin the event whose number of hits in the inner tracker > 10
      // Perform Muon Loop here to save cpu time
      float myElectronMuonDeltaR = 999.99;

      // Loop over all Muons
      for(pat::MuonCollection::const_iterator iMuon = myMuonHandle->begin(); iMuon != myMuonHandle->end(); ++iMuon) {
	// Check that there are muons present
	if(!myMuonHandle->size()){
	  continue;
	}
	
	// Obtain reference to a Muon track
	reco::TrackRef myGlobalTrackRef = (*iMuon).globalTrack();
	reco::TrackRef myInnerTrackRef = (*iMuon).innerTrack(); // inner tracks give best resolution for muons with Pt up to 200 GeV/c

      // Check that track was found for both Global AND Tracker Muons
      if ( myInnerTrackRef.isNull() || myGlobalTrackRef.isNull() ){
	continue; 
      }

      // Muon Variables (Pt, Eta etc..)
      // float myMuonPt = myInnerTrackRef->pt();
      float myMuonEta = myInnerTrackRef->eta();
      float myMuonPhi = myInnerTrackRef->phi();
      int myInnerTrackNTrkHits   = myInnerTrackRef->hitPattern().numberOfValidTrackerHits();
      
      // Demand that the Muon is both a "GlobalMuon" And a "TrackerMuon"
      if( (!(*iMuon).isGlobalMuon()) || (!(*iMuon).isTrackerMuon()) ) continue;

      // Demand Global or Tracker Muons to have at least 10 hits in the inner tracker
      if ( myInnerTrackNTrkHits < 10) continue;

      // Calculate DeltaR between Electron candidate and Global or Tracker Muon
      myElectronMuonDeltaR = deltaR( myMuonEta, myMuonPhi,myElectronEta, myElectronPhi); 

    }//eof: for(pat::MuonCollection::const_iterator iMuon = myMuonHandle->begin(); iMuon != myMuonHandle->end(); ++iMuon) {
      if(myElectronMuonDeltaR < 0.1) continue;
      bElecDeltaRFromGlobalOrTrkerMuonCut = true;
      
      // 6) Relative Isolation for Electron candidate
      if(myRelativeIsolation > 0.15) continue;
      bElecRelIsolationR03Cut = true;

      // If Electron survives all cuts (1->6) then it is considered an isolated Electron. Now find the max Electron Pt.
      if (myElectronPt > myHighestElecPt) {
	myHighestElecPt = myElectronPt;
	myHighestElecEta = myElectronEta;
	// std::cout << "myHighestElecPt = " << myHighestElecPt << ", myHighestElecEta = " << myHighestElecEta << std::endl;
      }
      
      // Fill histos after Selection
      hElectronPt_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronPt_gsfTrack_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      hElectronEta_gsfTrack_AfterSelection->Fill(myGsfTrackRef->pt(), fEventWeight.getWeight());
      
    }//eof: for(pat::ElectronCollection::const_iterator iElectron = myElectronHandle->begin(); iElectron != myElectronHandle->end(); ++iElectron) {
    
    if(bElecPresent) increment(fElecSelectionSubCountElectronPresent);

    if(bElecHasGsfTrkOrTrk) increment(fElecSelectionSubCountElectronHasGsfTrkOrTrk);
    
    if(bElecPtCut) increment(fElecSelectionSubCountPtCut);
    
    if(bElecEtaCut) increment(fElecSelectionSubCountEtaCut);
    
    if(bElecNLostHitsInTrkerCut) increment(fElecSelectionSubCountNLostHitsInTrkerCut);
    
    if(bElecElectronDeltaCotThetaCut) increment(fElecSelectionSubCountmyElectronDeltaCotThetaCut);
    
    if(bElecElectronDistanceCut) increment(fElecSelectionSubCountmyElectronDistanceCut);
    
    if(bElecTransvImpactParCut) increment(fElecSelectionSubCountTransvImpactParCut);
    
    if(bElecDeltaRFromGlobalOrTrkerMuonCut) increment(fElecSelectionSubCountDeltaRFromGlobalOrTrkerMuonCut);

    if(bElecRelIsolationR03Cut) increment(fElecSelectionSubCountRelIsolationR03Cut);
    
    // Make a boolean that describes whether a Global Electron (passing all selection criteria) is found.
    bool bDecision = bElecPresent*bElecHasGsfTrkOrTrk*bElecPtCut*bElecEtaCut*bElecNLostHitsInTrkerCut*bElecElectronDeltaCotThetaCut*bElecElectronDistanceCut*bElecRelIsolationR03Cut*bElecTransvImpactParCut*bElecDeltaRFromGlobalOrTrkerMuonCut;

    // Now store the highest Electron Pt and Eta
    fSelectedElectronPt = myHighestElecPt;
    fSelectedElectronEta = myHighestElecEta;
    // std::cout << "fSelectedElectronPt = " << fSelectedElectronPt << ", fSelectedElectronEta = " << fSelectedElectronEta << std::endl;
    
    // If a Global Electron (passing all selection criteria) is found, do not increment counter. Return false.
    if(bDecision) return false;

    // Otherwise increment counter and return true.
    else increment(fGlobalElectronVetoCounter);
    return true;
    
  }//eof: bool GlobalElectronVeto::CustomElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){

}//eof: namespace HPlus {
