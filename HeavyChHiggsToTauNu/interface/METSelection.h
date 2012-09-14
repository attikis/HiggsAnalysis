// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_METSelection_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_METSelection_h

#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/PatCandidates/interface/Tau.h"
#include "DataFormats/PatCandidates/interface/Jet.h"

#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/EventCounter.h"

namespace edm {
  class ParameterSet;
  class Event;
  class EventSetup;
}

namespace HPlus {
  class HistoWrapper;
  class WrappedTH1;

  class METSelection {
  public:
    /**
     * Class to encapsulate the access to the data members of
     * TauSelection. If you want to add a new accessor, add it here
     * and keep all the data of TauSelection private.
     */
    class Data {
    public:
      // The reason for pointer instead of reference is that const
      // reference allows temporaries, while const pointer does not.
      // Here the object pointed-to must live longer than this object.
      Data(const METSelection *metSelection, bool passedEvent);
      ~Data();

      bool passedEvent() const { return fPassedEvent; }
      const edm::Ptr<reco::MET> getSelectedMET() const { return fMETSelection->fSelectedMET; }
      const edm::Ptr<reco::MET> getRawMET() const { return fMETSelection->fRawMET; }
      const edm::Ptr<reco::MET> getType1MET() const { return fMETSelection->fType1MET; }
      const edm::Ptr<reco::MET> getType2MET() const { return fMETSelection->fType2MET; }

      const edm::Ptr<reco::MET> getCaloMET() const { return fMETSelection->fCaloMET; }
      const edm::Ptr<reco::MET> getTcMET() const { return fMETSelection->fTcMET; }

      const double getCutValue() const { return fMETSelection->fMetCut; }

    private:
      const METSelection *fMETSelection;
      const bool fPassedEvent;
    };
    
    METSelection(const edm::ParameterSet& iConfig, EventCounter& eventCounter, HistoWrapper& histoWrapper, std::string label);
    ~METSelection();

    Data analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup, const edm::Ptr<reco::Candidate>& selectedTau, const edm::PtrVector<pat::Jet>& allJets);
    
  private:
    enum Select {kRaw, kType1, kType2};

    reco::MET undoJetCorrectionForSelectedTau(const edm::Ptr<reco::MET>& met, const edm::Ptr<reco::Candidate>& selectedTau, const edm::PtrVector<pat::Jet>& allJets, Select type);

    // Input parameters
    edm::InputTag fRawSrc;
    edm::InputTag fType1Src;
    edm::InputTag fType2Src;
    edm::InputTag fCaloSrc;
    edm::InputTag fTcSrc;
    Select fSelect;

    // For type I/II correction
    double fMetCut;
    double fTauJetMatchingCone;
    double fJetType1Threshold;
    std::string fJetOffsetCorrLabel;
    //double fType2ScaleFactor;


    // Counters
    Count fMetCutCount;

    // Histograms
    WrappedTH1 *hMet;
    WrappedTH1 *hMetSignif;
    WrappedTH1 *hMetSumEt;
    WrappedTH1 *hMetDivSumEt;
    WrappedTH1 *hMetDivSqrSumEt;

    // MET objects
    edm::Ptr<reco::MET> fSelectedMET;
    edm::Ptr<reco::MET> fRawMET;
    edm::Ptr<reco::MET> fType1MET;
    edm::Ptr<reco::MET> fType2MET;
    edm::Ptr<reco::MET> fCaloMET;
    edm::Ptr<reco::MET> fTcMET;

    // For type I/II correction
    std::vector<reco::MET> fType1METCorrected;
    //std::vector<reco::MET> fType2METCorrected;
  };
}

#endif
