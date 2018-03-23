// -*- c++ -*-
#include "EventSelection/interface/QuarkGluonLikelihoodRatio.h"

#include "Framework/interface/ParameterSet.h"
#include "EventSelection/interface/CommonPlots.h"
#include "DataFormat/interface/Event.h"
#include "Framework/interface/HistoWrapper.h"
#include "Framework/interface/Exception.h"
#include "DataFormat/interface/HLTBJet.h"

#include "Math/VectorUtil.h"
#include <cmath>
#include <algorithm>

// --- QGLInputItem ---

// Constructor
QGLInputItem::QGLInputItem(float minQGL, float maxQGL, float minPt, float maxPt, float prob, float probErr)
: fminQGL(minQGL),
  fmaxQGL(maxQGL),
  fminPt(minPt),
  fmaxPt(maxPt),
  fProb(prob),
  fProbErr(probErr)
{}

// Destructor
QGLInputItem::~QGLInputItem() {}

// --- QGLInputStash ---

// Constructor
QGLInputStash::QGLInputStash() {}

// Destructor
QGLInputStash::~QGLInputStash() {
  
  std::vector<std::vector<QGLInputItem*>> collections = { fLight, fGluon};
  for (auto& container: collections) {
    for (size_t i = 0; i < container.size(); ++i) {
      delete container[i];
    }
    container.clear();
  }
}

// Create new input item corresponding to certain jet type 
void QGLInputStash::addInput(std::string jetType, float minQGL, float maxQGL, float minPt, float maxPt, float Prob, float ProbErr) {
  getCollection(jetType).push_back(new QGLInputItem(minQGL, maxQGL, minPt, maxPt, Prob, ProbErr));
}


// Return the Probability based on QGL value
const float QGLInputStash::getInputValue(std::string jetType, float QGL, float pt) {
  for (auto &p: getCollection(jetType)) {
    if (!p->isWithinPtRange(pt)) continue;
    if (!p->isWithinQGLRange(QGL)) continue;
    return p->getProb();
  }
  return 1.0;
}

// Get vector of input items (according to jetType)
std::vector<QGLInputItem*>& QGLInputStash::getCollection(std::string jetType) {
  if (jetType == "Light")
    return fLight;
  else if (jetType == "Gluon")
    return fGluon;
  throw hplus::Exception("Logic") << "Unknown jet type requested! " << jetType;
}



QuarkGluonLikelihoodRatio::Data::Data() 
: bPassedSelection(false)
{ }

QuarkGluonLikelihoodRatio::Data::~Data() { }

QuarkGluonLikelihoodRatio::QuarkGluonLikelihoodRatio(const ParameterSet& config, EventCounter& eventCounter, HistoWrapper& histoWrapper, CommonPlots* commonPlots, const std::string& postfix)
: BaseSelection(eventCounter, histoWrapper, commonPlots, postfix),
  fQGLRCut(config, "QGLRCut"),
  fnumberOfJetsCut(config, "numberOfJetsCut"),
  fJetsCut(config.getParameter<float>("numberOfJetsCutValue")),
  // Event counter for passing selection
  cPassedQuarkGluonLikelihoodRatio(fEventCounter.addCounter("passed QGLR selection ("+postfix+")")),
  // Sub counters
  cSubAll(fEventCounter.addSubCounter("QGLR selection ("+postfix+")", "All events")),
  cSubRequiredJetsResize(fEventCounter.addSubCounter("QGLR selection ("+postfix+")", "Required jets resizing")),
  cSubNoJetsResize(fEventCounter.addSubCounter("QGLR selection ("+postfix+")", "No jets resizing")),
  fProb()
{
  initialize(config);
}

QuarkGluonLikelihoodRatio::QuarkGluonLikelihoodRatio(const ParameterSet& config)
: BaseSelection(),
  fQGLRCut(config, "QGLRCut"),
  fnumberOfJetsCut(config, "numberOfJetsCut"),
  fJetsCut(config.getParameter<float>("numberOfJetsCutValue")),
  // Event counter for passing selection
  cPassedQuarkGluonLikelihoodRatio(fEventCounter.addCounter("passed QGLR selection")),
  // Sub counters
  cSubAll(fEventCounter.addSubCounter("QGLR selection", "All events")),
  cSubRequiredJetsResize(fEventCounter.addSubCounter("QGLR selection", "Required jets resizing")),
  cSubNoJetsResize(fEventCounter.addSubCounter("QGLR selection", "No jets resizing")),
  fProb()
{
  initialize(config);
  bookHistograms(new TDirectory());
}

