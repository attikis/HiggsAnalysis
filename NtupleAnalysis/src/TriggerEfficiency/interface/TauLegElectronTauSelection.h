#ifndef TriggerEfficiency_TauLegElectronTauSelection_h
#define TriggerEfficiency_TauLegElectronTauSelection_h

#include "TriggerEfficiency/interface/TrgBaseSelection.h"
#include "DataFormat/interface/HLTTau.h"

#include "Math/VectorUtil.h"

class TauLegElectronTauSelection : public TrgBaseSelection {
 public:
  explicit TauLegElectronTauSelection(const ParameterSet&, EventCounter&, HistoWrapper&);
  ~TauLegElectronTauSelection();

  bool offlineSelection(Event&,Xvar xvar = pt);
  bool onlineSelection(Event&);

  void bookHistograms(TDirectory*);
  void print();

 private:
  short fnprongs;
  bool relaxedSelection;

  WrappedTH1 *hElePt;
  WrappedTH1 *hTauPt;
  WrappedTH1 *hInvM;
  WrappedTH1 *hMt;
  WrappedTH1 *hNjets;

  Count cTauLegAll;
  Count cTauLegEle;
  Count cTauLegTau;
  Count cTauLegCharge;
  Count cTauLegInvMass;
  Count cTauLegMt;
};
TauLegElectronTauSelection::TauLegElectronTauSelection(const ParameterSet& setup, EventCounter& fEventCounter, HistoWrapper& histoWrapper):
  TrgBaseSelection(histoWrapper),
  cTauLegAll(fEventCounter.addCounter("TauLeg:all")),
  cTauLegEle(fEventCounter.addCounter("TauLeg:ele")),
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
TauLegElectronTauSelection::~TauLegElectronTauSelection(){}

void TauLegElectronTauSelection::bookHistograms(TDirectory* dir){
  TDirectory* subdir = fHistoWrapper.mkdir(HistoLevel::kVital, dir, "Histograms");
  hElePt = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "elept", "elept", 200, 0, 200.0);
  hTauPt = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "taupt", "taupt", 200, 0, 200.0);
  hInvM  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "InvMass", "InvMass", 200, 0, 200.0);
  hMt    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "Mt", "Mt", 200, 0, 200.0);
  hNjets = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "Njets", "Njets", 10, 0, 10);
}

void TauLegElectronTauSelection::print(){
  std::cout << "        Tau leg: all events    " << cTauLegAll.value() << std::endl;
  std::cout << "        Tau leg: electron selection  " << cTauLegEle.value() << std::endl;
  std::cout << "        Tau leg: tau selection " << cTauLegTau.value() << std::endl;
  std::cout << "        Tau leg: eTau charge  " << cTauLegCharge.value() << std::endl;
  std::cout << "        Tau leg: eTauInvMass  " << cTauLegInvMass.value() << std::endl;
  std::cout << "        Tau leg: eMetMt       " << cTauLegMt.value() << std::endl;
}

bool TauLegElectronTauSelection::offlineSelection(Event& fEvent, Xvar xvar){

  cTauLegAll.increment();

  boost::optional<Electron> selectedElectron;
  size_t nelectrons = 0;
  for(Electron electron: fEvent.electrons()) {
    if(!(electron.pt() > 17)) continue;
    if(!(std::abs(electron.eta()) < 2.1)) continue;
    //if(!electron.configurableDiscriminators()) continue;
    //    if(!(muon.isGlobalMuon())) continue;

    nelectrons++;
    if(!selectedElectron || (electron.pt() > selectedElectron->pt()) ) selectedElectron = electron;
  }
  if(nelectrons != 1) return false;
  if(xvar == pt) hElePt->Fill(selectedElectron->pt());

  cTauLegEle.increment();

  boost::optional<Tau> selectedTau;
  size_t ntaus = 0;
  for(Tau tau: fEvent.taus()) {
    double drEleTau = ROOT::Math::VectorUtil::DeltaR(selectedElectron->p4(),tau.p4());
    if(drEleTau < 0.4) continue;

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

  ////FIXME!  if(selectedTau->charge() * selectedElectron->charge() != -1 ) return false;
  cTauLegCharge.increment();

  double eTauInvMass = (selectedElectron->p4() + selectedTau->p4()).M();
  if(xvar == pt) hInvM->Fill(eTauInvMass);

  if(!(eTauInvMass > 20 && eTauInvMass < 80)) return false;

  //  if(!(muTauInvMass < 100)) return false; // 80 -> 100 because of H125 sample. 23112015/S.Lehti
  cTauLegInvMass.increment();

  double eMetMt = sqrt( 2 * selectedElectron->pt() * fEvent.met_Type1().et() * (1-cos(selectedElectron->phi()-fEvent.met_Type1().phi())) );
  if(xvar == pt) hMt->Fill(eMetMt);
  if(!(eMetMt < 40)) return false;

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

bool TauLegElectronTauSelection::onlineSelection(Event& fEvent){
  return fEvent.configurableTriggerDecision2();
}

#endif
