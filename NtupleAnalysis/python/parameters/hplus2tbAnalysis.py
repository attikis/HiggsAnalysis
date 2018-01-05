#!/usr/bin/env python

from HiggsAnalysis.NtupleAnalysis.main import PSet
import HiggsAnalysis.NtupleAnalysis.parameters.scaleFactors as scaleFactors

#================================================================================================
# General parameters
#================================================================================================
verbose               = True
histogramAmbientLevel = "Debug"  # Options: Systematics, Vital, Informative, Debug

#================================================================================================
# Trigger
#================================================================================================
trigger = PSet(
    triggerOR = [
        "HLT_PFHT400_SixJet30_DoubleBTagCSV_p056", # scanned in range _v1--_v100 (=>remove the '_v' suffix)
        "HLT_PFHT450_SixJet40_BTagCSV_p056",       # scanned in range _v1--_v100 (=>remove the '_v' suffix)
        "HLT_PFJet450", # for trg eff recovery in 2016H
        #"HLT_PFHT400_SixJet30", #Prescale 110 at inst. lumi 1.35E+34
        #"HLT_PFHT450_SixJet40", #Prescale 26 at inst. lumi 1.35E+34
        ],
    triggerOR2 = [],
    )


#================================================================================================
# Tau selection (sync with HToTauNu analysis)
#================================================================================================
tauSelection = PSet(
    applyTriggerMatching = False,
    triggerMatchingCone  =   0.1, # DeltaR for matching offline tau with trigger tau
    tauPtCut             =  20.0, #
    tauEtaCut            =   2.3, #
    tauLdgTrkPtCut       =   0.0, #
    prongs               =  -1,   # options: 1, 2, 3, 12, 13, 23, 123 or -1 (all)
    rtau                 =   0.0, # to disable set to 0.0
    againstElectronDiscr = "againstElectronTightMVA6",
    againstMuonDiscr     = "againstMuonLoose3",
    isolationDiscr       = "byLooseCombinedIsolationDeltaBetaCorr3Hits",
    )

#================================================================================================
# MET filter
#================================================================================================
metFilter = PSet(
    discriminators = [
        "hbheNoiseTokenRun2Loose", # Loose is recommended
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_CSCTightHaloFilter",
        "Flag_eeBadScFilter",
        "Flag_goodVertices"]
    )

#================================================================================================
# Electron veto
#================================================================================================
eVeto = PSet(
    electronPtCut     = 15.0,
    electronEtaCut    = 2.5,
    electronID        = "cutBasedElectronID_Spring15_25ns_V1_standalone_veto",
    electronIsolation = "veto", # loosest possible for vetoing ("veto"), "tight" for selecting
    )

#================================================================================================
# Muon veto
#================================================================================================
muVeto = PSet(
    muonPtCut         = 10.0,
    muonEtaCut        = 2.5,
    muonID            = "muIDLoose", # loosest option for vetoing (options: muIDLoose, muIDMedium, muIDTight)
    muonIsolation     = "veto",      # loosest possible for vetoing ("veto"), "tight" for selecting
)

#================================================================================================
# Jet selection
#================================================================================================
jetSelection = PSet(
    jetType                  = "Jets",    # options: Jets (AK4PFCHS), JetsPuppi (AK4Puppi)
    jetPtCuts                = [40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 30.0],
#    jetPtCuts                = [30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0],  #test for topSelection
    jetEtaCuts               = [2.4],
    numberOfJetsCutValue     = 7,
    numberOfJetsCutDirection = ">=",      # options: ==, !=, <, <=, >, >=
    jetIDDiscr               = "IDloose", # options: IDloose, IDtight, IDtightLeptonVeto
    jetPUIDDiscr             = "",        # does not work at the moment 
    tauMatchingDeltaR        = 0.4,
    HTCutValue               = 500.0,
    HTCutDirection           = ">=",
    JTCutValue               = 0.0,
    JTCutDirection           = ">=",
    MHTCutValue              = 0.0,
    MHTCutDirection          = ">=",
)

