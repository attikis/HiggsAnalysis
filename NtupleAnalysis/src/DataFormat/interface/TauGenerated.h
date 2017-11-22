// -*- c++ -*-
// This file has been auto-generated with HiggsAnalysis/NtupleAnalysis/scripts/hplusGenerateDataFormats.py

#ifndef DataFormat_TauGenerated_h
#define DataFormat_TauGenerated_h

#include "DataFormat/interface/Particle.h"
#include <string>
#include <vector>
#include <functional>

class TauGeneratedCollection: public ParticleCollection<double> {
public:
  explicit TauGeneratedCollection(const std::string& prefix="Taus")
  : ParticleCollection(prefix),
    fMCVisibleTau(prefix),
    fmatchingJet(prefix)
  {
    fMCVisibleTau.setEnergySystematicsVariation("_MCVisibleTau");
    fmatchingJet.setEnergySystematicsVariation("_matchingJet");
  }
  ~TauGeneratedCollection() {}

  void setupBranches(BranchManager& mgr);

  std::vector<std::string> getIsolationDiscriminatorNames() const {
    static std::vector<std::string> n = { std::string("byLooseCombinedIsolationDeltaBetaCorr3Hits"), std::string("byMediumCombinedIsolationDeltaBetaCorr3Hits"), std::string("byTightCombinedIsolationDeltaBetaCorr3Hits"), std::string("byVLooseIsolationMVArun2v1DBoldDMwLT")};
    return n;
  }
  std::vector<std::string> getAgainstMuonDiscriminatorNames() const {
    static std::vector<std::string> n = { std::string("againstMuonLoose3"), std::string("againstMuonTight3")};
    return n;
  }
  std::vector<std::string> getAgainstElectronDiscriminatorNames() const {
    static std::vector<std::string> n = { std::string("againstElectronLooseMVA6"), std::string("againstElectronMediumMVA6"), std::string("againstElectronTightMVA6"), std::string("againstElectronVLooseMVA6"), std::string("againstElectronVTightMVA6")};
    return n;
  }

  const ParticleCollection<double>* getMCVisibleTauCollection() const { return &fMCVisibleTau; }
  const ParticleCollection<double>* getmatchingJetCollection() const { return &fmatchingJet; }
protected:
  ParticleCollection<double> fMCVisibleTau;
  ParticleCollection<double> fmatchingJet;

protected:
  const Branch<std::vector<bool>> *fAgainstElectronLooseMVA6;
  const Branch<std::vector<bool>> *fAgainstElectronMediumMVA6;
  const Branch<std::vector<bool>> *fAgainstElectronTightMVA6;
  const Branch<std::vector<bool>> *fAgainstElectronVLooseMVA6;
  const Branch<std::vector<bool>> *fAgainstElectronVTightMVA6;
  const Branch<std::vector<bool>> *fAgainstMuonLoose3;
  const Branch<std::vector<bool>> *fAgainstMuonTight3;
  const Branch<std::vector<bool>> *fByLooseCombinedIsolationDeltaBetaCorr3Hits;
  const Branch<std::vector<bool>> *fByMediumCombinedIsolationDeltaBetaCorr3Hits;
  const Branch<std::vector<bool>> *fByTightCombinedIsolationDeltaBetaCorr3Hits;
  const Branch<std::vector<bool>> *fByVLooseIsolationMVArun2v1DBoldDMwLT;
  const Branch<std::vector<bool>> *fDecayModeFinding;
  const Branch<std::vector<bool>> *fDecayModeFindingNewDMs;
  const Branch<std::vector<double>> *fLChTrkEta;
  const Branch<std::vector<double>> *fLChTrkPt;
  const Branch<std::vector<double>> *fLNeutrTrkEta;
  const Branch<std::vector<double>> *fLNeutrTrkPt;
  const Branch<std::vector<float>> *fIPxy;
  const Branch<std::vector<float>> *fIPxySignif;
  const Branch<std::vector<short>> *fCharge;
  const Branch<std::vector<short>> *fDecayMode;
  const Branch<std::vector<short>> *fMcNPizero;
  const Branch<std::vector<short>> *fMcNProngs;
  const Branch<std::vector<short>> *fNProngs;
  const Branch<std::vector<short>> *fPdgOrigin;
};


template <typename Coll>
class TauGenerated: public Particle<Coll> {
public:
  TauGenerated() {}
  TauGenerated(const Coll* coll, size_t index)
  : Particle<Coll>(coll, index),
    fMCVisibleTau(coll->getMCVisibleTauCollection(), index),
    fmatchingJet(coll->getmatchingJetCollection(), index)
  {}
  ~TauGenerated() {}

