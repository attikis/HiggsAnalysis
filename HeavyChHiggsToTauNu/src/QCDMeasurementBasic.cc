#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/QCDMeasurementBasic.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TransverseMass.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/DeltaPhi.h"

#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/MakeTH.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TH1F.h"
#include "TH2F.h"
#include "TNamed.h"

namespace HPlus {
  QCDMeasurementBasic::QCDMeasurementBasic(const edm::ParameterSet& iConfig, EventCounter& eventCounter, EventWeight& eventWeight):
    fEventWeight(eventWeight),
    fAllCounter(eventCounter.addCounter("allEvents")),
    fTriggerAndHLTMetCutCounter(eventCounter.addCounter("Trigger_and_HLT_MET")),
    fPrimaryVertexCounter(eventCounter.addCounter("PrimaryVertex")),
    fOneProngTauSelectionCounter(eventCounter.addCounter("TauCandSelection")),
    fOneSelectedTauCounter(eventCounter.addCounter("TauCands==1")),
    fGlobalElectronVetoCounter(eventCounter.addCounter("GlobalElectronVeto")),
    fGlobalMuonVetoCounter(eventCounter.addCounter("GlobalMuonVeto")),
    fJetSelectionCounter(eventCounter.addCounter("JetSelection")),
    fNonIsolatedElectronVetoCounter(eventCounter.addCounter("NonIsolatedElectronVeto")),
    fNonIsolatedMuonVetoCounter(eventCounter.addCounter("NonIsolatedMuonVeto")),
    fDeltaPhiTauMETCounter(eventCounter.addCounter("DeltaPhiTauMET")),
    fMETCounter(eventCounter.addCounter("MET")),
    fBTaggingCounter(eventCounter.addCounter("bTagging")),
    fOneProngTauIDWithoutRtauCounter(eventCounter.addCounter("TauID_noRtau")),
    fOneProngTauIDWithRtauCounter(eventCounter.addCounter("TauID_withRtau")),
    fTriggerSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("trigger"), eventCounter, eventWeight),
    fPrimaryVertexSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("primaryVertexSelection"), eventCounter, eventWeight),
    fOneProngTauSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("tauSelection"), eventCounter, eventWeight, 1, "tauCandidate"),
    fGlobalElectronVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("GlobalElectronVeto"), eventCounter, eventWeight),
    fNonIsolatedElectronVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("NonIsolatedElectronVeto"), eventCounter, eventWeight),
    fGlobalMuonVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("GlobalMuonVeto"), eventCounter, eventWeight),
    fNonIsolatedMuonVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("NonIsolatedMuonVeto"), eventCounter, eventWeight),
    fJetSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("jetSelection"), eventCounter, eventWeight),
    fMETSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("MET"), eventCounter, eventWeight, "MET"),
    //fInvMassVetoOnJets(iConfig.getUntrackedParameter<edm::ParameterSet>("InvMassVetoOnJets"), eventCounter, eventWeight),
    fEvtTopology(iConfig.getUntrackedParameter<edm::ParameterSet>("EvtTopology"), eventCounter, eventWeight),
    fBTagging(iConfig.getUntrackedParameter<edm::ParameterSet>("bTagging"), eventCounter, eventWeight),
    //fFakeMETVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("fakeMETVeto"), eventCounter, eventWeight),
    //fTopSelection(iConfig.getUntrackedParameter<edm::ParameterSet>("topSelection"), eventCounter, eventWeight),
    //fForwardJetVeto(iConfig.getUntrackedParameter<edm::ParameterSet>("forwardJetVeto"), eventCounter, eventWeight),
    //fWeightedSelectedEventsAnalyzer("QCDm3p2_afterAllSelections_weighted"),
    //fNonWeightedSelectedEventsAnalyzer("QCDm3p2_afterAllSelections_nonWeighted"),
    fGenparticleAnalysis(iConfig.getUntrackedParameter<edm::ParameterSet>("GenParticleAnalysis"), eventCounter, eventWeight),
    fVertexWeight(iConfig.getUntrackedParameter<edm::ParameterSet>("vertexWeight")),
    fFakeTauIdentifier(fEventWeight),
    fTriggerEfficiencyScaleFactor(iConfig.getUntrackedParameter<edm::ParameterSet>("triggerEfficiencyScaleFactor"), fEventWeight),
    fTree(iConfig.getUntrackedParameter<edm::ParameterSet>("Tree"), fBTagging.getDiscriminator()),
    fSFUncertaintyAfterStandardSelections("AfterStandardSelections")
    // fTriggerEmulationEfficiency(iConfig.getUntrackedParameter<edm::ParameterSet>("TriggerEmulationEfficiency"))
    // ftransverseMassCutCount(eventCounter.addCounter("transverseMass cut")),
   {
    edm::Service<TFileService> fs;
    // Save the module configuration to the output ROOT file as a TNamed object
    fs->make<TNamed>("parameterSet", iConfig.dump().c_str());

    // Book histograms
    hVerticesBeforeWeight = makeTH<TH1F>(*fs, "verticesBeforeWeight", "Number of vertices without weightingVertices;N_{events} / 1 Vertex", 30, 0, 30);
    hVerticesAfterWeight =  makeTH<TH1F>(*fs, "verticesAfterWeight", "Number of vertices with weighting; Vertices;N_{events} / 1 Vertex", 30, 0, 30);

    // Histograms for later change of factorization map
    // Tau pT factorisation bins
    fTauPtBinLowEdges.push_back(40);
    fTauPtBinLowEdges.push_back(50);
    fTauPtBinLowEdges.push_back(60);
    fTauPtBinLowEdges.push_back(70);
    fTauPtBinLowEdges.push_back(80);
    fTauPtBinLowEdges.push_back(100);
    fTauPtBinLowEdges.push_back(120);
    fTauPtBinLowEdges.push_back(150);
    int myTauPtBins = static_cast<int>(fTauPtBinLowEdges.size()) + 1;
    // Transverse mass bins
    for (double i = 0; i < 41; ++i) {
      fTransverseMassBinLowEdges.push_back(i * 10.0);
    }
    int myTransverseMassBins = static_cast<int>(fTransverseMassBinLowEdges.size()) + 1;

    // Other control histograms
    //hTauCandidateSelectionIsolatedPtMax = makeTH<TH1F>(*fs, "QCD_SelectedTauCandidateMaxIsolatedPt", "QCD_SelectedTauCandidateMaxIsolatedPt;Isol. track p_{T}, GeV/c; N_{jets} / 1 GeV/c", 100, 0., 100.);

    // Histograms for standard selections (i.e. big box)
    TFileDirectory myDir = fs->mkdir("QCDStandardSelections");
    hAfterTauCandidateSelection = makeTH<TH1F>(myDir, "AfterTauCandidateSelection", "AfterTauCandidateSelection;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterIsolatedElectronVeto = makeTH<TH1F>(myDir, "AfterIsolatedElectronVeto", "AfterIsolatedElectronVeto;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterIsolatedMuonVeto = makeTH<TH1F>(myDir, "AfterIsolatedMuonVeto", "AfterIsolatedMuonVeto;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterJetSelection = makeTH<TH1F>(myDir, "AfterJetSelection", "AfterJetSelection;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hFakeTauAfterTauCandidateSelection = makeTH<TH1F>(myDir, "FakeTauAfterTauCandidateSelection", "FakeTauAfterTauCandidateSelection;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hFakeTauAfterIsolatedElectronVeto = makeTH<TH1F>(myDir, "FakeTauAfterIsolatedElectronVeto", "FakeTauAfterIsolatedElectronVeto;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hFakeTauAfterIsolatedMuonVeto = makeTH<TH1F>(myDir, "FakeTauAfterIsolatedMuonVeto", "FakeTauAfterIsolatedMuonVeto;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hFakeTauAfterJetSelection = makeTH<TH1F>(myDir, "FakeTauAfterJetSelection", "FakeTauAfterJetSelection;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterTauCandidateSelectionAndTauID = makeTH<TH1F>(myDir, "AfterTauCandidateSelectionAndTauID", "AfterTauCandidateSelectionAndTauID;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterIsolatedElectronVetoAndTauID = makeTH<TH1F>(myDir, "AfterIsolatedElectronVetoAndTauID", "AfterIsolatedElectronVetoAndTauID;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterIsolatedMuonVetoAndTauID = makeTH<TH1F>(myDir, "AfterIsolatedMuonVetoAndTauID", "AfterIsolatedMuonVetoAndTauID;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);
    hAfterJetSelectionAndTauID = makeTH<TH1F>(myDir, "AfterJetSelectionAndTauID", "AfterJetSelectionAndTauID;tau p_{T} bin;N_{events}", myTauPtBins, 0., myTauPtBins);

    hMtAfterJetSelection = makeTH<TH2F>(myDir, "MtAfterJetSelection", "MtAfterJetSelection;tau p_{T} bin;transverse mass bin", myTauPtBins, 0., myTauPtBins, myTransverseMassBins, 0., myTransverseMassBins);
    
    hSelectionFlow = makeTH<TH1F>(myDir, "QCD_SelectionFlow", "QCD_SelectionFlow;;N_{events}", 12, 0, 12);
    hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderTrigger,"Trigger");
    //hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderVertexSelection,"Vertex");
    hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderTauCandidateSelection,"#tau candidate");
    hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderElectronVeto,"Isol. e veto");
    hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderMuonVeto,"Isol. #mu veto");
    hSelectionFlow->GetXaxis()->SetBinLabel(1+kQCDOrderJetSelection,"#geq 3 jets");

    // Analysis variations
    std::vector<double> myMETVariation;
    myMETVariation.push_back(40);
    myMETVariation.push_back(50);
    myMETVariation.push_back(60);
    myMETVariation.push_back(70);
    std::vector<double> myDeltaPhiTauMETVariation;
    myDeltaPhiTauMETVariation.push_back(90);
    myDeltaPhiTauMETVariation.push_back(130);
    //myDeltaPhiTauMETVariation.push_back(150);
    myDeltaPhiTauMETVariation.push_back(160);
    myDeltaPhiTauMETVariation.push_back(180);
    std::vector<int> myTauIsolVariation;
    myTauIsolVariation.push_back(1);
    //myTauIsolVariation.push_back(3);
    myTauIsolVariation.push_back(11);
    //myTauIsolVariation.push_back(21);
    for (size_t i = 0; i < myMETVariation.size(); ++i) {
      for (size_t j = 0; j < myDeltaPhiTauMETVariation.size(); ++j) {
        for (size_t k = 0; k < myTauIsolVariation.size(); ++k) {
          fAnalyses.push_back(AnalysisVariation(myMETVariation[i], myDeltaPhiTauMETVariation[j], myTauIsolVariation[k], myTauPtBins, myTransverseMassBins));
        }
      }
    }

    fTree.enableNonIsoLeptons(true);
    fTree.init(*fs);

   }

  QCDMeasurementBasic::~QCDMeasurementBasic() {}

  bool QCDMeasurementBasic::filter(edm::Event& iEvent, const edm::EventSetup& iSetup) {
    return analyze(iEvent, iSetup);
  }

  bool QCDMeasurementBasic::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
//------ Read the prescale for the event and set the event weight as the prescale
    fEventWeight.updatePrescale(iEvent);
    fTree.setPrescaleWeight(fEventWeight.getWeight());


//------ Vertex weight
    std::pair<double, size_t> weightSize = fVertexWeight.getWeightAndSize(iEvent, iSetup);
    if(!iEvent.isRealData()) {
      fEventWeight.multiplyWeight(weightSize.first);
      fTree.setPileupWeight(weightSize.first);
    }
    hVerticesBeforeWeight->Fill(weightSize.second);
    hVerticesAfterWeight->Fill(weightSize.second, fEventWeight.getWeight());
    fTree.setNvertices(weightSize.second);
    
    increment(fAllCounter);


//------ Apply trigger and HLT_MET cut or trigger parametrisation
    TriggerSelection::Data triggerData = fTriggerSelection.analyze(iEvent, iSetup);
    if (!triggerData.passedEvent()) return false;
    increment(fTriggerAndHLTMetCutCounter);
    hSelectionFlow->Fill(kQCDOrderTrigger, fEventWeight.getWeight());
    fTree.setHltTaus(triggerData.getTriggerTaus());

    hVerticesBeforeWeight->Fill(weightSize.second);
    hVerticesAfterWeight->Fill(weightSize.second, fEventWeight.getWeight());


//------ GenParticle analysis (must be done here when we effectively trigger all MC)
    if (!iEvent.isRealData()) {
      GenParticleAnalysis::Data genData = fGenparticleAnalysis.analyze(iEvent, iSetup);
      fTree.setGenMET(genData.getGenMET());
    }


//------ Primary vertex selection
    VertexSelection::Data pvData = fPrimaryVertexSelection.analyze(iEvent, iSetup);
    if (!pvData.passedEvent()) return false;
    increment(fPrimaryVertexCounter);
    //hSelectionFlow->Fill(kQCDOrderVertexSelection, fEventWeight.getWeight());
  
    
//------ Tau candidate selection
    // Store weight of event
    double myWeightBeforeTauID = fEventWeight.getWeight();
    // Do tau candidate selection
    TauSelection::Data tauCandidateData = fOneProngTauSelection.analyze(iEvent, iSetup);
    if (!tauCandidateData.passedEvent()) return false;
    // note: do not require here that only one tau has been found; instead take first item from mySelectedTau as the tau in the event
    increment(fOneProngTauSelectionCounter);
    // Apply trigger scale factor here, because it depends only on tau
    TriggerEfficiencyScaleFactor::Data triggerWeight = fTriggerEfficiencyScaleFactor.applyEventWeight(*(tauCandidateData.getCleanedTauCandidates()[0]), iEvent.isRealData());
    double myTauTriggerWeight = triggerWeight.getEventWeight();
    fTree.setTriggerWeight(triggerWeight.getEventWeight(), triggerWeight.getEventWeightAbsoluteUncertainty());
    increment(fOneSelectedTauCounter);
    hSelectionFlow->Fill(kQCDOrderTauCandidateSelection, fEventWeight.getWeight());
    // Obtain MC matching - for EWK without genuine taus
    FakeTauIdentifier::MCSelectedTauMatchType myTauMatch = fFakeTauIdentifier.matchTauToMC(iEvent, *(tauCandidateData.getCleanedTauCandidates()[0]));
    bool myTypeIIStatus = fFakeTauIdentifier.isFakeTau(myTauMatch); // True if the selected tau is a fake
    // Obtain tau pT bin index
    int myTauPtBinIndex = getTauPtBinIndex(tauCandidateData.getCleanedTauCandidates()[0]->pt());
    hAfterTauCandidateSelection->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    if (myTypeIIStatus) hFakeTauAfterTauCandidateSelection->Fill(myTauPtBinIndex, fEventWeight.getWeight());

    // Obtain boolean for rest of tauID
    TauSelection::Data tauIDData = fOneProngTauSelection.analyzeTauIDWithoutRtauOnCleanedTauCandidates(iEvent, iSetup, tauCandidateData.getCleanedTauCandidates()[0]);
    bool myPassedTauIDStatus = tauIDData.passedEvent() && tauCandidateData.getBestTauCandidatePassedRtauStatus();
    // Control plot
    if (myPassedTauIDStatus) hAfterTauCandidateSelectionAndTauID->Fill(myTauPtBinIndex, fEventWeight.getWeight());


//------ Global electron veto
    GlobalElectronVeto::Data electronVetoData = fGlobalElectronVeto.analyze(iEvent, iSetup);
    if (!electronVetoData.passedEvent()) return false;
    increment(fGlobalElectronVetoCounter);
    hSelectionFlow->Fill(kQCDOrderElectronVeto, fEventWeight.getWeight());
    hAfterIsolatedElectronVeto->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    if (myTypeIIStatus) hFakeTauAfterIsolatedElectronVeto->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    /*NonIsolatedElectronVeto::Data nonIsolatedElectronVetoData = fNonIsolatedElectronVeto.analyze(iEvent, iSetup);
    if (!nonIsolatedElectronVetoData.passedEvent())  return false;
    increment(fNonIsolatedElectronVetoCounter);*/
    // Control plot
    if (myPassedTauIDStatus) hAfterIsolatedElectronVetoAndTauID->Fill(myTauPtBinIndex, fEventWeight.getWeight());


//------ Global muon veto
    GlobalMuonVeto::Data muonVetoData = fGlobalMuonVeto.analyze(iEvent, iSetup, pvData.getSelectedVertex());
    if (!muonVetoData.passedEvent()) return false;
    increment(fGlobalMuonVetoCounter);
    hSelectionFlow->Fill(kQCDOrderMuonVeto, fEventWeight.getWeight());
    hAfterIsolatedMuonVeto->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    if (myTypeIIStatus) hFakeTauAfterIsolatedMuonVeto->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    /*NonIsolatedMuonVeto::Data nonIsolatedMuonVetoData = fNonIsolatedMuonVeto.analyze(iEvent, iSetup, pvData.getSelectedVertex());
    if (!nonIsolatedMuonVetoData.passedEvent()) return; 
    increment(fNonIsolatedMuonVetoCounter);*/
    // Control plot
    if (myPassedTauIDStatus) hAfterIsolatedMuonVetoAndTauID->Fill(myTauPtBinIndex, fEventWeight.getWeight());


//------ Jet selection
    JetSelection::Data jetData = fJetSelection.analyze(iEvent, iSetup, tauCandidateData.getCleanedTauCandidates()[0]);
    if (!jetData.passedEvent()) return false;
    increment(fJetSelectionCounter);
    hSelectionFlow->Fill(kQCDOrderJetSelection, fEventWeight.getWeight());
    hAfterJetSelection->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    if (myTypeIIStatus) hFakeTauAfterJetSelection->Fill(myTauPtBinIndex, fEventWeight.getWeight());
    // Control plot
    if (myPassedTauIDStatus) hAfterJetSelectionAndTauID->Fill(myTauPtBinIndex, fEventWeight.getWeight());


//------ Standard selections is done, obtain data objects, fill tree, and loop over analysis variations
    // Obtain MET data
    METSelection::Data metData = fMETSelection.analyze(iEvent, iSetup);
    // Obtain btagging data
    BTagging::Data btagData = fBTagging.analyze(iEvent, iSetup, jetData.getSelectedJets());
    // Obtain alphaT
    EvtTopology::Data evtTopologyData = fEvtTopology.analyze(*(tauCandidateData.getCleanedTauCandidates()[0]), jetData.getSelectedJets());

    // Fill tree
    if(metData.getRawMET().isNonnull())
      fTree.setRawMET(metData.getRawMET());
    if(metData.getType1MET().isNonnull())
      fTree.setType1MET(metData.getType1MET());
    if(metData.getType2MET().isNonnull())
      fTree.setType2MET(metData.getType2MET());
    if(metData.getCaloMET().isNonnull())
      fTree.setCaloMET(metData.getCaloMET());
    if(metData.getTcMET().isNonnull())
      fTree.setTcMET(metData.getTcMET());
    fTree.setFillWeight(fEventWeight.getWeight());
    if (!iEvent.isRealData()) {
      fEventWeight.multiplyWeight(btagData.getScaleFactor()); // needed to calculate the scale factor and the uncertainties
    }
    fTree.setBTagging(btagData.passedEvent(), btagData.getScaleFactor(), btagData.getScaleFactorAbsoluteUncertainty());
    //fTree.setTop(TopSelectionData.getTopP4());
    //fTree.setAlphaT(evtTopologyData.alphaT().fAlphaT);
    //fTree.setDeltaPhi(fakeMETData.closestDeltaPhi());
    edm::PtrVector<pat::Tau> mySelectedTaus;
    mySelectedTaus.push_back(tauCandidateData.getCleanedTauCandidates()[0]);
    fTree.fill(iEvent, mySelectedTaus, jetData.getSelectedJets());

    // Uncertainties after standard selections
    fSFUncertaintyAfterStandardSelections.setScaleFactorUncertainties(fEventWeight.getWeight(),
                                                                      triggerWeight.getEventWeight(), triggerWeight.getEventWeightAbsoluteUncertainty(),
                                                                      1.0, 0.0); // these values are valid because btagging is not yet applied at this stage

    // Loop over analysis variations (that's where the rest of the tau pT spectrum plots and mT shapes are obtained ...)
    double transverseMass = TransverseMass::reconstruct(*(tauCandidateData.getCleanedTauCandidates()[0]), *(metData.getSelectedMET()));
    for(std::vector<AnalysisVariation>::iterator it = fAnalyses.begin(); it != fAnalyses.end(); ++it) {
      (*it).analyse(iEvent.isRealData(), electronVetoData.getSelectedElectronPtBeforePtCut(), muonVetoData.getSelectedMuonPtBeforePtCut(), jetData.getHadronicJetCount(),
                    metData, tauCandidateData, btagData, myTauPtBinIndex, myWeightBeforeTauID, triggerWeight, myTauMatch, getMtBinIndex(transverseMass));
    }

//------ End of QCD measurement
    return true;
  }

  // Returns index to tau pT bin; 0 is underflow and size() is highest bin
  int QCDMeasurementBasic::getTauPtBinIndex(double pt) {
    size_t mySize = fTauPtBinLowEdges.size();
    for (size_t i = 0; i < mySize; ++i) {
      if (pt < fTauPtBinLowEdges[i])
        return static_cast<int>(i);
    }
    return static_cast<int>(mySize);
  }
  
  int QCDMeasurementBasic::getMtBinIndex(double mt) {
    size_t mySize = fTransverseMassBinLowEdges.size();
    for (size_t i = 0; i < mySize; ++i) {
      if (mt < fTransverseMassBinLowEdges[i])
        return static_cast<int>(i);
    }
    return static_cast<int>(mySize);
  }
    
  // Analysis variations
  QCDMeasurementBasic::AnalysisVariation::AnalysisVariation(double METcut, double deltaPhiTauMETCut, int tauIsolation, int nTauPtBins, int nMtBins)
    : fMETCut(METcut),
      fDeltaPhiTauMETCut(deltaPhiTauMETCut),
      iTauIsolation(tauIsolation) {
    std::stringstream myName;
    myName << "QCDMeasurementVariation_METcut" << METcut << "_DeltaPhiTauMETCut" << deltaPhiTauMETCut << "_tauIsol" << tauIsolation;
    // Create histograms
    edm::Service<TFileService> fs;
    TFileDirectory myCtrlDir = fs->mkdir(myName.str()+"/ControlPlots");
    std::stringstream myLabel;
    for (int i = 0; i < nTauPtBins; ++i) {
      myLabel.str("");
      myLabel << "SelectedTau_pT_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauPtAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 80, 0.0, 400.0));
      myLabel.str("");
      myLabel << "SelectedTau_eta_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauEtaAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 60, -3.0, 3.0));
      myLabel.str("");
      myLabel << "SelectedTau_phi_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauPhiAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 360, -3.1415926, 3.1415926));
      myLabel.str("");
      myLabel << "SelectedTau_etavsphi_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauEtaVsPhiAfterStandardSelections.push_back(makeTH<TH2F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 60, -3.0, 3.0, 36, -3.1415926, 3.1415926));
      myLabel.str("");
      myLabel << "SelectedTau_LeadingTrackPt_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauLeadingTrkPtAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 80, 0.0, 400.0));
      myLabel.str("");
      myLabel << "SelectedTau_Rtau_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauRtauAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 120, 0., 1.2));
      myLabel.str("");
      myLabel << "SelectedTau_p_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauPAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 80, 0.0, 400.0));
      myLabel.str("");
      myLabel << "SelectedTau_LeadingTrackP_AfterStandardSelections_taupTbin" << i;
      hCtrlSelectedTauLeadingTrkPAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 80, 0.0, 400.0));
      myLabel.str("");
      myLabel << "IdentifiedElectronPt_AfterStandardSelections_taupTbin" << i;
      hCtrlIdentifiedElectronPtAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 20, 0., 20.));
      myLabel.str("");
      myLabel << "IdentifiedMuonPt_AfterStandardSelections_taupTbin" << i;
      hCtrlIdentifiedMuonPtAfterStandardSelections.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 20, 0., 20.));
      myLabel.str("");
      myLabel << "Njets_taupTbin" << i;
      hCtrlNjets.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 10, 0., 10.));
      myLabel.str("");
      myLabel << "MET_taupTbin" << i;
      hCtrlMET.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 100, 0., 500.));
      myLabel.str("");
      myLabel << "NBjets_taupTbin" << i;
      hCtrlNbjets.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 10, 0., 10.));
      myLabel.str("");
      myLabel << "DeltaPhi_taupTbin" << i;
      hCtrlDeltaPhi.push_back(makeTH<TH1F>(myCtrlDir, myLabel.str().c_str(), myLabel.str().c_str(), 36, 0., 180.));
    }

    TFileDirectory myDir = fs->mkdir(myName.str());
    /*hAfterTauCandidateSelection = makeTH<TH1F>(myDir, "AfterTauCandidateSelection", "AfterTauCandidateSelection", nTauPtBins, 0, nTauPtBins);
    hAfterElectronLeptonVeto= makeTH<TH1F>(myDir, "AfterElectronLeptonVeto", "AfterElectronLeptonVeto", nTauPtBins, 0, nTauPtBins);
    hAfterMuonLeptonVeto = makeTH<TH1F>(myDir, "AfterMuonLeptonVeto", "AfterMuonLeptonVeto", nTauPtBins, 0, nTauPtBins);
    hAfterJetSelection = makeTH<TH1F>(myDir, "AfterJetSelection", "AfterJetSelection", nTauPtBins, 0, nTauPtBins);*/
    hLeg1AfterMET = makeTH<TH1F>(myDir, "Leg1AfterMET", "Leg1AfterMET", nTauPtBins, 0, nTauPtBins);
    hLeg1AfterBTagging = makeTH<TH1F>(myDir, "Leg1AfterBTagging", "Leg1AfterBTagging", nTauPtBins, 0, nTauPtBins);
    hLeg1AfterDeltaPhiTauMET = makeTH<TH1F>(myDir, "Leg1AfterDeltaPhiTauMET", "Leg1AfterDeltaPhiTauMET", nTauPtBins, 0, nTauPtBins);
    fSFUncertaintyAfterMetLeg = new ScaleFactorUncertaintyManager("AfterMETLeg", myName.str());
    hLeg2AfterTauIDNoRtau = makeTH<TH1F>(myDir, "Leg2AfterTauIDNoRtau", "Leg2AfterTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    hLeg2AfterTauIDWithRtau = makeTH<TH1F>(myDir, "Leg2AfterTauIDWithRtau", "Leg2AfterTauIDWithRtau", nTauPtBins, 0, nTauPtBins);
    fSFUncertaintyAfterTauLeg = new ScaleFactorUncertaintyManager("AfterTauLeg", myName.str());
    hFakeTauLeg1AfterMET = makeTH<TH1F>(myDir, "FakeTauLeg1AfterMET", "FakeTauLeg1AfterMET", nTauPtBins, 0, nTauPtBins);
    hFakeTauLeg1AfterBTagging = makeTH<TH1F>(myDir, "FakeTauLeg1AfterBTagging", "FakeTauLeg1AfterBTagging", nTauPtBins, 0, nTauPtBins);
    hFakeTauLeg1AfterDeltaPhiTauMET = makeTH<TH1F>(myDir, "FakeTauLeg1AfterDeltaPhiTauMET", "FakeTauLeg1AfterDeltaPhiTauMET", nTauPtBins, 0, nTauPtBins);
    hFakeTauLeg2AfterTauIDNoRtau = makeTH<TH1F>(myDir, "FakeTauLeg2AfterTauIDNoRtau", "FakeTauLeg2AfterTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    hFakeTauLeg2AfterTauIDWithRtau = makeTH<TH1F>(myDir, "FakeTauLeg2AfterTauIDWithRtau", "FakeTauLeg2AfterTauIDWithRtau", nTauPtBins, 0, nTauPtBins);
    // Transverse mass histograms
    hMtLegAfterMET = makeTH<TH1F>(myDir, "MtLegAfterMET", "MtLegAfterMET", nTauPtBins, 0, nTauPtBins);
    hMtLegAfterDeltaPhiTauMET = makeTH<TH1F>(myDir, "MtLegAfterDeltaPhiTauMET", "MtLegAfterDeltaPhiTauMET", nTauPtBins, 0, nTauPtBins);
    fSFUncertaintyMtAfterMETAndDeltaPhi = new ScaleFactorUncertaintyManager("MtAfterMETAndDeltaPhi", myName.str());
    hMtLegAfterMETAndTauIDNoRtau = makeTH<TH1F>(myDir, "MtLegAfterTauIDNoRtau", "MtLegAfterTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    hMtLegAfterMETAndTauIDWithRtau = makeTH<TH1F>(myDir, "MtLegAfterTauIDWithRtau", "MtLegAfterTauIDWithRtau", nTauPtBins, 0, nTauPtBins);
    fSFUncertaintyMtAfterTauID = new ScaleFactorUncertaintyManager("MtAfterTauID", myName.str());
    hMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau = makeTH<TH1F>(myDir, "MtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau", "MtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    fSFUncertaintyMtAfterMETAndDeltaPhiAndInvertedTauID = new ScaleFactorUncertaintyManager("MtAfterMETAndDeltaPhiAndInvertedTauID", myName.str());
    hFakeTauMtLegAfterDeltaPhiTauMET = makeTH<TH1F>(myDir, "FakeTauMtLegAfterDeltaPhiTauMET", "FakeTauMtLegAfterDeltaPhiTauMET", nTauPtBins, 0, nTauPtBins);
    hFakeTauMtLegAfterMET = makeTH<TH1F>(myDir, "FakeTauMtLegAfterMET", "FakeTauMtLegAfterMET", nTauPtBins, 0, nTauPtBins);
    hFakeTauMtLegAfterMETAndTauIDNoRtau = makeTH<TH1F>(myDir, "FakeTauMtLegAfterTauIDNoRtau", "FakeTauMtLegAfterTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    hFakeTauMtLegAfterMETAndTauIDWithRtau = makeTH<TH1F>(myDir, "FakeTauMtLegAfterTauIDWithRtau", "MFakeTautLegAfterTauIDWithRtau", nTauPtBins, 0, nTauPtBins);
    hFakeTauMtLegAfterMETAndInvertedTauIDNoRtau = makeTH<TH1F>(myDir, "FakeTauMtLegAfterInvertedTauIDNoRtau", "FakeTauMtLegAfterInvertedTauIDNoRtau", nTauPtBins, 0, nTauPtBins);
    hFakeTauMtLegAfterMETAndInvertedTauIDWithRtau = makeTH<TH1F>(myDir, "FakeTauMtLegAfterInvertedTauIDWithRtau", "MFakeTautLegAfterInvertedTauIDWithRtau", nTauPtBins, 0, nTauPtBins);

    h2DMtLegAfterDeltaPhiTauMET = makeTH<TH2F>(myDir, "2DMtLegAfterDeltaPhiTauMET", "2DMtLegAfterDeltaPhiTauMET", nTauPtBins, 0, nTauPtBins, nMtBins, 0, nMtBins);
    h2DMtLegAfterMETAndTauIDNoRtau = makeTH<TH2F>(myDir, "hMtLegAfterMETAndTauIDNoRtau", "hMtLegAfterMETAndTauIDNoRtau", nTauPtBins, 0, nTauPtBins, nMtBins, 0, nMtBins);
    h2DMtLegAfterMETAndTauIDWithRtau = makeTH<TH2F>(myDir, "hMtLegAfterMETAndTauIDNoRtau", "hMtLegAfterMETAndTauIDNoRtau", nTauPtBins, 0, nTauPtBins, nMtBins, 0, nMtBins);
    h2DMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau = makeTH<TH2F>(myDir, "h2DMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau", "h2DMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau", nTauPtBins, 0, nTauPtBins, nMtBins, 0, nMtBins);

    for (int i = 0; i < nTauPtBins; ++i) {
      myName.str("");
      myName << "MtShapeAfterMETAndDeltaPhi_bin" << i;
      hMtShapesAfterMETAndDeltaPhi.push_back(makeTH<TH1F>(myDir, myName.str().c_str(), myName.str().c_str(), 20, 0, 400.));
      myName.str("");
      myName << "FakeTauMtShapeAfterMETAndDeltaPhi_bin" << i;
      hFakeTauMtShapesAfterMETAndDeltaPhi.push_back(makeTH<TH1F>(myDir, myName.str().c_str(), myName.str().c_str(), 20, 0, 400.));
      myName.str("");
      myName << "MtShapeAfterMETAndDeltaPhiAndInvertedTau_bin" << i; 
      hMtShapesAfterMETAndDeltaPhiAndInvertedTau.push_back(makeTH<TH1F>(myDir, myName.str().c_str(), myName.str().c_str(), 20, 0, 400.));
      myName.str("");
      myName << "FakeTauMtShapeAfterMETAndDeltaPhiAndInvertedTau_bin" << i;
      hFakeTauMtShapesAfterMETAndDeltaPhiAndInvertedTau.push_back(makeTH<TH1F>(myDir, myName.str().c_str(), myName.str().c_str(), 20, 0, 400.));
    }
  }
  
  QCDMeasurementBasic::AnalysisVariation::~AnalysisVariation() { }
  
  void QCDMeasurementBasic::AnalysisVariation::analyse(bool isRealData, const float maxElectronPt, const float maxMuonPt, const int njets, const HPlus::METSelection::Data& METData, const HPlus::TauSelection::Data& tauCandidateData, const HPlus::BTagging::Data& btagData, int tauPtBinIndex, double weightAfterVertexReweight, HPlus::TriggerEfficiencyScaleFactor::Data& trgEffData, HPlus::FakeTauIdentifier::MCSelectedTauMatchType tauMatch, double mTBinIndex) {
    // Make sure that event weight is 1 for real data
    double myBTagSF = 1.0;
    if (isRealData) {
      weightAfterVertexReweight = 1.0;
    } else {
      myBTagSF = btagData.getScaleFactor();
    }

    // Big box i.e. standard selections have been passed, now look at the rest of the selections
    bool myFakeTauStatus = !(tauMatch == FakeTauIdentifier::kkTauToTau || tauMatch == FakeTauIdentifier::kkTauToTauAndTauOutsideAcceptance);
    double myDeltaPhi = DeltaPhi::reconstruct(*(tauCandidateData.getCleanedTauCandidates()[0]), *(METData.getSelectedMET())) * 57.29578; // converted to degrees
    double transverseMass = TransverseMass::reconstruct(*(tauCandidateData.getCleanedTauCandidates()[0]), *(METData.getSelectedMET()));
    
    // Obtain boolean for tau isolation and inverted isolation
    bool myPassedTauIsol = false;
    if (iTauIsolation == 1 || iTauIsolation == 3) // Tight isolation + 1/3 prong
      myPassedTauIsol = tauCandidateData.applyDiscriminatorOnBestTauCandidate("byTightIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    else if (iTauIsolation == 11 || iTauIsolation == 13) // Medium isolation + 1/3 prong
      myPassedTauIsol = tauCandidateData.applyDiscriminatorOnBestTauCandidate("byMediumIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    else if (iTauIsolation == 21 || iTauIsolation == 23) // Loose isolation + 1/3 prong
      myPassedTauIsol = tauCandidateData.applyDiscriminatorOnBestTauCandidate("byLooseIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    // inverted tau isolation and prongs (assuming HPS tau)
    bool myPassedInvertedTauIsol = false;
    if (iTauIsolation == 1 || iTauIsolation == 3) // Tight isolation + 1/3 prong
      myPassedInvertedTauIsol = !tauCandidateData.applyDiscriminatorOnBestTauCandidate("byTightIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    else if (iTauIsolation == 11 || iTauIsolation == 13) // Medium isolation + 1/3 prong
      myPassedInvertedTauIsol = !tauCandidateData.applyDiscriminatorOnBestTauCandidate("byMediumIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    else if (iTauIsolation == 21 || iTauIsolation == 23) // Loose isolation + 1/3 prong
      myPassedInvertedTauIsol = !tauCandidateData.applyDiscriminatorOnBestTauCandidate("byLooseIsolation") &&
        tauCandidateData.getBestTauCandidateProngCount() == iTauIsolation;
    bool myPassedRtau = tauCandidateData.getBestTauCandidatePassedRtauStatus();

    // Fill control plots here for point "standard selections with full tauID"
    hCtrlSelectedTauRtauAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getRtauOfBestTauCandidate(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauLeadingTrkPtAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->leadPFChargedHadrCand()->pt(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauPtAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->pt(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauEtaAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->eta(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauPhiAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->phi()*180.0/3.1415926, weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauEtaVsPhiAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->eta(), tauCandidateData.getCleanedTauCandidates()[0]->phi()*180.0/3.1415926, weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauPAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->p(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlSelectedTauLeadingTrkPAfterStandardSelections[tauPtBinIndex]->Fill(tauCandidateData.getCleanedTauCandidates()[0]->leadPFChargedHadrCand()->p(), weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlIdentifiedElectronPtAfterStandardSelections[tauPtBinIndex]->Fill(maxElectronPt, weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlIdentifiedMuonPtAfterStandardSelections[tauPtBinIndex]->Fill(maxMuonPt, weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlNjets[tauPtBinIndex]->Fill(njets, weightAfterVertexReweight*trgEffData.getEventWeight());
    hCtrlMET[tauPtBinIndex]->Fill(METData.getSelectedMET()->et(), weightAfterVertexReweight*trgEffData.getEventWeight());
    // MET leg ---------------------------------------------------------------
    // MET cut
    if (METData.getSelectedMET()->et() > fMETCut) {
      hLeg1AfterMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      if (myFakeTauStatus) hFakeTauLeg1AfterMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      hCtrlNbjets[tauPtBinIndex]->Fill(btagData.getBJetCount(), weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
      // btagging
      if (btagData.passedEvent()) {
        hLeg1AfterBTagging->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
        if (myFakeTauStatus) hFakeTauLeg1AfterBTagging->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
        // DeltaPhi(tau,MET) cut
        hCtrlDeltaPhi[tauPtBinIndex]->Fill(myDeltaPhi, weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
        if (myDeltaPhi < fDeltaPhiTauMETCut) {
          hLeg1AfterDeltaPhiTauMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
          if (myFakeTauStatus) hFakeTauLeg1AfterDeltaPhiTauMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF);
          fSFUncertaintyAfterMetLeg->setScaleFactorUncertainties(weightAfterVertexReweight*trgEffData.getEventWeight()*myBTagSF,
                                                                 trgEffData.getEventWeight(), trgEffData.getEventWeightAbsoluteUncertainty(),
                                                                 btagData.getScaleFactor(), btagData.getScaleFactorAbsoluteUncertainty());
        }
      }
    }
    
    // tau leg ---------------------------------------------------------------
    // tau isolation and prongs (assuming HPS tau)
    if (myPassedTauIsol) {
      hLeg2AfterTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      if (myFakeTauStatus) hFakeTauLeg2AfterTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      // Rtau
      if (myPassedRtau) {
        hLeg2AfterTauIDWithRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        if (myFakeTauStatus) hFakeTauLeg2AfterTauIDWithRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        fSFUncertaintyAfterTauLeg->setScaleFactorUncertainties(weightAfterVertexReweight*trgEffData.getEventWeight(),
                                                               trgEffData.getEventWeight(), trgEffData.getEventWeightAbsoluteUncertainty(),
                                                               1.0, 0.0);
      }
    }

    // mT shape and normalisation --------------------------------------------
    // MET cut
    if (METData.getSelectedMET()->et() > fMETCut) {
      hMtLegAfterMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      if (myFakeTauStatus) hFakeTauMtLegAfterMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      // DeltaPhi(tau,MET) cut
      if (myDeltaPhi < fDeltaPhiTauMETCut) {
        hMtLegAfterDeltaPhiTauMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        if (myFakeTauStatus) hFakeTauMtLegAfterDeltaPhiTauMET->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        h2DMtLegAfterDeltaPhiTauMET->Fill(tauPtBinIndex, mTBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        // Obtain mT shape
        hMtShapesAfterMETAndDeltaPhi[tauPtBinIndex]->Fill(transverseMass, weightAfterVertexReweight*trgEffData.getEventWeight());
        if (myFakeTauStatus) hFakeTauMtShapesAfterMETAndDeltaPhi[tauPtBinIndex]->Fill(transverseMass, weightAfterVertexReweight*trgEffData.getEventWeight());
        fSFUncertaintyMtAfterMETAndDeltaPhi->setScaleFactorUncertainties(weightAfterVertexReweight*trgEffData.getEventWeight(),
                                                                         trgEffData.getEventWeight(), trgEffData.getEventWeightAbsoluteUncertainty(),
                                                                         1.0, 0.0);
        // Obtain mT shape for inverted tau isolation
        if (myPassedInvertedTauIsol) {
          hMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
          if (myFakeTauStatus) hFakeTauMtLegAfterMETAndInvertedTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
          hMtShapesAfterMETAndDeltaPhiAndInvertedTau[tauPtBinIndex]->Fill(transverseMass, weightAfterVertexReweight*trgEffData.getEventWeight());
          if (myFakeTauStatus) hFakeTauMtShapesAfterMETAndDeltaPhiAndInvertedTau[tauPtBinIndex]->Fill(transverseMass, weightAfterVertexReweight*trgEffData.getEventWeight());
          h2DMtLegAfterMETAndDeltaPhiAndInvertedTauIDNoRtau->Fill(tauPtBinIndex, mTBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
          fSFUncertaintyMtAfterMETAndDeltaPhiAndInvertedTauID->setScaleFactorUncertainties(weightAfterVertexReweight*trgEffData.getEventWeight(),
                                                                                           trgEffData.getEventWeight(), trgEffData.getEventWeightAbsoluteUncertainty(),
                                                                                           1.0, 0.0);
        }
      }
    }
    // Obtain normalisation from tau leg after standard selections
    if (myPassedTauIsol) {
      hMtLegAfterMETAndTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      if (myFakeTauStatus) hFakeTauMtLegAfterMETAndTauIDNoRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      h2DMtLegAfterMETAndTauIDNoRtau->Fill(tauPtBinIndex, mTBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
      // Rtau
      if (myPassedRtau) {
        hMtLegAfterMETAndTauIDWithRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        if (myFakeTauStatus) hFakeTauMtLegAfterMETAndTauIDWithRtau->Fill(tauPtBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        h2DMtLegAfterMETAndTauIDWithRtau->Fill(tauPtBinIndex, mTBinIndex, weightAfterVertexReweight*trgEffData.getEventWeight());
        fSFUncertaintyMtAfterTauID->setScaleFactorUncertainties(weightAfterVertexReweight*trgEffData.getEventWeight(),
                                                                trgEffData.getEventWeight(), trgEffData.getEventWeightAbsoluteUncertainty(),
                                                                1.0, 0.0);
      }
    }
  }

}