#================================================================================================
# B-jet selection
#================================================================================================
bjetSelection = PSet(
    triggerMatchingApply      = False,
    triggerMatchingCone       = 0.1,  # DeltaR for matching offline bjet with trigger::TriggerBjet
    jetPtCuts                 = [40.0, 40.0, 30.0],
    jetEtaCuts                = [2.4],
    bjetDiscr                 = "pfCombinedInclusiveSecondaryVertexV2BJetTags",
    bjetDiscrWorkingPoint     = "Medium",
    numberOfBJetsCutValue     = 3,
    numberOfBJetsCutDirection = ">=", # options: ==, !=, <, <=, >, >=
)

#================================================================================================
# Scale Factors
#================================================================================================
scaleFactors.setupBtagSFInformation(btagPset               = bjetSelection, 
                                    btagPayloadFilename    = "CSVv2.csv",
                                    #btagEfficiencyFilename = "btageff_hybrid_HToTB.json",
                                    btagEfficiencyFilename = "btageff_HToTB.json",
                                    direction              = "nominal")

#================================================================================================
# MET selection
#================================================================================================
metSelection = PSet(
    METCutValue                 = -1000.0,
    METCutDirection             = ">",         # options: ==, !=, <, <=, >, >=
    METSignificanceCutValue     = -1000.0,
    METSignificanceCutDirection = ">",         # options: ==, !=, <, <=, >, >=
    METType                     = "MET_Type1", # options: MET_Type1, MET_Type1_NoHF, MET_Puppi, GenMET, L1MET, HLTMET, CaloMET
    applyPhiCorrections          = False
    )

#================================================================================================
# Topology selection
#================================================================================================
topologySelection = PSet(
    SphericityCutValue           = 100.0,   # 0.0 <= S <= 1.0
    SphericityCutDirection       = "<=",    # options: ==, !=, <, <=, >, >=
    AplanarityCutValue           = 100.0,   # 0.0 <= A <= 0.5
    AplanarityCutDirection       = "<=",  
    PlanarityCutValue            = 100.0,   # 0.0 <= P <= 0.5
    PlanarityCutDirection        = "<=",  
    CircularityCutValue          = 100.0,   # 0.0 <= C <= 0.5
    CircularityCutDirection      = "<=",  
    Y23CutValue                  = 100.0,   # 0.0 <= y23 <= 0.25
    Y23CutDirection              = "<=",  
    CparameterCutValue           = 100.0,   # 0.0 <= C <= 1.0
    CparameterCutDirection       = "<=", 
    DparameterCutValue           = 100.0,   # 0.0 <= D <= 1.0
    DparameterCutDirection       = "<=",  
    FoxWolframMomentCutValue     = 100.0,   # 0.0 <= H2 <= 1.0
    FoxWolframMomentCutDirection = "<=", 
    AlphaTCutValue               = 1000.0,  # 0.0 <= alphaT ~ 2.0 (alphaT->0.5 for perfectly balanced events)
    AlphaTCutDirection           = "<=", 
    CentralityCutValue           = 100.0,   # 0.0 <= Centrality ~ 1.0
    CentralityCutDirection       = "<=",
)

#================================================================================================
# Top selection BDT                                               
#================================================================================================        
topSelectionBDT = PSet(
    LdgMVACutValue         = 0.8,     # [default: 0.9]
    LdgMVACutDirection     =  ">=",   # [default: ">="]
    SubldgMVACutValue      = 0.8,     # [default: 0.9]
    SubldgMVACutDirection  =  ">=",   # [default: ">="]
    NjetsMax               = 999,     # [default: 999]
    NBjetsMax              = 999,     # [default: 999]
    # Speed-up calculation by skipping top candidates failing some criteria
    CSV_bDiscCutValue      = 0.5426,  # [default: 0.8484] #Do not evaluate top candidate if b-jet assigned as b from top fails this cut
    CSV_bDiscCutDirection  = ">=",    # [default: ">="]
    MassCutValue           = 600.0,   # [default: 400.0]
    MassCutDirection       = "<=",    # [default: "<"]
    # FIXME: Phase this out (currently only used in plots)
    MVACutValue            = 0.8,     # [default: 0.9]
    MVACutDirection        =  ">=",   # [default: ">="]
)

