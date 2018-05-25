#!/usr/bin/env python
'''
DESCRIPTION:


USAGE:
./plotMC_ValueVsCutflow.py -m <pseudo_mcrab_directory> [opts]


EXAMPLES:
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ -r "passed trigger" 
./plotMC_ValueVsCutflow.py  -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ -r "passed PV" --gridX --yMin 0.00001
./plotMC_ValueVsCutflow.py  -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --refCounter "passed PV" --yMin 0.00001
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --refCounter "passed PV" --yMin 0.00001


LAST USED:
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --refCounter "passed PV" --events
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --refCounter "passed PV" --efficiency
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --acceptance -e "5000|10000" --gridX --gridY
./plotMC_ValueVsCutflow.py -m Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018/ --acceptance -e "5000|10000" --gridX --gridY --yMax 400 


USE WITH:
hplusPrintCounters.py --mainCounterOnly --dataEra "Run2016" --mergeData Hplus2tbAnalysis_Preapproval_MVA0p40_Syst_28Apr2018 --includeTasks "2016|M_500"

'''

#================================================================================================ 
# Imports
#================================================================================================ 
import sys
import math
import copy
import os
import array
from optparse import OptionParser

import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import *

import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.systematics as systematics
import HiggsAnalysis.NtupleAnalysis.tools.histograms as histograms
import HiggsAnalysis.NtupleAnalysis.tools.counter as counter
import HiggsAnalysis.NtupleAnalysis.tools.tdrstyle as tdrstyle
import HiggsAnalysis.NtupleAnalysis.tools.styles as styles
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.crosssection as xsect
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux
import HiggsAnalysis.NtupleAnalysis.tools.multicrabConsistencyCheck as consistencyCheck
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
import HiggsAnalysis.NtupleAnalysis.tools.analysisModuleSelector as analysisModuleSelector
import HiggsAnalysis.NtupleAnalysis.tools.errorPropagation as errorPropagation

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


def GetDatasetsFromDir(opts):
    
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

    # Apply TDR style
    style = tdrstyle.TDRStyle()
    style.setGridX(opts.gridX)
    style.setGridY(opts.gridY)
    
    # Obtain dsetMgrCreator and register it to module selector
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=opts.mcrab)

    # Get list of eras, modes, and optimisation modes
    erasList      = dsetMgrCreator.getDataEras()
    modesList     = dsetMgrCreator.getSearchModes()
    optList       = dsetMgrCreator.getOptimizationModes()
    sysVarList    = dsetMgrCreator.getSystematicVariations()
    sysVarSrcList = dsetMgrCreator.getSystematicVariationSources()

    # If user does not define optimisation mode do all of them
    if opts.optMode == None:
        if len(optList) < 1:
            optList.append("")
        else:
            pass
        optModes = optList
    else:
        optModes = [opts.optMode]


    # For-loop: All optimisation modes
    for opt in optModes:
        opts.optMode = opt

        # Setup & configure the dataset manager 
        datasetsMgr = GetDatasetsFromDir(opts)
        datasetsMgr.updateNAllEventsToPUWeighted()
        datasetsMgr.loadLuminosities() # from lumi.json
        
        # Print PSets used for FakeBMeasurement
        if 0:
            datasetsMgr.printSelections()

        # Set/Overwrite cross-sections
        for d in datasetsMgr.getAllDatasets():
            if "ZJetsToQQ_HT600toInf" in d.getName():
                datasetsMgr.remove(d.getName())

            if "ChargedHiggs" in d.getName():
                datasetsMgr.getDataset(d.getName()).setCrossSection(1.0)
                if d.getName() not in opts.signal:
                    if not opts.acceptance:
                        datasetsMgr.remove(d.getName())

        # For acceptance plot use all available masses
        if opts.acceptance:
            opts.signal = []
            opts.signalMasses = []
            for d in datasetsMgr.getAllDatasets():
                if "ChargedHiggs" in d.getName():
                    s = d.getName()
                    m = int(d.getName().split("M_")[-1])
                    opts.signal.append(s)
                    opts.signalMasses.append(m)

        if opts.verbose:
            datasetsMgr.PrintCrossSections()
            datasetsMgr.PrintLuminosities()
            datasetsMgr.PrintInfo()
               
        # Merge histograms (see NtupleAnalysis/python/tools/plots.py) 
        plots.mergeRenameReorderForDataMC(datasetsMgr) 

        # Get Luminosity
        if opts.intLumi < 0:
            if "Data" in datasetsMgr.getAllDatasetNames():
                opts.intLumi = datasetsMgr.getDataset("Data").getLuminosity()
            else:
                opts.intLumi = 1.0

        # Merge EWK samples
        if 1:
            datasetsMgr.merge("EWK", aux.GetListOfEwkDatasets())
            plots._plotStyles["EWK"] = styles.getAltEWKStyle()
            
        # Print post EWK-merge dataset summary
        datasetsMgr.PrintInfo()

        # Get the efficiency graphs
        hGraphList = []
        histoName  = os.path.join(opts.folder, "counter")
        hGraphList, _kwargs = GetHistoGraphs(datasetsMgr, opts.folder, histoName)

        # Plot the histo graphs
        PlotHistoGraphs(hGraphList, _kwargs)

    Print("All plots saved under directory %s" % (ShellStyles.NoteStyle() + aux.convertToURL(opts.saveDir, opts.url) + ShellStyles.NormalStyle()), True)
    return


