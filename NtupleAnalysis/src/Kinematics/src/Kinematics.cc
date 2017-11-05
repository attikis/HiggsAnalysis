// -*- c++ -*-
#include "Framework/interface/BaseSelector.h"
#include "Framework/interface/makeTH.h"
// User
#include "Auxiliary/interface/Table.h"
#include "Auxiliary/interface/Tools.h"
#include "Tools/interface/MCTools.h"
#include "Tools/interface/DirectionalCut.h"
#include "EventSelection/interface/CommonPlots.h"
#include "EventSelection/interface/EventSelections.h"

// ROOT
#include "TDirectory.h"
#include "Math/VectorUtil.h"
#include "TMatrixDSym.h"
#include "TMatrixDSymEigen.h"

typedef Particle<ParticleCollection<double> > genParticle;

struct PtComparator
{
  bool operator() (const genParticle p1, const genParticle p2) const { return ( p1.pt() > p2.pt() ); }
  bool operator() (const math::XYZTLorentzVector p1, const math::XYZTLorentzVector p2) const { return ( p1.pt() > p2.pt() ); }
};


class Kinematics: public BaseSelector {
public:
  explicit Kinematics(const ParameterSet& config, const TH1* skimCounters);
  virtual ~Kinematics() {}

  /// Books histograms
  virtual void book(TDirectory *dir) override;
  /// Sets up branches for reading the TTree
  virtual void setupBranches(BranchManager& branchManager) override;
  /// Called for each event
  virtual void process(Long64_t entry) override;  
  virtual vector<genParticle> GetGenParticles(const vector<genParticle> genParticles, double ptCut, double etaCut, const int pdgId, const bool isLastCopy=true, const bool hasNoDaughters=false);
  virtual vector<GenJet> GetGenJets(const GenJetCollection& genJets, std::vector<float> ptCut, std::vector<float> etaCut);
  virtual vector<GenJet> GetGenJets(const vector<GenJet> genJets, std::vector<float> ptCut, std::vector<float> etaCut, vector<genParticle> genParticlesToMatch);
  virtual TMatrixDSym ComputeMomentumTensor(std::vector<math::XYZTLorentzVector> jets, double r = 2.0); 
  virtual TMatrixDSym ComputeMomentumTensor2D(std::vector<math::XYZTLorentzVector> jets);
  virtual vector<float> GetMomentumTensorEigenValues(std::vector<math::XYZTLorentzVector> jets,
						     float &C,
						     float &D,
						     float &H2);
  virtual vector<float> GetMomentumTensorEigenValues2D(std::vector<math::XYZTLorentzVector> jets, 
						       float &Circularity);
  virtual vector<float> GetSphericityTensorEigenValues(std::vector<math::XYZTLorentzVector> jets,
						       float &y23, float &Sphericity, float &SphericityT, float &Aplanarity, float &Planarity, float &Y);
  virtual double GetAlphaT(std::vector<math::XYZTLorentzVector> jets,
			   float &HT,
			   float &JT,
			   float &MHT,
			   float &Centrality);

  std::vector<math::XYZTLorentzVector> SortInPt(std::vector<math::XYZTLorentzVector> Vector);
  Bool_t IsBjet(math::XYZTLorentzVector jet,vector<GenJet> selectedBJets);
  
  double DeltaRmin(math::XYZTLorentzVector jet, vector<GenJet> jetSelection);
  std::vector<math::XYZTLorentzVector> TrijetJets(vector<math::XYZTLorentzVector> JETS, vector<GenJet> selectedBJets);
private:
  // Input parameters
  const double cfg_Verbose;
  const ParameterSet PSet_ElectronSelection;
  const double cfg_ElectronPtCut;
  const double cfg_ElectronEtaCut;
  const ParameterSet PSet_MuonSelection;
  const double cfg_MuonPtCut;
  const double cfg_MuonEtaCut;
  const ParameterSet PSet_TauSelection;
  const double cfg_TauPtCut;
  const double cfg_TauEtaCut;
  const ParameterSet PSet_JetSelection;
  const std::vector<float> cfg_JetPtCuts;
  const std::vector<float> cfg_JetEtaCuts;
  const DirectionalCut<int> cfg_JetNumberCut;
  const ParameterSet PSet_HtSelection;
  const DirectionalCut<float> cfg_HtCut;
  const ParameterSet PSet_BJetSelection;
  const std::vector<float> cfg_BJetPtCuts;
  const std::vector<float> cfg_BJetEtaCuts;
  const DirectionalCut<int> cfg_BJetNumberCut;
  // METSelection PSet_METSelection;
  TopologySelection PSet_TopologySelection;
  const DirectionalCut<double> cfg_SphericityCut;
  const DirectionalCut<double> cfg_AplanarityCut;
  const DirectionalCut<double> cfg_PlanarityCut;
  const DirectionalCut<double> cfg_CircularityCut;
  const DirectionalCut<double> cfg_Y23Cut;
  const DirectionalCut<double> cfg_CparameterCut;
  const DirectionalCut<double> cfg_DparameterCut;
  const DirectionalCut<double> cfg_FoxWolframMomentCut;
  const DirectionalCut<double> cfg_AlphaTCut;
  const DirectionalCut<double> cfg_CentralityCut;
  // TopSelection PSet_TopSelection;
  const HistogramSettings cfg_PtBinSetting;
  const HistogramSettings cfg_EtaBinSetting;
  const HistogramSettings cfg_PhiBinSetting;
  const HistogramSettings cfg_MassBinSetting;
  const HistogramSettings cfg_DeltaEtaBinSetting;
  const HistogramSettings cfg_DeltaPhiBinSetting;
  const HistogramSettings cfg_DeltaRBinSetting;
  
  Tools auxTools;
  
  // Counters
  Count cAllEvents;  
  Count cTrigger;
  Count cElectronVeto;
  Count cMuonVeto;
  Count cTauVeto;
  Count cJetSelection;
  Count cBJetSelection;
  Count cTopologySelection;
  Count cTopSelection;
  Count cSelected;
  
  // Event Variables
  WrappedTH1 *h_genMET_Et;
  WrappedTH1 *h_genMET_Phi;
  WrappedTH1 *h_genHT_GenJets;  

  // Event-Shape Variables
  WrappedTH1 *h_y23;
  WrappedTH1 *h_Sphericity;
  WrappedTH1 *h_SphericityT;
  WrappedTH1 *h_Y;
  WrappedTH2 *h_S_Vs_Y;
  WrappedTH1 *h_Aplanarity;
  WrappedTH1 *h_Planarity;
  WrappedTH1 *h_CParameter;
  WrappedTH1 *h_DParameter;
  WrappedTH1 *h_H2;
  WrappedTH1 *h_Circularity;
  WrappedTH1 *h_Centrality;
  WrappedTH1 *h_HT;
  WrappedTH1 *h_JT;
  WrappedTH1 *h_MHT;
  WrappedTH1 *h_AlphaT;

  // GenParticles: BQuarks
  WrappedTH1 *h_BQuarks_N;
  WrappedTH1 *h_BQuark1_Pt;
  WrappedTH1 *h_BQuark2_Pt;
  WrappedTH1 *h_BQuark3_Pt;
  WrappedTH1 *h_BQuark4_Pt;
  vector<WrappedTH1*> vh_BQuarks_Pt;
  //
  WrappedTH1 *h_BQuark1_Eta;
  WrappedTH1 *h_BQuark2_Eta;
  WrappedTH1 *h_BQuark3_Eta;
  WrappedTH1 *h_BQuark4_Eta;
  vector<WrappedTH1*> vh_BQuarks_Eta;

  // GenParticles: BQuarks pair closest together
  WrappedTH1 *h_BQuarkPair_dR;
  WrappedTH1 *h_BQuarkPair_dEta;
  WrappedTH1 *h_BQuarkPair_dPhi;
  WrappedTH1 *h_BQuarkPair_dRAverage;
  WrappedTH1 *h_BQuarkPair_dEtaAverage;
  WrappedTH1 *h_BQuarkPair_dPhiAverage;
  //
  WrappedTH1 *h_BQuarkPair_MaxPt_Pt;
  WrappedTH1 *h_BQuarkPair_MaxPt_Eta;
  WrappedTH1 *h_BQuarkPair_MaxPt_Phi;
  WrappedTH1 *h_BQuarkPair_MaxPt_M;
  WrappedTH1 *h_BQuarkPair_MaxPt_dEta;
  WrappedTH1 *h_BQuarkPair_MaxPt_dPhi;
  WrappedTH1 *h_BQuarkPair_MaxPt_dR;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet1_dR;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet1_dEta;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet1_dPhi;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet2_dR;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet2_dEta;
  WrappedTH1 *h_BQuarkPair_MaxPt_jet2_dPhi;
  //  
  WrappedTH1 *h_BQuarkPair_MaxMass_Pt;
  WrappedTH1 *h_BQuarkPair_MaxMass_Eta;
  WrappedTH1 *h_BQuarkPair_MaxMass_Phi;
  WrappedTH1 *h_BQuarkPair_MaxMass_M;
  WrappedTH1 *h_BQuarkPair_MaxMass_dEta;
  WrappedTH1 *h_BQuarkPair_MaxMass_dPhi;
  WrappedTH1 *h_BQuarkPair_MaxMass_dR;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet1_dR;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet1_dEta;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet1_dPhi;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet2_dR;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet2_dEta;
  WrappedTH1 *h_BQuarkPair_MaxMass_jet2_dPhi;

  WrappedTH1 *h_BQuarkPair_dRMin_Pt;
  WrappedTH1 *h_BQuarkPair_dRMin_Eta;
  WrappedTH1 *h_BQuarkPair_dRMin_Rap;
  WrappedTH1 *h_BQuarkPair_dRMin_Phi;
  WrappedTH1 *h_BQuarkPair_dRMin_dEta;
  WrappedTH1 *h_BQuarkPair_dRMin_dPhi;
  WrappedTH1 *h_BQuarkPair_dRMin_dR;
  WrappedTH1 *h_BQuarkPair_dRMin_Mass;
  WrappedTH2 *h_BQuarkPair_dRMin_Eta1_Vs_Eta2;
  WrappedTH2 *h_BQuarkPair_dRMin_Phi1_Vs_Phi2;
  WrappedTH2 *h_BQuarkPair_dRMin_Pt1_Vs_Pt2;
  WrappedTH2 *h_BQuarkPair_dRMin_dEta_Vs_dPhi;
  WrappedTH1 *h_BQuarkPair_dRMin_jet1_dR;
  WrappedTH1 *h_BQuarkPair_dRMin_jet1_dEta;
  WrappedTH1 *h_BQuarkPair_dRMin_jet1_dPhi;
  WrappedTH1 *h_BQuarkPair_dRMin_jet2_dR;
  WrappedTH1 *h_BQuarkPair_dRMin_jet2_dEta;
  WrappedTH1 *h_BQuarkPair_dRMin_jet2_dPhi;

  // GenJets
  WrappedTH1 *h_GenJets_N;
  WrappedTH1 *h_GenJet1_Pt;
  WrappedTH1 *h_GenJet2_Pt;
  WrappedTH1 *h_GenJet3_Pt;
  WrappedTH1 *h_GenJet4_Pt;
  WrappedTH1 *h_GenJet5_Pt;
  WrappedTH1 *h_GenJet6_Pt;
  vector<WrappedTH1*> vh_GenJets_Pt;
  //
  WrappedTH1 *h_GenJet1_Eta;
  WrappedTH1 *h_GenJet2_Eta;
  WrappedTH1 *h_GenJet3_Eta;
  WrappedTH1 *h_GenJet4_Eta;
  WrappedTH1 *h_GenJet5_Eta;
  WrappedTH1 *h_GenJet6_Eta;
  vector<WrappedTH1*> vh_GenJets_Eta;

  // GenJets: Dijet with largest mass
  WrappedTH1 *h_MaxDiJetMass_Pt;
  WrappedTH1 *h_MaxDiJetMass_Eta;
  WrappedTH1 *h_MaxDiJetMass_Rap; 
  WrappedTH1 *h_MaxDiJetMass_Mass;
  WrappedTH1 *h_MaxDiJetMass_dR;
  WrappedTH1 *h_MaxDiJetMass_dRrap;
  WrappedTH1 *h_MaxDiJetMass_dEta;
  WrappedTH1 *h_MaxDiJetMass_dPhi;
  WrappedTH1 *h_MaxDiJetMass_dRap;
  WrappedTH2 *h_MaxDiJetMass_dEta_Vs_dPhi;
  WrappedTH2 *h_MaxDiJetMass_dRap_Vs_dPhi;  

  // GenJets: Untagged jet pair with min dR
  WrappedTH1 *h_dRMinDiJet_NoBJets_Pt;
  WrappedTH1 *h_dRMinDiJet_NoBJets_Eta;
  WrappedTH1 *h_dRMinDiJet_NoBJets_Rap; 
  WrappedTH1 *h_dRMinDiJet_NoBJets_Mass;
  WrappedTH1 *h_dRMinDiJet_NoBJets_dR;
  WrappedTH1 *h_dRMinDiJet_NoBJets_dEta;
  WrappedTH1 *h_dRMinDiJet_NoBJets_dPhi;

  // GenJets: Trijet with largest pT
  WrappedTH1 *h_MaxTriJetPt_Pt;
  WrappedTH1 *h_MaxTriJetPt_Eta;
  WrappedTH1 *h_MaxTriJetPt_Rap; 
  WrappedTH1 *h_MaxTriJetPt_Mass;
  WrappedTH1 *h_MaxTriJetPt_dEtaMax;
  WrappedTH1 *h_MaxTriJetPt_dPhiMax;
  WrappedTH1 *h_MaxTriJetPt_dRMax;
  WrappedTH1 *h_MaxTriJetPt_dEtaMin;
  WrappedTH1 *h_MaxTriJetPt_dPhiMin;
  WrappedTH1 *h_MaxTriJetPt_dRMin;
  WrappedTH1 *h_MaxTriJetPt_dEtaAverage;
  WrappedTH1 *h_MaxTriJetPt_dPhiAverage;
  WrappedTH1 *h_MaxTriJetPt_dRAverage;


  //cosTheta
  WrappedTH1 *h_CosTheta_Bjet1TopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_Bjet1TopCM_Zaxis;
  WrappedTH1 *h_CosTheta_Bjet2TopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_Bjet2TopCM_Zaxis;
  WrappedTH1 *h_CosTheta_Bjet3TopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_Bjet3TopCM_Zaxis;

  WrappedTH1 *h_CosTheta_LdgTrijetLdgJetTopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_LdgTrijetSubldgJetTopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_LdgTrijetBjetTopCM_TrijetLab;

  WrappedTH1 *h_CosTheta_SubldgTrijetLdgJetTopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab;
  WrappedTH1 *h_CosTheta_SubldgTrijetBjetTopCM_TrijetLab;


  // Correlations 
  WrappedTH2 *h_BQuark1_BQuark2_dEta_Vs_dPhi;
  WrappedTH2 *h_BQuark1_BQuark3_dEta_Vs_dPhi;
  WrappedTH2 *h_BQuark1_BQuark4_dEta_Vs_dPhi;
  WrappedTH2 *h_BQuark2_BQuark3_dEta_Vs_dPhi;
  WrappedTH2 *h_BQuark2_BQuark4_dEta_Vs_dPhi;
  WrappedTH2 *h_BQuark3_BQuark4_dEta_Vs_dPhi;

  WrappedTH2 *h_Jet1Jet2_dEta_Vs_Jet3Jet4_dEta;
  WrappedTH2 *h_Jet1Jet2_dPhi_Vs_Jet3Jet4_dPhi;  
  WrappedTH2 *h_Jet1Jet2_dEta_Vs_Jet1Jet2_Mass;
  WrappedTH2 *h_Jet3Jet4_dEta_Vs_Jet3Jet4_Mass;

  WrappedTH2 *h_DPhiJ34vsDPhiJ56;
  //next wrapped

};

#include "Framework/interface/SelectorFactory.h"
REGISTER_SELECTOR(Kinematics);