#================================================================================================
# FakeB Measurement Options
#================================================================================================
fakeBMeasurement = PSet(
    prelimTopMVACutValue              = 0.4,      # [default: 0.4]
    prelimTopMVACutDirection          =  ">=",    # [default: ">="]
    # CSVv2-Medium requirements (Baseline b-jets)
    numberOfBJetsCutValue             = 2,        # [default: 2]
    numberOfBJetsCutDirection         = "==",     # [default: "=="]
    # CSVv2-Loose requirements (Inverted b-jets)
    numberOfInvertedBJetsCutValue     = 1,        # [default: 1]
    numberOfInvertedBJetsCutDirection = ">=",     # [default: ">="]
    invertedBJetsDiscr                = bjetSelection.bjetDiscr,
    invertedBJetsDiscrMaxCutValue     = 0.8,      # [default: 0.7]
    invertedBJetsDiscrMaxCutDirection = "<=",     # [default: "<="]
    invertedBJetsWorkingPoint         = "Loose",  # [default: "Loose"]
    # Does this make any difference?
    invertedBJetsSortType             = "Random", # [default: "Random"] ("AscendingPt", "DescendingPt", "AscendingBDiscriminator", "DescendingBDiscriminator", "Random")
    # NOTE: Do I need new entries to also invert BDT2?
    )


#================================================================================================
# Common plots options
#================================================================================================
commonPlotsOptions = PSet(
    histogramSplitting         = [],    # Splitting of histograms as function of one or more parameters
    enableGenuineBHistograms   = False,
    enablePUDependencyPlots    = True,  # Enable/Disable some debug-level plots
    # Bin settings (final bin setting done in datacardGenerator, there also variable bin width is supported)
    nVerticesBins     = PSet(nBins = 100, axisMin =  0.0, axisMax =  100.0),
    ptBins            = PSet(nBins =  50, axisMin =  0.0, axisMax =  500.0),
    etaBins           = PSet(nBins =  50, axisMin = -5.0, axisMax =    5.0),
    phiBins           = PSet(nBins =  64, axisMin = -3.2, axisMax =    3.2),
    deltaEtaBins      = PSet(nBins = 100, axisMin =  0.0, axisMax =   10.0),
    deltaPhiBins      = PSet(nBins =  32, axisMin =  0.0, axisMax =    3.2),
    deltaRBins        = PSet(nBins =  50, axisMin =  0.0, axisMax =   10.0),
    rtauBins          = PSet(nBins =  55, axisMin =  0.0, axisMax =    1.1), # HToTauNu
    njetsBins         = PSet(nBins =  18, axisMin =  0.0, axisMax =   18.0),
    metBins           = PSet(nBins =  80, axisMin =  0.0, axisMax =  400.0), #  5 GeV bin width
    htBins            = PSet(nBins = 500, axisMin =  0.0, axisMax = 5000.0), # 10 GeV bin width 
    bjetDiscrBins     = PSet(nBins = 120, axisMin =  0.0, axisMax =    1.2),
    angularCuts1DBins = PSet(nBins =  52, axisMin =  0.0, axisMax =  260.0), 
    topMassBins       = PSet(nBins = 300, axisMin =  0.0, axisMax = 1500.0), # 5 GeV bin width 
    wMassBins         = PSet(nBins = 200, axisMin =  0.0, axisMax = 1000.0), # 5 GeV bin width 
    mtBins            = PSet(nBins = 800, axisMin =  0.0, axisMax = 4000.0), # 5 GeV bin width
    invMassBins       = PSet(nBins = 800, axisMin =  0.0, axisMax = 4000.0), # 5 GeV bin width    
)

#================================================================================================
# Build all selections group
#================================================================================================
allSelections = PSet(
    BJetSelection         = bjetSelection,
    CommonPlots           = commonPlotsOptions,
    ElectronSelection     = eVeto,
    HistogramAmbientLevel = histogramAmbientLevel,
    JetSelection          = jetSelection,
    TauSelection          = tauSelection,
    METFilter             = metFilter,
    METSelection          = metSelection,
    TopologySelection     = topologySelection,
    TopSelectionBDT       = topSelectionBDT,
    MuonSelection         = muVeto,
    Trigger               = trigger,
    Verbose               = verbose,
    FakeBMeasurement      = fakeBMeasurement,
)
