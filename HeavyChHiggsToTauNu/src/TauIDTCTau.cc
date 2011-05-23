#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TauIDTCTau.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/MakeTH.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"

#include "TH1F.h"

namespace HPlus {
  TauIDTCTau::TauIDTCTau(const edm::ParameterSet& iConfig, EventCounter& eventCounter, EventWeight& eventWeight, int prongCount, std::string label, TFileDirectory& myDir):
    TauIDBase(iConfig, eventCounter, eventWeight, label+"_TCTau", myDir)
  {
    edm::Service<TFileService> fs;

    // Initialize counter objects for tau isolation
    fIDIsolation = fCounterPackager.addSubCounter(label+"_TCTau", "Isolation", 0);
    // Histograms
    
    // Initialize rest counter objects 
    createSelectionCounterPackagesBeyondIsolation(prongCount);
  }

  TauIDTCTau::~TauIDTCTau() { }

  bool TauIDTCTau::passLeadingTrackCuts(const edm::Ptr<pat::Tau> tau) {
    // Check that leading track exists
    if (tau->leadTrack().isNull()) return false;
    fCounterPackager.incrementSubCount(fIDLdgTrackExistsCut);
    // Leading track pt cut
    double myLdgTrackPt = tau->leadTrack()->pt();
    fCounterPackager.fill(fIDLdgTrackPtCut, myLdgTrackPt);
    if (!(myLdgTrackPt > fLeadTrkPtCut)) return false;
    fCounterPackager.incrementSubCount(fIDLdgTrackPtCut);
    // All cuts passed, return true
    return true;
  }
  
  bool TauIDTCTau::passIsolation(const edm::Ptr<pat::Tau> tau) {
    if (tau->tauID("byIsolation") < 0.5) return false;
    fCounterPackager.incrementSubCount(fIDIsolation);
    // All cuts passed, return true
    return true;
  }
  
  bool TauIDTCTau::passAntiIsolation(const edm::Ptr<pat::Tau> tau) {
    if (tau->tauID("byIsolation") > 0.5) return false;
    fCounterPackager.incrementSubCount(fIDIsolation);
    // All cuts passed, return true
    return true;
  }

  bool TauIDTCTau::passOneProngCut(const edm::Ptr<pat::Tau> tau) {
    size_t myTrackCount = tau->signalTracks().size();
    fCounterPackager.fill(fIDOneProngNumberCut, myTrackCount);
    if (!(myTrackCount == 1)) return false;
    fCounterPackager.incrementSubCount(fIDOneProngNumberCut);
    // All cuts passed, return true
    return true;
  }
  
  bool TauIDTCTau::passThreeProngCut(const edm::Ptr<pat::Tau> tau) {
    size_t myTrackCount = tau->signalTracks().size();
    fCounterPackager.fill(fIDThreeProngNumberCut, myTrackCount);
    if (!(myTrackCount == 3)) return false;
    fCounterPackager.incrementSubCount(fIDThreeProngNumberCut);
    // All cuts passed, return true
    return true;
  }

  bool TauIDTCTau::passRTauCut(const edm::Ptr<pat::Tau> tau) {
    double myRtauValue = tau->leadTrack()->p() / tau->p() - 1.0e-10; // value 1 goes in the bin below 1 in the histogram
    hRtauVsEta->Fill(myRtauValue, tau->eta(), fEventWeight.getWeight());
    fCounterPackager.fill(fIDRTauCut, myRtauValue);
    if (!(myRtauValue > fRtauCut)) return false;
    fCounterPackager.incrementSubCount(fIDRTauCut);
    // All cuts passed, return true
    return true;
  }

  bool TauIDTCTau::passAntiRTauCut(const edm::Ptr<pat::Tau> tau) {
    double myRtauValue = tau->leadTrack()->p() / tau->p() - 1.0e-10; // value 1 goes in the bin below 1 in the histogram
    hRtauVsEta->Fill(myRtauValue, tau->eta(), fEventWeight.getWeight());
    fCounterPackager.fill(fIDRTauCut, myRtauValue);
    if (!(myRtauValue < fAntiRtauCut)) return false;
    fCounterPackager.incrementSubCount(fIDRTauCut);
    // All cuts passed, return true
    return true;
  }

  double TauIDTCTau::getRtauValue(const edm::Ptr<pat::Tau> tau) const {
    return tau->leadTrack()->p() / tau->p() - 1.0e-10; // value 1 goes in the bin below 1 in the histogram
  }
}
