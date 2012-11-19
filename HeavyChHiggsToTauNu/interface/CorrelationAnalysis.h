// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_CorrelationAnalysis_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_CorrelationAnalysis_h

#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/Candidate/interface/Candidate.h"
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

  class CorrelationAnalysis {
  public:
    CorrelationAnalysis(const edm::ParameterSet& iConfig, EventCounter& eventCounter, HistoWrapper& histoWrapper , std::string HistoName);
    CorrelationAnalysis(EventCounter& eventCounter, HistoWrapper& histoWrapper , std::string HistoName);
    //CorrelationAnalysis();
    ~CorrelationAnalysis();

    // PtrVector has implicit conversion from PtrVector of anything deriving from reco::Candidate
    void analyze(const edm::PtrVector<reco::Candidate>&,const edm::PtrVector<reco::Candidate>& , std::string HistoName);

  private:
    void init(HistoWrapper& histoWrapper, std::string HistoName);

    // Histograms
    WrappedTH1 *hPtB1;
    WrappedTH1 *hPtB2;
    WrappedTH1 *hEtaB1;
    WrappedTH1 *hEtaB2;
    WrappedTH1 *hDeltaR_tauB1;
    WrappedTH1 *hDeltaR_tauB2;
  };
}

#endif
