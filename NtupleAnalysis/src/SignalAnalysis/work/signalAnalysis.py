#!/usr/bin/env python
import sys

dataEras = ["2016"]
#dataEras = ["2015B","2015C"]
searchModes = ["80to1000"]

lightAnalysis = False
#lightAnalysis = True

if len(sys.argv) < 2:
    print "Usage: ./exampleAnalysis.py <path-to-multicrab-directory> <1pr> <2pr> <3pr>"
    sys.exit(0)

from HiggsAnalysis.NtupleAnalysis.main import Process, PSet, Analyzer
from HiggsAnalysis.NtupleAnalysis.parameters.signalAnalysisParameters import obtainAnalysisSuffix 
process = Process("SignalAnalysis"+obtainAnalysisSuffix(sys.argv))
blacklist = ["ChargedHiggs_TTToHplusBWB",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_180",
#	"ChargedHiggs_HplusTB_HplusToTauNu_M_200",
	"ChargedHiggs_HplusTB_HplusToTauNu_M_220",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_250",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_300",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_350",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_400",
#        "ChargedHiggs_HplusTB_HplusToTauNu_M_500",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_750",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_800",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_1000",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_2000",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_3000",
        "ChargedHiggs_HplusTB_HplusToTauNu_M_200",
#        "Tau_Run2016C_23Sep2016_v1_275420_276283",
#        "Tau_Run2016D_23Sep2016_v1_276315_276437",
#        "Tau_Run2016D_23Sep2016_v1_276453_276811",
#        "Tau_Run2016E_23Sep2016_v1_276824_277420",
#        "Tau_Run2016F_23Sep2016_v1_277816_278800",
#        "Tau_Run2016F_23Sep2016_v1_278801_278808",
#        "Tau_Run2016G_23Sep2016_v1_278816_280385",
        "Tau_Run2016H_PromptReco_v1_281010_281202",
#        "Tau_Run2016H_PromptReco_v2_281207_284035",
#        "Tau_Run2016H_PromptReco_v3_271036_284044",
#        "DYJetsToLL_M_50_ext",
#	"DYJetsToLL_M_50",
        "DYJetsToQQ_HT180",
#        "ST_tW_antitop_5f_inclusiveDecays_ext",
#        "ST_tW_top_5f_inclusiveDecays_ext",
#        "ST_tW_antitop_5f_inclusiveDecays",
#        "ST_tW_top_5f_inclusiveDecays",
#        "ST_t_channel_antitop_4f_inclusiveDecays",
#        "ST_t_channel_top_4f_inclusiveDecays",
#        "WJetsToLNu_ext",
#	"WJetsToLNu",
#        "WZ_ext",
#        "WZ",
#	"TT",
]

if lightAnalysis:
    blacklist = ["ChargedHiggs_HplusTB"]
process.addDatasetsFromMulticrab(sys.argv[1],blacklist=blacklist)

# Add config
from HiggsAnalysis.NtupleAnalysis.parameters.signalAnalysisParameters import allSelections,applyAnalysisCommandLineOptions,setAngularCutsWorkingPoint
# Set splitting of phase space (first bin is below first edge value and last bin is above last edge value)
allSelections.CommonPlots.histogramSplitting = [
    #PSet(label="tauPt", binLowEdges=[60.0, 70.0, 80.0, 100.0], useAbsoluteValues=False),
  ]
#===== Selection customisations
allSelections.TauSelection.prongs = 1
if lightAnalysis:
    allSelections.TauSelection.tauPtCut = 50.0 #uncomment for light H+ (default 60.0 for heavy H+)
    allSelections.METSelection.METCutValue = 80.0 #uncomment for light H+ (default 100.0 for heavy H+)
#allSelections.METSelection.METCutValue = 80.0
#allSelections.AngularCutsBackToBack.cutValueJet1 = 0.0
#allSelections.AngularCutsBackToBack.cutValueJet2 = 0.0
#allSelections.AngularCutsBackToBack.cutValueJet3 = 0.0
#allSelections.AngularCutsBackToBack.cutValueJet4 = 0.0
allSelections.AngularCutsCollinear.cutValueJet1 = 80.0
allSelections.AngularCutsCollinear.cutValueJet2 = 80.0
allSelections.AngularCutsCollinear.cutValueJet3 = 80.0
allSelections.AngularCutsCollinear.cutValueJet4 = 80.0

#allSelections.TauSelection.rtau = 0.7
#allSelections.BJetSelection.bjetDiscrWorkingPoint = "Medium"
#allSelections.BJetSelection.numberOfBJetsCutValue = 0
#allSelections.BJetSelection.numberOfBJetsCutDirection = "=="
#setAngularCutsWorkingPoint(allSelections.AngularCutsCollinear, "Loose")
#===== End of selection customisations

applyAnalysisCommandLineOptions(sys.argv, allSelections)

# Build analysis modules
from HiggsAnalysis.NtupleAnalysis.AnalysisBuilder import AnalysisBuilder
builder = AnalysisBuilder("SignalAnalysis", 
                          dataEras,
                          searchModes,
                          #### Options ####
                          usePUreweighting=True,
                          doSystematicVariations=False
                          )
#builder.addVariation("METSelection.METCutValue", [100,120,140])
#builder.addVariation("AngularCutsBackToBack.workingPoint", ["Loose","Medium","Tight"])
builder.build(process, allSelections)

# Pick events
#process.addOptions(EventSaver = PSet(enabled = True,pickEvents = True))

# Run the analysis
if "proof" in sys.argv:
    #raise Exception("Proof messes up the event weights, do not use for the moment!")
    process.run(proof=True)
else:
    process.run()

# Run the analysis with PROOF
# By default it uses all cores, but you can give proofWorkers=<N> as a parameter
#process.run(proof=True)
