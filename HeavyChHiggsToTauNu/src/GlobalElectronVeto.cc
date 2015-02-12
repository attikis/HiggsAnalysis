#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/GlobalElectronVeto.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/HistoWrapper.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/GenParticleAnalysis.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"
#include "Math/GenVector/VectorUtil.h"

#include "DataFormats/EgammaCandidates/interface/ConversionFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include <string>

namespace HPlus {
  GlobalElectronVeto::Data::Data(const GlobalElectronVeto *globalElectronVeto, bool passedEvent):
    fGlobalElectronVeto(globalElectronVeto), fPassedEvent(passedEvent) {}
  GlobalElectronVeto::Data::~Data() {}
  
  GlobalElectronVeto::GlobalElectronVeto(const edm::ParameterSet& iConfig, const edm::InputTag& vertexSrc, HPlus::EventCounter& eventCounter, HPlus::HistoWrapper& histoWrapper):
    fElecCollectionName(iConfig.getUntrackedParameter<edm::InputTag>("ElectronCollectionName")),
    fVertexSrc(vertexSrc),
    fConversionSrc(iConfig.getUntrackedParameter<edm::InputTag>("conversionSrc")),
    fBeamspotSrc(iConfig.getUntrackedParameter<edm::InputTag>("beamspotSrc")),
    fRhoSrc(iConfig.getUntrackedParameter<edm::InputTag>("rhoSrc")),
    fElecSelection(iConfig.getUntrackedParameter<std::string>("ElectronSelection")),
    fElecPtCut(iConfig.getUntrackedParameter<double>("ElectronPtCut")),
    fElecEtaCut(iConfig.getUntrackedParameter<double>("ElectronEtaCut")),
    fElecSelectionSubCountAllEvents(eventCounter.addSubCounter("GlobalElectron Selection", "All events")),
    fElecSelectionSubCountElectronPresent(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Present")),
    fElecSelectionSubCountElectronHasGsfTrkOrTrk(eventCounter.addSubCounter("GlobalElectron Selection", "Electron has gsfTrack or track")),
    fElecSelectionSubCountFiducialVolumeCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron fiducial volume")),
    fElecSelectionSubCountId(eventCounter.addSubCounter("GlobalElectron Selection", "Electron ID")),
    fElecSelectionSubCountPtCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Pt " )),
    fElecSelectionSubCountEtaCut(eventCounter.addSubCounter("GlobalElectron Selection", "Electron Eta")),
    fElecSelectionSubCountSelected(eventCounter.addSubCounter("GlobalElectron Selection", "Electron selected")),
    fElecSelectionSubCountMatchingMCelectron(eventCounter.addSubCounter("GlobalElectron Selection","Electron matching MC electron")),
    fElecSelectionSubCountMatchingMCelectronFromW(eventCounter.addSubCounter("GlobalElectron Selection","Electron matching MC electron From W"))
  {
    edm::Service<TFileService> fs;
    TFileDirectory myDir = fs->mkdir("GlobalElectronVeto");

    hElectronPt  = histoWrapper.makeTH<TH1F>(HistoWrapper::kInformative, myDir, "GlobalElectronPt", "GlobalElectronPt;isolated electron p_{T}, GeV/c;N_{electrons} / 5 GeV/c", 80, 0.0, 400.0);
    hElectronEta = histoWrapper.makeTH<TH1F>(HistoWrapper::kInformative, myDir, "GlobalElectronEta", "GlobalElectronEta;isolated electron #eta;N_{electrons} / 0.1", 60, -3.0, 3.0);
    hElectronEta_identified = histoWrapper.makeTH<TH1F>(HistoWrapper::kVital, myDir, "GlobalElectronEta_identified", "GlobalElectronEta_identified;isolated electron #eta;N_{electrons} / 0.1", 60, -3.0, 3.0);
    hElectronPt_identified  = histoWrapper.makeTH<TH1F>(HistoWrapper::kVital, myDir, "GlobalElectronPt_identified", "GlobalElectronPt;isolated electron p_{T}, GeV/c;N_{electrons} / 5 GeV/c", 80, 0.0, 400.0);

    hElectronPt_matchingMCelectron  = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_matchingMCelectron", "GlobalElectronPt_matchingMCelectron", 400, 0.0, 400.0);
    hElectronEta_matchingMCelectron = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronEta_matchingMCelectron", "GlobalElectronEta_matchingMCelectron", 400, -3.0, 3.0);
    hElectronPt_matchingMCelectronFromW  = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_matchingMCelectronFromW", "GlobalElectronPt_matchingMCelectronFromW", 400, 0.0, 400.0);
    hElectronEta_matchingMCelectronFromW = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronEta_matchingMCelectronFromW", "GlobalElectronEta_matchingMCelectronFromW", 400, -3.0, 3.0);
    hElectronPt_gsfTrack  = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_gsfTrack", "GlobalElectronPt_gsfTrack", 400, 0.0, 400.0);
    hElectronEta_gsfTrack = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronEta_gsfTrack", "GlobalElectronEta_gsfTrack", 300, -3.0, 3.0);
    hElectronEta_superCluster = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronEta_superCluster", "GlobalElectronEta_superCluster", 60, -3.0, 3.0);
    hElectronPt_AfterSelection = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_AfterSelection", "GlobalElectronPt_AfterSelection", 100, 0.0, 200.0);
    hElectronEta_AfterSelection = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_AfterSelection", "GlobalElectronEta_AfterSelection", 60, -3.0, 3.0);
    hElectronPt_gsfTrack_AfterSelection = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_gsfTrack_AfterSelection", "GlobalElectronPt_gsfTrack_AfterSelection", 100, 0.0, 200.0);
    hElectronEta_gsfTrack_AfterSelection = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "GlobalElectronPt_gsfTrack_AfterSelection", "GlobalElectronPt_gsTrack_AfterSelection", 60, -3.0, 3.0);
    hElectronImpactParameter = histoWrapper.makeTH<TH1F>(HistoWrapper::kDebug, myDir, "ElectronImpactParameter", "ElectronImpactParameter", 100, 0.0, 0.1);

    hElectronEtaPhiForSelectedElectrons = histoWrapper.makeTH<TH2F>(HistoWrapper::kInformative, myDir,
        "ElectronEtaPhiForSelectedElectrons", "ElectronEtaPhiForSelectedElectrons;electron #eta; electronu #phi",
        60, -3.0, 3.0, 72, -3.14159265, 3.14159265);
    hMCElectronEtaPhiForPassedEvents = histoWrapper.makeTH<TH2F>(HistoWrapper::kInformative, myDir,
        "MCElectronEtaPhiForPassedEvents", "MCElectronEtaPhiForPassedEvents;MC electron #eta; MC electronu #phi",
        60, -3.0, 3.0, 72, -3.14159265, 3.14159265);

    // Check Whether official eID will be applied
    if (fElecSelection == "VETO") fElectronIdEnumerator = EgammaCutBasedEleId::VETO;
    else{
      throw cms::Exception("Error") << "The ElectronSelection \"" << fElecSelection << "\" used as input in the python config file is invalid!\nPlease choose one of the following valid options:" << std::endl
        << "'VETO'" << std::endl;
    }
  }