QuarkGluonLikelihoodRatio::~QuarkGluonLikelihoodRatio() {
  delete hAllJetsNonBJetsQGL;
  delete hGluonJetQGL;
  delete hLightJetQGL;

  delete hQGLR;
  delete hQGLR_vs_HT;
  delete hQGLR_vs_NJets;
}

void QuarkGluonLikelihoodRatio::initialize(const ParameterSet& config) {
  handleQGLInput(config, "Light"); 
  handleQGLInput(config, "Gluon");
  
  return;
}

void QuarkGluonLikelihoodRatio::handleQGLInput(const ParameterSet& config, std::string jetType) { 
  
  boost::optional<std::vector<ParameterSet>> psets;
  if (jetType == "Light") psets = config.getParameterOptional<std::vector<ParameterSet>>("LightJetsQGL");
  if (jetType == "Gluon") psets = config.getParameterOptional<std::vector<ParameterSet>>("GluonJetsQGL");
  
  if (!psets) return;
  
  for (auto &p: *psets) {
    
    // Obtain variables
    float minQGL = p.getParameter<float>("QGLmin");
    float maxQGL = p.getParameter<float>("QGLmax");
    float minPt  = p.getParameter<float>("Ptmin");
    float maxPt  = p.getParameter<float>("Ptmax");
    float Prob   = p.getParameter<float>("prob");
    float ProbErr= p.getParameter<float>("probError");
    
    if (0) std::cout<<"minQGL="<<minQGL<<" maxQGL="<<maxQGL<<"  minPt="<<minPt<<"  maxPt="<<maxPt<<"   Probability="<<Prob<<"  Error="<<ProbErr<<std::endl;
    
    // Store them
    fProb.addInput(jetType, minQGL, maxQGL, minPt, maxPt, Prob, ProbErr);
  }
  return;
}


void QuarkGluonLikelihoodRatio::bookHistograms(TDirectory* dir) {
  TDirectory* subdir = fHistoWrapper.mkdir(HistoLevel::kDebug, dir, "QGLRSelection_" + sPostfix);
  
  // Histogram binning options
  int nQGLBins      = 100;
  float fQGLMin     = 0.0;
  float fQGLMax     = 1.0;
    
  hAllJetsNonBJetsQGL = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "AllJetsNonBJetsQGL", "Quark-Gluon discriminant for all jets bot identified as b-jets", nQGLBins, fQGLMin, fQGLMax);
  hGluonJetQGL = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "GluonJetQGL", "Quark-Gluon discriminant for Gluon Jets", nQGLBins, fQGLMin, fQGLMax);
  hLightJetQGL = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "LightJetQGL", "Quark-Gluon discriminant for Light Jets", nQGLBins, fQGLMin, fQGLMax);
  
  hQGLR = fHistoWrapper.makeTH<TH1F>(HistoLevel::kVital, subdir, "QGLR", "Quark-Gluon likelihood ratio", nQGLBins, fQGLMin, fQGLMax);
  hQGLR_vs_HT = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, subdir, "QGLR_vs_HT", "QGLR Vs H_{T} (GeVc^{-1})", 50, 0.0, 4000.0, nQGLBins, fQGLMin, fQGLMax);
  hQGLR_vs_NJets = fHistoWrapper.makeTH<TH2F>(HistoLevel::kVital, subdir, "QGLR_vs_NJets", "QGLR Vs Jets Multiplicity", 15, -0.5, 14.5, nQGLBins, fQGLMin, fQGLMax); 
}

QuarkGluonLikelihoodRatio::Data QuarkGluonLikelihoodRatio::silentAnalyze(const Event& event, const JetSelection::Data& jetData, const BJetSelection::Data& bjetData) {
  ensureSilentAnalyzeAllowed(event.eventID());
  // Disable histogram filling and counter
  disableHistogramsAndCounters();
  Data myData = privateAnalyze(event, jetData, bjetData);
  enableHistogramsAndCounters();
  return myData;
}

QuarkGluonLikelihoodRatio::Data QuarkGluonLikelihoodRatio::analyze(const Event& event, const JetSelection::Data& jetData, const BJetSelection::Data& bjetData) {
  ensureAnalyzeAllowed(event.eventID());
  QuarkGluonLikelihoodRatio::Data data = privateAnalyze(event, jetData, bjetData);
  // Send data to CommonPlots
  //if (fCommonPlots != nullptr)
  //  fCommonPlots->fillControlPlotsAtBtagging(event, data);
  // Return data
  return data;
}