def GetHistoGraphs(datasetsMgr, folder, hName):

    # Get histogram customisations
    _kwargs  = GetHistoKwargs(opts)

    # Get histos (Data, EWK) for Inclusive
    p1 = plots.DataMCPlot(datasetsMgr, hName, saveFormats=[])
    kwargs = copy.deepcopy(_kwargs)
    kwargs["opts"]       = {"ymin": 1.0, "ymaxfactor": 10.0}
    kwargs["xlabelsize"] = 10
    kwargs["ratio"]      = False
    plots.drawPlot(p1, hName, **kwargs)
    SavePlot(p1, hName, os.path.join(opts.saveDir, opts.optMode), saveFormats = [".C", ".png", ".pdf"] )

    # Clone histograms 
    histoList = []
    graphList = []
    hgList    = []

    # Append some bkg samples as well
    opts.datasets = opts.signal
    if not opts.acceptance:        
        opts.datasets.extend(opts.backgrounds)

    for d in opts.datasets:
        h = p1.histoMgr.getHisto(d).getRootHisto().Clone(d)
        histoList.append(h)

    # Create the Efficiency histos
    for i, h in enumerate(histoList, 1):
        if opts.efficiency:
            histo = GetEfficiencyHisto(histoList[i-1], opts.refCounter, _kwargs, printValues=True, hideZeros=True)
            histo.SetName("Efficiency_%d" % (i))
        elif opts.events:
            histo = GetEventsHisto(histoList[i-1], opts.refCounter, _kwargs, printValues=True, hideZeros=True)
            histo.SetName("Events_%d" % (i))
        elif opts.acceptance:
            histo = GetAcceptanceHisto(histoList[i-1], _kwargs, printValues=True, hideZeros=True)
            histo.SetName("Acceptance_%d" % (i))
        
        # Convert histos to TGraph (don't do it for acceptance to get better positioning of markers wrt x-axis!)
        if not opts.acceptance:
            tgraph = convertHisto2TGraph(histo, printValues=False)
        else:
            tgraph = histo

        # Apply random histo styles  and append
        if "charged" in h.GetName().lower():
            s = styles.getSignalStyleHToTB_M(h.GetName().split("M_")[-1])
            s.apply(tgraph)
            
        if "QCD" in  h.GetName():
            styles.fakeBStyle.apply(tgraph)
        if "EWK" in  h.GetName():
            s = styles.ttStyle.apply(tgraph)

        # Append to list
        graphList.append(tgraph)
        
        # Create histoGraph object
        htgraph = histograms.HistoGraph( tgraph, plots._legendLabels[opts.signal[i-1]], "LP", "LP")
        
        # Append to list
        hgList.append(htgraph)
        
    return hgList, _kwargs