  GlobalElectronVeto::~GlobalElectronVeto() {}

  GlobalElectronVeto::Data GlobalElectronVeto::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
    // Reset data variables
    fSelectedElectronPt = -1.0;
    fSelectedElectronPtBeforePtCut = -1.0;
    fSelectedElectronEta = -999.99;
    fSelectedElectrons.clear();

    return Data(this, ElectronSelection(iEvent,iSetup));
  }

  bool GlobalElectronVeto::ElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){
    // Create and attach handle to Electron Collection
    edm::Handle<edm::View<pat::Electron> > myElectronHandle;
    iEvent.getByLabel(fElecCollectionName, myElectronHandle);
    edm::PtrVector<pat::Electron> electrons = myElectronHandle->ptrVector();

    increment(fElecSelectionSubCountAllEvents);
    // In the case where the Electron Collection handle is empty...
    if ( !myElectronHandle->size() ) return true;

    edm::Handle <reco::GenParticleCollection> genParticles;
    iEvent.getByLabel("genParticles", genParticles); // FIXME: bad habbit to hard-code InputTags

    // Get Conversions, Vertices, BeamSpot, and Rho
    edm::Handle<reco::ConversionCollection> hConversion;
    iEvent.getByLabel(fConversionSrc, hConversion);
    edm::Handle<reco::VertexCollection> hVertex;
    iEvent.getByLabel(fVertexSrc, hVertex);
    edm::Handle<reco::BeamSpot> hBeamspot;
    iEvent.getByLabel(fBeamspotSrc, hBeamspot);
    edm::Handle<double> hRho;
    iEvent.getByLabel(fRhoSrc, hRho);

    // Reset/initialise variables
    float myHighestElecPt = -1.0;
    float myHighestElecPtBeforePtCut = -1.0;
    float myHighestElecEta = -999.99;
    // 
    bool bElecPresent = false;
    bool bElecHasGsfTrkOrTrk = false;
    bool bElecFiducialVolumeCut  = false;
    bool bPassedElecID = false;
    bool bElecPtCut = false;
    bool bElecEtaCut = false;
    bool bElecMatchingMCelectron = false;
    bool bElecMatchingMCelectronFromW = false;
    bool bElectronSelected = false;

    // Loop over all Electrons
    for(edm::PtrVector<pat::Electron>::const_iterator iElectron = electrons.begin(); iElectron != electrons.end(); ++iElectron) {
      // keep track of the electrons analyzed
      bElecPresent = true;
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
      hElectronPt->Fill(myElectronPt);
      hElectronEta->Fill(myElectronEta);
      hElectronPt_gsfTrack->Fill(myGsfTrackRef->pt());
      hElectronEta_gsfTrack->Fill(myGsfTrackRef->eta());

      // Apply electron fiducial volume cut
      // Obtain reference to the superCluster
      reco::SuperClusterRef mySuperClusterRef = (*iElectron)->superCluster();

      // Check that superCluster was found
      if ( mySuperClusterRef.isNull()) continue;

      hElectronEta_superCluster->Fill(mySuperClusterRef->eta());

      if ( fabs(mySuperClusterRef->eta()) > 1.4442 && fabs(mySuperClusterRef->eta()) < 1.566) continue;
      bElecFiducialVolumeCut = true;

      // 1) Apply Electron ID (choose low efficiency => High Purity)
      bPassedElecID = EgammaCutBasedEleId::PassWP(fElectronIdEnumerator, **iElectron, hConversion, *hBeamspot, hVertex,
                                                  (*iElectron)->chargedHadronIso(), (*iElectron)->photonIso(), (*iElectron)->neutralHadronIso(),
                                                  *hRho);
      //std::cout << "Electron " << (iElectron-electrons.begin()) << "/" << electrons.size() << ": pass veto: " << bVeto << std::endl;
      if(!bPassedElecID) continue;
      fSelectedElectrons.push_back(*iElectron);

      hElectronEta_identified->Fill(myElectronEta);

      if(std::abs(myElectronEta) < fElecEtaCut) {
        myHighestElecPtBeforePtCut = std::max(myHighestElecPtBeforePtCut, myElectronPt);
      hElectronPt_identified->Fill(myElectronPt);
      }

      // 2) Apply Pt cut requirement
      if (myElectronPt < fElecPtCut) continue;
      bElecPtCut = true;


      // 3) Apply Eta cut requirement      
      if (std::abs(myElectronEta) >= fElecEtaCut) continue;
      bElecEtaCut = true;

      // If Electron survives all cuts (1->3) then it is considered an isolated Electron. Now find the max Electron Pt.
      if (myElectronPt > myHighestElecPt) {
        myHighestElecPt = myElectronPt;
        myHighestElecEta = myElectronEta;
      }
      bElectronSelected = true;
      // Fill histos after Selection
      hElectronPt_AfterSelection->Fill(myGsfTrackRef->pt());
      hElectronEta_AfterSelection->Fill(myGsfTrackRef->eta());
      hElectronPt_gsfTrack_AfterSelection->Fill(myGsfTrackRef->pt());
      hElectronEta_gsfTrack_AfterSelection->Fill(myGsfTrackRef->eta());
      hElectronEtaPhiForSelectedElectrons->Fill((*iElectron)->eta(), (*iElectron)->phi());
      // Selection purity from MC
      if(!iEvent.isRealData()) {
        for (size_t i=0; i < genParticles->size(); ++i){  
          const reco::Candidate & p = (*genParticles)[i];
          const reco::Candidate & electron = (**iElectron);
          int status = p.status();
          double deltaR = ROOT::Math::VectorUtil::DeltaR( p.p4() , electron.p4() );
          if ( deltaR > 0.05 || status != 1) continue;
          bElecMatchingMCelectron = true;
          hElectronPt_matchingMCelectron->Fill(myGsfTrackRef->pt());
          hElectronEta_matchingMCelectron->Fill(myGsfTrackRef->eta());
          int id = p.pdgId();
          if ( std::abs(id) == 11 ) {
            int numberOfTauMothers = p.numberOfMothers(); 
            for (int im=0; im < numberOfTauMothers; ++im){  
              const reco::GenParticle* dparticle = dynamic_cast<const reco::GenParticle*>(p.mother(im));
              if ( !dparticle) continue;
              int idmother = dparticle->pdgId();
              if ( std::abs(idmother) == 24 ) {
                bElecMatchingMCelectronFromW = true;
                hElectronPt_matchingMCelectronFromW->Fill(myGsfTrackRef->pt());
                hElectronEta_matchingMCelectronFromW->Fill(myGsfTrackRef->eta());
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
        if(bElecFiducialVolumeCut) {
          increment(fElecSelectionSubCountFiducialVolumeCut);
          if(bPassedElecID) {
            increment(fElecSelectionSubCountId);
            if(bElecPtCut) {
              increment(fElecSelectionSubCountPtCut);
              if(bElecEtaCut) {
                increment(fElecSelectionSubCountEtaCut);
                increment(fElecSelectionSubCountSelected);
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
    

    // Now store the highest Electron Pt and Eta
    fSelectedElectronPt = myHighestElecPt;
    fSelectedElectronEta = myHighestElecEta;

    // If a Global Electron (passing all selection criteria) is found, do not increment counter. Return false.
    if(bElectronSelected)
      return false;
    // Otherwise increment counter and return true.
    else {
      if(!iEvent.isRealData()) {
        for (size_t i=0; i < genParticles->size(); ++i) {
          const reco::Candidate & p = (*genParticles)[i];
          if (p.status() != 1) continue;
          if (std::abs(p.pdgId()) != 11) continue;
          if (p.pt() < fElecPtCut) continue;
          // Plot eta-phi map of MC electrons above pT threshold
          hMCElectronEtaPhiForPassedEvents->Fill(p.eta(), p.phi());
        }
      }
    }

    return true;
  }//eof: bool GlobalElectronVeto::ElectronSelection(const edm::Event& iEvent, const edm::EventSetup& iSetup){

}//eof: namespace HPlus {