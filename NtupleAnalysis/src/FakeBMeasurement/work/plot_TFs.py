#!/usr/bin/env python
'''
DESCRIPTION:
Try to prove that there is not systematics associated with the
definition of the Control Region (CR). In the FakeB measurement
we define the CR2 and VR by inverting both the b-jet selection
and the 2nd top BDT. 

Here, we need to show that moving the BDT of the second top to smaller
values than the maximum allowable one (default) does not change
the closure tests.


USAGE:
./plot_TFs.py -m <pseudo_mcrab1> -n <pseudo_mcrab2> -l <pseudo_mcrab3> [opts]


EXAMPLES:
./plot_TFs.py -m FakeBMeasurement_3CSVv2M_Default_22Nov2018 -n FakeBMeasurement_BDT0p4_dBDTm0p2_23Nov2018 -l FakeBMeasurement_BDT0p4_dBDTm0p4_23Nov2018 --logY
./plot_TFs.py -m FakeBMeasurement_3CSVv2M_Default_22Nov2018,FakeBMeasurement_BDT0p4_dBDTm0p2_23Nov2018,FakeBMeasurement_BDT0p4_dBDTm0p4_23Nov2018,FakeBMeasurement_BDT0p6_dBDTm0p4_23Nov2018,FakeBMeasurement_BDT0p6_dBDTm0p2_23Nov2018 --bandValue 5


LAST USED:
./plot_TFs.py -m FakeBMeasurement_3CSVv2M_Default_22Nov2018,FakeBMeasurement_BDT0p4_dBDTm0p2_23Nov2018,FakeBMeasurement_BDT0p4_dBDTm0p4_23Nov2018 --bandValue 5

'''

#================================================================================================ 
# Imports
#================================================================================================ 
import sys
import math
import copy
import os
import array
import imp
import re
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
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux
import HiggsAnalysis.NtupleAnalysis.tools.systematics as systematics
import HiggsAnalysis.NtupleAnalysis.tools.crosssection as xsect
import HiggsAnalysis.NtupleAnalysis.tools.multicrabConsistencyCheck as consistencyCheck
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
import HiggsAnalysis.FakeBMeasurement.FakeBNormalization as FakeBNormalization


#================================================================================================ 
# Definitions
#================================================================================================ 
ss = ShellStyles.SuccessStyle()
ns = ShellStyles.NormalStyle()
ts = ShellStyles.NoteStyle()
ls = ShellStyles.HighlightStyle()
hs = ShellStyles.HighlightAltStyle()
es = ShellStyles.ErrorStyle()
styleList = [styles.Style(24, ROOT.kBlack)] + styles.getStyles()

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
    aux.Print(msg, printHeader)
    return


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


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


def GetDatasetsFromDir(mcrab, opts):
    if (not opts.includeOnlyTasks and not opts.excludeTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode, 
                                                        analysisName=opts.analysisName,
                                                        optimizationMode=opts.optMode)
    elif (opts.includeOnlyTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode,
                                                        analysisName=opts.analysisName,
                                                        includeOnlyTasks=opts.includeOnlyTasks,
                                                        optimizationMode=opts.optMode)
    elif (opts.excludeTasks):
        datasets = dataset.getDatasetsFromMulticrabDirs([mcrab],
                                                        dataEra=opts.dataEra,
                                                        searchMode=opts.searchMode,
                                                        analysisName=opts.analysisName,
                                                        excludeTasks=opts.excludeTasks,
                                                        optimizationMode=opts.optMode)
    else:
        raise Exception("This should never be reached")
    return datasets
    

def setGraphStyle(graph):
    graph.SetLineStyle(2)
    graph.SetLineWidth(3)
    graph.SetLineColor(ROOT.kBlack)
    graph.SetMarkerStyle(20)
    return


