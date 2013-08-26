#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TauTriggerEfficiencyScaleFactor.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/HistoWrapper.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/EventWeight.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/PatCandidates/interface/Tau.h"

namespace HPlus {
  TauTriggerEfficiencyScaleFactor::TauTriggerEfficiencyScaleFactor(const edm::ParameterSet& iConfig, HistoWrapper& histoWrapper):
    fBinned(iConfig, "pt") {
  
    edm::Service<TFileService> fs;
    TFileDirectory dir = fs->mkdir("TauTriggerScaleFactor");
    hScaleFactor = histoWrapper.makeTH<TH1F>(HistoWrapper::kVital, dir, "TriggerScaleFactor", "TriggerScaleFactor;TriggerScaleFactor;N_{events}/0.01", 200., 0., 2.0);

    const size_t NBUF = 10;
    char buf[NBUF];

    WrappedTH1 *hsf = histoWrapper.makeTH<TH1F>(HistoWrapper::kVital, dir, "ScaleFactor", "Scale factor;Tau p_{T} bin;Scale factor", fBinned.nbins()+1, 0, fBinned.nbins()+1);
    WrappedTH1 *hsfu = histoWrapper.makeTH<TH1F>(HistoWrapper::kVital, dir, "ScaleFactorUncertainty", "Scale factor;Tau p_{T} bin;Scale factor uncertainty", fBinned.nbins()+1, 0, fBinned.nbins()+1);
    if(hsf->getHisto()) {
      hsf->getHisto()->SetBinContent(1, 1); hsf->GetXaxis()->SetBinLabel(1, "control");
      hsfu->getHisto()->SetBinContent(1, 1); hsfu->GetXaxis()->SetBinLabel(1, "control");
      for(size_t i=0; i<fBinned.nbins(); ++i) {
        size_t bin = i+2;
        snprintf(buf, NBUF, "%.0f", fBinned.binLowEdge(i));

        hsf->getHisto()->SetBinContent(bin, fBinned.binScaleFactor(i));
        hsfu->getHisto()->SetBinContent(bin, fBinned.binScaleFactorAbsoluteUncertainty(i));
        hsf->GetXaxis()->SetBinLabel(bin, buf);
        hsfu->GetXaxis()->SetBinLabel(bin, buf);
      }
    }
  }
  TauTriggerEfficiencyScaleFactor::~TauTriggerEfficiencyScaleFactor() {}

  double TauTriggerEfficiencyScaleFactor::dataEfficiency(const pat::Tau& tau) const {
    return fBinned.dataEfficiency(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::dataEfficiencyRelativeUncertainty(const pat::Tau& tau) const {
    return fBinned.dataEfficiencyRelativeUncertainty(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::dataEfficiencyAbsoluteUncertainty(const pat::Tau& tau) const {
    return fBinned.dataEfficiencyAbsoluteUncertainty(tau.pt());
  }

  double TauTriggerEfficiencyScaleFactor::dataAverageEfficiency(const pat::Tau& tau) const {
    return fBinned.dataAverageEfficiency(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::dataAverageEfficiencyRelativeUncertainty(const pat::Tau& tau) const {
    return fBinned.dataAverageEfficiencyRelativeUncertainty(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::dataAverageEfficiencyAbsoluteUncertainty(const pat::Tau& tau) const {
    return fBinned.dataAverageEfficiencyAbsoluteUncertainty(tau.pt());
  }


  double TauTriggerEfficiencyScaleFactor::mcEfficiency(const pat::Tau& tau) const {
    return fBinned.mcEfficiency(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::mcEfficiencyRelativeUncertainty(const pat::Tau& tau) const {
    return fBinned.mcEfficiencyRelativeUncertainty(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::mcEfficiencyAbsoluteUncertainty(const pat::Tau& tau) const {
    return fBinned.mcEfficiencyAbsoluteUncertainty(tau.pt());
  }

  double TauTriggerEfficiencyScaleFactor::scaleFactor(const pat::Tau& tau) const {
    return fBinned.scaleFactor(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::scaleFactorRelativeUncertainty(const pat::Tau& tau) const {
    return fBinned.scaleFactorRelativeUncertainty(tau.pt());
  }
  double TauTriggerEfficiencyScaleFactor::scaleFactorAbsoluteUncertainty(const pat::Tau& tau) const {
    return fBinned.scaleFactorAbsoluteUncertainty(tau.pt());
  }

  TauTriggerEfficiencyScaleFactor::Data TauTriggerEfficiencyScaleFactor::applyEventWeight(const pat::Tau& tau, bool isData, EventWeight& eventWeight) {
    Data output = fBinned.getEventWeight(tau.pt(), isData);

    if(fBinned.getMode() == BinnedEfficiencyScaleFactor::kScaleFactor) {
      hScaleFactor->Fill(output.getEventWeight());
    }
    eventWeight.multiplyWeight(output.getEventWeight());
    return output;
  }
}