Kinematics::Kinematics(const ParameterSet& config, const TH1* skimCounters)
  : BaseSelector(config, skimCounters),
    cfg_Verbose(config.getParameter<bool>("verbose")),
    PSet_ElectronSelection(config.getParameter<ParameterSet>("ElectronSelection")),
    cfg_ElectronPtCut(config.getParameter<float>("ElectronSelection.electronPtCut")),  
    cfg_ElectronEtaCut(config.getParameter<float>("ElectronSelection.electronEtaCut")),
    PSet_MuonSelection(config.getParameter<ParameterSet>("MuonSelection")),
    cfg_MuonPtCut(config.getParameter<float>("MuonSelection.muonPtCut")),
    cfg_MuonEtaCut(config.getParameter<float>("MuonSelection.muonEtaCut")),
    PSet_TauSelection(config.getParameter<ParameterSet>("TauSelection")),
    cfg_TauPtCut(config.getParameter<float>("TauSelection.tauPtCut")),
    cfg_TauEtaCut(config.getParameter<float>("TauSelection.tauEtaCut")),
    PSet_JetSelection(config.getParameter<ParameterSet>("JetSelection")),
    cfg_JetPtCuts(config.getParameter<std::vector<float>>("JetSelection.jetPtCuts")),
    cfg_JetEtaCuts(config.getParameter<std::vector<float>>("JetSelection.jetEtaCuts")),
    cfg_JetNumberCut(config, "JetSelection.numberOfJetsCut"),
    PSet_HtSelection(config.getParameter<ParameterSet>("JetSelection")),
    cfg_HtCut(config, "JetSelection.HTCut"),
    PSet_BJetSelection(config.getParameter<ParameterSet>("BJetSelection")),
    cfg_BJetPtCuts(config.getParameter<std::vector<float>>("BJetSelection.jetPtCuts")),
    cfg_BJetEtaCuts(config.getParameter<std::vector<float>>("BJetSelection.jetEtaCuts")),
    cfg_BJetNumberCut(config, "BJetSelection.numberOfBJetsCut"),
    // PSet_METSelection(config.getParameter<ParameterSet>("METSelection")),
    PSet_TopologySelection(config.getParameter<ParameterSet>("TopologySelection")),
    cfg_SphericityCut(config, "TopologySelection.SphericityCut"),
    cfg_AplanarityCut(config, "TopologySelection.AplanarityCut"),
    cfg_PlanarityCut(config, "TopologySelection.PlanarityCut"),
    cfg_CircularityCut(config, "TopologySelection.CircularityCut"),
    cfg_Y23Cut(config, "TopologySelection.Y23Cut"),
    cfg_CparameterCut(config, "TopologySelection.CparameterCut"),
    cfg_DparameterCut(config, "TopologySelection.DparameterCut"),
    cfg_FoxWolframMomentCut(config, "TopologySelection.FoxWolframMomentCut"),
    cfg_AlphaTCut(config, "TopologySelection.AlphaTCut"),
    cfg_CentralityCut(config, "TopologySelection.CentralityCut"),
    // PSet_TopSelection(config.getParameter<ParameterSet>("TopSelection")),
    cfg_PtBinSetting(config.getParameter<ParameterSet>("CommonPlots.ptBins")),
    cfg_EtaBinSetting(config.getParameter<ParameterSet>("CommonPlots.etaBins")),
    cfg_PhiBinSetting(config.getParameter<ParameterSet>("CommonPlots.phiBins")),
    cfg_MassBinSetting(config.getParameter<ParameterSet>("CommonPlots.invMassBins")),
    cfg_DeltaEtaBinSetting(config.getParameter<ParameterSet>("CommonPlots.deltaEtaBins")),
    cfg_DeltaPhiBinSetting(config.getParameter<ParameterSet>("CommonPlots.deltaPhiBins")),
    cfg_DeltaRBinSetting(config.getParameter<ParameterSet>("CommonPlots.deltaRBins")),
    cAllEvents(fEventCounter.addCounter("All events")),
    cTrigger(fEventCounter.addCounter("Trigger")),
    cElectronVeto(fEventCounter.addCounter("e-veto")),
    cMuonVeto(fEventCounter.addCounter("#mu-veto")),
    cTauVeto(fEventCounter.addCounter("#tau-veto")),
    cJetSelection(fEventCounter.addCounter("Jets + H_{T}")),
    cBJetSelection(fEventCounter.addCounter("b-jets")),
    cTopologySelection(fEventCounter.addCounter("Topology")),
    cTopSelection(fEventCounter.addCounter("Top")),
    cSelected(fEventCounter.addCounter("All Selections"))
{ }

void Kinematics::book(TDirectory *dir) {

  // Fixed binning
  const int nBinsPt   = 4*cfg_PtBinSetting.bins();
  const double minPt  = cfg_PtBinSetting.min();
  const double maxPt  = 4*cfg_PtBinSetting.max();

  const int nBinsEta  = 2*cfg_EtaBinSetting.bins();
  const double minEta = 2*cfg_EtaBinSetting.min();
  const double maxEta = 2*cfg_EtaBinSetting.max();

  const int nBinsRap  = cfg_EtaBinSetting.bins();
  const double minRap = cfg_EtaBinSetting.min();
  const double maxRap = cfg_EtaBinSetting.max();

  const int nBinsPhi  = cfg_PhiBinSetting.bins();
  const double minPhi = cfg_PhiBinSetting.min();
  const double maxPhi = cfg_PhiBinSetting.max();

  const int nBinsM  = cfg_MassBinSetting.bins();
  const double minM = cfg_MassBinSetting.min();
  const double maxM = cfg_MassBinSetting.max();
  
  const int nBinsdEta  = 2*cfg_DeltaEtaBinSetting.bins();
  const double mindEta = cfg_DeltaEtaBinSetting.min();
  const double maxdEta = cfg_DeltaEtaBinSetting.max();

  const int nBinsdRap  = 2*cfg_DeltaEtaBinSetting.bins();
  const double mindRap = cfg_DeltaEtaBinSetting.min();
  const double maxdRap = cfg_DeltaEtaBinSetting.max();

  const int nBinsdPhi  = 2*cfg_DeltaPhiBinSetting.bins();
  const double mindPhi = cfg_DeltaPhiBinSetting.min();
  const double maxdPhi = cfg_DeltaPhiBinSetting.max();

  const int nBinsdR  = 2*cfg_DeltaRBinSetting.bins();
  const double mindR = cfg_DeltaRBinSetting.min();
  const double maxdR = cfg_DeltaRBinSetting.max();

  TDirectory* th1 = fHistoWrapper.mkdir(HistoLevel::kVital, dir, "TH1");
  TDirectory* th2 = fHistoWrapper.mkdir(HistoLevel::kVital, dir, "TH2");

  // Event Variables
  h_genMET_Et         =  fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital      , th1, "genMET_Et"    , ";Gen E_{T}^{miss} (GeV)"       , 100,  0.0,   +500.0);
  h_genMET_Phi        =  fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "genMET_Phi"   , ";Gen E_{T}^{miss} #phi (rads)" , nBinsPhi, minPhi, maxPhi);
  h_genHT_GenJets     =  fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital      , th1, "genHT_GenJets", ";GenJ H_{T} (GeV)"             , nBinsM  , minM  , maxM   );

  // Event-Shape Variables
  h_y23         = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "y23"        , ";y_{23}"        , 25, 0.0,    0.25);
  h_Sphericity  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Sphericity" , ";Sphericity"    , 20, 0.0,    1.00);
  h_SphericityT = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "SphericityT", ";Sphericity_{T}", 20, 0.0,    1.00);
  h_Y           = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Y"          , ";Y"             , 50, 0.0,    0.50);
  h_S_Vs_Y      = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "S_Vs_Y"     , ";Sphericity;Y=#frac{#sqrt{3}}{2}x(Q1-Q2)", 100, 0.0, 1.0, 50, 0.0, 0.5);
  h_Aplanarity  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Aplanarity" , ";Aplanarity" , 25, 0.0, 0.5);
  h_Planarity   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Planarity"  , ";Planarity"  , 25, 0.0, 0.5);
  h_CParameter  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "CParameter" , ";C"          , 20, 0.0, 1.0);
  h_DParameter  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "DParameter" , ";D"          , 20, 0.0, 1.0);
  h_H2          = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "H2"         , ";H_{2}"      , 20, 0.0, 1.0);
  h_Circularity = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Circularity", ";Circularity", 20, 0.0, 1.0);
  h_Centrality  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "Centrality" , ";Centrality" , 20, 0.0, 1.0);
  h_HT          = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "HT"         , ";H_{T}"      , 30, 0.0, 4000.0);
  h_JT          = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "JT"         , ";J_{T}"      , 30, 0.0, 4000.0);
  h_MHT         = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "MHT"        , ";MHT"        , 50, 0.0,  500.0);
  h_AlphaT      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "AlphaT"     , ";#alpha_{T}" , 20, 0.0,    1.0);

  // GenParticles: B-quarks
  h_BQuarks_N   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarks_N" , ";N (b-quarks)" , 20, 0.0, +20.0);
  h_BQuark1_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark1_Pt", ";p_{T} (GeV/c)" , nBinsPt, minPt, maxPt);
  h_BQuark2_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark2_Pt", ";p_{T} (GeV/c)" , nBinsPt, minPt, maxPt);
  h_BQuark3_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark3_Pt", ";p_{T} (GeV/c)" , nBinsPt, minPt, maxPt);
  h_BQuark4_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark4_Pt", ";p_{T} (GeV/c)" , nBinsPt, minPt, maxPt);
  vh_BQuarks_Pt.push_back(h_BQuark1_Pt);
  vh_BQuarks_Pt.push_back(h_BQuark2_Pt);
  vh_BQuarks_Pt.push_back(h_BQuark3_Pt);
  vh_BQuarks_Pt.push_back(h_BQuark4_Pt);

  h_BQuark1_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark1_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_BQuark2_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark2_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_BQuark3_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark3_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_BQuark4_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuark4_Eta", ";#eta", nBinsEta, minEta, maxEta);
  vh_BQuarks_Eta.push_back(h_BQuark1_Eta);
  vh_BQuarks_Eta.push_back(h_BQuark2_Eta);
  vh_BQuarks_Eta.push_back(h_BQuark3_Eta);
  vh_BQuarks_Eta.push_back(h_BQuark4_Eta);

  // GenParticles: BQuarks pairs
  h_BQuarkPair_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dR"  , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dEta", ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dPhi", ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_dRAverage   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRAverage"   , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_dEtaAverage = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dEtaAverage" , ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_dPhiAverage = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dPhiAverage" , ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);

  // GenParticles: BQuarks pairs with maximum pT
  h_BQuarkPair_MaxPt_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_Pt"  , ";p_{T} (GeV/c)"     , nBinsPt  , minPt  , maxPt  );
  h_BQuarkPair_MaxPt_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_Eta" , ";#eta"              , nBinsEta , minEta , maxEta );
  h_BQuarkPair_MaxPt_Phi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_Phi" , ";#phi (rads)"       , nBinsPhi , minPhi , maxPhi );
  h_BQuarkPair_MaxPt_M   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_M"   , ";M (GeV/c^{2})"     , nBinsM   , minM   , maxM  );
  h_BQuarkPair_MaxPt_dEta= fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_dEta", ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxPt_dPhi= fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_dPhi", ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxPt_dR  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_dR"  , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_MaxPt_jet1_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet1_dEta", ";#Delta#eta"        ,  nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxPt_jet1_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet1_dPhi", ";#Delta#phi (rads)" ,  nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxPt_jet1_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet1_dR"  , ";#DeltaR"           ,  nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_MaxPt_jet2_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet2_dEta", ";#Delta#eta"        ,  nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxPt_jet2_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet2_dPhi", ";#Delta#phi (rads)" ,  nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxPt_jet2_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxPt_jet2_dR"  , ";#DeltaR"           ,  nBinsdR  , mindR  , maxdR  );

  // GenParticles: BQuarks pairs with maximum mass
  h_BQuarkPair_MaxMass_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_Pt"  , ";p_{T} (GeV/c)"     , nBinsPt, minPt  , maxPt );
  h_BQuarkPair_MaxMass_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_Eta" , ";#eta"              , nBinsEta , minEta , maxEta );
  h_BQuarkPair_MaxMass_Phi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_Phi" , ";#phi (rads)"       , nBinsPhi , minPhi , maxPhi );
  h_BQuarkPair_MaxMass_M   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_M"   , ";M (GeV/c^{2})"     , nBinsM   , minM   , maxM   );
  h_BQuarkPair_MaxMass_dEta= fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_dEta", ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxMass_dPhi= fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_dPhi", ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxMass_dR  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_dR"  , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_MaxMass_jet1_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet1_dEta", ";#Delta#eta"        ,  nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxMass_jet1_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet1_dPhi", ";#Delta#phi (rads)" ,  nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxMass_jet1_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet1_dR"  , ";#DeltaR"           ,  nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_MaxMass_jet2_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet2_dEta", ";#Delta#eta"        ,  nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_MaxMass_jet2_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet2_dPhi", ";#Delta#phi (rads)" ,  nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_MaxMass_jet2_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_MaxMass_jet2_dR"  , ";#DeltaR"           ,  nBinsdR  , mindR  , maxdR  );

  // GenParticles: BQuarks pair closest together
  h_BQuarkPair_dRMin_Pt        = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_Pt"       , ";p_{T} (GeV/c)"     , nBinsPt  , minPt  , maxPt  );
  h_BQuarkPair_dRMin_Eta       = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_Eta"      , ";#eta"              , nBinsEta , minEta , maxEta );
  h_BQuarkPair_dRMin_Rap       = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_Rap"      , ";#omega"            , nBinsRap , minRap , maxRap );
  h_BQuarkPair_dRMin_Phi       = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_Phi"      , ";#phi (rads)"       , nBinsPhi , minPhi , maxPhi );
  h_BQuarkPair_dRMin_dEta      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_dEta"     , ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_dRMin_dPhi      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_dPhi"     , ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_dRMin_dR        = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_dR"       , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_dRMin_Mass      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_Mass"     , ";M (GeV/c^{2})"     , nBinsM   , minM   , maxM   );
  h_BQuarkPair_dRMin_jet1_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet1_dEta", ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_dRMin_jet1_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet1_dPhi", ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_dRMin_jet1_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet1_dR"  , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  h_BQuarkPair_dRMin_jet2_dEta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet2_dEta", ";#Delta#eta"        , nBinsdEta, mindEta, maxdEta);
  h_BQuarkPair_dRMin_jet2_dPhi = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet2_dPhi", ";#Delta#phi (rads)" , nBinsdPhi, mindPhi, maxdPhi);
  h_BQuarkPair_dRMin_jet2_dR   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "BQuarkPair_dRMin_jet2_dR"  , ";#DeltaR"           , nBinsdR  , mindR  , maxdR  );
  //
  h_BQuarkPair_dRMin_Eta1_Vs_Eta2 = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuarkPair_dRMin_Eta1_Vs_Eta2", ";#eta;#eta", nBinsEta, minEta, maxEta, nBinsEta, minEta, maxEta);
  h_BQuarkPair_dRMin_Phi1_Vs_Phi2 = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuarkPair_dRMin_Phi1_Vs_Phi2", ";#phi;#phi", nBinsPhi, minPhi, maxPhi, nBinsPhi, minPhi, maxPhi);
  h_BQuarkPair_dRMin_Pt1_Vs_Pt2   = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuarkPair_dRMin_Pt1_Vs_Pt2"  , ";p_{T} (GeV/c); p_{T} (GeV/c)", nBinsPt, minPt, maxPt, nBinsPt, minPt, maxPt);
  h_BQuarkPair_dRMin_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuarkPair_dRMin_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  
  // Leading Jets
  h_Jet1Jet2_dEta_Vs_Jet3Jet4_dEta = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "Jet1Jet2_dEta_Vs_Jet3Jet4_dEta", ";#Delta#eta(j_{1},j_{2});#Delta#eta(j_{3},j_{4})", nBinsdEta, mindEta, maxdEta, nBinsdEta, mindEta, maxdEta);

  h_Jet1Jet2_dPhi_Vs_Jet3Jet4_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "Jet1Jet2_dPhi_Vs_Jet3Jet4_dPhi", ";#Delta#phi(j_{1},j_{2}) (rads);#Delta#phi(j_{3},j_{4}) (rads)", nBinsdPhi, mindPhi, maxdPhi, nBinsdPhi, mindPhi, maxdPhi);

  h_Jet1Jet2_dEta_Vs_Jet1Jet2_Mass = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "Jet1Jet2_dEta_Vs_Jet1Jet2_Mass", ";#Delta#eta(j_{1},j_{2});M(j_{1},j_{2}) (GeV/c^{2})", nBinsdEta, mindEta, maxdEta, nBinsM, minM, maxM);

  h_Jet3Jet4_dEta_Vs_Jet3Jet4_Mass = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "Jet3Jet4_dEta_Vs_Jet3Jet4_Mass", ";#Delta#eta(j_{3},j_{4});M(j_{3},j_{4}) (GeV/c^{2})", nBinsdEta, mindEta, maxdEta, nBinsM, minM, maxM);
  
  // GenJets
  h_GenJets_N   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJets_N" , ";genJet multiplicity" , 30, 0.0, 30.0);
  h_GenJet1_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet1_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  h_GenJet2_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet2_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  h_GenJet3_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet3_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  h_GenJet4_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet4_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  h_GenJet5_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet5_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  h_GenJet6_Pt  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet6_Pt", ";p_{T} (GeV/c)", nBinsPt, minPt, maxPt);
  // To ease manipulation put in vector
  vh_GenJets_Pt.push_back(h_GenJet1_Pt);
  vh_GenJets_Pt.push_back(h_GenJet2_Pt);
  vh_GenJets_Pt.push_back(h_GenJet3_Pt);
  vh_GenJets_Pt.push_back(h_GenJet4_Pt);
  vh_GenJets_Pt.push_back(h_GenJet5_Pt);
  vh_GenJets_Pt.push_back(h_GenJet6_Pt);
  //
  h_GenJet1_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet1_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_GenJet2_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet2_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_GenJet3_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet3_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_GenJet4_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet4_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_GenJet5_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet5_Eta", ";#eta", nBinsEta, minEta, maxEta);
  h_GenJet6_Eta = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, th1, "GenJet6_Eta", ";#eta", nBinsEta, minEta, maxEta);
  vh_GenJets_Eta.push_back(h_GenJet1_Eta);
  vh_GenJets_Eta.push_back(h_GenJet2_Eta);
  vh_GenJets_Eta.push_back(h_GenJet3_Eta);
  vh_GenJets_Eta.push_back(h_GenJet4_Eta);
  vh_GenJets_Eta.push_back(h_GenJet5_Eta);
  vh_GenJets_Eta.push_back(h_GenJet6_Eta);

  // GenJets: Dijet with largest mass
  h_MaxDiJetMass_Pt    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_Pt"   , ";p_{T} (GeV/c)"    , nBinsPt  , minPt, maxPt*2);
  h_MaxDiJetMass_Eta   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_Eta"  , ";#eta"             , nBinsEta , minEta, maxEta);
  h_MaxDiJetMass_Rap   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_Rap"  , ";#omega"           , nBinsRap , minRap, maxRap);
  h_MaxDiJetMass_Mass  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_Mass" , ";M (GeV/c^{2})"    , nBinsM   , minM  , maxM  );
  h_MaxDiJetMass_dEta  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_dEta" , ";#Delta#eta"       , nBinsdEta, mindEta, maxdEta);
  h_MaxDiJetMass_dRap  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_dRap" , ";#Delta#omega"     , nBinsdRap, mindRap, maxdRap);
  h_MaxDiJetMass_dPhi  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_dPhi" , ";#Delta#phi"       , nBinsdPhi, mindPhi, maxdPhi);  
  h_MaxDiJetMass_dR    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_dR"   , ";#DeltaR"          , nBinsdR, mindR, maxdR);  
  h_MaxDiJetMass_dRrap = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxDiJetMass_dRrap", ";#DeltaR_{#omega}" , nBinsdR, mindR, maxdR);  
  h_MaxDiJetMass_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kInformative, th2, "MaxDiJetMass_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)"  , nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_MaxDiJetMass_dRap_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kInformative, th2, "MaxDiJetMass_dRap_Vs_dPhi", ";#Delta#omega;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);

  // GenJets: Untagged jet pair with min dR
  h_dRMinDiJet_NoBJets_Pt    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_Pt"   , ";p_{T} (GeV/c)"    , nBinsPt  , minPt  , maxPt );
  h_dRMinDiJet_NoBJets_Eta   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_Eta"  , ";#eta"             , nBinsEta , minEta , maxEta);
  h_dRMinDiJet_NoBJets_Rap   = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_Rap"  , ";#omega"           , nBinsRap , minRap , maxRap);
  h_dRMinDiJet_NoBJets_Mass  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_Mass" , ";M (GeV/c^{2})"    , nBinsM   , minM   , maxM );
  h_dRMinDiJet_NoBJets_dEta  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_dEta" , ";#Delta#eta"       , nBinsdEta, mindEta, maxdEta);
  h_dRMinDiJet_NoBJets_dPhi  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_dPhi" , ";#Delta#phi"       , nBinsdPhi, mindPhi, maxdPhi);  
  h_dRMinDiJet_NoBJets_dR    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "dRMinDiJet_NoBJets_dR"   , ";#DeltaR"          , nBinsdR  , mindR  , maxdR);  

  // GenJets: Trijet with largest pT
  h_MaxTriJetPt_Pt       = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_Pt"     , ";p_{T} (GeV/c)", nBinsPt  , minPt  , maxPt );
  h_MaxTriJetPt_Eta      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_Eta"    , ";#eta"         , nBinsEta , minEta , maxEta);
  h_MaxTriJetPt_Rap      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_Rap"    , ";#omega"       , nBinsRap , minRap , maxRap);
  h_MaxTriJetPt_Mass     = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_Mass"   , ";M (GeV/c^{2})", nBinsM   , minM   , maxM  );
  h_MaxTriJetPt_dEtaMax  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dEtaMax", ";#Delta#eta"   , nBinsdEta, mindEta, maxdEta);
  h_MaxTriJetPt_dPhiMax  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dPhiMax", ";#Delta#phi"   , nBinsdPhi, mindPhi, maxdPhi);  
  h_MaxTriJetPt_dRMax    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dRMax"  , ";#DeltaR"      , nBinsdR  , mindR  , maxdR  );
  h_MaxTriJetPt_dEtaMin  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dEtaMin", ";#Delta#eta"   , nBinsdEta, mindEta, maxdEta);
  h_MaxTriJetPt_dPhiMin  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dPhiMin", ";#Delta#phi"   , nBinsdPhi, mindPhi, maxdPhi);  
  h_MaxTriJetPt_dRMin    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dRMin"  , ";#DeltaR"      , nBinsdR  , mindR  , maxdR  );
  h_MaxTriJetPt_dEtaAverage  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dEtaAverage", ";#Delta#eta"  , nBinsdEta, mindEta, maxdEta);
  h_MaxTriJetPt_dPhiAverage  = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dPhiAverage", ";#Delta#phi"  , nBinsdPhi, mindPhi, maxdPhi);  
  h_MaxTriJetPt_dRAverage    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kInformative, th1, "MaxTriJetPt_dRAverage"  , ";#Delta#omega", nBinsdRap, mindRap, maxdRap);

  // Correlations
  h_BQuark1_BQuark2_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark1_BQuark2_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_BQuark1_BQuark3_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark1_BQuark3_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_BQuark1_BQuark4_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark1_BQuark4_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_BQuark2_BQuark3_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark2_BQuark3_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_BQuark2_BQuark4_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark2_BQuark4_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);
  h_BQuark3_BQuark4_dEta_Vs_dPhi = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, th2, "BQuark3_BQuark4_dEta_Vs_dPhi", ";#Delta#eta;#Delta#phi (rads)", nBinsdEta, mindEta, maxdEta, nBinsdPhi, mindPhi, maxdPhi);

  h_DPhiJ34vsDPhiJ56     = fHistoWrapper.makeTH<TH2F>(HistoLevel::kDebug, dir, "DPhiJ34vsDPhiJ56"     , ";#Delta #phi(j3,j4);#Delta #phi(j5,j6)"     , 40, 0.0, 3.15,     40  ,0.0, 3.15);

  h_CosTheta_Bjet1TopCM_TrijetLab = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet1TopCM_TrijetLab",";cos#theta(Bjet1_{TopCM},Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_Bjet2TopCM_TrijetLab = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet2TopCM_TrijetLab",";cos#theta(Bjet2_{TopCM},Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_Bjet3TopCM_TrijetLab = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet3TopCM_TrijetLab",";cos#theta(Bjet3_{TopCM},Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_Bjet1TopCM_Zaxis     = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet1TopCM_Zaxis",";cos#theta(Bjet1_{TopCM},zaxis)",40, -1., 1.);
  h_CosTheta_Bjet2TopCM_Zaxis     = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet2TopCM_Zaxis",";cos#theta(Bjet2_{TopCM},zaxis)",40, -1., 1.);
  h_CosTheta_Bjet3TopCM_Zaxis     = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_Bjet3TopCM_Zaxis",";cos#theta(Bjet3_{TopCM},zaxis)",40, -1., 1.);

  h_CosTheta_LdgTrijetLdgJetTopCM_TrijetLab    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_LdgTrijetLdgJetTopCM_TrijetLab",";cos#theta(LdgTrijetLdgJet_{TopCM},Trije\