def SavePlot(plot, plotName, saveFormats = [".C", ".png", ".pdf"]):
    if not os.path.exists(opts.saveDir):
        os.makedirs(opts.saveDir)

    # Create the name under which plot will be saved
    saveName = os.path.join(opts.saveDir, plotName.replace("/", "_"))
    
    # For-loop: All save formats
    for i, ext in enumerate(saveFormats):
        saveNameURL = saveName + ext
        saveNameURL = aux.convertToURL(saveNameURL, opts.url)
        Print(saveNameURL, i==0)
        plot.saveAs(saveName, formats=saveFormats)
    return

def PlotGraphs(legendLabels, graphs, saveName="SaveName"):
    
    # Definitions
    hg = []
    ll = {}
    nGraphs = len(graphs)

    # For-loop: All HistoGraphs
    for i in xrange(nGraphs):
        gName = graphs[i].GetName()
        hg.append(histograms.HistoGraph(graphs[i], gName, drawStyle="P", legendStyle="lp"))
        ll[gName] = legendLabels[i]

    # Create a plot-base object
    p = plots.ComparisonManyPlot(hg[0], hg[1:], saveFormats=[])
    p.histoMgr.forEachHisto(styles.Generator(styleList[0:nGraphs]))
    
    # Take care of styling
    def sty(h):
        r = h.getRootHisto()
        r.SetMarkerSize(1.2)
        r.SetLineWidth(2)
        r.SetLineStyle(ROOT.kSolid)
        return

    # Apply style and set label
    p.histoMgr.forEachHisto(sty)
    p.histoMgr.setHistoLegendLabelMany(ll)
    
    # Set draw/legend style
    p.createFrame("c_" + saveName, opts={})
    # plots.drawPlot(p, saveName, **GetKwargs(saveName))

    # Enable/Disable logscale for axes 
    ROOT.gPad.SetLogx(opts.logX)
    ROOT.gPad.SetLogy(opts.logY)

    # Add cut line?
    if opts.cutLineX != 999.9:
        kwargs = {"greaterThan": True}
        p.addCutBoxAndLine(cutValue=opts.cutLineX, fillColor=ROOT.kRed, box=False, line=True, **kwargs)

    if opts.cutLineY != 999.9:
        kwargs = {"greaterThan": True, "mainCanvas": True, "ratioCanvas": False}
        p.addCutBoxAndLineY(cutValue=opts.cutLineY, fillColor=ROOT.kRed, box=False, line=True, **kwargs)

    if opts.bandValue != 0:
        kwargs = {"cutValue": 1.0 + float(opts.bandValue)/100.0, "fillColor": ROOT.kGray, "fillStyle": 3001, "box": False, "line": True, "greaterThan": True, "mainCanvas": False, "ratioCanvas": True, "mirror": True}
        p.addCutBoxAndLineY(**kwargs)    

    # Save plots and return
    plots.drawPlot(p, saveName, **GetKwargs(saveName))
    SavePlot(p, saveName, [".png", ".C", ".pdf"])
    return


