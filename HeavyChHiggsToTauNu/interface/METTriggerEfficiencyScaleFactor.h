// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_METTriggerEfficiencyScaleFactor_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_METTriggerEfficiencyScaleFactor_h

#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/BinnedEfficiencyScaleFactor.h"

namespace edm {
  class ParameterSet;
}
namespace reco {
  class MET;
}

namespace HPlus {
  class HistoWrapper;
  class WrappedTH1;
  class EventWeight;

  class METTriggerEfficiencyScaleFactor {
  public:
    typedef BinnedEfficiencyScaleFactor::Data Data;

    METTriggerEfficiencyScaleFactor(const edm::ParameterSet& iConfig, HistoWrapper& histoWrapper);
    ~METTriggerEfficiencyScaleFactor();

    void setRun(unsigned run) { fBinned.setRun(run); }

    double dataEfficiency(const reco::MET& met) const;
    double dataEfficiencyRelativeUncertainty(const reco::MET& met) const;
    double dataEfficiencyAbsoluteUncertainty(const reco::MET& met) const;

    double dataAverageEfficiency(const reco::MET& met) const;
    double dataAverageEfficiencyRelativeUncertainty(const reco::MET& met) const;
    double dataAverageEfficiencyAbsoluteUncertainty(const reco::MET& met) const;

    double mcEfficiency(const reco::MET& met) const;
    double mcEfficiencyRelativeUncertainty(const reco::MET& met) const;
    double mcEfficiencyAbsoluteUncertainty(const reco::MET& met) const;

    double scaleFactor(const reco::MET& met) const;
    double scaleFactorRelativeUncertainty(const reco::MET& met) const;
    double scaleFactorAbsoluteUncertainty(const reco::MET& met) const;

    Data applyEventWeight(const reco::MET& met, bool isData, HPlus::EventWeight& eventWeight);

  private:
    BinnedEfficiencyScaleFactor fBinned;

    WrappedTH1 *hScaleFactor;
    WrappedTH1 *hScaleFactorRelativeUncertainty;
    WrappedTH1 *hScaleFactorAbsoluteUncertainty;
  };
}


#endif