t_{Lab})",40, -1., 1.);
  h_CosTheta_LdgTrijetSubldgJetTopCM_TrijetLab = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_LdgTrijetSubldgJetTopCM_TrijetLab",";cos#theta(LdgTrijetSubldgJet_{TopCM}\
,Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_LdgTrijetBjetTopCM_TrijetLab      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_LdgTrijetBjetTopCM_TrijetLab",";cos#theta(LdgTrijetBjet_{TopCM},Trijet_{L\
ab})",40, -1., 1.);

  h_CosTheta_SubldgTrijetLdgJetTopCM_TrijetLab    = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_SubldgTrijetLdgJetTopCM_TrijetLab",";cos#theta(SubldgTrijetLdgJet_{Top\
CM},Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab",";cos#theta(SubldgTrijetSubldgJe\
t_{TopCM},Trijet_{Lab})",40, -1., 1.);
  h_CosTheta_SubldgTrijetBjetTopCM_TrijetLab      = fHistoWrapper.makeTH<TH1F>(HistoLevel::kDebug, dir, "CosTheta_SubldgTrijetBjetTopCM_TrijetLab",";cos#theta(SubldgTrijetBjet_{TopCM},\
Trijet_{Lab})",40, -1., 1.);

  //next histogram
  return;
}

void Kinematics::setupBranches(BranchManager& branchManager) {
  fEvent.setupBranches(branchManager);
}


