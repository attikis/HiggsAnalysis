#!/usr/bin/env python

from HiggsAnalysis.NtupleAnalysis.main import PSet
import HiggsAnalysis.NtupleAnalysis.parameters.scaleFactors as scaleFactors
import HiggsAnalysis.NtupleAnalysis.parameters.jsonReader as jsonReader

#================================================================================================
# General parameters
#================================================================================================
verbose               = True
histogramAmbientLevel = "Debug"  # (options: "Systematics", "Vital", "Informative", "Debug")

#================================================================================================
# Trigger [scanned in range _v1--_v100 (=>remove the '_v' suffix)]
#================================================================================================
trigger = PSet(
    triggerOR = [
        "HLT_PFHT400_SixJet30_DoubleBTagCSV_p056",
        "HLT_PFHT450_SixJet40_BTagCSV_p056",       
        "HLT_PFJet450", #for trg eff recovery in 2016H
        ],
    triggerOR2 = [],
    )

#================================================================================================
# MET filter
#================================================================================================
metFilter = PSet(
    discriminators = [
        "Flag_HBHENoiseFilter",
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_eeBadScFilter",
        "Flag_goodVertices",
        "Flag_globalTightHalo2016Filter",
        "badPFMuonFilter",
        "badChargedCandidateFilter"]
    )

#================================================================================================
# Electron veto
#================================================================================================
eVeto = PSet(
    electronPtCut     = 10.0,    # [default: 10.0]
    electronEtaCut    = 2.4,     # [default: 2.4]
    electronIDType    = "MVA",   # [default: "MVA] (options: "default", "MVA")
    electronID        = "cutBasedElectronID_Spring15_25ns_V1_standalone_veto",
    electronMVA       = "ElectronMVAEstimatorRun2Spring16GeneralPurposeV1Values",
    electronMVACut    = "Loose", # [default: "Loose"]
    electronIsolation = "veto",  # [default: "veto"] (options: "veto", "tight")
    electronIsolType  = "mini",  # [default: "mini"] (options: "mini", "default")
    )

#================================================================================================
# Muon veto
#================================================================================================
muVeto = PSet(
    muonPtCut         = 10.0,        # [default: 10.0]
    muonEtaCut        = 2.4,         # [default: 2.4]
    muonID            = "muIDLoose", # [default: "muIDLoose"] (options: "muIDLoose", "muIDMedium", "muIDTight")
    muonIsolation     = "veto",      # [default: "veto"] (options: "veto", "tight")
    muonIsolType      = "mini",      # [default: "mini"] (options: "mini", "default")
)

#================================================================================================
# Tau selection (sync with HToTauNu analysis)
#================================================================================================
tauVeto = PSet(
    applyTriggerMatching = False, # [default: False]
    triggerMatchingCone  =   0.1, # [default: False]
    tauPtCut             =  20.0, # [default: 20.0]
    tauEtaCut            =   2.3, # [default: 2.3]
    tauLdgTrkPtCut       =   0.0, # [default: 0.0]
    prongs               =  -1,   # [default: -1] (options: 1, 2, 3, 12, 13, 23, 123 or -1 (all))
    rtau                 =   0.0, # [default: 0.0] (to disable set to 0.0)
    againstElectronDiscr = "againstElectronTightMVA6",
    againstMuonDiscr     = "againstMuonLoose3",
    isolationDiscr       = "byLooseCombinedIsolationDeltaBetaCorr3Hits", # [higher signal efficiency]
    # isolationDiscr       = "byVLooseIsolationMVArun2v1DBoldDMwLT", # [boosted analysis]
    )

#================================================================================================
# Jet selection
#================================================================================================
jetSelection = PSet(
    jetType                  = "Jets",    # [default: "jets"] (options: "Jets" (AK4PFCHS), "JetsPuppi" (AK4Puppi))
    jetPtCuts                = [40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 30.0],
    jetEtaCuts               = [2.4],     # [default: [2.4]]
    numberOfJetsCutValue     = 7,         # [default: 7]
    numberOfJetsCutDirection = ">=",      # [default: ">="] (options: ==, !=, <, <=, >, >=)
    jetIDDiscr               = "IDloose", # [default: "IDloose"] (options: IDloose, IDtight, IDtightLeptonVeto)
    jetPUIDDiscr             = "",        # [default: ""]
    tauMatchingDeltaR        = 0.4,       # [default: 0.4] (does nothing for h2tb)
    HTCutValue               = 500.0,     # [default: 500.0]
    HTCutDirection           = ">=",      # [default: ">="]
    JTCutValue               = 0.0,       # [default: 0.0]
    JTCutDirection           = ">=",      # [default: ">="]
    MHTCutValue              = 0.0,       # [default: 0.0]
    MHTCutDirection          = ">=",      # [default: ">="]
)

