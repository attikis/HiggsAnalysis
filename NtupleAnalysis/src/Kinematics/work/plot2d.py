#!/usr/bin/env python
'''

Usage:
./plotTemplate.py -m <pseudo_mcrab_directory>

'''

#================================================================================================
# Imports
#================================================================================================
import os
import sys
from optparse import OptionParser
import getpass
import socket

import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.tdrstyle as tdrstyle
import HiggsAnalysis.NtupleAnalysis.tools.styles as styles
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.histograms as histograms
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux
from plotAux import *

import ROOT

#================================================================================================
# Variable Definition
#================================================================================================
kwargs = {
    "verbose"        : False,
    "dataEra"        : "Run2016",
    "searchMode"     : "80to1000",
    "analysis"       : "Kinematics",
    "optMode"        : "",
    #"savePath"       : "/Users/attikis/latex/talks/post_doc.git/HPlus/HIG-XY-XYZ/2016/Kinematics_06September2016/figures/M_200/",
    #"savePath"       : None,
    "refDataset"     : "TT", #"ChargedHiggs_HplusTB_HplusToTB_M_500",
    "savePath"       : os.getcwd() + "/Plots/TT_ext3", #M_500
    #"savePath"       : "/publicweb/a/aattikis/EvtShapeVars/",
    "saveFormats"    : [".png", ".pdf"],
    "normalizeTo"    : "One", #One", "XSection", "Luminosity"
    "zMin"           : 1e-1,
    "zMax"           : None,
    "rebinX"         : 1,
    "rebinY"         : 1,
    "createRatio"    : False,
    "logX"           : False,
    "logY"           : False,
    "logZ"           : True,
    "gridX"          : True,
    "gridY"          : True,
    "drawStyle"      : "COLZ", #"CONT4" "COLZ" "COL"
    "legStyle"       : "F",     # "LP", "F"
    "cutValue"       : None,
    "cutBox"         : False,
    "cutLine"        : False,
    "cutLessthan"    : False,
    "cutFillColour"  : ROOT.kAzure-4,
}


hNames = [
    "MaxDiJetMass_dEta_Vs_dPhi",
    "MaxDiJetMass_dRap_Vs_dPhi",
    "BQuark1_BQuark2_dEta_Vs_dPhi",
    "BQuark1_BQuark3_dEta_Vs_dPhi",
    "BQuark1_BQuark4_dEta_Vs_dPhi",
    "BQuark2_BQuark3_dEta_Vs_dPhi",
    "BQuark2_BQuark4_dEta_Vs_dPhi",
    "BQuark3_BQuark4_dEta_Vs_dPhi",
    "BQuarkPair_dRMin_Eta1_Vs_Eta2",
    "BQuarkPair_dRMin_Phi1_Vs_Phi2",
    "BQuarkPair_dRMin_Pt1_Vs_Pt2",
    "BQuarkPair_dRMin_dEta_Vs_dPhi",
    "Jet1Jet2_dEta_Vs_Jet3Jet4_dEta",
    "Jet1Jet2_dPhi_Vs_Jet3Jet4_dPhi",
    "Jet1Jet2_dEta_Vs_Jet1Jet2_Mass",
    "Jet3Jet4_dEta_Vs_Jet3Jet4_Mass",
    "S_Vs_Y",
#    "Htb_tbW_bqq_dRMax_dRap_Vs_dPhi",
#    "gtt_tbW_bqq_dRMax_dRap_Vs_dPhi",
#    "tbWPlus_bqq_dRMax_dRap_Vs_dPhi",
#    "tbWMinus_bqq_dRMax_dRap_Vs_dPhi",

]