void Kinematics::process(Long64_t entry) {

  if ( !fEvent.isMC() ) return;
    
  // Increment Counter
  cAllEvents.increment();
  
  // Initialise MCTools object
  MCTools mcTools(fEvent);

  //================================================================================================
  // 1) Apply trigger
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== Trigger" << std::endl;
  if ( !(fEvent.passTriggerDecision()) ) return;
  cTrigger.increment();


  //================================================================================================
  // 2) MET filters (to remove events with spurious sources of fake MET)       
  //================================================================================================
  // nothing to do

  //================================================================================================
  // 3) Primarty Vertex (Check that a PV exists)
  //================================================================================================
  // nothing to do

  //================================================================================================
  // 4) Electron veto (fully hadronic + orthogonality)  
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== Electron veto" << std::endl;
  vector<genParticle> selectedElectrons = GetGenParticles(fEvent.genparticles().getGenParticles(), cfg_ElectronPtCut, cfg_ElectronEtaCut, 11, true, false);
  if (0)
    {
      std::cout << "\nnElectrons = " << selectedElectrons.size() << std::endl;
      for (auto& p: selectedElectrons) std::cout << "\tpT = " << p.pt() << " (GeV/c), eta = " << p.eta() << ", phi = " << p.phi() << " (rads)" << std::endl;
    }
  if ( selectedElectrons.size() > 0 ) return;
  cElectronVeto.increment();


  //================================================================================================
  // 5) Muon veto (fully hadronic + orthogonality)  
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== Muon veto" << std::endl;
  vector<genParticle> selectedMuons = GetGenParticles(fEvent.genparticles().getGenParticles(), cfg_MuonPtCut, cfg_MuonEtaCut, 13, true, false);
  if (cfg_Verbose)
    {
      std::cout << "\nnMuons = " << selectedMuons.size() << std::endl;
      for (auto& p: selectedMuons) std::cout << "\tpT = " << p.pt() << " (GeV/c), eta = " << p.eta() << ", phi = " << p.phi() << " (rads)" << std::endl;
    }
  if ( selectedMuons.size() > 0 ) return;
  cMuonVeto.increment();


  //================================================================================================
  // 6) Tau veto (HToTauNu orthogonality)  
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== Tau veto" << std::endl;
  vector<genParticle> selectedTaus = GetGenParticles(fEvent.genparticles().getGenParticles(), cfg_TauPtCut, cfg_TauEtaCut, 15, true, false);
  if (0)
    {
      std::cout << "\nnTaus = " << selectedTaus.size() << std::endl;
      for (auto& p: selectedTaus) std::cout << "\tpT = " << p.pt() << " (GeV/c), eta = " << p.eta() << ", phi = " << p.phi() << " (rads)" << std::endl;
      std::cout << "" << std::endl;
    }
  if ( selectedTaus.size() > 0 ) return;
  cTauVeto.increment();


  //================================================================================================
  // 7) Jet Selection
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== Jet Selection" << std::endl;
  vector<GenJet> selectedJets = GetGenJets(fEvent.genjets(), cfg_JetPtCuts, cfg_JetEtaCuts);
  // for (auto& p: selectedJets) std::cout << "\tpT = " << p.pt() << " (GeV/c), eta = " << p.eta() << ", phi = " << p.phi() << " (rads)" << std::endl;
  if (!cfg_JetNumberCut.passedCut(selectedJets.size())) return;

  // HT Selection
  double genJ_HT = 0.0;
  std::vector<math::XYZTLorentzVector> selJets_p4;
  math::XYZTLorentzVector jet_p4;
  for(auto jet: selectedJets) 
    {
        jet_p4 = jet.p4();
	genJ_HT += jet.pt();
	selJets_p4.push_back( jet_p4 );
    }

  if ( !cfg_HtCut.passedCut(genJ_HT) ) return;
  cJetSelection.increment();

  //================================================================================================
  // 8) BJet Selection
  //================================================================================================
  if (cfg_Verbose) std::cout << "=== BJet Selection" << std::endl;
  vector<genParticle> selectedBQuarks = GetGenParticles(fEvent.genparticles().getGenParticles(), 10, 3, 5, true, false);
  std::sort( selectedBQuarks.begin(), selectedBQuarks.end(), PtComparator() );
  if (0) for (auto& p: selectedBQuarks) mcTools.PrintGenParticle(p);

  // Match b-quarks with GenJets
  vector<GenJet> selectedBJets = GetGenJets(selectedJets, cfg_BJetPtCuts, cfg_BJetEtaCuts, selectedBQuarks);
  // for (auto& p: selectedBJets) std::cout << "\tpT = " << p.pt() << " (GeV/c), eta = " << p.eta() << ", phi = " << p.phi() << " (rads)" << std::endl;

  // Get selected jets excluding the matched bjets
  bool isBJet = false;
  std::vector<math::XYZTLorentzVector> selJets_NoBJets_p4;

  // For-loop: Selected jets
  for (auto& jet: selectedJets) 
    {
      isBJet = false;
	    
      // For-loop: Selected bjets
      for (auto& bjet: selectedBJets) 
	{
	  double dR = ROOT::Math::VectorUtil::DeltaR(jet.p4(), bjet.p4());
	  if (dR < 0.01) isBJet = true;
	}
      if (isBJet) continue;
      jet_p4 = jet.p4();
      selJets_NoBJets_p4.push_back(jet_p4);
    }

  if (!cfg_BJetNumberCut.passedCut(selectedBJets.size())) return;
  cBJetSelection.increment();


  //================================================================================================
  // 9) BJet SF
  //================================================================================================
  // nothing to do
  

  //================================================================================================
  // 10) MET selection 
  //================================================================================================
  // nothing to do


  //================================================================================================
  // 11) Topology selection 
  //================================================================================================
  float C, D, H2;
  float Circularity;
  float y23, Sphericity, SphericityT, Aplanarity, Planarity, Y; // functions to return values when properly implemented
  float HT, JT, MHT, Centrality;
  vector<float> a = GetMomentumTensorEigenValues(selJets_p4, C, D, H2);
  vector<float> b = GetMomentumTensorEigenValues2D(selJets_p4, Circularity);
  vector<float> c = GetSphericityTensorEigenValues(selJets_p4, y23, Sphericity, SphericityT, Aplanarity, Planarity, Y);
  double alphaT   = GetAlphaT(selJets_p4, HT, JT, MHT, Centrality);
  
  // Apply cuts
  if ( !cfg_CparameterCut.passedCut(C) ) return;
  if ( !cfg_DparameterCut.passedCut(D) ) return;
  if ( !cfg_FoxWolframMomentCut.passedCut(H2) ) return;
  if ( !cfg_CircularityCut.passedCut(Circularity) ) return;
  if ( !cfg_Y23Cut.passedCut(y23) ) return;
  if ( !cfg_SphericityCut.passedCut(Sphericity) ) return;
  if ( !cfg_AplanarityCut.passedCut(Aplanarity) ) return;
  if ( !cfg_PlanarityCut.passedCut(Planarity) ) return;
  if ( !cfg_CentralityCut.passedCut(Centrality) ) return;
  if ( !cfg_AlphaTCut.passedCut(alphaT) ) return;
  cTopologySelection.increment();


  //================================================================================================
  // 12) Top selection 
  //================================================================================================
  cTopSelection.increment();


  //================================================================================================
  // Standard Selections    
  //================================================================================================


  //================================================================================================
  // All Selections
  //================================================================================================
  cSelected.increment();

  // Fill Histograms
  h_GenJets_N    ->Fill(selectedJets.size());
  h_genMET_Et    ->Fill(fEvent.genMET().et()); 
  h_genMET_Phi   ->Fill(fEvent.genMET().Phi());
  h_genHT_GenJets->Fill(genJ_HT);
  h_y23          ->Fill(y23);
  h_Sphericity   ->Fill(Sphericity);
  h_SphericityT  ->Fill(SphericityT);
  h_Y            ->Fill(Y);
  h_S_Vs_Y       ->Fill(Sphericity, Y);
  h_Aplanarity   ->Fill(Aplanarity);
  h_Planarity    ->Fill(Planarity);
  h_CParameter   ->Fill(C);
  h_DParameter   ->Fill(D);
  h_H2           ->Fill(H2);
  h_Circularity  ->Fill(Circularity);
  h_Centrality   ->Fill(Centrality);
  h_HT           ->Fill(HT);
  h_JT           ->Fill(JT);
  h_MHT          ->Fill(MHT);
  h_AlphaT       ->Fill(alphaT);

  ///////////////////////////////////////////////////////////////////////////
  // GenParticles 
  ///////////////////////////////////////////////////////////////////////////
  if (0) std::cout << "=== GenParticles" << std::endl;
  std::vector<math::XYZTLorentzVector> bQuarks_p4;
  math::XYZTLorentzVector tbWPlus_BQuark_p4;
  math::XYZTLorentzVector tbWPlus_Wqq_Quark_p4;
  math::XYZTLorentzVector tbWPlus_Wqq_AntiQuark_p4;
  math::XYZTLorentzVector tbWMinus_BQuark_p4;
  math::XYZTLorentzVector tbWMinus_Wqq_Quark_p4;
  math::XYZTLorentzVector tbWMinus_Wqq_AntiQuark_p4;

  // Define the table
  Table table("Evt | Index | PdgId | Status | Charge | Pt | Eta | Phi | E | Vertex (mm) | Lxy (mm) | d0 (mm) | Mothers | Daughters |", "Text"); //LaTeX or Text    
  int row = 0;

  // For-loop: GenParticles
  for (auto& p: fEvent.genparticles().getGenParticles()) {

    // mcTools.PrintGenParticle(p);
    // mcTools.PrintGenDaughters(p);

    // Particle properties
    short genP_index   = p.index();
    int genP_pdgId     = p.pdgId();
    int genP_status    = p.status();
    double genP_pt     = p.pt();
    double genP_eta    = p.eta();
    double genP_phi    = p.phi();
    double genP_energy = p.e();
    int genP_charge    = p.charge();
    // ROOT::Math::XYZPoint genP_vtx(p.vtxX()*10, p.vtxY()*10, p.vtxZ()*10); // in mm
    math::XYZTLorentzVector genP_p4;
    genP_p4 = p.p4();
    
    // Get vectors for mom/daus
    std::vector<short> genP_mothers   = p.mothers();
    std::vector<short> genP_daughters = p.daughters();
    
    // Assign mother/daughers for Lxy & d0 calculation
    // genParticle m;
    // genParticle d;
    // if (genP_mothers.size() > 0  ) m = fEvent.genparticles().getGenParticles()[genP_mothers.at(0)];
    // if (genP_daughters.size() > 0) d = fEvent.genparticles().getGenParticles()[genP_daughters.at(0)];
    
    // Filtering    
    if (!p.isLastCopy()) continue;
    // // if ( !mcTools.IsQuark(genP_pdgId) ) continue;
    // if (!p.isPrompt()) continue;
    // if (!p.isPromptDecayed()) continue;
    // if (!p.isPromptFinalState()) continue;
    // if (!p.isDecayedLeptonHadron()) continue;
    // if (!p.isTauDecayProduct()) continue;
    // if (!p.isPromptTauDecayProduct()) continue;
    // if (!p.isDirectTauDecayProduct()) continue;
    // if (!p.isDirectPromptTauDecayProduct()) continue;
    // if (!p.isDirectPromptTauDecayProductFinalState()) continue;
    // if (!p.isDirectHadronDecayProduct()) continue;	
    // if (!p.isDirectHardProcessTauDecayProductFinalState()) continue;
    //// if (!p.isHardProcess()) continue;
    // if (!p.fromHardProcess()) continue;
    // if (!p.fromHardProcessDecayed()) continue;
    // if (!p.fromHardProcessFinalState()) continue;
    // if (!p.isHardProcessTauDecayProduct()) continue;
    // if (!p.isDirectHardProcessTauDecayProduct()) continue;
    // if (!p.fromHardProcessBeforeFSR()) continue;
    // if (!p.isFirstCopy()) continue;
    // if (!p.isLastCopyBeforeFSR()) continue;
      
    // Add table rows
    if (cfg_Verbose)
      {
	table.AddRowColumn(row, auxTools.ToString(entry)           );
	table.AddRowColumn(row, auxTools.ToString(genP_index)      );
	table.AddRowColumn(row, auxTools.ToString(genP_pdgId)      );
	table.AddRowColumn(row, auxTools.ToString(genP_status)     );
	table.AddRowColumn(row, auxTools.ToString(genP_charge)     );
	table.AddRowColumn(row, auxTools.ToString(genP_pt , 3)     );
	table.AddRowColumn(row, auxTools.ToString(genP_eta, 4)     );
	table.AddRowColumn(row, auxTools.ToString(genP_phi, 3)     );
	table.AddRowColumn(row, auxTools.ToString(genP_energy, 3)  );
	// table.AddRowColumn(row, "("+auxTools.ToString(genP_vtx.x(), 3)+", "+auxTools.ToString(genP_vtx.y(), 3) +", "+auxTools.ToString(genP_vtx.z(), 3) + ")" );
	table.AddRowColumn(row, "N/A" );
	table.AddRowColumn(row, "N/A" ); // auxTools.ToString(genP_Lxy, 3)
	table.AddRowColumn(row, "N/A" ); // auxTools.ToString(genP_d0,  3)
	if (genP_mothers.size() < 6)
	  {
	    table.AddRowColumn(row, auxTools.ConvertIntVectorToString(genP_mothers) );
	  }
	else table.AddRowColumn(row, ".. Too many .." );
	if (genP_daughters.size() < 6)
	  {
	    table.AddRowColumn(row, auxTools.ConvertIntVectorToString(genP_daughters) );
	  }
	else table.AddRowColumn(row, ".. Too many .." );
	row++;
      }
    
    //    if (std::abs(genP_pdgId) == 6) TOP_p4.push_back(genP_p4);
    // b-quarks
    if(std::abs(genP_pdgId) == 5)
      {	
	bQuarks_p4.push_back( genP_p4 );	    
	if ( mcTools.HasMother(p, +6) ) tbWPlus_BQuark_p4  = genP_p4;
	if ( mcTools.HasMother(p, -6) ) tbWMinus_BQuark_p4 = genP_p4;	
      }// b-quarks	
    

    // W-
    if (mcTools.HasMother(p, -24) )
      {
	if (genP_pdgId > 0) tbWPlus_Wqq_Quark_p4 = genP_p4;
	else tbWPlus_Wqq_AntiQuark_p4 = genP_p4;
      }

    // W+
    if (mcTools.HasMother(p, +24) )
      {
	//	std::cout << auxTools.ConvertIntVectorToString(genP_mothers) << std::endl;
	if (genP_pdgId > 0) tbWMinus_Wqq_Quark_p4 = genP_p4;
	else tbWMinus_Wqq_AntiQuark_p4 = genP_p4;
      }
    
  }//for-loop: genParticles
  
  if (cfg_Verbose) table.Print();
  
  
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // GenJets
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  if (0) std::cout << "=== GenJets" << std::endl;
  std::vector<math::XYZTLorentzVector> v_dijet_p4;
  std::vector<double> v_dijet_masses;
  std::vector<double> v_dijet_dR;
  std::vector<double> v_dijet_dRrap;
  std::vector<double> v_dijet_dEta;
  std::vector<double> v_dijet_dPhi;
  std::vector<double> v_dijet_dRap;
  
  double maxDijetMass_mass;
  math::XYZTLorentzVector maxDijetMass_p4;
  int maxDijetMass_pos;
  double maxDijetMass_dR;
  double maxDijetMass_dRrap;
  double maxDijetMass_dEta;
  double maxDijetMass_dPhi;
  double maxDijetMass_dRap;
  double maxDijetMass_rapidity;

  int iJet = 0;  
  // For-loop: All selected jets    for (auto& jet: selJets_p4) 
  for (size_t i=0; i < selJets_p4.size(); i++)
    {
      iJet++;
      double genJ_Pt  = selJets_p4.at(i).pt();
      double genJ_Eta = selJets_p4.at(i).eta();
      
      // Fill vector containers
      if (i < 6)
	{
	  vh_GenJets_Pt.at(i) -> Fill( genJ_Pt  );
	  vh_GenJets_Eta.at(i)-> Fill( genJ_Eta  );     
	}
	
       // For-loop: All selected jets (nested)
       for (size_t j=i+1; j < selJets_p4.size(); j++)
	 {
       	  math::XYZTLorentzVector p4_i = selJets_p4.at(i);
       	  math::XYZTLorentzVector p4_j = selJets_p4.at(j);
       	  math::XYZTLorentzVector p4   = p4_i + p4_j;
       	  double rap_i = mcTools.GetRapidity(p4_i);
       	  double rap_j = mcTools.GetRapidity(p4_j);
       	  double dR    = ROOT::Math::VectorUtil::DeltaR(p4_i, p4_j);
       	  double dRap  = std::abs(rap_i - rap_j);
       	  double dEta  = std::abs(p4_i.eta() - p4_j.eta());
       	  double dPhi  = std::abs(ROOT::Math::VectorUtil::DeltaPhi(p4_i, p4_j));
          
       	  v_dijet_p4.push_back( p4 );
       	  v_dijet_masses.push_back( p4.mass() );
       	  v_dijet_dR.push_back( dR );
       	  v_dijet_dRrap.push_back( sqrt( pow(dRap, 2) + pow(dPhi, 2) ) ); 
       	  v_dijet_dEta.push_back( dEta ); 
       	  v_dijet_dRap.push_back( dRap );
       	  v_dijet_dPhi.push_back( dPhi );
	 }// For-loop: Jets
    }// For-loop: Jets


  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // MaxDiJet System (DiJet combination with largest mass)
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  if (0) std::cout << "=== MaxDiJet System" << std::endl;
  if (v_dijet_masses.size() > 0)
    {
      maxDijetMass_pos      = std::max_element(v_dijet_masses.begin(), v_dijet_masses.end()) - v_dijet_masses.begin();
      maxDijetMass_mass     = v_dijet_masses.at(maxDijetMass_pos);
      maxDijetMass_p4       = v_dijet_p4.at(maxDijetMass_pos);
      maxDijetMass_dR       = v_dijet_dR.at(maxDijetMass_pos);
      maxDijetMass_dRrap    = v_dijet_dRrap.at(maxDijetMass_pos);
      maxDijetMass_dEta     = v_dijet_dEta.at(maxDijetMass_pos);
      maxDijetMass_dPhi     = v_dijet_dPhi.at(maxDijetMass_pos);
      maxDijetMass_dRap     = v_dijet_dRap.at(maxDijetMass_pos);
      maxDijetMass_rapidity = mcTools.GetRapidity(maxDijetMass_p4);
    }

  // Fill histos
  h_MaxDiJetMass_Mass ->Fill( maxDijetMass_mass     );
  h_MaxDiJetMass_Pt   ->Fill( maxDijetMass_p4.pt()  );
  h_MaxDiJetMass_Eta  ->Fill( maxDijetMass_p4.eta() );
  h_MaxDiJetMass_Rap  ->Fill( maxDijetMass_rapidity );
  h_MaxDiJetMass_dR   ->Fill( maxDijetMass_dR       );
  h_MaxDiJetMass_dRrap->Fill( maxDijetMass_dRrap    );
  h_MaxDiJetMass_dEta ->Fill( maxDijetMass_dEta     );
  h_MaxDiJetMass_dPhi ->Fill( maxDijetMass_dPhi     );
  h_MaxDiJetMass_dRap ->Fill( maxDijetMass_dRap     );
  h_MaxDiJetMass_dEta_Vs_dPhi->Fill( maxDijetMass_dEta, maxDijetMass_dPhi );
  h_MaxDiJetMass_dRap_Vs_dPhi->Fill( maxDijetMass_dRap, maxDijetMass_dPhi );


  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // GenJets Correlations
  //////////////////////////////////////////////////////////////////////////////////////////////////////  
  if (0) std::cout << "=== GenJets Correlations" << std::endl;

  // Fill Histos
  if (selJets_p4.size() >= 2)
    {
      double jet1_Eta = selJets_p4.at(0).eta();
      double jet1_Phi = selJets_p4.at(0).phi();
      double jet2_Eta = selJets_p4.at(1).eta();
      double jet2_Phi = selJets_p4.at(1).phi();      
      h_Jet1Jet2_dEta_Vs_Jet1Jet2_Mass ->Fill(std::abs(jet1_Eta - jet2_Eta), (selJets_p4.at(0) + selJets_p4.at(1)).mass() );

      if (selJets_p4.size() >= 4)
	{
	  double jet3_Eta = selJets_p4.at(2).eta();
	  double jet3_Phi = selJets_p4.at(2).phi();
	  double jet4_Eta = selJets_p4.at(3).eta();
	  double jet4_Phi = selJets_p4.at(3).phi();
	  h_Jet1Jet2_dEta_Vs_Jet3Jet4_dEta ->Fill(std::abs(jet1_Eta - jet2_Eta), std::abs(jet3_Eta - jet4_Eta));
	  h_Jet1Jet2_dPhi_Vs_Jet3Jet4_dPhi ->Fill(std::abs(jet1_Phi - jet2_Phi), std::abs(jet3_Phi - jet4_Phi));      
	  h_Jet3Jet4_dEta_Vs_Jet3Jet4_Mass ->Fill(std::abs(jet3_Eta - jet4_Eta), (selJets_p4.at(2) + selJets_p4.at(3)).mass() );
	}     
    }  
    
  
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // GenJets: Trijet with largest pT
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  if(0) std::cout << "=== Trijet (Max Pt)" << std::endl;

  int nTriJetCands = 0;
  double dR_ij     = 0.0;
  double dR_ik     = 0.0;
  double dR_jk     = 0.0;
  double dEta_ij   = 0.0;
  double dEta_ik   = 0.0;
  double dEta_jk   = 0.0;
  double dPhi_ij   = 0.0;
  double dPhi_ik   = 0.0;
  double dPhi_jk   = 0.0;
  double dRSum     = 0.0;
  double dEtaSum   = 0.0;
  double dPhiSum   = 0.0;
  std::vector<double> dEta_ijk;
  std::vector<double> dPhi_ijk;
  std::vector<double> dR_ijk;

  math::XYZTLorentzVector TriJetMaxPt_p4(0,0,0,0), SubldgTrijet_p4(0,0,0,0), j1(0,0,0,0), j2(0,0,0,0), j3(0,0,0,0);
  vector<math::XYZTLorentzVector> LdgTrijet_JETS, SubldgTrijet_JETS;

  if (selJets_p4.size() > 2)
    {

      // For-loop: All Selected Jets
      for (auto i = selJets_p4.begin(); i != selJets_p4.end()-2; ++i) {
	
	// Initialise values
	dR_ij     = 0.0;
	dR_ik     = 0.0;
	dR_jk     = 0.0;
	dEta_ij   = 0.0;
	dEta_ik   = 0.0;
	dEta_jk   = 0.0;
	dPhi_ij   = 0.0;
	dPhi_ik   = 0.0;
	dPhi_jk   = 0.0;

	// For-loop: All Selected Jets (nested)
	for (auto j = i+1; j != selJets_p4.end()-1; ++j) {

	// For-loop: All Selected Jets (doubly-nested)
	  for (auto k = j+1; k != selJets_p4.end(); ++k) {
	    nTriJetCands++;
	    
	    // Calculations
	    dR_ij = ROOT::Math::VectorUtil::DeltaR(*i, *j);
	    dR_ijk.push_back(dR_ij);
	    dR_ik = ROOT::Math::VectorUtil::DeltaR(*i, *k);
	    dR_ijk.push_back(dR_ik);
	    dR_jk = ROOT::Math::VectorUtil::DeltaR(*j, *k);
	    dR_ijk.push_back(dR_jk);

	    dEta_ij = std::abs( i->Eta() - j->Eta() );
	    dEta_ijk.push_back(dEta_ij);
	    dEta_ik = std::abs( i->Eta() - k->Eta() );
	    dEta_ijk.push_back(dEta_ik);
	    dEta_jk = std::abs( j->Eta() - k->Eta() );
	    dEta_ijk.push_back(dEta_jk);

	    dPhi_ij = std::abs( ROOT::Math::VectorUtil::DeltaPhi(*i, *j) );
	    dPhi_ijk.push_back(dEta_ij);
	    dPhi_ik = std::abs( ROOT::Math::VectorUtil::DeltaPhi(*i, *k) );
	    dPhi_ijk.push_back(dEta_ik);
	    dPhi_jk = std::abs( ROOT::Math::VectorUtil::DeltaPhi(*j, *k) );
	    dPhi_ijk.push_back(dEta_jk);	    

	    math::XYZTLorentzVector p4 = *i + *j + *k;
	    Bool_t BjetInTrijet = IsBjet(*i,selectedBJets) || IsBjet(*j,selectedBJets) || IsBjet(*k,selectedBJets);

	    if ( p4.Pt() > TriJetMaxPt_p4.Pt() && BjetInTrijet){
	      SubldgTrijet_p4 = TriJetMaxPt_p4;
	      SubldgTrijet_JETS.clear();
	      SubldgTrijet_JETS.push_back(j1); SubldgTrijet_JETS.push_back(j2); SubldgTrijet_JETS.push_back(j3);
	      TriJetMaxPt_p4 = p4;
	      j1 = *i;
	      j2 = *j;
	      j3 = *k;
	      LdgTrijet_JETS.clear();
	      LdgTrijet_JETS.push_back(*i); LdgTrijet_JETS.push_back(*j); LdgTrijet_JETS.push_back(*k);
	    }
	    
	    // Calculate
	    dRSum   += (dR_ij   + dR_ik   + dR_jk  )/3;
	    dEtaSum += (dEta_ij + dEta_ik + dEta_jk)/3;
	    dPhiSum += (dPhi_ij + dPhi_ik + dPhi_jk)/3;
	  }
	}
      }
    }
  	
  // Fill Histos
  h_MaxTriJetPt_Pt          ->Fill( TriJetMaxPt_p4.Pt()  );
  h_MaxTriJetPt_Eta         ->Fill( TriJetMaxPt_p4.Eta() );
  h_MaxTriJetPt_Rap         ->Fill( mcTools.GetRapidity(TriJetMaxPt_p4));
  h_MaxTriJetPt_Mass        ->Fill( TriJetMaxPt_p4.M() );
  h_MaxTriJetPt_dEtaMax     ->Fill( *max_element(dEta_ijk.begin(), dEta_ijk.end() ) );
  h_MaxTriJetPt_dPhiMax     ->Fill( *max_element(dPhi_ijk.begin(), dPhi_ijk.end() ) );
  h_MaxTriJetPt_dRMax       ->Fill( *max_element(dR_ijk.begin()  , dR_ijk.end()   ) );
  h_MaxTriJetPt_dEtaMin     ->Fill( *min_element(dEta_ijk.begin(), dEta_ijk.end() ) );
  h_MaxTriJetPt_dPhiMin     ->Fill( *min_element(dPhi_ijk.begin(), dPhi_ijk.end() ) );
  h_MaxTriJetPt_dRMin       ->Fill( *min_element(dR_ijk.begin()  , dR_ijk.end()   ) );
  h_MaxTriJetPt_dEtaAverage ->Fill( dEtaSum/nTriJetCands );
  h_MaxTriJetPt_dPhiAverage ->Fill( dPhiSum/nTriJetCands );  
  h_MaxTriJetPt_dRAverage   ->Fill( dRSum/nTriJetCands   );


  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // B-quarks (pT sorted)
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  if (0) std::cout << "=== BQuark cuts" << std::endl;
  std::sort( bQuarks_p4.begin(), bQuarks_p4.end(), PtComparator() );  
   
  std::vector<math::XYZTLorentzVector> selBQuarks_p4;
  unsigned int bQuark_index  = -1;
  unsigned int ptCut_index   = 0;
  unsigned int etaCut_index  = 0;

  // For-loop: All b-quarks
  for (auto i = bQuarks_p4.begin(); i != bQuarks_p4.end(); ++i) {

    // Jet index (for pT and eta cuts)
    bQuark_index++;

    // Apply selection cuts
    const float cfg_JetPtCut  = cfg_JetPtCuts.at(ptCut_index);
    const float cfg_JetEtaCut = cfg_JetEtaCuts.at(etaCut_index);

    // if (i->Pt() < 15.0) continue;
    if (i->Pt() < cfg_JetPtCut) continue;
    if (std::abs(i->Eta()) > cfg_JetEtaCut) continue;
    
    // Save this BQuark
    selBQuarks_p4.push_back(*i);

    // Increment cut index only. Cannot be bigger than the size of the cut list provided
    if (ptCut_index  < cfg_JetPtCuts.size()-1  ) ptCut_index++;
    if (etaCut_index  < cfg_JetEtaCuts.size()-1  ) etaCut_index++;
  }

  // Fill histos
  h_BQuarks_N->Fill(bQuarks_p4.size());

  // Selected BQuarks, Pairs
  int nBPairs = 0;
  double dR   = 0.0;
  double dEta = 0.0;
  double dPhi = 0.0;
  dRSum       = 0.0;
  dEtaSum     = 0.0;
  dPhiSum     = 0.0;
  math::XYZTLorentzVector maxPt_p4(0,0,0,0);
  double maxPt_dEta   = 0.0;
  double maxPt_dPhi   = 0.0;
  double maxPt_dR     = 0.0;
  double maxMass_dEta = 0.0;
  double maxMass_dPhi = 0.0;
  double maxMass_dR   = 0.0;

  math::XYZTLorentzVector maxMass_p4(0,0,0,0);

  if (selBQuarks_p4.size() > 1)
    {

      // For-loop: All Buarks
      for (auto i = selBQuarks_p4.begin(); i != selBQuarks_p4.end(); ++i) {
	
	// Initialise values
	dR      = 0.0;
	dEta    = 0.0;
	dPhi    = 0.0;

	// For-loop: All BQuarks (nested)
	for (auto j = i+1; j != selBQuarks_p4.end(); ++j) {
	  
	  dR   = ROOT::Math::VectorUtil::DeltaR(*i, *j);
	  dEta = std::abs(i->Eta() - j->Eta() );
	  dPhi = std::abs(ROOT::Math::VectorUtil::DeltaPhi(*i, *j));
	  nBPairs++;

	  math::XYZTLorentzVector pair_p4 = *i + *j;
	  if ( pair_p4.Pt() > maxPt_p4.Pt() )
	    {
	      maxPt_dEta = dEta;
	      maxPt_dPhi = dPhi;
	      maxPt_dR   = dR;
	      maxPt_p4   = pair_p4;
	    }
	  if ( pair_p4.M() > maxMass_p4.M() ) 
	    {
	      maxMass_p4   = pair_p4;
	      maxMass_dEta = dEta;
	      maxMass_dPhi = dPhi;
	      maxMass_dR   = dR;
	    }
	  
	  // Fill Histos
	  h_BQuarkPair_dR->Fill(dR);
	  h_BQuarkPair_dEta->Fill(dEta);
	  h_BQuarkPair_dPhi->Fill(dPhi);
	  
	  // Calculate
	  dRSum   += dR;
	  dEtaSum += dEta;
	  dPhiSum += dPhi;
	}
      }

      // Fill Histos
      h_BQuarkPair_dRAverage->Fill  ( dRSum/nBPairs   );
      h_BQuarkPair_dEtaAverage->Fill( dEtaSum/nBPairs );
      h_BQuarkPair_dPhiAverage->Fill( dPhiSum/nBPairs );
      //
      h_BQuarkPair_MaxPt_Pt  ->Fill( maxPt_p4.Pt()  );
      h_BQuarkPair_MaxPt_Eta ->Fill( maxPt_p4.Eta() );
      h_BQuarkPair_MaxPt_Phi ->Fill( maxPt_p4.Phi() );
      h_BQuarkPair_MaxPt_M   ->Fill( maxPt_p4.M()   );
      h_BQuarkPair_MaxPt_dEta->Fill( maxPt_dEta );
      h_BQuarkPair_MaxPt_dPhi->Fill( maxPt_dPhi );
      h_BQuarkPair_MaxPt_dR  ->Fill( maxPt_dR   );

      if (selJets_p4.size() > 0)
	{
	  h_BQuarkPair_MaxPt_jet1_dEta ->Fill( std::abs(maxPt_p4.eta() - selJets_p4.at(0).eta()) );
	  h_BQuarkPair_MaxPt_jet1_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(maxPt_p4, selJets_p4.at(0) ) ) );
	  h_BQuarkPair_MaxPt_jet1_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(maxPt_p4, selJets_p4.at(0) ) );
	}
      
      if (selJets_p4.size() > 1)
	{
	  h_BQuarkPair_MaxPt_jet2_dEta ->Fill( std::abs(maxPt_p4.eta() - selJets_p4.at(1).eta()) );
	  h_BQuarkPair_MaxPt_jet2_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(maxPt_p4, selJets_p4.at(1) ) ) );
	  h_BQuarkPair_MaxPt_jet2_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(maxPt_p4, selJets_p4.at(1) ) );
	}
      //
      h_BQuarkPair_MaxMass_Pt  ->Fill( maxMass_p4.Pt()  );
      h_BQuarkPair_MaxMass_Eta ->Fill( maxMass_p4.Eta() );
      h_BQuarkPair_MaxMass_Phi ->Fill( maxMass_p4.Phi() );
      h_BQuarkPair_MaxMass_M   ->Fill( maxMass_p4.M()   );
      h_BQuarkPair_MaxMass_dEta->Fill( maxMass_dEta     );
      h_BQuarkPair_MaxMass_dPhi->Fill( maxMass_dPhi     );
      h_BQuarkPair_MaxMass_dR  ->Fill( maxMass_dR       );
      if (selJets_p4.size() > 0)
	{
	  h_BQuarkPair_MaxMass_jet1_dEta ->Fill( std::abs(maxMass_p4.eta() - selJets_p4.at(0).eta()) );
	  h_BQuarkPair_MaxMass_jet1_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(maxMass_p4, selJets_p4.at(0) ) ) );
	  h_BQuarkPair_MaxMass_jet1_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(maxMass_p4, selJets_p4.at(0) ) );
	}
      
      if (selJets_p4.size() > 1)
	{
	  h_BQuarkPair_MaxMass_jet2_dEta ->Fill( std::abs(maxMass_p4.eta() - selJets_p4.at(1).eta()) );
	  h_BQuarkPair_MaxMass_jet2_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(maxMass_p4, selJets_p4.at(1) ) ) );
	  h_BQuarkPair_MaxMass_jet2_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(maxMass_p4, selJets_p4.at(1) ) );
	}
      
    } // if (selBQuarks_p4.size() > 1)


  // Dijet with all selected jets (no b-jets)
  if (selJets_NoBJets_p4.size()>1)
    {
      double _deltaRMin = 999999.9;
      int _deltaRMin_i  = -1;
      int _deltaRMin_j  = -1;  
      int _i=-1;
      int _j=-1;

      // For-loop: Selected jets, no b-jets
      for (auto& i: selJets_NoBJets_p4)
	{
	  _i++;
	  
	  _j=-1;
	  // For-loop: Selected jets, no b-jets (nested)
	  for (auto& j: selJets_NoBJets_p4)
	    {
	      _j++;
	      if (_i==_j) continue;
	      double deltaR = ROOT::Math::VectorUtil::DeltaR(i, j);
	      if (deltaR < _deltaRMin)
		{
		  _deltaRMin = deltaR;
		  _deltaRMin_i = _i;
		  _deltaRMin_j = _j;
		}
	    }
	}
    
      if (_deltaRMin_i > -1  && _deltaRMin_j > -1)
	{
	  // GenJets: Untagged jet pair with min dR
	  math::XYZTLorentzVector dRMinDiJet_NoBJets_p4 = selJets_NoBJets_p4.at(_deltaRMin_i) + selJets_NoBJets_p4.at(_deltaRMin_j);
	  h_dRMinDiJet_NoBJets_Pt   ->Fill( dRMinDiJet_NoBJets_p4.Pt() );
	  h_dRMinDiJet_NoBJets_Eta  ->Fill( dRMinDiJet_NoBJets_p4.Eta() );
	  h_dRMinDiJet_NoBJets_Rap  ->Fill( mcTools.GetRapidity( dRMinDiJet_NoBJets_p4 ) );
	  h_dRMinDiJet_NoBJets_Mass ->Fill( dRMinDiJet_NoBJets_p4.M() );
	  h_dRMinDiJet_NoBJets_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(selJets_NoBJets_p4.at(_deltaRMin_i), selJets_NoBJets_p4.at(_deltaRMin_j)) );
	  h_dRMinDiJet_NoBJets_dEta ->Fill( selJets_NoBJets_p4.at(_deltaRMin_i).Eta() - selJets_NoBJets_p4.at(_deltaRMin_j).Eta() );
	  h_dRMinDiJet_NoBJets_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(selJets_NoBJets_p4.at(_deltaRMin_i), selJets_NoBJets_p4.at(_deltaRMin_j) ) ) );  
	}
    }
  
  
  if (bQuarks_p4.size() >= 2)
    {
      double dEta_1_2 = std::abs(bQuarks_p4.at(0).eta() - bQuarks_p4.at(1).eta());
      double dPhi_1_2 = std::abs(bQuarks_p4.at(0).phi() - bQuarks_p4.at(1).phi());
      // Fill Histos
      h_BQuark1_BQuark2_dEta_Vs_dPhi->Fill( dEta_1_2 , dPhi_1_2 );
    }
  
  if (bQuarks_p4.size() >= 3) 
    {
      double dEta_1_3 = std::abs(bQuarks_p4.at(0).eta() - bQuarks_p4.at(2).eta());
      double dPhi_1_3 = std::abs(bQuarks_p4.at(0).phi() - bQuarks_p4.at(2).phi());
      double dEta_2_3 = std::abs(bQuarks_p4.at(1).eta() - bQuarks_p4.at(2).eta());
      double dPhi_2_3 = std::abs(bQuarks_p4.at(1).phi() - bQuarks_p4.at(2).phi());
      // Fill Histos
      h_BQuark1_BQuark3_dEta_Vs_dPhi->Fill( dEta_1_3 , dPhi_1_3 );
      h_BQuark2_BQuark3_dEta_Vs_dPhi->Fill( dEta_2_3 , dPhi_2_3 );
    }
  
  if (bQuarks_p4.size() >= 4) 
    {
      double dEta_1_4 = std::abs(bQuarks_p4.at(0).eta() - bQuarks_p4.at(3).eta());
      double dPhi_1_4 = std::abs(bQuarks_p4.at(0).phi() - bQuarks_p4.at(3).phi());
      double dEta_2_4 = std::abs(bQuarks_p4.at(1).eta() - bQuarks_p4.at(3).eta());
      double dPhi_2_4 = std::abs(bQuarks_p4.at(1).phi() - bQuarks_p4.at(3).phi());
      double dEta_3_4 = std::abs(bQuarks_p4.at(2).eta() - bQuarks_p4.at(3).eta());
      double dPhi_3_4 = std::abs(bQuarks_p4.at(2).phi() - bQuarks_p4.at(3).phi());
      // Fill Histos
      h_BQuark1_BQuark4_dEta_Vs_dPhi->Fill( dEta_1_4 , dPhi_1_4 );
      h_BQuark2_BQuark4_dEta_Vs_dPhi->Fill( dEta_2_4 , dPhi_2_4 );
      h_BQuark3_BQuark4_dEta_Vs_dPhi->Fill( dEta_3_4 , dPhi_3_4 );
    }


  double deltaRMin = 999999.9;
  int deltaRMin_i  = -1;
  int deltaRMin_j  = -1;  
  // For-loop: All b-quarks
  for (size_t i = 0; i < bQuarks_p4.size(); i++)
    {

      if (i < 4)
	{
	  vh_BQuarks_Pt.at(i) ->Fill( bQuarks_p4.at(i).pt()  );
	  vh_BQuarks_Eta.at(i)->Fill( bQuarks_p4.at(i).eta() );
	}
      
      // For-Loop (Nested): All b-quarks
      for (size_t j = i+1; j < bQuarks_p4.size(); j++)
	{	  

	  double deltaR = ROOT::Math::VectorUtil::DeltaR(bQuarks_p4.at(i), bQuarks_p4.at(j));
	  
	  if (deltaR < deltaRMin)
	    {
	      deltaRMin = deltaR;
	      deltaRMin_i = i;
	      deltaRMin_j = j;
	    }	  
	}      
    } // For-loop: All b-quarks

  //////////////////////////////////////////////////////////////////////////////////////////////////////
  // BquarkPair - Ldg Jets Correlations
  //////////////////////////////////////////////////////////////////////////////////////////////////////
  if (0) std::cout << "=== BQuarkPair" << std::endl;
  if (deltaRMin_i>= 0  && deltaRMin_j >= 0)
    {
      math::XYZTLorentzVector bQuarkPair_dRMin_p4 = bQuarks_p4.at(deltaRMin_i) + bQuarks_p4.at(deltaRMin_j);
      double bQuarkPair_dEta = std::abs(bQuarks_p4.at(deltaRMin_i).eta() - bQuarks_p4.at(deltaRMin_j).eta());
      double bQuarkPair_dPhi = std::abs(ROOT::Math::VectorUtil::DeltaPhi(bQuarks_p4.at(deltaRMin_i), bQuarks_p4.at(deltaRMin_j)));

      // Fill Histos
      h_BQuarkPair_dRMin_Pt   ->Fill( bQuarkPair_dRMin_p4.pt() );
      h_BQuarkPair_dRMin_Eta  ->Fill( bQuarkPair_dRMin_p4.eta() );
      h_BQuarkPair_dRMin_Rap  ->Fill( mcTools.GetRapidity( bQuarkPair_dRMin_p4) );
      h_BQuarkPair_dRMin_Phi  ->Fill( bQuarkPair_dRMin_p4.phi() );
      h_BQuarkPair_dRMin_dEta ->Fill( bQuarkPair_dEta );
      h_BQuarkPair_dRMin_dPhi ->Fill( bQuarkPair_dPhi );
      h_BQuarkPair_dRMin_dR   ->Fill( deltaRMin );
      h_BQuarkPair_dRMin_Mass ->Fill( bQuarkPair_dRMin_p4.mass() );
      h_BQuarkPair_dRMin_Eta1_Vs_Eta2->Fill( bQuarks_p4.at(deltaRMin_i).eta(), bQuarks_p4.at(deltaRMin_j).eta());
      h_BQuarkPair_dRMin_Phi1_Vs_Phi2->Fill( bQuarks_p4.at(deltaRMin_i).phi(), bQuarks_p4.at(deltaRMin_j).phi());
      h_BQuarkPair_dRMin_Pt1_Vs_Pt2  ->Fill(bQuarks_p4.at(deltaRMin_i).pt(), bQuarks_p4.at(deltaRMin_j).pt());
      h_BQuarkPair_dRMin_dEta_Vs_dPhi->Fill( bQuarkPair_dEta, bQuarkPair_dPhi);
 
      // Fill histos
      if (selJets_p4.size() > 0)
	{
	  h_BQuarkPair_dRMin_jet1_dEta ->Fill( std::abs(bQuarkPair_dRMin_p4.eta() - selJets_p4.at(0).eta()) );
	  h_BQuarkPair_dRMin_jet1_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(bQuarkPair_dRMin_p4, selJets_p4.at(0) ) ) );
	  h_BQuarkPair_dRMin_jet1_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(bQuarkPair_dRMin_p4, selJets_p4.at(0) ) );
	}
      
      if (selJets_p4.size() > 1)
	{
	  h_BQuarkPair_dRMin_jet2_dEta ->Fill( std::abs(bQuarkPair_dRMin_p4.eta() - selJets_p4.at(1).eta()) );
	  h_BQuarkPair_dRMin_jet2_dPhi ->Fill( std::abs(ROOT::Math::VectorUtil::DeltaPhi(bQuarkPair_dRMin_p4, selJets_p4.at(1) ) ) );
	  h_BQuarkPair_dRMin_jet2_dR   ->Fill( ROOT::Math::VectorUtil::DeltaR(bQuarkPair_dRMin_p4, selJets_p4.at(1) ) );
	}
    }




  // double jet_Pt, jet_Eta;
  math::XYZTLorentzVector ldgJet_p4(0,0,0,0), temp_p4(0,0,0,0);
  std::vector<math::XYZTLorentzVector> Jets_p4, BJets_p4;
  std::vector<TLorentzVector> VecJets;

  // For-Loop: Selected Jets
  for (auto& jet: selectedJets)
    {
      math::XYZTLorentzVector jetP4;
      jetP4 = jet.p4();
      Jets_p4.push_back(jetP4);

    } // For-loop: Selected Jets      

  // For-Loop: Selected BJets
  for (auto& jet: selectedBJets)
    {
      math::XYZTLorentzVector jetP4;
      jetP4 = jet.p4();
      BJets_p4.push_back(jetP4);

    } // For-loop: Selected Jets      
                                
  Jets_p4 = SortInPt(Jets_p4);         
  BJets_p4 = SortInPt(BJets_p4);         


  // int ilast = Jets_p4.size()-1;

  
  float dPhi_j3j4   = std::abs(ROOT::Math::VectorUtil::DeltaPhi(Jets_p4.at(2),Jets_p4.at(3)));
  float dPhi_j5j6   = std::abs(ROOT::Math::VectorUtil::DeltaPhi(Jets_p4.at(4),Jets_p4.at(5)));

  // float dPhi_j3j4 = std::abs(ROOT::Math::VectorUtil::DeltaPhi(Jets_p4.at(2),Jets_p4.at(3)));
  // float dEta_j3j4 = std::abs(Jets_p4.at(2).Eta() - Jets_p4.at(3).Eta() );
  // float dR_j3j4   = ROOT::Math::VectorUtil::DeltaR(Jets_p4.at(2),Jets_p4.at(3));

  // float dPhi_j5j6 = std::abs(ROOT::Math::VectorUtil::DeltaPhi(Jets_p4.at(4),Jets_p4.at(5)));
  // float dEta_j5j6 = std::abs(Jets_p4.at(4).Eta() - Jets_p4.at(5).Eta() );
  // float dR_j5j6   = ROOT::Math::VectorUtil::DeltaR(Jets_p4.at(4),Jets_p4.at(5));

  h_DPhiJ34vsDPhiJ56     -> Fill(dPhi_j3j4,dPhi_j5j6);

  double cosTheta_Bjet1TopCM_TrijetLab, cosTheta_Bjet1TopCM_Zaxis, cosTheta_Bjet2TopCM_TrijetLab, cosTheta_Bjet2TopCM_Zaxis, cosTheta_Bjet3TopCM_TrijetLab, cosTheta_Bjet3TopCM_Zaxis;
  double cosTheta_LdgTrijetLdgJetTopCM_TrijetLab, cosTheta_LdgTrijetSubldgJetTopCM_TrijetLab, cosTheta_LdgTrijetBjetTopCM_TrijetLab;
  double cosTheta_SubldgTrijetLdgJetTopCM_TrijetLab, cosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab, cosTheta_SubldgTrijetBjetTopCM_TrijetLab;

  //
  //  math::XYZTLorentzVector TriJetMaxPt_p4(0,0,0,0), SubldgTrijet_p4(0,0,0,0);
  //  vector<math::XYZTLorentzVector> LdgTrijet_JETS, SubldgTrijet_JETS;
  TLorentzVector TrijetLorentz;
  TrijetLorentz.SetPtEtaPhiE(TriJetMaxPt_p4.pt(), TriJetMaxPt_p4.eta(), TriJetMaxPt_p4.phi(), TriJetMaxPt_p4.e());

  int i=0; 
  for (auto& bjet: selectedBJets){
    TLorentzVector bjetP4;
    bjetP4.SetPtEtaPhiE(bjet.pt(), bjet.eta(), bjet.phi(), bjet.e());
    bjetP4.Boost(-TrijetLorentz.BoostVector());
    
    float b_theta = 2*atan(exp(-bjetP4.Eta()));                           
    float t_theta = 2*atan(exp(-TrijetLorentz.Eta() ));                                  
    if (i==0) {                                                                                
      cosTheta_Bjet1TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));        
      cosTheta_Bjet1TopCM_Zaxis     = std::cos(b_theta);
    }                                                                               
    if (i==1){
      cosTheta_Bjet2TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));
      cosTheta_Bjet2TopCM_Zaxis     = std::cos(b_theta);
    }
    if (i==2){
      cosTheta_Bjet3TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));
      cosTheta_Bjet3TopCM_Zaxis     = std::cos(b_theta);
    }
    i=i+1;
  }

  TLorentzVector ldgtrijetJet1, ldgtrijetJet2, ldgtrijetB;
  TLorentzVector subldgtrijetJet1, subldgtrijetJet2, subldgtrijetB;
  //  trijet_check.Boost(-TrijetLorentz.BoostVector());

  math::XYZTLorentzVector jet1, jet2, bjet, sjet1, sjet2, sbjet;
  vector <math::XYZTLorentzVector> trijet_jets;
  trijet_jets = TrijetJets(LdgTrijet_JETS, selectedBJets);
  //  TrijetJets(SubldgTrijet_JETS, selectedBJets, sjet1, sjet2, sbjet);
  jet1 = trijet_jets.at(0);
  jet2 = trijet_jets.at(1);
  bjet = trijet_jets.at(2);

  ldgtrijetJet1.SetPtEtaPhiE(jet1.pt(), jet1.eta(), jet1.phi(), jet1.e());  
  ldgtrijetJet2.SetPtEtaPhiE(jet2.pt(), jet2.eta(), jet2.phi(), jet2.e());  
  ldgtrijetB.SetPtEtaPhiE(bjet.pt(), bjet.eta(), bjet.phi(), bjet.e());

  subldgtrijetJet1.SetPtEtaPhiE(sjet1.pt(), sjet1.eta(), sjet1.phi(), sjet1.e());  
  subldgtrijetJet2.SetPtEtaPhiE(sjet2.pt(), sjet2.eta(), sjet2.phi(), sjet2.e());  
  subldgtrijetB.SetPtEtaPhiE(sbjet.pt(), sbjet.eta(), sbjet.phi(), sbjet.e());

  //  std::cout<<ldgtrijetJet1.Pt()<<" "<<ldgtrijetJet2.Pt()<<" "<<ldgtrijetB.Pt()<<" "<<subldgtrijetJet1.Pt()<<" "<<subldgtrijetJet2.Pt()<<" "<<subldgtrijetB.Pt()<<std::endl;
  //  std::cout<<jet1.pt()<<" "<<jet2.pt()<<" "<<bjet.pt()<<" "<<" "<<sjet1.pt()<<" "<<sjet2.pt()<<" "<<sbjet.pt()<<std::endl;

  ldgtrijetJet1.Boost(-TrijetLorentz.BoostVector());
  ldgtrijetJet2.Boost(-TrijetLorentz.BoostVector());
  ldgtrijetB.Boost(-TrijetLorentz.BoostVector());

  subldgtrijetJet1.Boost(-TrijetLorentz.BoostVector());
  subldgtrijetJet2.Boost(-TrijetLorentz.BoostVector());
  subldgtrijetB.Boost(-TrijetLorentz.BoostVector());

  /*  //change for Kinematics

  TLorentzVector TrijetLorentz;
  TrijetLorentz.SetPtEtaPhiE(TopData.getLdgTrijet().Pt(),TopData.getLdgTrijet().Eta(),TopData.getLdgTrijet().Phi(),TopData.getLdgTrijet().E());
  TLorentzVector trijet_check;
  trijet_check = TrijetLorentz;

  trijet_check.Boost(-TrijetLorentz.BoostVector()); //Check that trijet is at rest at its center of mass                                                                                 
  //  std::cout<<"px = "<<trijet_check.Px()<<" py = "<<trijet_check.Py()<<" pz = "<<trijet_check.Pz()<<" E = "<<trijet_check.E()<<" M = "<<trijet_check.M()<<std::endl;                  

  for (size_t i=0; i < bjetData.getSelectedBJets().size(); i++ ){
    TLorentzVector bjetP4;
    bjetP4.SetPtEtaPhiE(jetData.getAllJets().at(i).pt(),jetData.getAllJets().at(i).eta(),jetData.getAllJets().at(i).phi(),jetData.getAllJets().at(i).e());
    bjetP4.Boost(-TrijetLorentz.BoostVector());

    float b_theta = 2*atan(exp(-bjetP4.Eta()));
    float t_theta = 2*atan(exp(-TrijetLorentz.Eta() ));

    if (i==0) {
      cosTheta_Bjet1TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));
      cosTheta_Bjet1TopCM_Zaxis     = std::cos(b_theta);
    }
    if (i==1){
      cosTheta_Bjet2TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));
      cosTheta_Bjet2TopCM_Zaxis     = std::cos(b_theta);
    }
    if (i==2){
      cosTheta_Bjet3TopCM_TrijetLab = std::cos(std::abs(b_theta-t_theta));
      cosTheta_Bjet3TopCM_Zaxis     = std::cos(b_theta);
    }
  }

  TLorentzVector ldgtrijetJet1, ldgtrijetJet2, ldgtrijetB;
  TLorentzVector subldgtrijetJet1, subldgtrijetJet2, subldgtrijetB;
  trijet_check.Boost(-TrijetLorentz.BoostVector());

  ldgtrijetJet1.Boost(-TrijetLorentz.BoostVector());
  ldgtrijetJet2.Boost(-TrijetLorentz.BoostVector());
  ldgtrijetB.Boost(-TrijetLorentz.BoostVector());

  subldgtrijetJet1.Boost(-TrijetLorentz.BoostVector());
  subldgtrijetJet2.Boost(-TrijetLorentz.BoostVector());
  subldgtrijetB.Boost(-TrijetLorentz.BoostVector());
  */
  float ldgtrijetJet1_theta    = 2*atan(exp(-ldgtrijetJet1.Eta()));
  float ldgtrijetJet2_theta    = 2*atan(exp(-ldgtrijetJet2.Eta()));
  float ldgtrijetB_theta       = 2*atan(exp(-ldgtrijetB.Eta()));
  float subldgtrijetJet1_theta = 2*atan(exp(-subldgtrijetJet1.Eta()));
  float subldgtrijetJet2_theta = 2*atan(exp(-subldgtrijetJet2.Eta()));
  float subldgtrijetB_theta    = 2*atan(exp(-subldgtrijetB.Eta()));

  float t_theta                = 2*atan(exp(-TrijetLorentz.Eta() ));

  cosTheta_LdgTrijetLdgJetTopCM_TrijetLab       =  std::cos(std::abs(ldgtrijetJet1_theta-t_theta));
  cosTheta_LdgTrijetSubldgJetTopCM_TrijetLab    =  std::cos(std::abs(ldgtrijetJet2_theta-t_theta));
  cosTheta_LdgTrijetBjetTopCM_TrijetLab         =  std::cos(std::abs(ldgtrijetB_theta-t_theta));
  cosTheta_SubldgTrijetLdgJetTopCM_TrijetLab    =  std::cos(std::abs(subldgtrijetJet1_theta-t_theta));
  cosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab =  std::cos(std::abs(subldgtrijetJet2_theta-t_theta));
  cosTheta_SubldgTrijetBjetTopCM_TrijetLab      =  std::cos(std::abs(subldgtrijetB_theta-t_theta));

  //change for Kinematics

  h_CosTheta_Bjet1TopCM_TrijetLab -> Fill(cosTheta_Bjet1TopCM_TrijetLab);
  h_CosTheta_Bjet1TopCM_Zaxis     -> Fill(cosTheta_Bjet1TopCM_Zaxis);
  h_CosTheta_Bjet2TopCM_TrijetLab -> Fill(cosTheta_Bjet2TopCM_TrijetLab);
  h_CosTheta_Bjet2TopCM_Zaxis     -> Fill(cosTheta_Bjet2TopCM_Zaxis);
  h_CosTheta_Bjet3TopCM_TrijetLab -> Fill(cosTheta_Bjet3TopCM_TrijetLab);
  h_CosTheta_Bjet3TopCM_Zaxis     -> Fill(cosTheta_Bjet3TopCM_Zaxis);


  h_CosTheta_LdgTrijetLdgJetTopCM_TrijetLab       -> Fill(cosTheta_LdgTrijetLdgJetTopCM_TrijetLab);
  h_CosTheta_LdgTrijetSubldgJetTopCM_TrijetLab    -> Fill(cosTheta_LdgTrijetSubldgJetTopCM_TrijetLab);
  h_CosTheta_LdgTrijetBjetTopCM_TrijetLab         -> Fill(cosTheta_LdgTrijetBjetTopCM_TrijetLab);

  h_CosTheta_SubldgTrijetLdgJetTopCM_TrijetLab    -> Fill(cosTheta_SubldgTrijetLdgJetTopCM_TrijetLab);
  h_CosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab -> Fill(cosTheta_SubldgTrijetSubldgJetTopCM_TrijetLab);
  h_CosTheta_SubldgTrijetBjetTopCM_TrijetLab      -> Fill(cosTheta_SubldgTrijetBjetTopCM_TrijetLab);

  return;
}