#================================================================================================
# B-jet selection
#================================================================================================
bjetSelection = PSet(
    triggerMatchingApply      = False,    # [default: False]
    triggerMatchingCone       = 0.1,      # [default: 0.1 ] (DR for matching offline bjet with trigger::TriggerBjet)
    jetPtCuts                 = [40.0],   # [default: [40.0, 40.0, 30.0]]
    jetEtaCuts                = [2.4],    # [default: [2.4]]
    bjetDiscr                 = "pfCombinedInclusiveSecondaryVertexV2BJetTags", # default
    #bjetDiscr                 = "pfCombinedMVAV2BJetTags", # MVA b-tagging (not default)
    bjetDiscrWorkingPoint     = "Medium", # [default: "Medium"] (options: "Medium", "Tight")
    numberOfBJetsCutValue     = 3,        # [default: 3]
    numberOfBJetsCutDirection = ">=",     # [default: ">="] (options: ==, !=, <, <=, >, >=)
)

#=================================================================================================
# Fat jet selection
#=================================================================================================
fatjetVeto = PSet(
    fatjetType                  = "FatJets", # [default: "FatJets"]  
    fatjetPtCuts                = [450.0],   # [default: [450.0] ]
    fatjetEtaCuts               = [2.4],     # [default: [2.4] ]
    fatjetIDDiscr               = "IDloose", # [default: "IDLoose"] (options: IDloose, IDtight, IDtightLeptonVeto)
    fatjetPUIDDiscr             = "",        # [default: ""]
    topMatchDeltaR              = 0.8,       # [default: 0.8]
    topMatchTypes               = [1],       # [default: 1]   (options: kJJB=1, kJJ=2, kJB=3, kJJBorJJ=4, kJJBorJB=5, kJJorJB=6, kAll=7, any = -1)
    numberOfFatJetsCutValue     = 0,         # [default: 0]
    numberOfFatJetsCutDirection = ">=",      # [default: "=="] (TO DISABLE: >=0)
)

#================================================================================================
# MET selection
#================================================================================================
metSelection = PSet(
    METCutValue                 = -1000.0,     #
    METCutDirection             = ">",         # (options: ==, !=, <, <=, >, >=)
    METSignificanceCutValue     = -1000.0,     # 
    METSignificanceCutDirection = ">",         # (options: ==, !=, <, <=, >, >=)
    METType                     = "MET_Type1", # (options: MET_Type1, MET_Type1_NoHF, MET_Puppi, GenMET, L1MET, HLTMET, CaloMET)
    applyPhiCorrections          = False       # 
    )

#================================================================================================
# Top selection BDT                                               
#================================================================================================        
topSelectionBDT = PSet(
    AnyTopMVACutValue      = -0.95,   # [default: -1.0] NOTE: Defines StandardSelections
    AnyTopMVACutDirection  =  ">",    # [default: ">"]
    TopMVACutValue         =  0.40,   # [default: 0.40] NOTE: Only use numbers with 2 decimals (e.g 0.40, 0.30, 0.00)
    TopMVACutDirection     =  ">=",   # [default: ">="]
    TopMassLowCutValue     =   0.0,   # [default: 0.0]
    TopMassLowCutDirection =  ">=",   # [default: ">="]
    TopMassUppCutValue     =  400.0,  # [default: 400.0]  # Do not evaluate top candidate if top mass greater than this cut (600 takes TOO long!)
    TopMassUppCutDirection =  "<=",   # [default: "<"]
    CSV_bDiscCutValue      = 0.8484,  # [default: 0.8484] # Do not evaluate top candidate if b-jet assigned as b from top fails this cut
    CSV_bDiscCutDirection  = ">=",    # [default: ">="]
    WeightFile             = "BDTG_DeltaR0p3_DeltaPtOverPt0p32_BJetPt40_14July2018.weight.xml", # (All XML files located in data/TopTaggerWeights/)
)


#================================================================================================
# FakeB Measurement Options
#================================================================================================
fakeBBjetSelection = PSet(
    triggerMatchingApply      = bjetSelection.triggerMatchingApply,
    triggerMatchingCone       = bjetSelection.triggerMatchingCone,
    jetPtCuts                 = bjetSelection.jetPtCuts,
    jetEtaCuts                = bjetSelection.jetEtaCuts,
    bjetDiscr                 = bjetSelection.bjetDiscr,    
    bjetDiscrWorkingPoint     = "Loose", # NOTE: Defines VR and CR2
    numberOfBJetsCutValue     = bjetSelection.numberOfBJetsCutValue,
    numberOfBJetsCutDirection = bjetSelection.numberOfBJetsCutDirection,
    )
