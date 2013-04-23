// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_JetDetailHistograms_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_JetDetailHistograms_h

#include "DataFormats/PatCandidates/interface/Jet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

namespace HPlus {
  class HistoWrapper;
  class WrappedTH1;
  class WrappedTH2;

  /**
   * Class for producing detailed information about jets.
   */
  class JetDetailHistograms {
  public:
    /// Creates a directory named prefix as a subdirectory under myDir for containting the jet detail histograms
    JetDetailHistograms(HistoWrapper& histoWrapper, TFileDirectory& myDir, std::string prefix);
    /// Detaul destructor
    ~JetDetailHistograms();
    /// Fill histograms
    void fill(const edm::Ptr<pat::Jet>& jet, const bool isRealData);

  private:
    // Histograms
    WrappedTH1 *hPt;
    WrappedTH1 *hEta;
    WrappedTH1 *hPhi;
    WrappedTH1 *hNeutralEmEnergyFraction;
    WrappedTH1 *hNeutralMultiplicity;
    WrappedTH1 *hNeutralHadronEnergyFraction;
    WrappedTH1 *hNeutralHadronMultiplicity;
    WrappedTH1 *hPhotonEnergyFraction;
    WrappedTH1 *hPhotonMultiplicity;
    WrappedTH1 *hMuonEnergyFraction;
    WrappedTH1 *hMuonMultiplicity;
    WrappedTH1 *hChargedHadronEnergyFraction;
    WrappedTH1 *hChargedEmEnergyFraction;
    WrappedTH1 *hChargedMultiplicity;
    WrappedTH1 *hPartonFlavour;
    WrappedTH1 *hJECFactor;
    WrappedTH1 *hN60;
    WrappedTH1 *hTowersArea;
    WrappedTH1 *hJetCharge;
    WrappedTH1 *hPtDiffToGenJet;
  };

}

#endif

