#ifndef TriggerEfficiency_TauLegSelection_h
#define TriggerEfficiency_TauLegSelection_h

#include "TriggerEfficiency/interface/TrgBaseSelection.h"
#include "DataFormat/interface/HLTTau.h"

#include "Math/VectorUtil.h"

class TauLegSelection : public TrgBaseSelection {
 public:
  explicit TauLegSelection(const ParameterSet&, EventCounter&, HistoWrapper&);
  ~TauLegSelection();

  bool offlineSelection(Event&,Xvar xvar = pt);
  bool onlineSelection(Event&);

  void bookHistograms(TDirectory*);
  void print();

 private:
  short fnprongs;
  bool relaxedSelection;

  WrappedTH1 *hMuPt;
  WrappedTH1 *hTauPt;
  WrappedTH1 *hInvM;
  WrappedTH1 *hMt;
  WrappedTH1 *hNjets;

  Count cTauLegAll;
  Count cTauLegMu;
  Count cTauLegTau;
  Count cTauLegCharge;
  Count cTauLegInvMass;
  Count cTauLegMt;
};
TauLegSelection::TauLegSelection(const ParameterSet& setup, EventCounter& fEventCounter, HistoWrapper& histoWrapper):
  TrgBaseSelection(histoWrapper),
  cTauLegAll(fEventCounter.addCounter("TauLeg:all")),
  cTauLegMu(fEventCounter.addCounter("TauLeg:mu")),
  cTauLegTau(fEventCounter.addCounter("TauLeg:tau")),
  cTauLegCharge(fEventCounter.addCounter("TauLeg:charge")),
  cTauLegInvMass(fEventCounter.addCounter("TauLeg:invMass")),
  cTauLegMt(fEventCounter.addCounter("TauLeg:Mt"))
{
  init(setup);
  //  fHistoWrapper = histoWrapper;
  const ParameterSet& tauSelection = setup.getParameter<ParameterSet>("TauSelection");
  fnprongs = tauSelection.getParameter<int>("nprongs");
  relaxedSelection = false;
  relaxedSelection = tauSelection.getParameter<bool>("relaxedOfflineSelection");
  //std::cout << "check relaxedSelection " << relaxedSelection<< std::endl;
  std::cout << "        Tau selection nprongs " << fnprongs << std::endl;
  std::vector<std::string> discrs = tauSelection.getParameter<std::vector<std::string> >("discriminators");
  for(std::string i: discrs) std::cout << "        Tau discriminators " << i << std::endl;
}
TauLegSelection::~TauLegSelection(){}

void TauLegSelection::bookHistograms(TDirectory* dir){
  TDirectory* subdir = fHistoWrapper.mkdir(HistoLevel::kVital, dir, "Histograms");
  hMuPt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "mupt", "mupt", 200, 0, 200.0);
  hTauPt = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "taupt", "taupt", 200, 0, 200.0);
  hInvM  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "InvMass", "InvMass", 200, 0, 200.0);
  hMt    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "Mt", "Mt", 200, 0, 200.0);
  hNjets = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "Njets", "Njets", 10, 0, 10);
}

void TauLegSelection::print(){
  std::cout << "        Tau leg: all events    " << cTauLegAll.value() << std::endl;
  std::cout << "        Tau leg: mu selection  " << cTauLegMu.value() << std::endl;
  std::cout << "        Tau leg: tau selection " << cTauLegTau.value() << std::endl;
  std::cout << "        Tau leg: muTau charge  " << cTauLegCharge.value() << std::endl;
  std::cout << "        Tau leg: muTauInvMass  " << cTauLegInvMass.value() << std::endl;
  std::cout << "        Tau leg: muMetMt       " << cTauLegMt.value() << std::endl;
}

