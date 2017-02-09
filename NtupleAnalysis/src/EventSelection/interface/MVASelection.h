#ifndef EventSelection_MVASelection_h
#define EventSelection_MVASelection_h


#include "EventSelection/interface/BaseSelection.h"
#include "EventSelection/interface/TauSelection.h"

#include <string>
#include <vector>

#include <TDirectory.h>

#include <TChain.h>
#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <TObjString.h>
#include <TSystem.h>
#include <TROOT.h>

#include <TMVA/Factory.h>
#include <TMVA/Tools.h>
#include <TMVA/TMVAGui.h>
#include <TMVA/Reader.h>

class ParameterSet;
class CommonPlots;
class Event;
class EventCounter;
class HistoWrapper;
class WrappedTH1;
class WrappedTH2;

class MVASelection: public BaseSelection {
public:

  class Data {
  public:
    Data();
    ~Data();
    bool passedSelection() const { return bPassedSelection;}
    float mvaValue() const { return fMVAOutputValue;}
    void setTrue() {this->bPassedSelection=true;}
    void setValue(float value) {this->fMVAOutputValue=value;}

    friend class MVASelection;

  private:
    float fMVAOutputValue;
    bool bPassedSelection;

  };

  explicit MVASelection(const ParameterSet& config, EventCounter& eventCounter, HistoWrapper& histoWrapper, CommonPlots* commonPlots, const std::string& prefix, const std::string& postfix);
  explicit MVASelection(const ParameterSet& config, const std::string& postfix);
  virtual ~MVASelection();

  virtual void bookHistograms(TDirectory* dir);

  Data analyze(const Event& event, TMVA::Reader& reader);
  Data silentAnalyze(const Event& event, TMVA::Reader& reader);

  TMVA::Reader *reader;
  Float_t R_bb, MET, TransMass, TransMass_jj, TransMass_muEt;
  Float_t tj1Dist,tj2Dist,tj3Dist;
  Float_t j1j2Dist,j1j3Dist,j2j3Dist;
  Float_t muj1Dist,muj2Dist,muj3Dist;
  Float_t ej1Dist,ej2Dist,ej3Dist;
  Float_t tetaj1eta,tetaj2eta,tetaj3eta;
  Float_t j1etaj2eta,j1etaj3eta,j2etaj3eta;
  Float_t SelectedTau_pt, SelectedTau_eta, SelectedTau_phi;
  Float_t Muon_pt, Muon_eta, Muon_phi;
  Float_t Electron_pt, Electron_eta, Electron_phi;
  Float_t Jet1_pt, Jet1_phi, Jet1_eta, Jet1_IncSecVer_Btag, Jet1_MVA_Btag;
  Float_t Jet2_pt, Jet2_phi, Jet2_eta, Jet2_IncSecVer_Btag, Jet2_MVA_Btag;
  Float_t Jet3_pt, Jet3_phi, Jet3_eta, Jet3_IncSecVer_Btag, Jet3_MVA_Btag;
  Float_t nTaus, nJets, nMuons, nElectrons;



private:
  void initialize(const ParameterSet& config, const std::string& postfix);

  Data privateAnalyze(const Event& iEvent);

  Count cPassedMVASelection;
  Count cSubAll;

  WrappedTH1 *hMVAValueAll;

};

#endif