#================================================================================================
# Main
#================================================================================================
def main(opts):

    style = tdrstyle.TDRStyle()
    #style.setWide(True)
    style.setPaletteMy()
    ROOT.gStyle.SetNumberContours(20)
    # tdrstyle.setDeepSeaPalette()
    # tdrstyle.setRainBowPalette()
    # tdrstyle.setDarkBodyRadiatorPalette()
    # tdrstyle.setGreyScalePalette()
    # tdrstyle.setTwoColorHuePalette()
 
    
    # Set ROOT batch mode boolean
    ROOT.gROOT.SetBatch(opts.batchMode)
    
    # ========================================
    # Datasets
    # ========================================
    # Setup & configure the dataset manager
    datasetsMgr = GetDatasetsFromDir(opts.mcrab, opts, **kwargs)
    intLumi     = GetLumi(datasetsMgr)
    datasetsMgr.updateNAllEventsToPUWeighted()
    datasetsMgr.PrintCrossSections()
    #datasetsMgr.PrintLuminosities()

    # Set/Overwrite cross-sections
    for d in datasetsMgr.getAllDatasets():
        if "ChargedHiggs" in d.getName():
            datasetsMgr.getDataset(d.getName()).setCrossSection(1.0)
    
    # Merge datasts (Note: Merged MC histograms must be normalized to something)
    plots.mergeRenameReorderForDataMC(datasetsMgr)

    # Remove datasets
    if 0:
        datasetsMgr.remove("TTJets")
        datasetsMgr.remove(filter(lambda name: not "QCD" in name, datasetsMgr.getAllDatasetNames()))
    
    # Print dataset information
    datasetsMgr.PrintInfo()
                  
    # For-loop: All Histogram names
    for counter, hName in enumerate(hNames):
        savePath, saveName = GetSavePathAndName(hName, **kwargs)                

        # Get Histos for Plotter
        refHisto, otherHistos = GetHistosForPlotter(datasetsMgr, hName, **kwargs)

        # Create a plot
        p = plots.PlotBase([refHisto], kwargs.get("saveFormats"))
        
        # Remove negative contributions
        #RemoveNegativeBins(datasetsMgr, hName, p)

        # Customize
        # p.histoMgr.setHistoDrawStyleAll("COL") #"CONT4" "COLZ" "COL"
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().RebinX(kwargs.get("rebinX")))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().RebinY(kwargs.get("rebinY")))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().GetXaxis().SetRangeUser(1.0, 5.0))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().GetYaxis().SetRangeUser(1.0, 5.0))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().GetZaxis().SetRangeUser(0.0, 0.015))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetMinimum(kwargs.get("zMin")))
        # p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetMaximum(kwargs.get("zMax")))
        
        # Create a frame
        opts = {"ymin": 0.0, "ymaxfactor": 1.0}
        p.createFrame(saveName, opts=opts)


        # Customise frame
        p.getFrame().GetXaxis().SetTitle( getTitleX(refHisto, **kwargs) )
        #p.getFrame().GetYaxis().SetTitle( getTitleY(refHisto, **kwargs) )
        
        # SetLog
        SetLogAndGrid(p, **kwargs)

        # Add cut line/box
        _kwargs = { "lessThan": kwargs.get("cutLessThan")}
        p.addCutBoxAndLine(cutValue=kwargs.get("cutValue"), fillColor=kwargs.get("cutFillColour"), box=kwargs.get("cutBox"), line=kwargs.get("cutLine"), **_kwargs)
        
        # Customise Legend
        moveLegend = {"dx": -0.1, "dy": +0.0, "dh": -0.1}
        p.setLegend(histograms.moveLegend(histograms.createLegend(), **moveLegend))
        p.removeLegend()

        # Add MC Uncertainty (Invalid method for a 2-d histogram)
        #p.addMCUncertainty()
        
        #  Draw plots
        p.draw()

        # Customise text
        histograms.addStandardTexts(lumi=intLumi)
        # histograms.addText(0.17, 0.95, plots._legendLabels[kwargs.get("refDataset")], 22)
        histograms.addText(0.17, 0.88, plots._legendLabels[kwargs.get("refDataset")], 17)
        
        # Save canvas under custom dir
        SaveAs(p, savePath, saveName, kwargs.get("saveFormats"), counter==0)

    return

#================================================================================================
# Main
#================================================================================================
if __name__ == "__main__":

    parser = OptionParser(usage="Usage: %prog [options]" , add_help_option=False,conflict_handler="resolve")

    parser.add_option("-m", "--mcrab", dest="mcrab", action="store", 
                      help="Path to the multicrab directory for input")

    parser.add_option("-b", "--batchMode", dest="batchMode", action="store_false", default=True, 
                      help="Enables batch mode (canvas creation does NOT generates a window)")

    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, 
                      help="Enables verbose mode (for debugging purposes)")

    parser.add_option("-i", "--includeTasks", dest="includeTasks" , default="", type="string",
                      help="Only perform action for this dataset(s) [default: '']")

    parser.add_option("-e", "--excludeTasks", dest="excludeTasks" , default="", type="string",
                      help="Exclude this dataset(s) from action [default: '']")

    (opts, parseArgs) = parser.parse_args()

    # Require at least two arguments (script-name, path to multicrab)
    if opts.mcrab == None:
        Print("Not enough arguments passed to script execution. Printing docstring & EXIT.")
        print __doc__
        sys.exit(0)
    else:
        pass

    # Program execution
    main(opts)

    if not opts.batchMode:
        raw_input("=== plotTemplate.py: Press any key to quit ROOT ...")


#        args = {
#            "xlabel": "x",
#            "ylabel": "y",
#            "zlabel": "z",
#            "xlabelsize": None,
#            "ylabelsize": None,
#            "zhisto": None,
#            "log": False,
#            "ratio": False,
#            "ratioYlabel": None, 
#            "ratioInvert": False,
#            "ratioType": None,
#            #"ratioErrorOptions": 
#            "ratioCreateLegend": True,
#            #"ratioMoveLegend":
#            #"opts":
#            #"optsLog":
#            #"opts2":
#            #"canvasOpts":
#            "backgroundColor": ROOT.kRed,
#            "rebin": 1,
#            "rebinX": 1,
#            "rebinY": 1,
#            "rebinToWidthX": None,
#            "rebinToWidthY": None,
#            "divideByBinWidth": None,
#            "errorBarsX": True,
#            "createLegend": None,
#            #"moveLegend": 
#            #"customizeBeforeFrame":
#            #"customizeBeforeDraw":
#            #"customizeBeforeSave":
#            #"addLuminosityText":
#            "stackMCHistograms": True,
#            "addMCUncertainty": True,
#            "cmsText": True,
#            "cmsExtraText": True,
#            "addCmsText": True,
#            "cmsTextPosition": None,
#            "cmsExtraTextPosition": None,
#        }
#        
#        p.setDrawOptions(**args)
