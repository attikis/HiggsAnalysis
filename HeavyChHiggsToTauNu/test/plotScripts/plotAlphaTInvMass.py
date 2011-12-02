#!/usr/bin/env python
########################################################################
# -*- python -*-
#       File Name:  myPlots.py
# Original Author:  Matti Kortelainen
#          Editor:  Alexandros Attikis
#         Created:  Mon 4 Oct 2010
#     Description:  ROOT plotting macro
#       Institute:  UCY
#         e-mail :  attikis@cern.ch
#        Comments:  
########################################################################

import ROOT
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle import *
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles

############################### LEGENDS ###############################
legendLabels = {
    "Data":                "Data",
    "TTbar_Htaunu_M80":    "H^{#pm} M=80",
    "TTToHpmToTauNu_M90":  "H^{#pm} M=90",
    "TTToHpmToTauNu_M100": "H^{#pm} M=100",
    "TTToHpmToTauNu_M120": "H^{#pm} M=120",
    "TTbar_Htaunu_M140":   "H^{#pm} M=140",
    "TTbar_Htaunu_M160":   "H^{#pm} M=160",
    "TTbar":               "t#bar{t}",
    "TTbarJets":           "t#bar{t}+jets",
    "WJets":               "W+jets",
    "QCD_Pt30to50":        "QCD, 30 < #hat{p}_T < 50",
    "QCD_Pt50to80":        "QCD, 50 < #hat{p}_T < 80",
    "QCD_Pt80to120":       "QCD, 80 < #hat{p}_T < 120",
    "QCD_Pt120to170":      "QCD, 120 < #hat{p}_T < 170",
    "QCD_Pt170to230":      "QCD, 170 < #hat{p}_T < 230",
    "QCD_Pt230to300":      "QCD, 230 < #hat{p}_T < 300"
    }
############################### CUSTOMISATION ###############################
### Go to batch mode, comment if interactive mode is wanted (see on the
### bottom of the script how to make it to wait input from user)
# ROOT.gROOT.SetBatch(True) # Comment out to open canvases

### Apply TDR style
style = TDRStyle()

############################### DATASETS ###############################
### Construct datasets as stated in the multicrab.cfg of the execution
### directory. The returned object is of type DatasetManager.
datasets = getDatasetsFromMulticrabCfg(counters="signalAnalysisCounters/weighted")

### Construct datasets from the given list of CRAB task directories
#datasets = getDatasetsFromCrabDirs(["TTToHpmToTauNu_M100"]) ### example: single dataset
#datasets = getDatasetsFromCrabDirs(["TTbar_Htaunu_M80", "TTToHpmToTauNu_M90", "TTToHpmToTauNu_M100","TTToHpmToTauNu_M120","TTbar_Htaunu_M140", "TTbar_Htaunu_M160", "QCD_Pt30to50", "QCD_Pt50to80", "QCD_Pt80to120", "QCD_Pt120to170"]) ### example: list of datasets

### Construct datasets from a given list of (name, pathToRooTFile) pairs
#datasets = getDatasetsFromRootFiles([("QCD_Pt50to80", "QCD_Pt50to80/res/histograms_1_1_zCl.root")])
#datasets = getDatasetsFromRootFiles([("WJets", "WJets/res/histograms_32_1_f4s.root")])
#datasets = getDatasetsFromRootFiles([("TTbar", "TTbar/res/histograms_3_1_oN4.root")])
#datasets = getDatasetsFromRootFiles([("TTToHpmToTauNu_M100", "TTToHpmToTauNu_M100/res/histograms_1_1_6Ac.root")])
#datasets = getDatasetsFromRootFiles([("BTau_141950-144114", "BTau_141950-144114/res/histograms_1_1_Dxo.root")])

############################### MERGING & REMOVING DATASETS ###############################
### Example how to merge histograms of several datasets
datasets.merge("QCD", ["QCD_Pt30to50", "QCD_Pt50to80", "QCD_Pt80to120", "QCD_Pt120to170", "QCD_Pt170to230", "QCD_Pt230to300"])