vector<float> Kinematics::GetMomentumTensorEigenValues(std::vector<math::XYZTLorentzVector> jets,
						       float &C,
						       float &D,
						       float &H2){

  // Tensor required for calculation of: Sphericity, Aplanarity, Planarity
  // Need all particles in event to calculate kinematic variables. Use all tracks (ch. particles) instead.
  // Links:
  // https://cmssdt.cern.ch/SDT/doxygen/CMSSW_8_0_24/doc/html/d5/d29/EventShapeVariables_8h_source.html
  // https://cmssdt.cern.ch/SDT/doxygen/CMSSW_8_0_24/doc/html/dd/d99/classEventShapeVariables.html

  // Get the Linear Momentum Tensor
  TMatrixDSym MomentumTensor = ComputeMomentumTensor(jets, 1.0);

  // Find the Momentum-Tensor EigenValues (Q1, Q2, Q3)
  TMatrixDSymEigen eigen(MomentumTensor);
  TVectorD eigenvals = eigen.GetEigenValues();

  // Store & Sort the eigenvalues
  vector<float> eigenvalues(3);
  eigenvalues.at(0) = eigenvals(0); // Q1
  eigenvalues.at(1) = eigenvals(1); // Q2
  eigenvalues.at(2) = eigenvals(2); // Q3
  sort( eigenvalues.begin(), eigenvalues.end(), std::greater<float>() );

  // Calculate the eigenvalues sum (Requirement: Q1 + Q2 + Q3 = 1)
  float eigenSum = std::accumulate(eigenvalues.begin(), eigenvalues.end(), 0);
  if ( (eigenSum - 1.0) > 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Q1+Q2+Q3=1. Found that Q1+Q2+Q3 = " << eigenSum << ", instead.";
    }

  // Save the final eigenvalues
  float Q1 = eigenvalues.at(0);
  float Q2 = eigenvalues.at(1);
  float Q3 = eigenvalues.at(2);

  // Sanity check on eigenvalues: Q1 >= Q2 >= Q3 (Q1 >= 0)
  bool bQ1Zero = (Q1 >= 0.0);
  bool bQ1Q2   = (Q1 >= Q2);
  bool bQ2Q3   = (Q2 >= Q3);
  bool bInequality = bQ1Zero * bQ1Q2 * bQ2Q3;
  
  if ( !(bInequality) )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that eigenvalues are ordered as Q1 >= Q2 >= Q3 (Q1 >= 0). Q1 = " << Q1 << ", Q2 = " << Q2 << ", Q3 = " << Q3;
    }

  // Calculate the linear combinations C and D
  C  = 3*(Q1*Q2 + Q1*Q3 + Q2*Q3); // Used to measure the 3-jet structure. Vanishes for perfece 2-jet event. Related to the 2nd Fox-Wolfram Moment (H2)
  D  = 27*Q1*Q2*Q3; // Used to measure the 4-jet structure. Vanishes for a planar event
  H2 = 1-C; // The C-measure is related to the second Fox-Wolfram moment (see below), $C = 1 - H_2$.

  // C
  if ( abs(C-1.0) > 1 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that the quantity C satisfies the inequality: 0.0 <= C <= 1.0. Found that C = " << C;
    }

  // D
  if ( abs(C-1.0) > 1 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that the quantity C satisfies the inequality: 0.0 <= D <= 1.0. Found that D = " << D;
    }

  // 2nd Fox-Wolfram Moment
  if ( abs(H2-1.0) > 1 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that the 2nd Fox-Wolfram Moment (H2) satisfies the inequality: 0.0 <= H2 <= 1.0. Found that H2 = " << H2;
    }
  
  if (0)
    {

      Table vars("Variable | Value | Allowed Range | Definition", "Text"); //LaTeX or Text
      vars.AddRowColumn(0, "C");
      vars.AddRowColumn(0, auxTools.ToString(C) );
      vars.AddRowColumn(0, "0.0 <= C <= 1.0");
      vars.AddRowColumn(0, "C = 3 x (Q1Q2 + Q1Q3 + Q2Q3");
      //
      vars.AddRowColumn(1, "D");
      vars.AddRowColumn(1, auxTools.ToString(D) );
      vars.AddRowColumn(1, "0.0 <= D <= 1.0");
      vars.AddRowColumn(1, "D = 27 x Q1 x Q2 x Q3");
      //
      vars.AddRowColumn(2, "2nd F-W Moment");
      vars.AddRowColumn(2, auxTools.ToString(H2) );
      vars.AddRowColumn(2, "0.0 <= H2 <= 1.0 ");
      vars.AddRowColumn(2, "H2 = 1-C");
      vars.Print();
    }

  return eigenvalues;
}