def main(opts):

    # Apply TDR style
    style = tdrstyle.TDRStyle()
    style.setOptStat(False)
    style.setGridX(opts.gridY)
    style.setGridY(opts.gridX)

    # Obtain dsetMgrCreator and register it to module selector
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=opts.mcrabs[0])    
    fileName = "FakeBTransferFactors_Run2016_80to1000.py"    

    # Dictionaries to store data
    tf_Value       = {}
    tf_Error       = {}
    tf_ErrorUp     = {}
    tf_ErrorUp2x   = {}
    tf_ErrorUp3x   = {}
    tf_ErrorDown   = {}
    tf_ErrorDown2x = {}
    tf_ErrorDown3x = {}
    tf_BinLabelMap = {}

    # For-loop: All multicrabs
    for i, d in enumerate(opts.mcrabs, 1):

        # Import the transfer factors file
        filePath   = os.path.join(d, fileName)
        importName = 'tf_%s' % (d)
        msg = "Importing file %s as %s" % (hs + filePath + ns, importName)
        Print(msg, i==1)

        # Save imported values
        iFile= imp.load_source(importName, filePath)
        tf_Value[d]        = iFile.FakeBNormalisation_Value # bin number -> TF
        tf_Error[d]        = iFile.FakeBNormalisation_Error # bin number -> TF error
        tf_ErrorUp[d]      = iFile.FakeBNormalisation_ErrorUp
        tf_ErrorUp2x[d]    = iFile.FakeBNormalisation_ErrorUp2x
        tf_ErrorUp3x[d]    = iFile.FakeBNormalisation_ErrorUp3x
        tf_ErrorDown[d]    = iFile.FakeBNormalisation_ErrorDown
        tf_ErrorDown2x[d]  = iFile.FakeBNormalisation_ErrorDown2x
        tf_ErrorDown3x[d]  = iFile.FakeBNormalisation_ErrorDown3x
        tf_BinLabelMap[d]  = iFile.BinLabelMap # bin number -> bin label

    # Definitions
    gValues       = []
    gErrors       = []
    gErrorsUp     = []
    gErrorsUp2x   = []
    gErrorsUp3x   = []
    gErrorsDown   = []
    gErrorsDown2x = []
    gErrorsDown3x = []
    myLegends     = []
    legendsDict   = {}
    legendsDict["FakeBMeasurement_3CSVv2M_Default_22Nov2018"] = "BDT < 0.4"
    legendsDict["FakeBMeasurement_BDT0p4_dBDTm0p2_23Nov2018"] = "BDT < 0.4, #deltaBDT = -0.2"
    legendsDict["FakeBMeasurement_BDT0p4_dBDTm0p4_23Nov2018"] = "BDT < 0.4, #deltaBDT = -0.4"
    legendsDict["FakeBMeasurement_BDT0p6_dBDTm0p4_23Nov2018"] = "BDT < 0.6, #deltaBDT = -0.4"
    legendsDict["FakeBMeasurement_BDT0p6_dBDTm0p2_23Nov2018"] = "BDT < 0.6, #deltaBDT = -0.2"

    # For-loop: All values
    for i, d in enumerate(opts.mcrabs, 1):

        # Get key
        k = opts.mcrabs[i-1]

        # Extract values for pseudo-multicrab "k" from the dictionary
        TF_Value       = tf_Value[k]
        TF_Error       = tf_Error[k]
        TF_ErrorUp     = tf_ErrorUp[k]
        TF_ErrorUp2x   = tf_ErrorUp2x[k]
        TF_ErrorUp3x   = tf_ErrorUp3x[k]
        TF_ErrorDown   = tf_ErrorDown[k]
        TF_ErrorDown2x = tf_ErrorDown2x[k]
        TF_ErrorDown3x = tf_ErrorDown3x[k]

        # Create lists for futre array casting
        lTF_Value       = []
        lTF_Error       = []
        lTF_ErrorUp     = []
        lTF_ErrorUp2x   = []
        lTF_ErrorUp3x   = []
        lTF_ErrorDown   = []
        lTF_ErrorDown2x = []
        lTF_ErrorDown3x = []

        if "Inclusive" in TF_Value.keys():
            TF_Value.pop('Inclusive', None)

        # Definitions
        myBins    = []
        myBinsE   = []
        myDumbieE = []
        myKeys    = sorted(TF_Value.keys(), key=natural_keys)
        
        # For-loop: All factorisation bins (0-19)
        for j, bin in enumerate(myKeys, 1):
            msg  = "%s: TF[%s] = %s" % (k, bin, TF_Value[bin])
            aux.PrintFlushed(ls + msg + ns, i*j==1)

            # Print bin labels (not same order as TF default plot)
            if 0:
                print "tf_BinLabelMap[%s] = %s" %  (bin, tf_BinLabelMap[d][bin])

            myBins.append(int(bin))
            myBinsE.append(1)
            myDumbieE.append(0.000000001)
            lTF_Value.append(      TF_Value[bin]       )
            lTF_Error.append(      TF_Error[bin]       )
            # lTF_ErrorUp.append(    abs( TF_Value[bin] - TF_ErrorUp[bin]    ) )
            # lTF_ErrorUp2x.append(  abs( TF_Value[bin] - TF_ErrorUp2x[bin]  ) )
            # lTF_ErrorUp3x.append(  abs( TF_Value[bin] - TF_ErrorUp3x[bin]  ) )
            # lTF_ErrorDown.append(  abs( TF_Value[bin] - TF_ErrorDown[bin]  ) )
            # lTF_ErrorDown2x.append(abs( TF_Value[bin] - TF_ErrorDown2x[bin]) )
            # lTF_ErrorDown3x.append(abs( TF_Value[bin] - TF_ErrorDown3x[bin]) )
            lTF_ErrorUp.append(    TF_ErrorUp[bin]    )
            lTF_ErrorUp2x.append(  TF_ErrorUp2x[bin]  )
            lTF_ErrorUp3x.append(  TF_ErrorUp3x[bin]  )
            lTF_ErrorDown.append(  TF_ErrorDown[bin]  )
            lTF_ErrorDown2x.append(TF_ErrorDown2x[bin])
            lTF_ErrorDown3x.append(TF_ErrorDown3x[bin])

        # Convert lists to arrays
        myLegends.append( legendsDict[k])
        aBins           = array.array("d", myBins)
        aBinsE          = array.array("d", myBinsE)
        aDumbieE        = array.array("d", myDumbieE)
        aTF_Value       = array.array("d", lTF_Value)
        aTF_Error       = array.array("d", lTF_Error)
        aTF_ErrorUp     = array.array("d", lTF_ErrorUp)
        aTF_ErrorUp2x   = array.array("d", lTF_ErrorUp2x)
        aTF_ErrorUp3x   = array.array("d", lTF_ErrorUp3x)
        aTF_ErrorDown   = array.array("d", lTF_ErrorDown)
        aTF_ErrorDown2x = array.array("d", lTF_ErrorDown2x) 
        aTF_ErrorDown3x = array.array("d", lTF_ErrorDown3x)
 
        # Make TGraphs (TF values)
        nPoints = len(myBins)
        #gr = ROOT.TGraphErrors(nPoints, aBins, aTF_Value, aTF_Error) #no support for ratio canvas!
        #gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_Value, aBinsE, aBinsE, aTF_ErrorDown, aTF_ErrorUp)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_Value, aBinsE, aBinsE, aTF_Error, aTF_Error)
        gr.SetName("%s-Value" % k)
        gValues.append(gr)

        # Make TGraphs (TF errors)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_Error, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-Error" % k)
        gErrors.append(gr)

        # Make TGraphs (TF errors up)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorUp, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorUp" % k)
        gErrorsUp.append(gr)

        # Make TGraphs (TF errors up2x)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorUp2x, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorUp2x" % k)
        gErrorsUp2x.append(gr)

        # Make TGraphs (TF errors up2x)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorUp3x, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorUp3x" % k)
        gErrorsUp3x.append(gr)

        # Make TGraphs (TF errors down)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorDown, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorDown" % k)
        gErrorsDown.append(gr)

        # Make TGraphs (TF errors down2x)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorDown2x, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorDown2x" % k)
        gErrorsDown2x.append(gr)

        # Make TGraphs (TF errors down2x)
        gr = ROOT.TGraphAsymmErrors(nPoints, aBins, aTF_ErrorDown3x, aBinsE, aBinsE, aDumbieE, aDumbieE)
        gr.SetName("%s-ErrorDown3x" % k)
        gErrorsDown3x.append(gr)
    print

    # Plot all the graphs on the same canvas
    PlotGraphs(myLegends, gValues, saveName="Values")
    if 0:
        PlotGraphs(myLegends, gErrors      , saveName="Errors")
        PlotGraphs(myLegends, gErrorsUp    , saveName="ErrorsUp")
        PlotGraphs(myLegends, gErrorsUp2x  , saveName="ErrorsUp2x")
        PlotGraphs(myLegends, gErrorsUp3x  , saveName="ErrorsUp3x")
        PlotGraphs(myLegends, gErrorsDown  , saveName="ErrorsDown")
        PlotGraphs(myLegends, gErrorsDown2x, saveName="ErrorsDown2x")
        PlotGraphs(myLegends, gErrorsDown3x, saveName="ErrorsDown3x")
        
    # Contruct nominal graph
    myLegends = []
    myLegends.append("TF")
    myLegends.append("TF + 1#sigma")
    myLegends.append("TF + 2#sigma")
    myLegends.append("TF + 3#sigma")
    myLegends.append("TF - 1#sigma")
    myLegends.append("TF - 2#sigma")
    myLegends.append("TF - 3#sigma")
    gList = [gValues[0], gErrorsUp[0], gErrorsUp2x[0], gErrorsUp3x[0], gErrorsDown[0], gErrorsDown2x[0], gErrorsDown3x[0]]
    PlotGraphs(myLegends, gList, saveName="Nominal_Variations")

    # 1 Sigma
    myLegends = []
    myLegends.append("TF")
    myLegends.append("TF + 1#sigma")
    myLegends.append("TF - 1#sigma")
    gList = [gValues[0], gErrorsUp[0], gErrorsDown[0]]
    PlotGraphs(myLegends, gList, saveName="Nominal_1Sigma")

    # 2 Sigma
    myLegends = []
    myLegends.append("TF")
    myLegends.append("TF + 2#sigma")
    myLegends.append("TF - 2#sigma")
    gList = [gValues[0], gErrorsUp2x[0], gErrorsDown2x[0]]
    PlotGraphs(myLegends, gList, saveName="Nominal_2Sigma")

    # 3 Sigma
    myLegends = []
    myLegends.append("TF")
    myLegends.append("TF + 3#sigma")
    myLegends.append("TF - 3#sigma")
    gList = [gValues[0], gErrorsUp3x[0], gErrorsDown3x[0]]
    PlotGraphs(myLegends, gList, saveName="Nominal_3Sigma")

    Print("All plots saved under directory %s" % (hs + aux.convertToURL(opts.saveDir, opts.url) + ns), True)
    return