### Example how to remove some datasets
#alphaTInvMass.removeDatasets(["BTau_141950-144114","BTau_146240-146729", "TTbar", "TTbarJets", "WJets", "QCD", "TTbar_Htaunu_M80", "TTToHpmToTauNu_M90", "TTToHpmToTauNu_M100", "TTToHpmToTauNu_M120", "TTbar_Htaunu_M140", "TTbar_Htaunu_M160"])
datasets.remove(["BTau_141950-144114","BTau_146240-146729", "TTbar", "TTbar_Htaunu_M80", "TTToHpmToTauNu_M90", "TTToHpmToTauNu_M100", "TTToHpmToTauNu_M120", "TTbar_Htaunu_M160"])

############################### HISTOS ###############################
### Get set of histograms with the given path. The returned object is of
### type HistoManager, which contains a histogram from each dataset in
### DatasetManager. The histograms can be e.g. merged/stacked or normalized
### in various ways before drawing.
alphaTInvMass = HistoManager(datasets, "signalAnalysis/alphaT-InvMass")

### Print the list of datasets in the given HistoManager
#print "\n".join(alphaTInvMass.getDatasetNames())

############################### DATA ###############################
### Merge all collision data datasets to one, it has name "Data"
### Note: this must be done before normalizeMCByLuminosity()
#alphaTInvMass.mergeDataDatasets()

### Example how to set the luminosity of a data dataset
#alphaTInvMass.getDataset("Data").setLuminosity(5)

### The default normalization is no normalization (i.e. number of MC
### events for MC, and number of events for data)

############################### NORMALISE ###############################
### Normalize MC histograms to their cross section
#alphaTInvMass.normalizeMCByCrossSection()
#ylabel = "Cross section (pb)"

### Normalize MC histograms to the luminosity of the collision data in
# the HistoManager
#alphaTInvMass.normalizeMCByLuminosity()
#ylabel = "Events"

### Normalize MC histograms to an explicit luminosity in pb
#alphaTInvMass.normalizeMCToLuminosity(2.89)
alphaTInvMass.normalizeMCToLuminosity(1.47)
ylabel = "Events"

### Normalize the area of *all* histograms to 1
#alphaTInvMass.normalizeToOne()
#ylabel = "a.u"

############################### STYLES ###############################
### Example how to set legend labels from defaults
alphaTInvMass.setHistoLegendLabelMany(legendLabels) # many datasets, with dict

### Example how to modify legend styles
alphaTInvMass.setHistoLegendStyleAll("F")
alphaTInvMass.setHistoLegendStyle("Data", "p")

### Apply the default styles (for all histograms, for MC histograms, for a single histogram)
alphaTInvMass.forEachMCHisto(styles.generator(fill=True)) # Apply SetFillColor too, needed for histogram stacking
alphaTInvMass.forHisto("Data", styles.getDataStyle())
#alphaTInvMass.setHistoDrawStyle("Data", "EP")

### Example how to stack all MC datasets. NOTE: this MUST be done after all legend/style manipulation
#alphaTInvMass.stackMCDatasets()

### Create TCanvas and TH1F such that they cover all histograms
cf = CanvasFrame(alphaTInvMass, "alphaTInvMass", ymin=0.01, ymax=None, xmin=0.0, xmax=1000.0)

### Set the frame options, e.g. axis labels
cf.frame.GetXaxis().SetTitle("Di-jet InvMass [GeV/c^{2}]")
cf.frame.GetYaxis().SetTitle(ylabel)

### Legend
legend = createLegend(0.7, 0.5, 0.9, 0.8)
alphaTInvMass.addToLegend(legend)

### Draw the plots
alphaTInvMass.draw()
legend.Draw()

### Set y-axis logarithmic (remember to give ymin for createCanvasFrame()
ROOT.gPad.SetLogy(True)

### The necessary texts, all take the position as arguments
addCmsPreliminaryText()
addEnergyText(x=0.3, y=0.85)
alphaTInvMass.addLuminosityText() ### need to comment out if normalising to unity 

############################### EXECUTION ###############################
### Script execution can be paused like this, it will continue after
### user has given some input (which must include enter)
raw_input("Hit enter to continue") ### keep canvas open until you hit enter

############################### SAVING ###############################
### Save TCanvas as png
cf.canvas.SaveAs(".png")
#cf.canvas.SaveAs(".eps")
#cf.canvas.SaveAs(".C")