vector<float> Kinematics::GetMomentumTensorEigenValues2D(std::vector<math::XYZTLorentzVector> jets,
							 float &Circularity){

  // For Circularity, the momentum tensor is the 2��2 submatrix of Mjk, normalized by the sum of pT instead by the sum of
  // This matrix has two eigenvalues Qi with 0 < Q1 < Q2. The following definition for the circularity C has been used:
  //  C = 2 �� min (Q1,Q2) / (Q1 +Q2)
  // The circularity C is especially interesting for hadron colliders because it only uses the momentum values in x and y direction transverse
  // to the beam line. So C is a two dimensional event shape variable and is therefore independent from a boost along z. 
  // In addition, the normalization by the sum of the particle momenta makes C highly independent from energy calibration effects  (systematic uncertainty).
  // C takes small values for linear and high values for circular events. 
  
  // Find the Momentum-Tensor EigenValues (E1, E2)
  TMatrixDSym MomentumTensor = ComputeMomentumTensor2D(jets);
  TMatrixDSymEigen eigen(MomentumTensor);
  TVectorD eigenvals = eigen.GetEigenValues();

  // Store & Sort the eigenvalues
  vector<float> eigenvalues(2);
  eigenvalues.at(0) = eigenvals[0]; // Q1
  eigenvalues.at(1) = eigenvals[1]; // Q2
  sort( eigenvalues.begin(), eigenvalues.end(), std::greater<float>() );

  // Save the final eigenvalues
  float Q1 = eigenvalues.at(0);
  float Q2 = eigenvalues.at(1);

  // Sanity check on eigenvalues: (Q1 > Q2)
  if (Q1 == 0) return eigenvalues;

  bool bInequality = (Q1 > 0 && Q1 > Q2);
  if ( !(bInequality) )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that eigenvalues are ordered as Q1 >= Q2. Found Q1 = " << Q1 << ", Q2 " << Q2;
    }
  
  // Calculate circularity
  Circularity = 2*std::min(Q1, Q2)/(Q1+Q2); // is this definition correct?

  if (0)
    {      
      Table vars("Variable | Value | Allowed Range | Definition", "Text"); //LaTeX or Text
      vars.AddRowColumn(0, "Circularity");
      vars.AddRowColumn(0, auxTools.ToString(Circularity) );
      vars.AddRowColumn(0, "0.0 <= C <= 1.0 ");
      vars.AddRowColumn(0, "C = 2 �� min (Q1,Q2)/(Q1+Q2)");
      vars.Print();
    }
  
  return eigenvalues;
}