scaleFactors.setupBtagSFInformation(btagPset               = fakeBBjetSelection, 
                                    btagPayloadFilename    = "CSVv2.csv",
                                    btagEfficiencyFilename = "btageff_HToTB.json",
                                    direction              = "nominal")

fakeBMeasurement = PSet(
    # b-jets
    baselineBJetsCutValue          = 2,
    baselineBJetsCutDirection      = "==",
    baselineBJetsDiscr             = bjetSelection.bjetDiscr,
    baselineBJetsDiscrWP           = bjetSelection.bjetDiscrWorkingPoint,
    # Tops
    LdgTopMVACutValue              = topSelectionBDT.TopMVACutValue,
    LdgTopMVACutDirection          = topSelectionBDT.TopMVACutDirection, 
    SubldgTopMVACutValue           = topSelectionBDT.TopMVACutValue,
    SubldgTopMVACutDirection       = "<",
    )

#================================================================================================
# Scale Factors (SFs)
#================================================================================================
if bjetSelection.bjetDiscr == "pfCombinedInclusiveSecondaryVertexV2BJetTags":
    scaleFactors.setupBtagSFInformation(btagPset               = bjetSelection, 
                                        btagPayloadFilename    = "CSVv2.csv",
                                        #btagEfficiencyFilename = "btageff_hybrid_HToTB.json",
                                        btagEfficiencyFilename = "btageff_HToTB.json",
                                        direction              = "nominal")
elif bjetSelection.bjetDiscr == "pfCombinedMVAV2BJetTags":
    scaleFactors.setupBtagSFInformation(btagPset               = bjetSelection, 
                                        btagPayloadFilename    = "cMVAv2_Moriond17_B_H.csv", # use this for MVA b-tagging
                                        btagEfficiencyFilename = "btageff_Hybrid_TT+WJetsHT.json", # use with taunu analysis and WJetsHT samples
                                        direction              = "nominal")
else:
    raise Exception("This should never be reached!")

# top-tagging (json files available for: defaut, fatJet, ldgJet)
MVAstring = "%.2f" % topSelectionBDT.TopMVACutValue
scaleFactors.setupToptagSFInformation(topTagPset                     = topSelectionBDT, 
                                      topTagMisidFilename            = "topMisID_BDT%s_TopMassCut400.json" % MVAstring.replace(".", "p").replace("-", "m"), 
                                      topTagEfficiencyFilename       = "toptagEff_BDT%s_GenuineTT_TopMassCut400.json" % MVAstring.replace(".", "p").replace("-", "m"),
                                      topTagEffUncertaintiesFilename = "toptagEffUncert_BDT%s_GenuineTT_TopMassCut400.json" % MVAstring.replace(".", "p").replace("-", "m"),
                                      direction                      = "nominal",
                                      variationInfo                  = None)

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
    deltaRBins        = PSet(nBins = 100, axisMin =  0.0, axisMax =   10.0),
    rtauBins          = PSet(nBins =  55, axisMin =  0.0, axisMax =    1.1), # HToTauNu
    njetsBins         = PSet(nBins =  18, axisMin =  0.0, axisMax =   18.0),
    metBins           = PSet(nBins =  80, axisMin =  0.0, axisMax =  400.0), #  5 GeV bin width
    htBins            = PSet(nBins = 500, axisMin =  0.0, axisMax = 5000.0), # 10 GeV bin width 
    bjetDiscrBins     = PSet(nBins = 120, axisMin =  0.0, axisMax =    1.2),
    angularCuts1DBins = PSet(nBins =  52, axisMin =  0.0, axisMax =  260.0), 
    topMassBins       = PSet(nBins = 200, axisMin =  0.0, axisMax = 1000.0), #  5 GeV bin width 
    wMassBins         = PSet(nBins = 200, axisMin =  0.0, axisMax = 1000.0), #  5 GeV bin width 
    mtBins            = PSet(nBins = 800, axisMin =  0.0, axisMax = 4000.0), #  5 GeV bin width
    invMassBins       = PSet(nBins = 600, axisMin =  0.0, axisMax = 3000.0), #  5 GeV bin width
)

#================================================================================================
# Build all selections group
#================================================================================================
allSelections = PSet(
    Verbose               = verbose,
    Trigger               = trigger,
    METFilter             = metFilter,
    ElectronSelection     = eVeto,
    MuonSelection         = muVeto,
    TauSelection          = tauVeto,
    JetSelection          = jetSelection,
    BJetSelection         = bjetSelection,
    METSelection          = metSelection,
    TopSelectionBDT       = topSelectionBDT,
    # FatJetSelection       = fatjetVeto,
    FakeBMeasurement      = fakeBMeasurement,
    FakeBBjetSelection    = fakeBBjetSelection,
    CommonPlots           = commonPlotsOptions,
    HistogramAmbientLevel = histogramAmbientLevel,
)
