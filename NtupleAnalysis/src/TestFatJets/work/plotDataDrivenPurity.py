#!/usr/bin/env python
'''
Description:
This scipt plots TH1 histograms produced by the
FakeBMeasurement.cc class. These histograms
are considered auxiliary to those created by
plotEwkVsQcd.py and plotBaselineVsInverted.py 
scripts. They show the QCD (or EWK) purity as a 
function of a given variable.

For the definition of the counter class see:
HiggsAnalysis/NtupleAnalysis/scripts

For more counter tricks and optios see also:
HiggsAnalysis/NtupleAnalysis/scripts/hplusPrintCounters.py

Usage:
./plotDataDrivenPurity.py -m <pseudo_mcrab_directory> [opts]

Examples:
./plotDataDrivenPurity.py -m Hplus2tbAnalysis_StdSelections_TopCut100_AllSelections_HLTBJetTrgMatch_TopCut10_H2Cut0p5_170720_104648 --url -o ""

Last Used:
./plotDataDrivenPurity.py -m Hplus2tbAnalysis_StdSelections_TopCut100_AllSelections_NoTrgMatch_TopCut10_H2Cut0p5_InvMassFix_170822_074229 --url

'''

#================================================================================================ 
# Imports
#================================================================================================ 
import sys
import math
import copy
import os
from optparse import OptionParser

import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import *

import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.histograms as histograms
import HiggsAnalysis.NtupleAnalysis.tools.counter as counter
import HiggsAnalysis.NtupleAnalysis.tools.tdrstyle as tdrstyle
import HiggsAnalysis.NtupleAnalysis.tools.styles as styles
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.crosssection as xsect
import HiggsAnalysis.NtupleAnalysis.tools.multicrabConsistencyCheck as consistencyCheck

#================================================================================================ 
# Function Definition
#================================================================================================ 
def Print(msg, printHeader=False):
    fName = __file__.split("/")[-1]
    if printHeader==True:
        print "=== ", fName
        print "\t", msg
    else:
        print "\t", msg
    return

def Verbose(msg, printHeader=True, verbose=False):
    if not opts.verbose:
        return
    Print(msg, printHeader)
    return

def GetLumi(datasetsMgr):
    Verbose("Determininig Integrated Luminosity")
    
    lumi = 0.0
    for d in datasetsMgr.getAllDatasets():
        if d.isMC():
            continue
        else:
            lumi += d.getLuminosity()
    Verbose("Luminosity = %s (pb)" % (lumi), True)
    return lumi

def GetListOfEwkDatasets():
    Verbose("Getting list of EWK datasets")
    #return ["TT", "WJetsToQQ_HT_600ToInf", "DYJetsToQQHT", "SingleTop", "TTWJetsToQQ", "TTZToQQ", "Diboson", "TTTT"]
    return  ["TT", "WJetsToQQ_HT_600ToInf", "SingleTop", "DYJetsToQQHT", "TTZToQQ",  "TTWJetsToQQ", "Diboson", "TTTT"]