def PlotHistoGraphs(hGraphList, _kwargs):
    
    # Create & draw the plot    
    p = plots.ComparisonManyPlot(hGraphList[0], hGraphList[1:], saveFormats=[])
    p.setLuminosity(opts.intLumi)

    if 0:
        p.histoMgr.setHistoLegendStyleAll("P")
        p.histoMgr.setHistoDrawStyleAll("LP")
        p.histoMgr.setHistoDrawStyle(hGraphList[0].getRootHisto().GetName(), "HIST")

    if opts.saveName == None:
        opts.saveName = hGraphList[0].getRootHisto().GetName().split("_")[0] + "VsCutflow"

    # Draw the plot
    p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetLineStyle(ROOT.kSolid))
    p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetLineWidth(3))
    p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetMarkerSize(1.3)) #1.2 
    if opts.acceptance:
        p.histoMgr.forEachHisto(lambda h: h.getRootHisto().SetMarkerStyle(ROOT.kFullCircle))
    plots.drawPlot(p, opts.saveName, **_kwargs)

    if not opts.acceptance:
        p.getPad2().SetLogy(True)

    # Add some text
    if opts.refCounter == "passed PV":
        xPos  = [0.15, 0.24, 0.37, 0.50, 0.65, 0.77, 0.90] #does not work for every reference counter!
    else:
        xPos = [0.15 + float(i)/(float(len(opts.binLabels))) for i in range(0, len(opts.binLabels))]

    # For-loop: All bin labels
    for i, b in enumerate(opts.binLabels, 0): 
        if opts.acceptance:
            break

        # Calculate coordinats
        dx     = 0.10*(i)
        dy     = 0.0
        if _kwargs["ratio"]:
            dy = -0.4

        # Basic text replacemenets to get compact bin text
        bin   = b.replace("passed ", "").replace(")", "").replace("selection", "").replace("(", "").replace("Selection", "").replace("PV", "pv")
        label = bin.replace("mu", "#mu").replace("Passed", "").replace("tau", "#tau").replace("  Veto", "-veto").replace("Selected Events", "selected")
        label = label.replace("jet", "jets").replace("-", " ")

        if 1:
            #histograms.addText(0.16+dx, 0.08+dy, label, 19)
            histograms.addText(xPos[i], 0.08+dy, label, 19)
        else:
            # Automatic assignment (not perfect, yet!)
            x     = opts.xValues[i]/opts.xValues[-1]
            xlow  = opts.xErrLow[i]/opts.xErrLow[-1]
            xhigh = opts.xErrHigh[i]/opts.xErrHigh[-1]
            if i == 0:
                x = 0.15
            if i > 2:
                x -= 0.05
            if i == len(opts.binLabels)-1:
                x = 0.92
            if not opts.acceptance:
                histograms.addText(x, 0.08+dy, label, 19)
            
    # Save the plot
    SavePlot(p, opts.saveName, os.path.join(opts.saveDir, opts.optMode), saveFormats = [".C", ".png", ".pdf"] )
    return