def GetKwargs(saveName):
    
    _ratio  = True
    _opts   = {"ymin": 0.0, "ymax": 1.0}
    _kwargs = {
        "ratioCreateLegend": True,
        "ratioType"        : "errorPropagation", # "errorScale"
        "ratioErrorOptions": {"numeratorStatSyst": False, "denominatorStatSyst": False}, # Include stat.+syst. to numerator (if syst globally enabled)
        "errorBarsX"       : True,
        "xlabel"           : "",
        "ylabel"           : "transfer factor",
        "ratioYlabel"      : "Ratio ",
        "ratio"            : _ratio,
        "ratioInvert"      : True, 
        "addLuminosityText": False,
        "addCmsText"       : True,
        "cmsExtraText"     : "Preliminary",
        "opts"             : _opts,
        "opts2"            : {"ymin": 0.80, "ymax": 1.20},
        "createLegend"     : {"x1": 0.52, "y1": 0.72, "x2": 0.92, "y2": 0.92},
        #"cutBox"           : _cutBox,
        }

    return _kwargs
        
def GetBinWidthMinMax(binList):
    if not isinstance(binList, list):
        raise Exception("Argument is not a list instance!")

    minWidth = +1e6
    maxWidth = -1e6
    # For-loop: All bin values (centre)
    for i in range(0, len(binList)-1):
        j = i + 1
        iBin = binList[i]
        jBin = binList[j]
        wBin = jBin-iBin
        if wBin < minWidth:
            minWidth = wBin

        if wBin > maxWidth:
            maxWidth = wBin
    return minWidth, maxWidth

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
    ANALYSISNAME = "FakeBMeasurement"
    SEARCHMODE   = "80to1000"
    DATAERA      = "Run2016"
    OPTMODE      = ""
    BATCHMODE    = True
    URL          = False
    SAVEDIR      = None
    VERBOSE      = False
    NORMALISE    = True
    SIGNALMASS   = 500
    FOLDER       = "ForFakeBMeasurement"
    LOGX         = False
    LOGY         = False
    GRIDX        = False
    GRIDY        = False
    CUTLINEX     = 999.9
    CUTLINEY     = 999.9
    BANDVALUE    = 0

    # Define the available script options
    parser = OptionParser(usage="Usage: %prog [options]")

    parser.add_option("-m", "--mcrabs", dest="mcrabs", action="store", 
                      help="Path to the multicrab directories for input (comma-seprated)")

    parser.add_option("--logX", dest="logX", action="store_true", default=LOGX, 
                      help="Set x-axis to logarithmic scalen [default: %s]" % LOGX)

    parser.add_option("--logY", dest="logY", action="store_true", default=LOGY, 
                      help="Set y-axis to logarithmic scalen [default: %s]" % LOGY)

    parser.add_option("--gridX", dest="gridX", action="store_true", default=GRIDX, 
                      help="Enable the x-axis grid [default: %s]" % GRIDX)

    parser.add_option("--gridY", dest="gridY", action="store_true", default=GRIDY, 
                      help="Enable the y-axis grid [default: %s]" % GRIDY)

    parser.add_option("-o", "--optMode", dest="optMode", type="string", default=OPTMODE, 
                      help="The optimization mode when analysis variation is enabled  [default: %s]" % OPTMODE)

    parser.add_option("-b", "--batchMode", dest="batchMode", action="store_false", default=BATCHMODE, 
                      help="Enables batch mode (canvas creation does NOT generate a window) [default: %s]" % BATCHMODE)

    parser.add_option("--analysisName", dest="analysisName", type="string", default=ANALYSISNAME,
                      help="Override default analysisName [default: %s]" % ANALYSISNAME)

    parser.add_option("--dataEra", dest="dataEra", type="string", default=DATAERA, 
                      help="Override default dataEra [default: %s]" % DATAERA)

    parser.add_option("--saveDir", dest="saveDir", type="string", default=SAVEDIR, 
                      help="Directory where all pltos will be saved [default: %s]" % SAVEDIR)

    parser.add_option("--url", dest="url", action="store_true", default=URL, 
                      help="Don't print the actual save path the histogram is saved, but print the URL instead [default: %s]" % URL)
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=VERBOSE, 
                      help="Enables verbose mode (for debugging purposes) [default: %s]" % VERBOSE)

    parser.add_option("--folder", dest="folder", type="string", default = FOLDER,
                      help="ROOT file folder under which all histograms to be plotted are located [default: %s]" % (FOLDER) )

    parser.add_option("--cutLinX", dest="cutLineX", type="float", default=CUTLINEX,
                      help="Add TLine on the x-axis at this value  [default: %s]" % (CUTLINEX) )
    
    parser.add_option("--cutLineY", dest="cutLineY", type="float", default=CUTLINEY,
                      help="Add TLine on the y-axis at this value  [default: %s]" % (CUTLINEY) )

    parser.add_option("--bandValue", dest="bandValue", type="int", default=BANDVALUE,
                      help="Add a +/- band around the ratio canvas at 1.0. Values passed should be the percentage [default = %s]" % (BANDVALUE) )

    (opts, parseArgs) = parser.parse_args()

    # Require at least two arguments (script-name, path to multicrab)
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if isinstance(opts.mcrabs, str):
        if "," not in opts.mcrabs:
            msg = "The directories must be provided in a single argument seperated with a comma (\",\")"
            raise Exception(es + msg + ns)

        # Make a list of pseudo-directories
        opts.mcrabs = opts.mcrabs.split(",")
        Print("Will use the following %d pseudo-multicrab directories:" % (len(opts.mcrabs)), True)
        # For-loop: All pseudo-multicrab dirs
        for i, d in enumerate(opts.mcrabs, 1):
            bIsDir = os.path.isdir(d)
            if not bIsDir:
                msg = "The provided path \"%s\" is not a directory!" % d
                raise Exception(es + msg + ns)
            else:
                msg = "%d) %s" % (i, hs + d + ns)
                Print(msg, False)
            
    if opts.saveDir == None:
        opts.saveDir = aux.getSaveDirPath(opts.mcrabs[0], prefix="", postfix="TFs")
        Verbose("Save directory set to %s" % (ls + opts.saveDir + ns), True)

    # Call the main function
    main(opts)

    if not opts.batchMode:
        raw_input("=== plot_TFs.py: Press any key to quit ROOT ...")