vector<float> Kinematics::GetSphericityTensorEigenValues(std::vector<math::XYZTLorentzVector> jets,
							 float &y23, float &Sphericity, float &SphericityT, float &Aplanarity, 
							 float &Planarity, float &Y){

  // C, D parameters
  // Need all particles in event to calculate kinematic variables. Use all tracks (ch. particles) instead.
  // Links:
  // http://home.fnal.gov/~mrenna/lutp0613man2/node234.html

  // Sanity check: at least 3 jets (for 3rd-jet resolution)
  if( (jets.size()) < 3 )
    {
      vector<float> zeros(3, 0);
      return zeros;
    }

  // Sort the jets by pT (leading jet first)
  std::sort( jets.begin(), jets.end(), PtComparator() );  

  // Get the Sphericity Tensor
  TMatrixDSym SphericityTensor = ComputeMomentumTensor(jets, 2.0);

  // Find the Momentum-Tensor EigenValues (Q1, Q2, Q3)
  TMatrixDSymEigen eigen(SphericityTensor);
  TVectorD eigenvals = eigen.GetEigenValues();

  // Store & Sort the eigenvalues
  vector<float> eigenvalues(3);
  eigenvalues.at(0) = eigenvals(0); // Q1
  eigenvalues.at(1) = eigenvals(1); // Q2
  eigenvalues.at(2) = eigenvals(2); // Q3
  sort( eigenvalues.begin(), eigenvalues.end(), std::greater<float>() );

  // Calculate the eigenvalues sum (Requirement: Q1 + Q2 + Q3 = 1)
  float eigenSum = std::accumulate(eigenvalues.begin(), eigenvalues.end(), 0);
  if ( (eigenSum - 1.0) > 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Q1+Q2+Q3=1. Found that Q1+Q2+Q3 = " << eigenSum << ", instead.";
    }

  // Save the final eigenvalues
  float Q1 = eigenvalues.at(0);
  float Q2 = eigenvalues.at(1);
  float Q3 = eigenvalues.at(2);

  // Sanity check on eigenvalues: Q1 >= Q2 >= Q3 (Q1 >= 0)
  bool bQ1Zero = (Q1 >= 0.0);
  bool bQ1Q2   = (Q1 >= Q2);
  bool bQ2Q3   = (Q2 >= Q3);
  bool bInequality = bQ1Zero * bQ1Q2 * bQ2Q3;
  
  if ( !(bInequality) )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that eigenvalues are ordered as Q1 >= Q2 >= Q3 (Q1 >= 0)";
    }


  // Calculate the event-shape variables
  float pT3Squared  = pow(jets.at(2).Pt(), 2);
  float HT2Squared  = pow(jets.at(0).Pt() + jets.at(1).Pt(), 2);
  y23         = pT3Squared/HT2Squared;
  Sphericity  = -1.0;
  SphericityT = -1.0;
  Aplanarity  = -1.0;
  Planarity   = -1.0;
  Y = (sqrt(3.0)/2.0)*(Q2-Q3); // (Since Q1>Q2, then my Q1 corresponds to Q3 when Q's are reversed-ordered). Calculate the Y (for Y-S plane)

  // Check the value of the third-jet resolution
  if (abs(y23-0.25) > 0.25 + 1e-4)
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that y23 satisfies the inequality: 0.0 <= y23 <= 0.25. Found that y23 = " << y23;
    }
  
  // Calculate the Sphericity (0 <= S <= 1). S~0 for a 2-jet event, and S~1 for an isotropic one
  Sphericity = 1.5*(Q2 + Q3); 
  if ( abs(Sphericity-1.0) > 1 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Sphericity (S) satisfies the inequality: 0.0 <= S <= 1.0. Found that S = " << Sphericity;
    }

  // Calculate the Sphericity (0 <= S <= 1). S~0 for a 2-jet event, and S~1 for an isotropic one
  SphericityT = 2.0*Q2/(Q1 + Q2); 
  if ( abs(SphericityT-1.0) > 1 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Transverse Sphericity (ST) satisfies the inequality: 0.0 <= ST <= 1.0. Found that ST = " << SphericityT;
    }

  // Calculate the Aplanarity (0 <= A <= 0.5).  It measures the transverse momentum component out of the event plane
  // A~0 for a planar event, A~0.5 for an isotropic one
  Aplanarity = 1.5*(Q3);
  if ( abs(Aplanarity-0.5) > 0.5 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Aplanarity (A) satisfies the inequality: 0.0 <= A <= 0.5";
    }

  // Calculate the Aplanarity (0 <= P <= 0.5)
  Planarity  = (2.0/3.0)*(Sphericity-2*Aplanarity);
  if ( abs(Planarity-0.5) > 0.5 + 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that Planarity (P) satisfies the inequality: 0.0 <= P <= 0.5";
    }

  if (0)
    {

      Table vars("Variable | Value | Allowed Range | Definition", "Text"); //LaTeX or Text
      vars.AddRowColumn(0, "y23");
      vars.AddRowColumn(0, auxTools.ToString(y23) );
      vars.AddRowColumn(0, "0.0 <= y23 <= 0.25");
      vars.AddRowColumn(0, "y23 = pow(jet3_Pt, 2) / pow(jet1_Pt + jet2_Pt, 2)" );
      //
      vars.AddRowColumn(1, "Sphericity");
      vars.AddRowColumn(1, auxTools.ToString(Sphericity) );
      vars.AddRowColumn(1, "0.0 <= S <= 1.0");
      vars.AddRowColumn(1, "S = 1.5 x (Q2 + Q3)");
      //
      vars.AddRowColumn(2, "Sphericity (T)");
      vars.AddRowColumn(2, auxTools.ToString(SphericityT) );
      vars.AddRowColumn(2, "0.0 <= S (T) <= 1.0");
      vars.AddRowColumn(2, "S (T) = (2 x Q2)/(Q1 + Q2)");
      //
      vars.AddRowColumn(3, "Aplanarity");
      vars.AddRowColumn(3, auxTools.ToString(Aplanarity) );
      vars.AddRowColumn(3, "0.0 <= A <= 0.5 ");
      vars.AddRowColumn(3, "A = 1.5 x Q3");
      //
      vars.AddRowColumn(4, "Planarity");
      vars.AddRowColumn(4, auxTools.ToString(Planarity) );
      vars.AddRowColumn(4, "0.0 <= P <= 0.5 ");
      vars.AddRowColumn(4, "P (2/3) x (S - 2A)");
      //
      vars.AddRowColumn(5, "Y");
      vars.AddRowColumn(5, auxTools.ToString(Y) );
      vars.AddRowColumn(5, "");
      vars.AddRowColumn(5, "Y = sqrt(3)/2 x (Q1 - Q2)");
      vars.Print();
    }
    
  return eigenvalues;
  
}

TMatrixDSym Kinematics::ComputeMomentumTensor(std::vector<math::XYZTLorentzVector> jets, double r)
{

  // r = 2: Corresponds to sphericity tensor (Get: Sphericity, Aplanarity, Planarity, ..)
  // r = 1: Corresponds to linear measures (Get: C, D, Second Fox-Wolfram moment, ...)
  TMatrixDSym momentumTensor(3);
  momentumTensor.Zero();
  
  if (r!=1.0 && r!=2.0)
    {
      throw hplus::Exception("LogicError") << "Invalid value r-value in computing the Momentum Tensor (r=" << r << ").  Supported valued are r=2.0 and r=1.0.";
    }
  
  // Sanity Check
  if ( jets.size() < 2 )
    {
      return momentumTensor;
    }
  
  // Declare the Matrix normalisation (sum of momentum magnitutes to power r). That is: sum(|p|^{r})
  double normalisation = 0.0;
  double trace = 0.0;

  // For-loop: Jets
  for (auto& jet: jets){
    
    // Get the |p|^2 of the jet
    double p2 = pow(jet.P(), 2); // jet.P(); 
    
    // For r=2, use |p|^{2}, for r=1 use |p| as the momentum weight
    double pR = ( r == 2.0 ) ? p2 : TMath::Power(p2, 0.5*r);
    
    // For r=2, use |1|, for r=1 use   (|p|^{2})^{-0.5} = |p|^{2 (-1/2)} = |p|^{-1} = 1.0/|p|
    double pRminus2 = ( r == 2.0 ) ? 1.0 : TMath::Power(p2, 0.5*r - 1.0); // 
    
    // Add pR to the matrix normalisation factor
    normalisation += pR;
       
    // Fill the momentum (r=1) or  sphericity (r=2) tensor (Must be symmetric: Mij = Mji)
    momentumTensor(0,0) += pRminus2*jet.px()*jet.px(); // xx
    momentumTensor(0,1) += pRminus2*jet.px()*jet.py(); // xy
    momentumTensor(0,2) += pRminus2*jet.px()*jet.pz(); // xz
    
    momentumTensor(1,0) += pRminus2*jet.py()*jet.px(); // yx
    momentumTensor(1,1) += pRminus2*jet.py()*jet.py(); // yy
    momentumTensor(1,2) += pRminus2*jet.py()*jet.pz(); // yz
    
    momentumTensor(2,0) += pRminus2*jet.pz()*jet.px(); // zx
    momentumTensor(2,1) += pRminus2*jet.pz()*jet.py(); // zy
    momentumTensor(2,2) += pRminus2*jet.pz()*jet.pz(); // zz
    
  }// for (auto& jet: jets){

  // Normalise the tensors to have unit trace (Mxx + Myy + Mzz = 1)
  momentumTensor *= (1.0/normalisation);
  trace = momentumTensor(0,0) + momentumTensor(1,1) + momentumTensor(2,2);
  
  // Print the tensor
  if (0)
    {
      std::cout << "\nMomentum Tensor (r = " << r << "):" << std::endl;
      Table tensor(" |  | ", "Text"); //LaTeX or Text    
      tensor.AddRowColumn(0, auxTools.ToString( momentumTensor(0,0) ) );
      tensor.AddRowColumn(0, auxTools.ToString( momentumTensor(0,1) ) );
      tensor.AddRowColumn(0, auxTools.ToString( momentumTensor(0,2) ) );
      tensor.AddRowColumn(1, auxTools.ToString( momentumTensor(1,0) ) );
      tensor.AddRowColumn(1, auxTools.ToString( momentumTensor(1,1) ) );
      tensor.AddRowColumn(1, auxTools.ToString( momentumTensor(1,2) ) );
      tensor.AddRowColumn(2, auxTools.ToString( momentumTensor(2,0) ) );
      tensor.AddRowColumn(2, auxTools.ToString( momentumTensor(2,1) ) );
      tensor.AddRowColumn(2, auxTools.ToString( momentumTensor(2,2) ) );
      tensor.AddRowColumn(3, "");
      tensor.AddRowColumn(4, "Normalisation");
      tensor.AddRowColumn(4, auxTools.ToString(normalisation));
      tensor.AddRowColumn(5, "IsSymmetric");
      tensor.AddRowColumn(5, auxTools.ToString(momentumTensor.IsSymmetric()));
      tensor.AddRowColumn(6, "Determinant");
      tensor.AddRowColumn(6, auxTools.ToString(momentumTensor.Determinant()));
      tensor.AddRowColumn(7, "Trace");
      tensor.AddRowColumn(7, auxTools.ToString(trace));
      tensor.Print(false);
    }

  if ( abs(trace-1.0) > 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that the Momentum-Tensor (r = " << r << ") Trace is 1.0. Found that abs(trace-1) = " << abs(trace-1) << ", instead.";
    }

  return momentumTensor;
}



TMatrixDSym Kinematics::ComputeMomentumTensor2D(std::vector<math::XYZTLorentzVector> jets)
{

  TMatrixDSym momentumTensor(3);
  momentumTensor.Zero();
  
  // Sanity Check
  if ( jets.size() < 2 )
    {
      return momentumTensor;
    }
  
  // Declare the Matrix normalisation (sum of momentum magnitutes to power r). That is: sum(|p|^{r})
  double normalisation = 0.0;
  double trace = 0.0;

  // For-loop: Jets
  for (auto& jet: jets){
    
    // Get the pT
    double pT = jet.Pt();
    
    // Add pT to the matrix normalisation factor
    normalisation += pow(pT,2);
       
    // Fill the two-dimensional momentum tensor
    momentumTensor(0,0) += jet.px()*jet.px(); // xx
    momentumTensor(0,1) += jet.px()*jet.py(); // xy
    momentumTensor(1,0) += jet.py()*jet.px(); // yx
    momentumTensor(1,1) += jet.py()*jet.py(); // yy
    
  }// for (auto& jet: jets){

  // Normalise tensor to get the normalised 2-d momentum tensor
  momentumTensor *= (1.0/normalisation);
  trace = momentumTensor(0,0) + momentumTensor(1,1);
  
  // Print the tensor
  if (0)
    {
      std::cout << "\nNormalied 2-D Momentum Tensor"  << std::endl;
      Table tensor(" |  | ", "Text"); //LaTeX or Text    
      tensor.AddRowColumn(0, auxTools.ToString( momentumTensor(0,0) ) );
      tensor.AddRowColumn(0, auxTools.ToString( momentumTensor(0,1) ) );
      tensor.AddRowColumn(1, auxTools.ToString( momentumTensor(1,0) ) );
      tensor.AddRowColumn(1, auxTools.ToString( momentumTensor(1,1) ) );
      tensor.AddRowColumn(2, "");
      tensor.AddRowColumn(3, "Normalisation");
      tensor.AddRowColumn(3, auxTools.ToString(normalisation));
      tensor.AddRowColumn(4, "IsSymmetric");
      tensor.AddRowColumn(4, auxTools.ToString(momentumTensor.IsSymmetric()));
      tensor.AddRowColumn(5, "Determinant");
      tensor.AddRowColumn(5, auxTools.ToString(momentumTensor.Determinant()));
      tensor.AddRowColumn(6, "Trace");
      tensor.AddRowColumn(6, auxTools.ToString(trace));
      tensor.Print(false);
    }

  if ( abs(trace-1.0) > 1e-4 )
    {
      throw hplus::Exception("LogicError") << "Failure of requirement that the 2D Momentum-Tensor Trace is 1.0. Found that abs(trace-1) = " << abs(trace-1) << ", instead.";
    }

  return momentumTensor;
}