def GetHistoKwargs(opts):
    histoKwargs = {}
    canvOpts    = {"ymin": 1e-1, "ymaxfactor": 3}
    ratioOpts   = {"ymin": 5e-4, "ymax": 10},
    mvLegend    = {"dx": -0.53, "dy": -0.1, "dh": -0.10}
    xlabel      = None
    ylabel      = "y-label"
    xLabelSize  = 0
    logy        = True
    errorsX     = False

    if opts.acceptance:
        #canvOpts    = {"ymin": 1, "ymaxfactor": 1.1}
        canvOpts    = {"xmin": min(opts.signalMasses), "xmax": max(opts.signalMasses), "ymin": 1, "ymax": 300, "ymaxfactor": 1.1}
        ratioOpts   = {"ymin": 1e-1, "ymax": 1.3e6}
        #mvLegend    = {"dx": -9999.9, "dy": -9999.9, "dh": -9999.9}
        mvLegend    = {"dx": -0.1, "dy": -0.01, "dh": +0.20}
        xlabel      = "m_{H^{+}} (GeV/c^{2})"
        ylabel      = "Events" #"Acceptance"
        ratio       = False
        logy        = False
        xLabelSize  = None
        #errorsX     = True

    if opts.events:
        mvLegend    = {"dx": -0.53 , "dy": -0.6, "dh": -0.05}
        canvOpts    = {"ymin": 1, "ymaxfactor": 3 }
        ratioOpts   = {"ymin": 1e-1, "ymax": 1.3e6}
        ylabel      = "Events"
        ratio       = True

    if opts.efficiency:
        mvLegend    = {"dx": -0.53 , "dy": -0.6, "dh": -0.05}
        canvOpts    = {"ymin": 1e-5, "ymaxfactor": 3 }
        ratioOpts   = {"ymin": 1e-3, "ymax": 10}
        ylabel      = "Efficiency"
        ratio       = True

    if opts.yMin != None:
        canvOpts["ymin"] = opts.yMin

    if opts.yMax != None:
        canvOpts["ymax"] = opts.yMax

    _kwargs     = {
        "xlabel"           : xlabel,
        "ylabel"           : ylabel,
        "ratioYlabel"      : "Ratio ",
        "ratio"            : ratio,
        "ratioInvert"      : False,
        "stackMCHistograms": False,
        "addMCUncertainty" : True,
        "addLuminosityText": True,
        "addCmsText"       : True,
        "errorBarsX"       : errorsX,
        "cmsExtraText"     : "Preliminary",
        "opts"             : canvOpts,
        "opts2"            : ratioOpts,
        "log"              : logy,
        "moveLegend"       : mvLegend, 
        "cutBox"           : {"cutValue": 1.0, "fillColor": 16, "box": False, "line": False, "greaterThan": True},
        # "cutBoxY"          : {"cutValue": 1.0, "fillColor": 16, "box": False, "line": True, "greaterThan": True, "mainCanvas": True, "ratioCanvas": False},
        "xlabelsize"       : xLabelSize
        }

    # Set x-axis divisions
    n1 = 10 # primary divisions (8)
    n2 = 0 # second order divisions (5)
    n3 = 0 # third order divisions (@)
    if opts.acceptance:
        n1 = 8
        n2 = 5

    nDivs = n1 + 100*n2 + 10000*n3
    ROOT.gStyle.SetNdivisions(nDivs, "X")
    return _kwargs


def GetSaveName(histoName):
    base = histoName.split("_")[0]
    var  = histoName.split("_")[1]
    sel  = histoName.split("_")[2]
    name = var + "_" + GetControlRegionLabel(histoName)
    return name


def SavePlot(plot, plotName, saveDir, saveFormats = [".C", ".png", ".pdf"]):
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # Create the name under which plot will be saved
    saveName = os.path.join(saveDir, plotName.replace("/", "_"))

    # For-loop: All save formats
    for i, ext in enumerate(saveFormats):
        saveNameURL = saveName + ext
        saveNameURL = aux.convertToURL(saveNameURL, opts.url)
        Print(saveNameURL, i==0)
        plot.saveAs(saveName, formats=saveFormats)
    return

def convertHisto2TGraph(histo, printValues=False):

    # Lists for values
    x      = []
    y      = []
    xerrl  = []
    xerrh  = []
    yerrl  = []
    yerrh  = []
    nBinsX = histo.GetNbinsX()
    opts.xValues  = []
    opts.xErrLow  = []
    opts.xErrHigh = []

    # For-loop: All histogram bins
    nBinsX_ = 0
    for i in range(1, nBinsX+1):

        # Get values
        xVal  = histo.GetBinLowEdge(i) +  0.5*histo.GetBinWidth(i)
        # Visually better to have zero x-bar
        if 1:
            xLow  = 0.0001
            xHigh = 0.0001
        else:
            xLow  = 0.5*histo.GetBinWidth(i)
            xHigh = 0.5*histo.GetBinWidth(i)
        yVal  = histo.GetBinContent(i)
        yLow  = histo.GetBinError(i)
        yHigh = yLow            

        if yVal == 0:
            continue

        # Update the number of bins
        nBinsX_ += 1

        # Store values
        x.append(xVal)
        xerrl.append(xLow)
        xerrh.append(xHigh)

        y.append(yVal)
        yerrl.append(yLow)
        yerrh.append(yHigh)
        
        # For x-axis labels
        opts.xValues.append(xVal)
        opts.xErrLow.append(xVal - 0.5*histo.GetBinWidth(i))
        opts.xErrHigh.append(xVal + 0.5*histo.GetBinWidth(i))


    # Create the TGraph with asymmetric errors
    tgraph = ROOT.TGraphAsymmErrors(nBinsX_,
                                    array.array("d", x),
                                    array.array("d", y),
                                    array.array("d", xerrl),
                                    array.array("d", xerrh),
                                    array.array("d", yerrl),
                                    array.array("d", yerrh))
    # Set the correct name
    tgraph.SetName(histo.GetName())

    # Construct info table (debugging)
    table  = []
    align  = "{:>6} {:^10} {:>10} {:>10} {:>10} {:^3} {:<10}"
    header = align.format("#", "xLow", "x", "xUp", "Efficiency", "+/-", "Error") #Purity = 1-EWK/Data
    hLine  = "="*70
    table.append("")
    table.append(hLine)
    table.append("{:^70}".format("TGraph"))
    table.append(header)
    table.append(hLine)
    
    # For-loop: All values x-y and their errors
    for i, xV in enumerate(x, 0):
        row = align.format(i+1, "%.2f" % xerrl[i], "%.2f" %  x[i], "%.2f" %  xerrh[i], "%.5f" %  y[i], "+/-", "%.5f" %  yerrh[i])
        table.append(row)
    table.append(hLine)

    if printValues:
        for i, line in enumerate(table, 1):
            Print(line, False) #i==1)
    return tgraph