def GetDatasetsFromDir(opts):
    Verbose("Getting datasets")
    
    if (not opts.includeOnlyTasks and not opts.excludeTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([opts.mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode, 
                                                        analysisName=opts.analysisName,
                                                        optimizationMode=opts.optMode)
    elif (opts.includeOnlyTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([opts.mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode,
                                                        analysisName=opts.analysisName,
                                                        includeOnlyTasks=opts.includeOnlyTasks,
                                                        optimizationMode=opts.optMode)
    elif (opts.excludeTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([opts.mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode,
                                                        analysisName=opts.analysisName,
                                                        excludeTasks=opts.excludeTasks,
                                                        optimizationMode=opts.optMode)
    else:
        raise Exception("This should never be reached")
    return datasets
    
def main(opts):

    #optModes = ["", "OptChiSqrCutValue50", "OptChiSqrCutValue100"]
    optModes = [""]

    if opts.optMode != None:
        optModes = [opts.optMode]
        
    # For-loop: All opt Mode
    for opt in optModes:
        opts.optMode = opt

        # Setup & configure the dataset manager 
        datasetsMgr = GetDatasetsFromDir(opts)
        datasetsMgr.updateNAllEventsToPUWeighted()
        datasetsMgr.loadLuminosities() # from lumi.json

        # Set/Overwrite cross-sections
        for d in datasetsMgr.getAllDatasets():
            if "ChargedHiggs" in d.getName():
                datasetsMgr.getDataset(d.getName()).setCrossSection(1.0) # ATLAS 13 TeV H->tb exclusion limits
                
        if opts.verbose:
            datasetsMgr.PrintCrossSections()
            datasetsMgr.PrintLuminosities()

        # Merge histograms (see NtupleAnalysis/python/tools/plots.py) 
        plots.mergeRenameReorderForDataMC(datasetsMgr) 

        # Merge EWK samples
        if opts.mergeEWK:
            datasetsMgr.merge("EWK", GetListOfEwkDatasets())
            plots._plotStyles["EWK"] = styles.getAltEWKStyle()
   
        # Custom Filtering of datasets 
        removeList = ["Data", "QCD-b", "Charged", "EWK"]
        for d in removeList:
            datasetsMgr.remove(filter(lambda name: d in name, datasetsMgr.getAllDatasetNames()))

        # Replace QCD MC with QCD-DataDriven
        qcdDatasetName    = "FakeBMeasurementTrijetMass"
        qcdDatasetNameNew = "QCD-Data"
        replaceQCDFromData(datasetsMgr, qcdDatasetName, qcdDatasetNameNew)

        # Print dataset information
        datasetsMgr.PrintInfo()

        # Apply TDR style
        style = tdrstyle.TDRStyle()
        style.setOptStat(True)

        # Do Purity histograms with DataDriven QCD
        PurityHistograms(datasetsMgr, qcdDatasetNameNew)
    return

def PurityHistograms(datasetsMgr, qcdDatasetName):
    '''
    '''
    Verbose("Plotting Purity Histograms")

    # Definitions
    histoNames  = []
    saveFormats = [".png"] #[".C", ".png", ".eps"]
    dataPath    = "ForDataDrivenCtrlPlots"
    histoList   = datasetsMgr.getDataset(qcdDatasetName).getDirectoryContent(dataPath)
    histoList   = [h for h in histoList if "_Purity" in h]
    # histoList   = [h for h in histoList if "_MCEWK" in h]
    histoPaths  = [dataPath+"/"+h for h in histoList]
    histoKwargs = GetHistoKwargs(histoPaths, opts)

    # For-loop: All histograms in list
    for histoName in histoPaths:
        if "_Vs_" in histoName:
            continue

        if "subldg" in histoName.lower():
            continue

        kwargs_  = histoKwargs[histoName]
        saveName = histoName.replace("/", "_")

        # Create the plotting object
        p = plots.MCPlot(datasetsMgr, histoName, normalizeToLumi=True, saveFormats=[])
        p.setLuminosity(GetLumi(datasetsMgr))

        # Apply QCD data-driven style
        p.histoMgr.forHisto(qcdDatasetName, styles.getQCDLineStyle())
        p.histoMgr.setHistoDrawStyle(qcdDatasetName, "AP")
        p.histoMgr.setHistoLegendStyle(qcdDatasetName, "LP")
        p.histoMgr.setHistoLegendLabelMany({
                #qcdDatasetName: "QCD (Data)",
                qcdDatasetName: "QCD",
                })

        # Draw and save the plot
        plots.drawPlot(p, saveName, **kwargs_) #the "**" unpacks the kwargs_ dictionary
        SavePlot(p, saveName, os.path.join(opts.saveDir, "", opts.optMode) )
    return

def GetHistoKwargs(histoList, opts):
    '''
    Dictionary with 
    key   = histogramName
    value = kwargs
    '''

    histoKwargs = {}
    _moveLegend = {"dx": -0.05, "dy": +0.06, "dh": -0.12}    
    yMin = 0.0
    yMax = 1.1
    _kwargs = {
        "rebinX"           : 1,
        "rebinY"           : None,
        "ratioYlabel"      : "Ratio",
        "ratio"            : False, 
        #"stackMCHistograms": True,
        "ratioInvert"      : False, 
        "addMCUncertainty" : False, 
        "addLuminosityText": True,
        "addCmsText"       : True,
        "cmsExtraText"     : "Preliminary",
        "opts"             : {"ymin": yMin, "ymax": yMax},
        "opts2"            : {"ymin": 0.0 , "ymax": 2.0},
        "log"              : False,
        "errorBarsX"       : True,        
        "moveLegend"       : _moveLegend,
        }

    for h in histoList:
        yAxis = "Events"
        if "Purity" in h:
            yAxis = "Purity "

        kwargs = copy.deepcopy(_kwargs)
        if "NVertices" in h:
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "Vertices"
        if "Njets" in h:                
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "Jets Multiplicity"
            kwargs["cutBox"] = {"cutValue": 7.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
        if "JetPt" in h:                
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 30.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
        if "JetEta" in h:                
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "#eta"
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": -2.5, "xmax": +2.5, "ymin": yMin, "ymax": yMax}
        if "NBjets" in h:                
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "b-Jets Multiplicity"
            kwargs["cutBox"] = {"cutValue": 3.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 10.0, "ymin": yMin, "ymax": yMax}
        if "BjetPt" in h:                
            units = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 30.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
        if "BjetEta" in h:                
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "#eta"
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": -2.5, "xmax": +2.5, "ymin": yMin, "ymax": yMax}
        if "BtagDiscriminator" in h:                
            kwargs["ylabel"]     = yAxis + "/ %.2f"
            kwargs["xlabel"]     = "b-Tag Discriminator"
            kwargs["cutBox"]     = {"cutValue": 0.8484, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["moveLegend"] = {"dx": -0.5, "dy": -0.01, "dh": 0.0}
            kwargs["opts"]       = {"xmin": 0.0, "xmax": 1.05, "ymin": yMin, "ymax": yMax}
        if "HT" in h:
            units            = "GeV"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "H_{T} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 500.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 4500, "ymin": yMin, "ymax": yMax}
        if "MHT" in h:
            units            = "GeV"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "MHT (%s)"  % units
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 400, "ymin": yMin, "ymax": yMax}
        if "Sphericity" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "Sphericity"
        if "Aplanarity" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "Aplanarity"
        if "Circularity" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "Circularity"
        if "Circularity" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "Circularity"
        if "ThirdJetResolution" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "y_{23}"
        if "FoxWolframMoment" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "H_{2}"
        if "Centrality" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "Centrality"
            kwargs["moveLegend"] = {"dx": -0.53, "dy": 0.0, "dh": 0.0}
        if "TopFitChiSqr" in h:
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "#chi^{2}"
            kwargs["cutBox"] = {"cutValue": 100.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 180.0, "ymin": yMin, "ymax": yMax}
        if "LdgTrijetPt" in h:
            units = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "LdgTrijetMass" in h:
            units            = "GeV/c^{2}"
            kwargs["rebinX"] = 1 # Cannot be bigger than 1 here! (Must rebin BEFORE calculating the purity)
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "m_{jjb} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 173.21, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 1000.0, "ymin": yMin, "ymax": yMax}
            startBlind       = 150
            endBlind         = 200
            kwargs["blindingRangeString"] = "%s-%s" % (startBlind, endBlind)
            kwargs["moveBlindedText"]     = {"dx": -0.22, "dy": +0.08, "dh": -0.12}
        if "LdgTrijetBjetPt" in h:
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "LdgTrijetBjetEta" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "#eta"
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": -2.5, "xmax": +2.5, "ymin": yMin, "ymax": yMax}
        if "SubldgTrijetPt" in h:
            units = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "SubldgTrijetMass" in h:
            units            = "GeV/c^{2}"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "m_{jjb} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 173.21, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": 1200.0, "ymin": yMin, "ymax": yMax}
            startBlind       = 150
            endBlind         = 200
            kwargs["blindingRangeString"] = "%s-%s" % (startBlind, endBlind)
            kwargs["moveBlindedText"]     = {"dx": -0.22, "dy": +0.08, "dh": -0.12}
        if "SubldgTrijetBjetPt" in h:
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "SubldgTrijetBjetEta" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "#eta"
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": -2.5, "xmax": +2.5, "ymin": yMin, "ymax": yMax}
        if "LdgTetrajetPt" in h:
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "LdgTetrajetMass" in h:
            startBlind       = 180
            endBlind         = 3000
            units            = "GeV/c^{2}"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "m_{jjbb} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 500.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": endBlind, "ymin": yMin, "ymax": yMax}
            kwargs["blindingRangeString"] = "%s-%s" % (startBlind, endBlind)
            kwargs["moveBlindedText"]     = {"dx": -0.22, "dy": +0.08, "dh": -0.12}
        if "SubldgTetrajetPt" in h:
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "SubldgTetrajetMass" in h:
            startBlind       = 180
            endBlind         = 3000
            units            = "GeV/c^{2}"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "m_{jjbb} (%s)"  % units
            kwargs["cutBox"] = {"cutValue": 500.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": endBlind}#, "ymin": 1e+0, "ymaxfactor": 10}
            kwargs["cutBox"] = {"cutValue": 7.0, "fillColor": 16, "box": False, "line": False, "greaterThan": True}
            kwargs["blindingRangeString"] = "%s-%s" % (startBlind, endBlind)
            kwargs["moveBlindedText"] = {"dx": -0.22, "dy": +0.08, "dh": -0.12}
        if "TetrajetBjetPt" in h:
            units            = "GeV/c"
            kwargs["ylabel"] = yAxis + "/ %.0f " + units
            kwargs["xlabel"] = "p_{T} (%s)"  % units
        if "TetrajetBjetEta" in h:
            kwargs["ylabel"] = yAxis + "/ %.2f"
            kwargs["xlabel"] = "#eta"
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": -2.5, "xmax": +2.5, "ymin": yMin, "ymax": yMax}
        if "HT" in h:
            units            = "GeV/c^{2}"
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "H_{T} (%s)" % (units)
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 500.0, "xmax": +1500, "ymin": yMin, "ymax": yMax}
            ROOT.gStyle.SetNdivisions(8, "X")
        if "MET" in h:
            units            = "GeV"
            kwargs["ylabel"] = yAxis + "/ %.0f"
            kwargs["xlabel"] = "E_{T}^{miss} (%s)" % (units)
            kwargs["cutBox"] = {"cutValue": 0.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True}
            kwargs["opts"]   = {"xmin": 0.0, "xmax": +400, "ymin": yMin, "ymax": yMax}
        histoKwargs[h] = kwargs
    return histoKwargs
    

def getHisto(datasetsMgr, datasetName, histoName):
    Verbose("getHisto()", True)

    h1 = datasetsMgr.getDataset(datasetName).getDatasetRootHisto(histoName)
    h1.setName(datasetName)
    return h1

def replaceQCDFromData(dMgr, dataDrivenDatasetName, newName="QCD-Data"):
    
    # Define variables
    mcQCDName      = "QCD"
    dataDrivenQCD  = dMgr.getDataset(dataDrivenDatasetName)
    dataDrivenQCD.setName(newName)

    # Get list of dataset names
    names = dMgr.getAllDatasetNames()

    # Return the index in the list of the first dataset whose name is mcQCDName.
    index = names.index(mcQCDName)

    # Remove the dataset at the given position in the list, and return it. 
    names.pop(index)
    
    # Insert the dataset to the given position  (index) of the list
    names.insert(index, dataDrivenQCD.getName())

    # Remove from the dataset manager the mcQCDName
    dMgr.remove(mcQCDName)
    names.pop(names.index(dataDrivenQCD.getName()))
    
    # Select and reorder Datasets. 
    # This method can be used to either select a set of dataset.Dataset objects. reorder them, or both.
    dMgr.selectAndReorder(names)
    return

def SavePlot(plot, plotName, saveDir, saveFormats = [".png", ".C", ".eps"]):
    Verbose("Saving the plot in %s formats: %s" % (len(saveFormats), ", ".join(saveFormats) ) )

    # Check that path exists
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # Create the name under which plot will be saved
    saveName = os.path.join(saveDir, plotName.replace("/", "_"))

    # For-loop: All save formats
    for i, ext in enumerate(saveFormats):
        saveNameURL = saveName + ext
        saveNameURL = saveNameURL.replace("/publicweb/a/aattikis/", "http://home.fnal.gov/~aattikis/")
        if opts.url:
            Print(saveNameURL, i==0)
        else:
            Print(saveName + ext, i==0)
        plot.saveAs(saveName, formats=saveFormats)
    return


#================================================================================================ 
# Main
#================================================================================================ 
if __name__ == "__main__":
    '''
    https://docs.python.org/3/library/argparse.html
 
    name or flags...: Either a name or a list of option strings, e.g. foo or -f, --foo.
    action..........: The basic type of action to be taken when this argument is encountered at the command line.
    nargs...........: The number of command-line arguments that should be consumed.
    const...........: A constant value required by some action and nargs selections.
    default.........: The value produced if the argument is absent from the command line.
    type............: The type to which the command-line argument should be converted.
    choices.........: A container of the allowable values for the argument.
    required........: Whether or not the command-line option may be omitted (optionals only).
    help............: A brief description of what the argument does.
    metavar.........: A name for the argument in usage messages.
    dest............: The name of the attribute to be added to the object returned by parse_args().
    '''
    
    # Default Settings
    ANALYSISNAME = "Hplus2tbAnalysis"
    SEARCHMODE   = "80to1000"
    DATAERA      = "Run2016"
    OPTMODE      = None
    BATCHMODE    = True
    PRECISION    = 3
    INTLUMI      = -1.0
    SUBCOUNTERS  = False
    LATEX        = False
    MCONLY       = False
    MERGEEWK     = True
    URL          = False
    NOERROR      = True
    SAVEDIR      = "/publicweb/a/aattikis/Purity/"
    VERBOSE      = False
    HISTOLEVEL   = "Vital" # 'Vital' , 'Informative' , 'Debug' 

    # Define the available script options
    parser = OptionParser(usage="Usage: %prog [options]")

    parser.add_option("-m", "--mcrab", dest="mcrab", action="store", 
                      help="Path to the multicrab directory for input")

    parser.add_option("-o", "--optMode", dest="optMode", type="string", default=OPTMODE, 
                      help="The optimization mode when analysis variation is enabled  [default: %s]" % OPTMODE)

    parser.add_option("-b", "--batchMode", dest="batchMode", action="store_false", default=BATCHMODE, 
                      help="Enables batch mode (canvas creation does NOT generate a window) [default: %s]" % BATCHMODE)

    parser.add_option("--analysisName", dest="analysisName", type="string", default=ANALYSISNAME,
                      help="Override default analysisName [default: %s]" % ANALYSISNAME)

    parser.add_option("--mcOnly", dest="mcOnly", action="store_true", default=MCONLY,
                      help="Plot only MC info [default: %s]" % MCONLY)

    parser.add_option("--intLumi", dest="intLumi", type=float, default=INTLUMI,
                      help="Override the integrated lumi [default: %s]" % INTLUMI)

    parser.add_option("--searchMode", dest="searchMode", type="string", default=SEARCHMODE,
                      help="Override default searchMode [default: %s]" % SEARCHMODE)

    parser.add_option("--dataEra", dest="dataEra", type="string", default=DATAERA, 
                      help="Override default dataEra [default: %s]" % DATAERA)

    parser.add_option("--mergeEWK", dest="mergeEWK", action="store_true", default=MERGEEWK, 
                      help="Merge all EWK samples into a single sample called \"EWK\" [default: %s]" % MERGEEWK)

    parser.add_option("--saveDir", dest="saveDir", type="string", default=SAVEDIR, 
                      help="Directory where all pltos will be saved [default: %s]" % SAVEDIR)

    parser.add_option("--url", dest="url", action="store_true", default=URL, 
                      help="Don't print the actual save path the histogram is saved, but print the URL instead [default: %s]" % URL)
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=VERBOSE, 
                      help="Enables verbose mode (for debugging purposes) [default: %s]" % VERBOSE)

    parser.add_option("--histoLevel", dest="histoLevel", action="store", default = HISTOLEVEL,
                      help="Histogram ambient level (default: %s)" % (HISTOLEVEL))

    parser.add_option("-i", "--includeOnlyTasks", dest="includeOnlyTasks", action="store", 
                      help="List of datasets in mcrab to include")

    parser.add_option("-e", "--excludeTasks", dest="excludeTasks", action="store", 
                      help="List of datasets in mcrab to exclude")

    (opts, parseArgs) = parser.parse_args()

    # Require at least two arguments (script-name, path to multicrab)
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if opts.mcrab == None:
        Print("Not enough arguments passed to script execution. Printing docstring & EXIT.")
        parser.print_help()
        #print __doc__
        sys.exit(1)

    # Call the main function
    main(opts)

    if not opts.batchMode:
        raw_input("=== plotDataDriven.py: Press any key to quit ROOT ...")
