// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_CorrelationAnalysis_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_CorrelationAnalysis_h

#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/EventCounter.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/EventWeight.h"

namespace edm {
  class ParameterSet;
  class Event;
  class EventSetup;
}

class TH1;

namespace HPlus {
  class CorrelationAnalysis {
  public:
    CorrelationAnalysis(const edm::ParameterSet& iConfig, EventCounter& eventCounter, EventWeight& eventWeight);
    CorrelationAnalysis(EventCounter& eventCounter, EventWeight& eventWeight);
    //CorrelationAnalysis();
    ~CorrelationAnalysis();

    // PtrVector has implicit conversion from PtrVector of anything deriving from reco::Candidate
    void analyze(const edm::PtrVector<reco::Candidate>&,const edm::PtrVector<reco::Candidate>&);
  
  private:
    void init();
    
    // EventWeight object
    EventWeight& fEventWeight;
    
    // Histograms
    TH1 *hPtB1;
    TH1 *hPtB2;
    TH1 *hEtaB1;
    TH1 *hEtaB2;
    TH1 *hDeltaR_tauB1;
    TH1 *hDeltaR_tauB2;
  };
}

#endif