def GetEfficiencyHisto(histo, refCounter, kwargs, printValues=False, hideZeros=True):
    
    # Define histos here
    xMax = histo.GetXaxis().GetXmax()
    hEff = ROOT.TH1D('Eff','Eff', int(xMax), 0, xMax)
    hNum = ROOT.TH1D('Num','Num', 1, 0, 1)
    hDen = ROOT.TH1D('Den','Den', 1, 0, 1)

    # Construct info table (debugging)
    table  = []
    align  = "{:>6} {:^20} {:<35} {:>15} {:>15} {:>10} {:^3} {:<10}"
    header = align.format("Bin", "Range", "Selection", "Numerator", "Denominator", "Eff Value", "+/-", "Eff Error")
    hLine  = "="*120
    nBinsX = histo.GetNbinsX()
    table.append("{:^100}".format(histo.GetName()))
    table.append(hLine)
    table.append(header)
    table.append(hLine)

    # First determine the bin number
    binNumber = -1
    for j in range (0, nBinsX+1):

        # Skip this counter?
        binLabel = histo.GetXaxis().GetBinLabel(j)

        if binLabel == refCounter:
            binNumber = j
        else:
            continue

    if binNumber == -1:
        raise Exception("Could not find reference counter \"%s\"" % refCounter)

    if binNumber > nBinsX:
        raise Exception("Invalid bin selected (bin = %d" % (binNumber) ) 

    # First get numerator
    denValue = ROOT.Double(0.0)
    denError = ROOT.Double(0.0)
    denValue = histo.IntegralAndError(binNumber, binNumber, denError)
    ROOT.gErrorIgnoreLevel = ROOT.kFatal #kPrint = 0,  kInfo = 1000, kWarning = 2000, kError = 3000, kBreak = 4000, kSysError = 5000, kFatal = 6000   

    # For-loop: All histogram bins
    binCounter = 0
    opts.binLabels = []
    for j in range (binNumber, nBinsX+1):

        # Skip this counter?
        binLabel = histo.GetXaxis().GetBinLabel(j)
        if binLabel in opts.skipList:
            Verbose("Skipping counter with name \"%s\"" % (binLabel), True)
            continue

        # Declare variables
        numValue    = ROOT.Double(0.0)
        numError    = ROOT.Double(0.0)
        numValue    = histo.IntegralAndError(j, j, numError)
        effValue    = 0
        effError    = 0

        # Sanity
        if numValue < 0.0:
            raise Exception("Integral is less than zero!")
        if numError < 0.0:
            raise Exception("Error is less than zero!")
        
        # Numerator and Denominator histos
        Verbose("Evaluating efficiency for \"%s\"" % (binLabel), j==binNumber)
        hNum.SetBinContent(1, numValue)
        hNum.SetBinError(1, numError)
        hDen.SetBinContent(1, denValue)
        hDen.SetBinError(1, denError)


        # Calculate Efficiency
        teff = ROOT.TEfficiency(hNum, hDen)
        teff.SetStatisticOption(ROOT.TEfficiency.kFNormal) #statistic option is 'normal approximation'
        effValue = teff.GetEfficiency(1)
        effError = teff.GetEfficiencyErrorLow(1)

        # Bin-range or overflow bin?
        binRange = "%.1f -> %.1f" % (histo.GetXaxis().GetBinLowEdge(j), histo.GetXaxis().GetBinUpEdge(j) )
        if j >= nBinsX:
            binRange = "> %.1f"   % (histo.GetXaxis().GetBinLowEdge(j) )

        # Fill histogram
        binCounter+= 1
        hEff.SetBinContent(binCounter, effValue)
        hEff.SetBinError(binCounter, effError)

        # Save bin labels 
        opts.binLabels.append(binLabel)

        # Save information in table
        row = align.format(binCounter, binRange, binLabel, "%.1f" % numValue, "%.1f" % denValue, "%.5f" % effValue, "+/-", "%.5f" % effError)
        table.append(row)

        # Reset histos 
        hNum.Reset()
        hDen.Reset()               

    # Finalise table
    table.append(hLine)

    # Print purity as function of final shape bins
    if printValues:
        for i, line in enumerate(table):
            Print(line, i==0)

    ROOT.gErrorIgnoreLevel = ROOT.kWarning #kPrint = 0,  kInfo = 1000, kWarning = 2000, kError = 3000, kBreak = 4000, kSysError = 5000, kFatal = 6000   
    return hEff