bool TauLegSelection::offlineSelection(Event& fEvent, Xvar xvar){

  cTauLegAll.increment();

  boost::optional<Muon> selectedMuon;
  size_t nmuons = 0;
  for(Muon muon: fEvent.muons()) {
    if(!(muon.pt() > 17)) continue;
    if(!(std::abs(muon.eta()) < 2.1)) continue;
    if(!muon.configurableDiscriminators()) continue;
    //    if(!(muon.isGlobalMuon())) continue;

    nmuons++;
    if(!selectedMuon || (muon.pt() > selectedMuon->pt()) ) selectedMuon = muon;
  }
  if(nmuons != 1) return false;
  if(xvar == pt) hMuPt->Fill(selectedMuon->pt());

  cTauLegMu.increment();

  boost::optional<Tau> selectedTau;
  size_t ntaus = 0;
  for(Tau tau: fEvent.taus()) {
    double drMuTau = ROOT::Math::VectorUtil::DeltaR(selectedMuon->p4(),tau.p4());
    if(drMuTau < 0.4) continue;

    if(!(tau.pt() > 20)) continue;
    if(xvar != pt && !(tau.pt() > 50)) continue;
    if(!(std::abs(tau.eta()) < 2.1)) continue;
    if(!(tau.lChTrkPt() > 20)) continue;
    if((fnprongs == 1 || fnprongs == 3) && !(tau.nProngs() == fnprongs)) continue;
    if(!tau.decayModeFinding()) continue;
    if(!tau.configurableDiscriminators()) continue;

    ntaus++;
    if(!selectedTau || (tau.pt() > selectedTau->pt()) ) selectedTau = tau;
  }
  if(ntaus != 1) return false;


  //  if(selectedTau->charge() * selectedMuon->charge() != -1 ) return false;

  //  boost::optional<HLTTau> selectedHltTau;
  math::LorentzVectorT<double> selectedHltTau;
  double drmin = 999;
  for(HLTTau hlttau: fEvent.triggerTaus()) {
    double drTauHlttau = ROOT::Math::VectorUtil::DeltaR(selectedTau->p4(),hlttau.p4());
    if(drTauHlttau < 0.4 && drTauHlttau < drmin) {
      //      selectedHltTau = hlttau;
      selectedHltTau = hlttau.p4();
      drmin = drTauHlttau;
    }
  }

  if(xvar == pt) {
    xvariable = selectedTau->pt();
    hTauPt->Fill(selectedTau->pt());
    xhltvariable = selectedHltTau.pt();
  }
  if(xvar == eta) xvariable = selectedTau->eta();
  if(xvar == phi) xvariable = selectedTau->phi();
  if(xvar == pu) xvariable = fEvent.vertexInfo().value();


  if(fEvent.isMC() && abs(selectedTau->pdgId()) == 15) mcmatch = true;
  //if(fEvent.isMC())  std::cout << "check tau mc match " << selectedTau->pdgId() << std::endl;
  cTauLegTau.increment();

  if(relaxedSelection) return true;

  if(selectedTau->charge() * selectedMuon->charge() != -1 ) return false;
  cTauLegCharge.increment();

  double muTauInvMass = (selectedMuon->p4() + selectedTau->p4()).M();
  if(xvar == pt) hInvM->Fill(muTauInvMass);
  //  std::cout << "check muTauInvMass " << selectedMuon->pt() << " " << selectedTau->pt() << " " << muTauInvMass << std::endl;

  if(!(muTauInvMass > 20 && muTauInvMass < 80)) return false;

  //  if(!(muTauInvMass < 100)) return false; // 80 -> 100 because of H125 sample. 23112015/S.Lehti
  cTauLegInvMass.increment();

  double muMetMt = sqrt( 2 * selectedMuon->pt() * fEvent.met_Type1().et() * (1-cos(selectedMuon->phi()-fEvent.met_Type1().phi())) );
  if(xvar == pt) hMt->Fill(muMetMt);
  if(!(muMetMt < 40)) return false;

  cTauLegMt.increment();

  size_t njets = 0;
  for(Jet jet: fEvent.jets()) {
    double deltaR = ROOT::Math::VectorUtil::DeltaR(jet.p4(),selectedTau->p4());
    if(deltaR < 0.5) continue;
    if(!(jet.pt() > 30)) continue;
    //    if(!jet.PUIDtight()) continue;
    ++njets;
  }
  //  std::cout << "check njets " << fEvent.jets().size() << " " << njets << std::endl;
  hNjets->Fill(njets);
  //if(njets > 2) return false;

  //bool selected = false;
  //if(ntaus > 0 && nmuons > 0 && muTauInvMass < 80 && muMetMt < 40) selected = true;
  //  if(ntaus > 0 && nmuons > 0) selected = true;
  //return selected;
  return true;
}

bool TauLegSelection::onlineSelection(Event& fEvent){
  return fEvent.configurableTriggerDecision2();
}

#endif
