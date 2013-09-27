#!/usr/bin/env python

# Description: Calculates the QCD factorised method result and creates a pseudo-multicrab directory as output
# Works for the QCD factorised method
# Author: Lauri Wendland

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import sys
import os
from optparse import OptionParser
import cProfile

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset as dataset
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.systematics as systematics
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.analysisModuleSelector import *
from HiggsAnalysis.HeavyChHiggsToTauNu.qcdCommon.dataDrivenQCDCount import *
from HiggsAnalysis.HeavyChHiggsToTauNu.qcdFactorised.qcdFactorisedResult import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.pseudoMultiCrabCreator import *

myMtSpecs = {
    "basicName": "QCDfactorised/MtAfterStandardSelections",
    "leg1Name": "QCDfactorised/MtAfterLeg1",
    "leg2Name": "QCDfactorised/MtAfterLeg2",
    "binList": systematics.getBinningForPlot("shapeTransverseMass"),
}

myFullMassSpecs = {
    "basicName": "QCDfactorised/MassAfterStandardSelections",
    "leg1Name": "QCDfactorised/MassAfterLeg1",
    "leg2Name": "QCDfactorised/MassAfterLeg2",
    "binList": systematics.getBinningForPlot("shapeInvariantMass"),
}

def doNominalModule(myMulticrabDir,era,searchMode,optimizationMode,myOutputCreator,myShapeString,myDisplayStatus):
    # Construct info string of module
    myModuleInfoString = "%s_%s_%s"%(era, searchMode, optimizationMode)
    # Obtain dataset manager
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=myMulticrabDir)
    dsetMgr = dsetMgrCreator.createDatasetManager(dataEra=era,searchMode=searchMode,optimizationMode=optimizationMode)
    # Do the usual normalisation
    dsetMgr.updateNAllEventsToPUWeighted()
    dsetMgr.loadLuminosities()
    plots.mergeRenameReorderForDataMC(dsetMgr)
    dsetMgr.merge("EWK", ["TTJets","WJets","DYJetsToLL","SingleTop","Diboson"])
    # Obtain luminosity
    myLuminosity = dsetMgr.getDataset("Data").getLuminosity()
    # Print info so that user can check that merge went correct
    if myDisplayStatus:
        dsetMgr.printDatasetTree()
        print "Luminosity = %f 1/fb"%(myLuminosity / 1000.0)
        print
        myDisplayStatus = False
    # Gather results
    # Create containers for results
    myModuleResults = PseudoMultiCrabModule(dsetMgr, era, searchMode, optimizationMode)
    myQCDNormalizationSystUpResults = PseudoMultiCrabModule(dsetMgr, era, searchMode, optimizationMode, "SystVarQCDNormPlus")
    myQCDNormalizationSystDownResults = PseudoMultiCrabModule(dsetMgr, era, searchMode, optimizationMode, "SystVarQCDNormMinus")
    # Obtain results
    myResult = None
    if massType == "mt":
        myResult = QCDFactorisedResultManager(myMtSpecs,dsetMgr,myLuminosity,myModuleInfoString,shapeOnly=False,displayPurityBreakdown=True)
    elif massType == "invmass":
        myResult = QCDFactorisedResultManager(myFullMassSpecs,dsetMgr,myLuminosity,myModuleInfoString,shapeOnly=False,displayPurityBreakdown=True)
    myModuleResults.addShape(myResult.getShape(), myShapeString)
    myModuleResults.addDataDrivenControlPlots(myResult.getControlPlots(),myResult.getControlPlotLabels())
    myOutputCreator.addModule(myModuleResults)
    # Up variation of QCD normalization (i.e. ctrl->signal region transition)
    myQCDNormalizationSystUpResults.addShape(myResult.getRegionSystUp(), myShapeString)
    myQCDNormalizationSystUpResults.addDataDrivenControlPlots(myResult.getRegionSystUpCtrlPlots(),myResult.getControlPlotLabels())
    myOutputCreator.addModule(myQCDNormalizationSystUpResults)
    # Down variation of QCD normalization (i.e. ctrl->signal region transition)
    myQCDNormalizationSystDownResults.addShape(myResult.getRegionSystDown(), myShapeString)
    myQCDNormalizationSystDownResults.addDataDrivenControlPlots(myResult.getRegionSystDownCtrlPlots(),myResult.getControlPlotLabels())
    myOutputCreator.addModule(myQCDNormalizationSystDownResults)
    myResult.delete()
    dsetMgr.close()

def doSystematicsVariation(myMulticrabDir,era,searchMode,optimizationMode,syst,myOutputCreator,myShapeString):
    myModuleInfoString = "%s_%s_%s_%s"%(era, searchMode, optimizationMode,syst)
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=myMulticrabDir)
    systDsetMgr = dsetMgrCreator.createDatasetManager(dataEra=era,searchMode=searchMode,optimizationMode=optimizationMode,systematicVariation=syst)
    # Do the usual normalisation
    systDsetMgr.updateNAllEventsToPUWeighted()
    systDsetMgr.loadLuminosities()
    plots.mergeRenameReorderForDataMC(systDsetMgr)
    systDsetMgr.merge("EWK", ["TTJets","WJets","DYJetsToLL","SingleTop","Diboson"])
    myLuminosity = systDsetMgr.getDataset("Data").getLuminosity()
    # Obtain results
    mySystModuleResults = PseudoMultiCrabModule(systDsetMgr, era, searchMode, optimizationMode, syst)
    mySystResult = None
    if massType == "mt":
        mySystResult = QCDFactorisedResultManager(myMtSpecs,systDsetMgr,myLuminosity,myModuleInfoString,shapeOnly=False)
    elif massType == "invmass":
        mySystResult = QCDFactorisedResultManager(myFullMassSpecs,systDsetMgr,myLuminosity,myModuleInfoString,shapeOnly=False)
    mySystModuleResults.addShape(mySystResult.getShape(), myShapeString)
    mySystModuleResults.addDataDrivenControlPlots(mySystResult.getControlPlots(),mySystResult.getControlPlotLabels())
    mySystResult.delete()
    ## Save module info
    myOutputCreator.addModule(mySystModuleResults)
    systDsetMgr.close()