def GetEventsHisto(histo, refCounter, kwargs, printValues=False, hideZeros=True):

    # Define the histo
    xMin  = 0
    xMax  = histo.GetXaxis().GetXmax()
    nBins = int(xMax)
    hEvts = ROOT.TH1D('Evts','Evts', nBins, xMin, xMax)

    # Construct info table (debugging)
    table  = []
    align  = "{:>6} {:^20} {:<35} {:>10} {:^3} {:<10}"
    header = align.format("Bin", "Range", "Selection", "Events", "+/-", "Stat.")
    hLine  = "="*120
    nBinsX = histo.GetNbinsX()
    table.append("{:^100}".format(histo.GetName()))
    table.append(hLine)
    table.append(header)
    table.append(hLine)

    # First determine the bin number of the reference counter
    binNumber = -1
    for j in range (0, nBinsX+1):

        # Skip this counter?
        binLabel = histo.GetXaxis().GetBinLabel(j)

        if binLabel == refCounter:
            binNumber = j
        else:
            continue

    if binNumber == -1:
        raise Exception("Could not find reference counter \"%s\"" % refCounter)

    if binNumber > nBinsX:
        raise Exception("Invalid bin selected (bin = %d" % (binNumber) ) 

    # For-loop: All histogram bins
    binCounter = 0
    opts.binLabels = []
    for j in range (binNumber, nBinsX+1):

        # Skip this counter?
        binLabel = histo.GetXaxis().GetBinLabel(j)
        if binLabel in opts.skipList:
            Verbose("Skipping counter with name \"%s\"" % (binLabel), True)
            continue

        # Declare variables
        numValue    = ROOT.Double(0.0)
        numError    = ROOT.Double(0.0)
        numValue    = histo.IntegralAndError(j, j, numError)

        # Sanity
        if numValue < 0.0:
            raise Exception("Integral is less than zero!")
        if numError < 0.0:
            raise Exception("Error is less than zero!")
        
        # Bin-range or overflow bin?
        binRange = "%.1f -> %.1f" % (histo.GetXaxis().GetBinLowEdge(j), histo.GetXaxis().GetBinUpEdge(j) )
        if j >= nBinsX:
            binRange = "> %.1f"   % (histo.GetXaxis().GetBinLowEdge(j) )

        # Fill histogram
        binCounter+= 1
        hEvts.SetBinContent(binCounter, numValue)
        hEvts.SetBinError(binCounter, numError)

        # Save bin labels 
        opts.binLabels.append(binLabel)

        # Save information in table
        row = align.format(binCounter, binRange, binLabel, "%.5f" % numValue, "+/-", "%.5f" % numError)
        table.append(row)

    # Finalise table
    table.append(hLine)

    # Print purity as function of final shape bins
    if printValues:
        for i, line in enumerate(table):
            Print(line, i==0)

    ROOT.gErrorIgnoreLevel = ROOT.kWarning #kPrint = 0,  kInfo = 1000, kWarning = 2000, kError = 3000, kBreak = 4000, kSysError = 5000, kFatal = 6000   
    return hEvts

