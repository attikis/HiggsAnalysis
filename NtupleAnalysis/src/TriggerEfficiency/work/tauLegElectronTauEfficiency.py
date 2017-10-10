#!/usr/bin/env python

from HiggsAnalysis.NtupleAnalysis.main import Process, PSet, Analyzer

import os
import re

#process = Process(outputPrefix="tauLegEfficiency")

# Example of adding a dataset which has its files defined in data/<dataset_name>.txt file
#process.addDatasets(["TTbar_HBWB_HToTauNu_M_160_13TeV_pythia6"])

# Example of adding datasets from a multicrab directory
import sys
if len(sys.argv) != 2:
    print "Usage: ./exampleAnalysis.py <path-to-multicrab-directory>"
    sys.exit(0)

#process.addDatasetsFromMulticrab(sys.argv[1])
#process.addDatasetsFromMulticrab(sys.argv[1],includeOnlyTasks="SingleMuon_Run2015D_PromptReco_v3_246908_260426_25ns$")
#process.addDatasetsFromMulticrab(sys.argv[1],includeOnlyTasks="SingleMuon_Run2015")
#process.addDatasetsFromMulticrab(sys.argv[1],includeOnlyTasks="DYJetsToLL_M50")
#process.addDatasetsFromMulticrab(sys.argv[1],includeOnlyTasks="GluGluHToTauTau_M125")

leg     = "taulegElectronTauSelection"
#binning = [20, 30, 40, 50, 60, 70, 80, 100, 120, 140, 160, 180, 200]
binning = [20, 30, 40, 50, 60, 80, 100, 120, 200, 250, 300, 400, 500]
xLabel  = "#tau-jet p_{T} (GeV/c)"
yLabel  = "HLT tau efficiency"

import HiggsAnalysis.NtupleAnalysis.tools.aux as aux

eras = {}
eras["2017"] = "SingleElectron_Run2017"

runmin = -1
runmax = -1

def getDatasetsForEras(dsets,era):
    dset_re = re.compile(era)
    dOUT = []
    for dset in dsets:
        if dset.getDataVersion().isData():
            match = dset_re.search(dset.getName())
            if match:
                dOUT.append(dset)
        else:
            dOUT.append(dset)
    return dOUT

def isData(dataVersion):
    dataVersion = str(dataVersion)
    #print type(dataVersion)
    #print dataVersion
    dv_re = re.compile("data")
    match = dv_re.search(dataVersion)
    if match:
        return True
    return False

def createAnalyzer(dataVersion,era):
    a = Analyzer("TriggerEfficiency",
        name = era,
        Trigger = PSet(
            triggerOR  = [],
            triggerOR2 = []
        ),
        usePileupWeights = True,
        offlineSelection = leg,
        ElectronSelection = PSet(
#            discriminators = ["muIDMedium"],
#            discriminators = ["TrgMatch_IsoMu20_eta2p1"],
#            discriminators = ["Muons_TrgMatch_IsoMu16_eta2p1"],
            discriminators = []
        ),
        TauSelection = PSet(
            discriminators = ["byLooseCombinedIsolationDeltaBetaCorr3Hits",#"byMediumIsolationMVA3newDMwLT",
                              "againstMuonTight3",
                              "againstElectronMediumMVA6"],
            nprongs = 1,
            relaxedOfflineSelection = False
        ),
        binning = binning,
        xLabel  = xLabel,
        yLabel  = yLabel,
    )

    if isData(dataVersion):
        if "2017" in era:
            a.Trigger.triggerOR = ["HLT_Ele24_eta2p1_WPTight_Gsf_vx","HLT_Ele35_WPTight_Gsf_vx"]
            a.Trigger.triggerOR2= ["HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1_vx"]

        a.runMin  = runmin
        a.runMax  = runmax
    else:
        print "MC not implemented yet"

    #print "check triggerOR",a.Trigger.triggerOR
    return a

def addAnalyzer(era):
    process = Process(outputPrefix="tauLegElectronTauEfficiency_"+era)
#    process.setDatasets([])
    process.addDatasetsFromMulticrab(sys.argv[1])
    ds = getDatasetsForEras(process.getDatasets(),eras[era])
    process.setDatasets(ds)
    global runmin,runmax
    runmin,runmax = process.getRuns()
    process.addAnalyzer("TauLeg_"+era, lambda dv: createAnalyzer(dv, era))
#    process.addAnalyzer("TauLeg_"+era, createAnalyzer(dv, era))
    process.run()


addAnalyzer("2017")

# Run the analysis
#process.run()


# Run the analysis with PROOF
# By default it uses all cores, but you can give proofWorkers=<N> as a parameter
#process.run(proof=True)