QuarkGluonLikelihoodRatio::Data QuarkGluonLikelihoodRatio::privateAnalyze(const Event& iEvent, const JetSelection::Data& jetData, const BJetSelection::Data& bjetData) {
  Data output;
  cSubAll.increment();
  bool doJetsResize = false;
  std::vector<Jet> selectedJets;

  // Get all the non-bjets jets
  for (auto jet: jetData.getSelectedJets())
    {
      if (isBJet(jet, bjetData.getSelectedBJets())) continue;
      selectedJets.push_back(jet);
    }

  // Impose restrition to max number of jet multiplicities to consider
  if (!fnumberOfJetsCut.passedCut(selectedJets.size())) 
    {
      doJetsResize = true;
      // std::cout << "selectedJets.size() = " << selectedJets.size() << ", doJetsResize = " << doJetsResize << std::endl;
      selectedJets.resize(fJetsCut);
    }
  
  // For-loop: All seleted jets (multiplicities up to "fJetsCut")
  for(const Jet& jet: selectedJets){
    
    // All jets not identified as b-jets QGL
    hAllJetsNonBJetsQGL -> Fill(jet.QGTaggerAK4PFCHSqgLikelihood());
    
    if (iEvent.isMC())
      {
	const short jetHadronFlavour = std::abs(jet.hadronFlavour());
	const short jetPartonFlavour = std::abs(jet.partonFlavour());
	
	// === Reject jets consistent with b or c  (jet flavors:  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagMCTools#Hadron_parton_based_jet_flavour )
	if (jetHadronFlavour != 0) continue;
	if (jetPartonFlavour != 1 && jetPartonFlavour != 2 && jetPartonFlavour != 3 && jetPartonFlavour != 21) continue;
	
	// Jets to keep
	output.fJetsForQGLR.push_back(jet);
	
	// Gluon Jets
	if (jetPartonFlavour == 21)
	  {
	    output.fGluonJets.push_back(jet);
	    hGluonJetQGL->Fill(jet.QGTaggerAK4PFCHSqgLikelihood());
	  }
	// Light Jets
	if (jetPartonFlavour == 1 || jetPartonFlavour == 2 || jetPartonFlavour == 3)
	  {
	    output.fLightJets.push_back(jet);
	    hLightJetQGL->Fill(jet.QGTaggerAK4PFCHSqgLikelihood());
	  }
      } 
    else 
      {
	// Data
	output.fJetsForQGLR.push_back(jet);
      }
  }
  
  // Calculate QGLR
  double QGLR = calculateQGLR(iEvent, output.fJetsForQGLR);
  output.fQGLR = QGLR;
  output.bPassedSelection = fQGLRCut.passedCut(QGLR);
  
  // Fill counters and sub-counters
  if (doJetsResize) cSubRequiredJetsResize.increment();
  else cSubNoJetsResize.increment();    
  if (fQGLRCut.passedCut(QGLR)) cPassedQuarkGluonLikelihoodRatio.increment();

  // Fill Histograms
  hQGLR          -> Fill(output.fQGLR);
  hQGLR_vs_HT    -> Fill(jetData.HT(), output.fQGLR);
  hQGLR_vs_NJets -> Fill(output.fJetsForQGLR.size(), output.fQGLR);
  
  // Return data object
  return output;
}

double QuarkGluonLikelihoodRatio::calculateQGLR(const Event& iEvent, const std::vector<Jet> Jets)
{
  // Quark term
  double LNq0g = calculateL(iEvent, Jets, Jets.size(), 0);
    
  // Gluon term
  double L0qNg = calculateL(iEvent, Jets, 0, Jets.size());
  
  double QGLR = LNq0g / ( LNq0g+L0qNg);

  // To see the ratio of all quarks to all possible combinations uncomment the following block
  /*
  double sum = 0;
  for (unsigned int iNg=1; iNg<Jets.size()+1; iNg++)
    {
      int iNq = Jets.size() - iNg;
      double L = calculateL(iEvent, Jets, iNq, iNg);
      sum +=  L;
    }
  QGLR = LNq0g / (LNq0g+sum);
  */
  
  return QGLR;
}

double QuarkGluonLikelihoodRatio::factorial(const int N)
{
  if (N > 1)
    return N * factorial(N-1);
  else
    return 1;
}