def printTimeEstimate(globalStart, localStart, nCurrent, nAll):
    myLocalDelta = time.time() - localStart
    myGlobalDelta = time.time() - globalStart
    myEstimate = myGlobalDelta / float(nCurrent) * float(nAll-nCurrent)
    s = "%02d:"%(myEstimate/60)
    myEstimate -= int(myEstimate/60)*60
    s += "%02d"%(myEstimate)
    print "Module finished in %.1f s, estimated time to complete: %s"%(myLocalDelta, s)

if __name__ == "__main__":
    myModuleSelector = AnalysisModuleSelector() # Object for selecting data eras, search modes, and optimization modes

    parser = OptionParser(usage="Usage: %prog [options]",add_help_option=True,conflict_handler="resolve")
    myModuleSelector.addParserOptions(parser)
    parser.add_option("--mdir", dest="multicrabDir", action="store", help="Multicrab directory")
    parser.add_option("--mtonly", dest="transverseMassOnly", action="store_true", default=False, help="Create only transverse mass plots")
    parser.add_option("--invmassonly", dest="invariantMassOnly", action="store_true", default=False, help="Create only invariant mass plots")
    parser.add_option("--test", dest="test", action="store_true", default=False, help="Make short test by limiting number of syst. variations")
    # Add here parser options, if necessary, following line is an example
    #parser.add_option("--showcard", dest="showDatacard", action="store_true", default=False, help="Print datacards also to screen")

    # Parse options
    (opts, args) = parser.parse_args()

    # Obtain multicrab directory
    myMulticrabDir = "."
    if opts.multicrabDir != None:
        myMulticrabDir = opts.multicrabDir

    myShapes = ["mt","invmass"]
    if opts.transverseMassOnly != None and opts.transverseMassOnly:
        myShapes = ["mt"]
    elif opts.invariantMassOnly != None and opts.invariantMassOnly:
        myShapes = ["invmass"]

    # Obtain dsetMgrCreator and register it to module selector
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=myMulticrabDir)
    # Obtain systematics names
    mySystematicsNamesRaw = dsetMgrCreator.getSystematicVariationSources()
    mySystematicsNames = []
    for item in mySystematicsNamesRaw:
        mySystematicsNames.append("%sPlus"%item)
        mySystematicsNames.append("%sMinus"%item)
    if opts.test:
        mySystematicsNames = [mySystematicsNames[0]]

    myModuleSelector.setPrimarySource("analysis", dsetMgrCreator)
    # Select modules
    myModuleSelector.doSelect(opts)
    #dsetMgrCreator.close()
    # Loop over era/searchMode/optimizationMode combos
    myDisplayStatus = True
    myTotalModules = myModuleSelector.getSelectedCombinationCount() * (len(mySystematicsNames)+1) * len(myShapes)
    myModuleSelector.printSelectedCombinationCount()
    # Loop over era/searchMode/optimizationMode options

    # Create pseudo-multicrab creator
    myOutputCreator = PseudoMultiCrabCreator("QCDfactorised", myMulticrabDir)
    n = 0
    myGlobalStartTime = time.time()
    for massType in myShapes:
        myShapeString = ""
        if massType == "mt":
            myShapeString = "shapeTransverseMass"
        elif massType == "invmass":
            myShapeString = "shapeInvariantMass"
        myOutputCreator.initialize(massType)
        print HighlightStyle()+"Creating dataset for shape: %s%s"%(massType,NormalStyle())
        for era in myModuleSelector.getSelectedEras():
            for searchMode in myModuleSelector.getSelectedSearchModes():
                for optimizationMode in myModuleSelector.getSelectedOptimizationModes():
                    myModuleInfoString = "%s_%s_%s"%(era, searchMode, optimizationMode)
                    n += 1
                    print CaptionStyle()+"Module %d/%d: %s/%s%s"%(n,myTotalModules,myModuleInfoString,massType,NormalStyle())
                    myStartTime = time.time()
                    doNominalModule(myMulticrabDir,era,searchMode,optimizationMode,myOutputCreator,myShapeString,myDisplayStatus)
                    printTimeEstimate(myGlobalStartTime, myStartTime, n, myTotalModules)
                    # Now do the rest of systematics variations
                    for syst in mySystematicsNames:
                        n += 1
                        print CaptionStyle()+"Analyzing systematics variations %d/%d: %s/%s/%s%s"%(n,myTotalModules,myModuleInfoString,syst,massType,NormalStyle())
                        myStartTime = time.time()
                        doSystematicsVariation(myMulticrabDir,era,searchMode,optimizationMode,syst,myOutputCreator,myShapeString)
                        printTimeEstimate(myGlobalStartTime, myStartTime, n, myTotalModules)
    # Now write output to disk
    print "\nWriting output to disk shape %s..."%massType
    myOutputCreator.writeRootFileToDisk(massType)
    # Create rest of pseudo multicrab directory
    myOutputCreator.finalize()
    print "Average processing time of one module: %.1f s"%((time.time()-myGlobalStartTime)/float(myTotalModules))