double Kinematics::GetAlphaT(std::vector<math::XYZTLorentzVector> jets,
			     float &HT,
			     float &JT,
			     float &MHT,
			     float &Centrality){

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  /// AlphaT:
  /// Calculates the AlphaT variable, defined as an N-jets. This definition reproduces the kinematics of a 
  // di-jet system by constructing two pseudo-jets, which balance one another in Ht. 
  // The two pseudo-jets are formed from the combination of the N objects that minimizes the quantity
  /// DeltaHt = |Ht_pseudoJet1 - Ht_pseudoJet2| of the pseudo-jets.                                             
  //
  // Detailed Explanation: 
  // The method "alphaT()" of this class takes as input all jets in the event and uses them to form 
  // two Pseudo-Jets to describe the event. 
  // If there are NJets in a given event this means there are 2^{NJets-1} combinations to do this.
  // The methods does exactly that and for the combination which minimises the quantity
  // DeltaHt = Ht_PseudoJet1 - Ht_PseudoJet2,
  // it calculates the quantity alphaT.
  // The method "alphaT()" employs a double loop to recreate all the possilbe jet combinations 
  // out of NJets, by the use of an NJets-binary system. For example, if NJets=5, the loop
  // indices ("k" outside, "l" inside) run both from "k"=0 to "k"=2^{4}=16 . The upper limit of 
  // the outside loop is given by the expression:
  // 1<<(NJets-1)) = shift the number 1 by (NJets-1) positions to the left. 
  // So, for NJets=5  (i.e. 1  --> 1 0 0 0 0 ) 
  // This is now the way we will represent grouping into 2 Pseudo-Jets. The 0's represent one group and the 1's the other.
  // So, for example 1 0 0 0 0 means 1 jet forms Pseudo-Jet1 and 4 jets form Pseudo-Jet2. 
  // Also, for example, 1 0 0 1 0 means 2 jets form Pseudo-Jet1 and 3 jets form Pseudo-Jet2.
  // The inside loop performs a bitwise right shift of index "k" by "l" positions and then
  // compares the resulting bit to 1. So, for "k"=0, all the resulting comparisons in the 
  // inside loop will result to 0, except the one with "l"=4.
  // This gives the first combination: 0 0 0 0 0   ( i.e. 0 jets form Pseudo-Jet1 and 5 jets form Pseudo-Jet2 )
  // For "k"=1 (00000001 in 8bit representation), the first comparison is 1, since k is shifted by zero positions 
  // and then compared to 1. The rest comparisons yield zero, since by shifting the bit by any position and comparing to 1 gives zero. 
  // Thus, for "k"=1 we have after the second loop: 0 0 0 0 1
  // In the same manner, we get for "k"=2 (00000001 in 8bit representation) we have after the second loop: 0 0 0 1 0
  //  To summarise, for NJets=5 we have 16 combinations:
  // For "k"=0  ( 00000000 in 8bit representation) we have after the second loop: 0 0 0 0 0
  // For "k"=1  ( 00000001 in 8bit representation) we have after the second loop: 0 0 0 0 1
  // For "k"=2  ( 00000001 in 8bit representation) we have after the second loop: 0 0 0 1 0
  // For "k"=3  ( 00000011 in 8bit representation) we have after the second loop: 0 0 0 1 1
  // For "k"=4  ( 00000100 in 8bit representation) we have after the second loop: 0 0 1 0 0
  // For "k"=5  ( 00000101 in 8bit representation) we have after the second loop: 0 0 1 0 1
  // For "k"=6  ( 00000110 in 8bit representation) we have after the second loop: 0 0 1 1 0
  // For "k"=7  ( 00000111 in 8bit representation) we have after the second loop: 0 0 1 1 1
  // For "k"=8  ( 00001000 in 8bit representation) we have after the second loop: 0 1 0 0 0
  // For "k"=9  ( 00001001 in 8bit representation) we have after the second loop: 0 1 0 0 1
  // For "k"=10 ( 00010000 in 8bit representation) we have after the second loop: 0 1 0 0 0
  // For "k"=11 ( 00010001 in 8bit representation) we have after the second loop: 0 1 0 0 1
  // For "k"=12 ( 00010010 in 8bit representation) we have after the second loop: 0 1 0 1 0
  // For "k"=13 ( 00010011 in 8bit representation) we have after the second loop: 0 1 0 1 1
  // For "k"=14 ( 00010100 in 8bit representation) we have after the second loop: 0 1 1 0 0
  // For "k"=15 ( 00010101 in 8bit representation) we have after the second loop: 0 1 1 0 1
  // For "k"=16 ( 00010110 in 8bit representation) we have after the second loop: 0 1 1 1 0
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

  /// Declaration of variables 
  unsigned nJets = jets.size();

  // Sanity Check
  if ( jets.size() < 2 )
    {
      return -1.0;
    }

  std::vector<float> vE, vEt, vPx, vPy, vPz;
  std::vector<bool> vPseudo_jet1;
  const bool bList = true;

  // For-Loop: All jets
  for (auto& jet: jets){
    vE.push_back( jet.E() );
    vEt.push_back( jet.Et() );
    vPx.push_back( jet.Px() );
    vPy.push_back( jet.Py() );
    vPz.push_back( jet.Pz() );
  }

  // Calculate sums
  float fSum_e  = accumulate( vE.begin() , vE.end() , 0.0 );
  float fSum_et = accumulate( vEt.begin(), vEt.end(), 0.0 );
  float fSum_px = accumulate( vPx.begin(), vPx.end(), 0.0 );
  float fSum_py = accumulate( vPy.begin(), vPy.end(), 0.0 );

  // Minimum Delta Et for two pseudo-jets
  float fMin_delta_sum_et = -1.0;

  // Iterate through different combinations
  for ( unsigned k=0; k < unsigned(1<<(nJets-1)); k++ ) { 
    float fDelta_sum_et = 0.0;
    std::vector<bool> jet;

    // Iterate through jets
    for ( unsigned l=0; l < vEt.size(); l++ ) { 
      /// Bitwise shift of "k" by "l" positions to the right and compare to 1 (&1)
      /// i.e.: fDelta_sum_et += vEt[l] * ( 1 - 2*0 );  if comparison is un-successful
      ///  or   fDelta_sum_et += vEt[l] * ( 1 - 2*1 );  if comparison is successful
      // in this way you add up all Et from PseudoJetsGroupA (belonging to 0's group) and subtract that from PseudoJetsGroupB (1's group)
      fDelta_sum_et += vEt[l] * ( 1 - 2 * (int(k>>l)&1) ); 
      if ( bList ) { jet.push_back( (int(k>>l)&1) == 0 ); } 
    }

    // Find configuration with minimum value of DeltaHt 
    if ( ( fabs(fDelta_sum_et) < fMin_delta_sum_et || fMin_delta_sum_et < 0.0 ) ) {
      fMin_delta_sum_et = fabs(fDelta_sum_et);
      if ( bList && jet.size() == vEt.size() ){vPseudo_jet1.resize(jet.size());}
    }

  }
    
  // Sanity check
  if ( fMin_delta_sum_et < 0.0 )
    { 
      throw hplus::Exception("LogicError") << "Minimum Delta(Sum_Et) is less than zero! fMin_delta_sum_et = " << fMin_delta_sum_et;
    }
  
  // Calculate Event-Shape Variables
  float dHT = fMin_delta_sum_et;
  HT  = fSum_et;
  JT  = fSum_et - vEt.at(0); // Ht without considering the Ldg Jet of the Event
  MHT = sqrt(pow(fSum_px,2) + pow(fSum_py,2));
  Centrality = fSum_et/fSum_e;
  float AlphaT = ( 0.5 * ( HT - dHT ) / sqrt( pow(HT,2) - pow(MHT,2) ) );

  if (0)
    {

      Table vars("Variable | Value | Definition", "Text"); //LaTeX or Text
      vars.AddRowColumn(0, "HT");
      vars.AddRowColumn(0, auxTools.ToString(HT) );
      vars.AddRowColumn(0, "HT = Sum(Jet_Et)");
      //
      vars.AddRowColumn(1, "JT");
      vars.AddRowColumn(1, auxTools.ToString(JT) );
      vars.AddRowColumn(1, "JT = Ht - Jet1_Et");
      //
      vars.AddRowColumn(2, "dHT");
      vars.AddRowColumn(2, auxTools.ToString(dHT) );
      vars.AddRowColumn(2, "DeltaHT = min[Delta(Pseudojet1_Et, Pseudojet2_Et)]");
      //
      vars.AddRowColumn(3, "MHT");
      vars.AddRowColumn(3, auxTools.ToString(MHT) );
      vars.AddRowColumn(3, "MHT = sqrt( pow(Sum(px), 2) + pow(Sum(py), 2))");
      //
      vars.AddRowColumn(4, "AlphaT");
      vars.AddRowColumn(4, auxTools.ToString(AlphaT) );
      vars.AddRowColumn(4, "AlphaT = 0.5 x (HT - dHT) /sqr( pow(HT, 2) - pow(MHT, 2))");
      vars.Print();
    }

  return AlphaT;
}

vector<GenJet> Kinematics::GetGenJets(const vector<GenJet> genJets, std::vector<float> ptCuts, std::vector<float> etaCuts, vector<genParticle> genParticlesToMatch)
{
  /*
    Jet-Flavour Definitions (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagMCTools)

    Algorithmic definition: (NOTE: Algorithmic definition is used by default for all b-tagging purposes)
    - Try to find the parton that most likely determines the properties of the jet and assign that flavour as the true flavour
    - Here, the ��final state�� partons (after showering, radiation) are analyzed (within ��R < 0.3 of the reconstructed jet axis). 
    Partons selected for the algorithmic definition are those partons that don't have other partons as daughters, 
    without any explicit requirement on their status (for Pythia6 these are status=2 partons).
    - Jets from radiation are matched with full efficiency
    -If there is a b/c within the jet cone: label as b/c
    -Otherwise: assign flavour of the hardest parton
   */

  // Definitions
  std::vector<GenJet> jets;
  unsigned int jet_index   = -1;
  unsigned int ptCut_index  = 0;
  unsigned int etaCut_index = 0;

  // For-loop: All genParticles
  for (auto& p: genParticlesToMatch) 
    {
      
      // Comparison variables
      double dR   = 1e6;
      double dPt  = 1e6;
      double dEta = 1e6;
      double dPhi = 1e6;
	  
      // For-loop: All Generated Jets
      for (auto jet: genJets) 
	{
	  
	  // Jet index (for pT and eta cuts)
	  jet_index++;
	  
	  dPt  = jet.pt() - p.pt();
	  dEta = jet.eta() - p.eta();
	  dPhi = jet.phi() - p.phi();
       	  dR   = ROOT::Math::VectorUtil::DeltaR(jet.p4(), p.p4());
      
	  // Fail to match
	  if (dR > 0.3) continue;
	  
	  // Apply cuts after the matching
	  const float ptCut  = ptCuts.at(ptCut_index);
	  const float etaCut = etaCuts.at(etaCut_index);
	  if (jet.pt() < ptCut) continue;
	  if (std::abs(jet.eta()) > etaCut) continue;
	  
	  // Save this particle
	  jets.push_back(jet);
	  if (0) std::cout << "dR = " << dR << ": dPt = " << dPt << ", dEta = " << dEta << ", dPhi = " << dPhi << std::endl;

	  // Increment cut index only. Cannot be bigger than the size of the cut list provided
	  if (ptCut_index  < ptCuts.size()-1  ) ptCut_index++;
	  if (etaCut_index < etaCuts.size()-1  ) etaCut_index++;
	  break;
	}
    }
  if (0) std::cout << "bjets.size() = " << jets.size() << std::endl;
  return jets;
}

vector<GenJet> Kinematics::GetGenJets(const GenJetCollection& genJets, std::vector<float> ptCuts, std::vector<float> etaCuts)
{
  std::vector<GenJet> jets;

  // Definitions
  unsigned int jet_index   = -1;
  unsigned int ptCut_index  = 0;
  unsigned int etaCut_index = 0;

  // For-loop: All Generated Jets
  for (auto jet: genJets) 
    {

      // Jet index (for pT and eta cuts)
      jet_index++;
      
      // Apply cuts
      const float ptCut  = ptCuts.at(ptCut_index);
      const float etaCut = etaCuts.at(etaCut_index);
      if (jet.pt() < ptCut) continue;
      if (std::abs(jet.eta()) > etaCut) continue;

      // Save this particle
      jets.push_back(jet);

      // Increment cut index only. Cannot be bigger than the size of the cut list provided
      if (ptCut_index  < ptCuts.size()-1  ) ptCut_index++;
      if (etaCut_index < etaCuts.size()-1  ) etaCut_index++;
    }
  return jets;
}

vector<genParticle> Kinematics::GetGenParticles(const vector<genParticle> genParticles, double ptCut, double etaCut, const int pdgId, const bool isLastCopy, const bool hasNoDaughters)
  {
  
  std::vector<genParticle> particles;

  // For-loop: All genParticles
  for (auto& p: genParticles) 
    {
      // Find last copy of a given particle
      if (isLastCopy) if (!p.isLastCopy()) continue;      

      // Commonly enables for parton-based jet flavour definition
      if (hasNoDaughters) if (p.daughters().size() > 0) continue;

      // Consider only particles
      if (std::abs(p.pdgId()) != pdgId) continue;
      
      // Apply cuts
      if ( p.pt() < ptCut ) continue;
      if (std::abs(p.eta()) > etaCut) continue;
      
      // Save this particle
      particles.push_back(p);
    }
  return particles;
  }


std::vector<math::XYZTLorentzVector> Kinematics::SortInPt(std::vector<math::XYZTLorentzVector> Vector)
{
  int size = Vector.size();
  for (int i=0; i<size-1; i++){
    math::XYZTLorentzVector p4_i = Vector.at(i);
    for (int j=i+1;  j<size; j++){
      math::XYZTLorentzVector p4_j = Vector.at(j);
      if (p4_i.pt() > p4_j.pt()) continue;
      math::XYZTLorentzVector temp = p4_i;
      Vector.at(i) = Vector.at(j);
      Vector.at(j) = temp;
    }
  }
  return Vector;
}

      
  
Bool_t Kinematics::IsBjet(math::XYZTLorentzVector jet, vector<GenJet> selectedBJets)
{
  for (auto& bjet: selectedBJets) 
    {
      double dR = ROOT::Math::VectorUtil::DeltaR(jet, bjet.p4());
      if (dR < 0.01) return true;
    }
  return false;
}

double Kinematics::DeltaRmin(math::XYZTLorentzVector jet, vector<GenJet> jetSelection){
  double drmin = 10000.0;
  for (auto& j: jetSelection)
    {
      double dR = ROOT::Math::VectorUtil::DeltaR(jet, j.p4());
      if (dR > drmin) continue;
      drmin = dR;
    }
  return drmin;
}

vector <math::XYZTLorentzVector> Kinematics::TrijetJets(vector<math::XYZTLorentzVector> JETS, vector<GenJet> selectedBJets){
  //Returns the vector of the vector of the jets that form the trijet 
  //First two: Untagged jets sorted in pt (ldg, subldg)
  //Third: Bjet 
  math::XYZTLorentzVector bjet(0,0,0,0);

  double drmin = 10000.0;
  size_t b_index = 0;
  
  for (size_t i=0; i<JETS.size(); i++){
    if (!IsBjet(JETS.at(i),selectedBJets) ) continue;
    double dr = DeltaRmin(JETS.at(i),selectedBJets);
    if (dr > drmin) continue;
    bjet = JETS.at(i);
    b_index = i;
  }
  
  vector <math::XYZTLorentzVector> untagged;
  for (size_t i=0; i<JETS.size(); i++){
    if (i ==b_index) continue;
    untagged.push_back(JETS.at(i));
  }
  
  //ldg jet, subldg jet, bjet
  untagged = SortInPt(untagged);
  untagged.push_back(bjet);
  // jet1 = untagged.at(0);
  // jet2 = untagged.at(1);
  //  std::cout<<jet1.pt()<<" "<<jet2.pt()<<" "<<bjet.pt()<<std::endl;
  return untagged;
}

  
  