def GetAcceptanceHisto(histo, kwargs, printValues=False, hideZeros=True):

    refCounter = "Selected Events"

    # Define the histo
    xMin  = 0.0 #180
    xMax  = 10000
    nBins = int(xMax)
    hEvts = ROOT.TH1D('Evts','Evts', nBins, xMin, xMax)

    # Construct info table (debugging)
    table  = []
    align  = "{:>6} {:^20} {:<35} {:>10} {:^3} {:<10}"
    header = align.format("Bin", "Range", "Selection", "Events", "+/-", "Stat.")
    hLine  = "="*120
    nBinsX = histo.GetNbinsX()
    table.append("{:^100}".format(histo.GetName()))
    table.append(hLine)
    table.append(header)
    table.append(hLine)

    # First determine the bin number of the reference counter
    binNumber = -1
    for j in range (0, nBinsX+1):
        
        mass = int(histo.GetName().split("M_")[-1])

        # Skip this counter?
        binLabel = histo.GetXaxis().GetBinLabel(j)

        if binLabel == refCounter:
            binNumber = j
        else:
            continue

    if binNumber == -1:
        raise Exception("Could not find reference counter \"%s\"" % refCounter)

    if binNumber > nBinsX:
        raise Exception("Invalid bin selected (bin = %d" % (binNumber) ) 

    # For-loop: All histogram bins
    opts.binLabels = [refCounter]

    # Declare variables
    numValue    = ROOT.Double(0.0)
    numError    = ROOT.Double(0.0)
    numValue    = histo.IntegralAndError(binNumber, binNumber, numError)

    # Bin-range or overflow bin?
    binRange = "%.1f -> %.1f" % (histo.GetXaxis().GetBinLowEdge(binNumber), histo.GetXaxis().GetBinUpEdge(binNumber) )
    if j >= nBinsX:
        binRange = "> %.1f"   % (histo.GetXaxis().GetBinLowEdge(binNumber) )

    # Fill histogram
    hEvts.SetBinContent(mass, numValue)
    hEvts.SetBinError(mass, numError)

    # Save bin labels 
    opts.binLabels.append(binLabel)

    # Save information in table
    row = align.format(binNumber, binRange, binLabel, "%.5f" % numValue, "+/-", "%.5f" % numError)
    table.append(row)
        
    # Finalise table
    table.append(hLine)

    # Print purity as function of final shape bins
    if printValues:
        for i, line in enumerate(table):
            Print(line, i==0)

    ROOT.gErrorIgnoreLevel = ROOT.kWarning #kPrint = 0,  kInfo = 1000, kWarning = 2000, kError = 3000, kBreak = 4000, kSysError = 5000, kFatal = 6000   
    return hEvts