  std::vector<std::function<bool()>> getIsolationDiscriminatorValues() const {
    static std::vector<std::function<bool()>> values = {
      [&](){ return this->byLooseCombinedIsolationDeltaBetaCorr3Hits(); },
      [&](){ return this->byMediumCombinedIsolationDeltaBetaCorr3Hits(); },
      [&](){ return this->byTightCombinedIsolationDeltaBetaCorr3Hits(); },
      [&](){ return this->byVLooseIsolationMVArun2v1DBoldDMwLT(); }
    };
    return values;
  }
  std::vector<std::function<bool()>> getAgainstMuonDiscriminatorValues() const {
    static std::vector<std::function<bool()>> values = {
      [&](){ return this->againstMuonLoose3(); },
      [&](){ return this->againstMuonTight3(); }
    };
    return values;
  }
  std::vector<std::function<bool()>> getAgainstElectronDiscriminatorValues() const {
    static std::vector<std::function<bool()>> values = {
      [&](){ return this->againstElectronLooseMVA6(); },
      [&](){ return this->againstElectronMediumMVA6(); },
      [&](){ return this->againstElectronTightMVA6(); },
      [&](){ return this->againstElectronVLooseMVA6(); },
      [&](){ return this->againstElectronVTightMVA6(); }
    };
    return values;
  }

  const Particle<ParticleCollection<double>>* MCVisibleTau() const { return &fMCVisibleTau; }
  const Particle<ParticleCollection<double>>* matchingJet() const { return &fmatchingJet; }

  bool againstElectronLooseMVA6() const { return this->fCollection->fAgainstElectronLooseMVA6->value()[this->index()]; }
  bool againstElectronMediumMVA6() const { return this->fCollection->fAgainstElectronMediumMVA6->value()[this->index()]; }
  bool againstElectronTightMVA6() const { return this->fCollection->fAgainstElectronTightMVA6->value()[this->index()]; }
  bool againstElectronVLooseMVA6() const { return this->fCollection->fAgainstElectronVLooseMVA6->value()[this->index()]; }
  bool againstElectronVTightMVA6() const { return this->fCollection->fAgainstElectronVTightMVA6->value()[this->index()]; }
  bool againstMuonLoose3() const { return this->fCollection->fAgainstMuonLoose3->value()[this->index()]; }
  bool againstMuonTight3() const { return this->fCollection->fAgainstMuonTight3->value()[this->index()]; }
  bool byLooseCombinedIsolationDeltaBetaCorr3Hits() const { return this->fCollection->fByLooseCombinedIsolationDeltaBetaCorr3Hits->value()[this->index()]; }
  bool byMediumCombinedIsolationDeltaBetaCorr3Hits() const { return this->fCollection->fByMediumCombinedIsolationDeltaBetaCorr3Hits->value()[this->index()]; }
  bool byTightCombinedIsolationDeltaBetaCorr3Hits() const { return this->fCollection->fByTightCombinedIsolationDeltaBetaCorr3Hits->value()[this->index()]; }
  bool byVLooseIsolationMVArun2v1DBoldDMwLT() const { return this->fCollection->fByVLooseIsolationMVArun2v1DBoldDMwLT->value()[this->index()]; }
  bool decayModeFinding() const { return this->fCollection->fDecayModeFinding->value()[this->index()]; }
  bool decayModeFindingNewDMs() const { return this->fCollection->fDecayModeFindingNewDMs->value()[this->index()]; }
  double lChTrkEta() const { return this->fCollection->fLChTrkEta->value()[this->index()]; }
  double lChTrkPt() const { return this->fCollection->fLChTrkPt->value()[this->index()]; }
  double lNeutrTrkEta() const { return this->fCollection->fLNeutrTrkEta->value()[this->index()]; }
  double lNeutrTrkPt() const { return this->fCollection->fLNeutrTrkPt->value()[this->index()]; }
  float IPxy() const { return this->fCollection->fIPxy->value()[this->index()]; }
  float IPxySignif() const { return this->fCollection->fIPxySignif->value()[this->index()]; }
  short charge() const { return this->fCollection->fCharge->value()[this->index()]; }
  short decayMode() const { return this->fCollection->fDecayMode->value()[this->index()]; }
  short mcNPizero() const { return this->fCollection->fMcNPizero->value()[this->index()]; }
  short mcNProngs() const { return this->fCollection->fMcNProngs->value()[this->index()]; }
  short nProngs() const { return this->fCollection->fNProngs->value()[this->index()]; }
  short pdgOrigin() const { return this->fCollection->fPdgOrigin->value()[this->index()]; }

protected:
  Particle<ParticleCollection<double>> fMCVisibleTau;
  Particle<ParticleCollection<double>> fmatchingJet;

};

#endif