std::vector<int> QuarkGluonLikelihoodRatio::getJetIndices(const std::vector<Jet> Jets)
{
  std::vector<int> v;
  for (unsigned int i=0; i<Jets.size(); i++)
    {
      v.push_back(Jets.at(i).index());
    }
  return v;
}

double QuarkGluonLikelihoodRatio::calculateL(const Event& iEvent, const std::vector<Jet> Jets, const int Nq, const int Ng)
{
  std::vector<int> v = getJetIndices(Jets);
  std::vector<std::vector<int> > permutations = getPermutations(v, Nq, Ng);
  
  // First Nq places are for Quarks and the last Ng are for Gluons
  double sum = 0;
  for (unsigned int i=0; i<permutations.size(); i++)
    {
      double productQuark = 1;
      double productGluon = 1;
      
      std::vector<int> v = permutations.at(i);

      for (int q=0; q<Nq; q++)
	{
	  int index    = v.at(q);
	  Jet QuarkJet = iEvent.jets()[index];
	  double QGL   = QuarkJet.QGTaggerAK4PFCHSqgLikelihood();
	  double pt    = QuarkJet.pt();
	  
	  productQuark *= fProb.getInputValue("Light", QGL, pt);
	  
	  if (0) std::cout<<"Light Jet |  q="<<q<<"  with index="<<index<<"   pt ="<<pt<<"  QGL="<<QGL<<"  Probability="<<fProb.getInputValue("Light", QGL, pt)<<std::endl;
	}
      
      for (unsigned int g=Nq; g<v.size(); g++)
	{
	  int index    = v.at(g);
	  Jet GluonJet = iEvent.jets()[index];
	  double QGL   = GluonJet.QGTaggerAK4PFCHSqgLikelihood();
	  double pt    = GluonJet.pt();
	  
	  productGluon *= fProb.getInputValue("Gluon", QGL, pt);
	  
	  if (0) std::cout<<"Gluon Jet |  g="<<g<<"  with index="<<index<<"   pt ="<<pt<<"  QGL="<<QGL<<"  Probability="<<fProb.getInputValue("Gluon", QGL, pt)<<std::endl;
	}
      sum+= productQuark * productGluon;
    }
  return sum;
}

std::vector<std::vector<int> > QuarkGluonLikelihoodRatio::getPermutations(std::vector<int> v, const int Nq, const int Ng)
{
  std::vector<std::vector<int> > permutations;
  int nPermutations = 0;
  
  do {    
    bool Found = PermutationFound(permutations, v, Nq, Ng);
    if (!Found)
      {
	nPermutations++;
	permutations.push_back(v);
	
	// Print permutations
	/*
	for (unsigned int i=0; i<v.size(); i++){
	  std::cout << v.at(i) << " ";
	}
	std::cout<<" "<<std::endl;
	*/
      }
  } while (std::next_permutation(v.begin(), v.end()));
  return permutations;
}

bool QuarkGluonLikelihoodRatio::PermutationFound(std::vector<std::vector<int> > p, std::vector<int> v, const int Nq, const int Ng)
{
  
  int nStart = 0;
  int nEnd   = 0;
  int nJets  = 0;

  if (Nq < Ng){
    nStart = 0;
    nEnd   = Nq;
    nJets  = Nq;
  }
  else{
    nStart = Nq;
    nEnd   = Nq+Ng;
    nJets  = Ng;
  }
  
  for (unsigned int row=0; row<p.size(); row++)
    {
      std::vector<int> perm = p.at(row);
      int FoundAll = 0;
      
      for (int j=nStart; j<nEnd; j++){
	
	int FindIndex =  v.at(j);
	
	bool FoundIndex = false;
	for (int k=nStart; k<nEnd;k++){
	  if (perm.at(k) == FindIndex) FoundIndex = true;
	}
	if (FoundIndex) FoundAll++;
	else break;	
      }
      if (FoundAll == nJets) return 1;
    }
  return 0;
}


bool QuarkGluonLikelihoodRatio::isBJet(const Jet& jet, const std::vector<Jet>& bjets) {
  for (auto bjet: bjets)
    {
      if (areSameJets(jet, bjet)) return true;
    }
  return false;
}

bool QuarkGluonLikelihoodRatio::areSameJets(const Jet& jet1, const Jet& jet2) {
  float dR = ROOT::Math::VectorUtil::DeltaR(jet1.p4(), jet2.p4());
  float dR_match = 0.1;
  if (dR <= dR_match) return true;
  else return false;
}