#================================================================================================ 
# Main
#================================================================================================ 
if __name__ == "__main__":
    '''g1

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
    OPTMODE      = ""
    BATCHMODE    = True
    INTLUMI      = -1.0
    URL          = False
    SAVEDIR      = None
    SAVENAME     = None #"EfficiencyVsCutflow"
    VERBOSE      = False
    FOLDER       = "counters/weighted/" #"counters"
    SIGNALMASS   = [180, 300, 500, 800]
    BACKGROUNDS  = ["EWK", "QCD"]
    REFCOUNTER   = "ttree: skimCounterAll"   #"passed trigger"
    SKIPLIST     = ["Passed tau selection and genuine (Veto)", "b tag SF", "passed fat jet selection (Veto)", "Selected Events",  "passed METFilter selection ()"]
    GRIDX        = False
    GRIDY        = False
    YMIN         = None
    YMAX         = None
    ACCEPTANCE   = False
    EFFICIENCY   = False
    EVENTS       = False

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

    parser.add_option("--intLumi", dest="intLumi", type=float, default=INTLUMI,
                      help="Override the integrated lumi [default: %s]" % INTLUMI)

    parser.add_option("-r", "--refCounter", dest="refCounter", type="string", default=REFCOUNTER,
                      help="Counter name to use as reference for calculating the relative efficiency of all other cuts [default: %s]" % REFCOUNTER)

    parser.add_option("--searchMode", dest="searchMode", type="string", default=SEARCHMODE,
                      help="Override default searchMode [default: %s]" % SEARCHMODE)

    parser.add_option("--yMin", dest="yMin", type=float, default=YMIN,
                      help="Minimum value of y-axis [default: %s]" % YMIN)

    parser.add_option("--yMax", dest="yMax", type=float, default=YMAX,
                      help="Maxmimum value of y-axis [default: %s]" % YMAX)

    parser.add_option("--gridX", dest="gridX", action="store_true", default=GRIDX,
                      help="Enable the grid in x-axis [default: %s]" % GRIDX)

    parser.add_option("--gridY", dest="gridY", action="store_true", default=GRIDY,
                      help="Enable the grid in y-axis [default: %s]" % GRIDY)

    parser.add_option("--dataEra", dest="dataEra", type="string", default=DATAERA, 
                      help="Override default dataEra [default: %s]" % DATAERA)

    parser.add_option("--saveDir", dest="saveDir", type="string", default=SAVEDIR, 
                      help="Directory where all pltos will be saved [default: %s]" % SAVEDIR)

    parser.add_option("--saveName", dest="saveName", type="string", default=SAVENAME, 
                      help="The Name of the histogram as it will be saved [default: %s]" % SAVENAME)

    parser.add_option("--url", dest="url", action="store_true", default=URL, 
                      help="Don't print the actual save path the histogram is saved, but print the URL instead [default: %s]" % URL)
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=VERBOSE, 
                      help="Enables verbose mode (for debugging purposes) [default: %s]" % VERBOSE)

    parser.add_option("--acceptance", dest="acceptance", action="store_true", default=ACCEPTANCE, 
                      help="Enables acceptance plots (instead of efficiency plots) [default: %s]" % ACCEPTANCE)

    parser.add_option("--efficiency", dest="efficiency", action="store_true", default=EFFICIENCY, 
                      help="Enables efficiency plots (instead of acceptance or events plots) [default: %s]" % EFFICIENCY)

    parser.add_option("--events", dest="events", action="store_true", default=EVENTS, 
                      help="Enables events plots (instead of acceptance or events plots) [default: %s]" % EVENTS)

    parser.add_option("-i", "--includeOnlyTasks", dest="includeOnlyTasks", action="store", 
                      help="List of datasets in mcrab to include")

    parser.add_option("-e", "--excludeTasks", dest="excludeTasks", action="store", 
                      help="List of datasets in mcrab to exclude")

    parser.add_option("--folder", dest="folder", type="string", default = FOLDER,
                      help="ROOT file folder under which all histograms to be plotted are located [default: %s]" % (FOLDER) )

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
        
    # Define counters to skip (if for example empty)
    opts.skipList = SKIPLIST

    # Define save directory
    if opts.saveDir == None:
        opts.saveDir = aux.getSaveDirPath(opts.mcrab, prefix="", postfix="MC")
        
    # Sanity check
    allowedFolders = ["counters", "counters/weighted/"]
    if opts.folder not in allowedFolders:
        Print("Invalid folder \"%s\"! Please select one of the following:" % (opts.folder), True)
        for m in allowedFolders:
            Print(m, False)
        sys.exit()

    # Signal list
    opts.signal     = []
    opts.signalMass = SIGNALMASS
    for m in SIGNALMASS:
        signal = "ChargedHiggs_HplusTB_HplusToTB_M_%i" % m
        opts.signal.append(signal)

    # Bkg list
    opts.backgrounds = []
    for b in BACKGROUNDS:
        opts.backgrounds.append(b)

    # Call the main function
    main(opts)

    if not opts.batchMode:
        raw_input("=== plot_ValueVsCutflow.py: Press any key to quit ROOT ...")
