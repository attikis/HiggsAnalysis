#!/usr/bin/env python
'''
Description:

Usage:

Examples:

'''
#================================================================================================ 
# Imports
#================================================================================================ 
import sys
import os
from optparse import OptionParser
import math
import time
import cProfile

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.analysisModuleSelector as analysisModuleSelector
import HiggsAnalysis.FakeBMeasurement.QCDInvertedResult as qcdInvertedResult
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
import HiggsAnalysis.NtupleAnalysis.tools.pseudoMultiCrabCreator as pseudoMultiCrabCreator

#================================================================================================ 
# Global variables
#================================================================================================ 
_generalOptions = {
    "normalizationPoint"         : "AfterStdSelections",
    "normalizationSourcePrefix"  : "ForQCDNormalization/Normalization",
    "ewkSourceForQCDPlusFakeTaus": "ForDataDrivenCtrlPlotsEWKGenuineTaus",
    "ewkSourceForQCDOnly"        : "ForDataDrivenCtrlPlots",
    }

#================================================================================================ 
# Class definition
#================================================================================================ 
class ModuleBuilder:
    def __init__(self, opts, outputCreator):
        self._opts                     = opts
        self._outputCreator            = outputCreator
        self._moduleInfoString         = None
        self._dsetMgrCreator           = None
        self._dsetMgr                  = None
        self._normFactors              = None
        self._luminosity               = None
        self._nominalResult            = None
        self._fakeWeightingPlusResult  = None
        self._fakeWeightingMinusResult = None
        
    ## Clean up memory
    def delete(self):
        if self._nominalResult != None:
            self._nominalResult.delete()
        if self._fakeWeightingPlusResult != None:
            self._fakeWeightingPlusResult.delete()
        if self._fakeWeightingMinusResult != None:
            self._fakeWeightingMinusResult.delete()
        if self._dsetMgr != None:
            self._dsetMgr.close()
        if self._dsetMgrCreator != None:
            self._dsetMgrCreator.close()
        ROOT.gDirectory.GetList().Delete()
        ROOT.gROOT.CloseFiles()
        ROOT.gROOT.GetListOfCanvases().Delete()
        
    def createDsetMgr(self, multicrabDir, era, searchMode, optimizationMode=None, systematicVariation=None):
        self._era = era
        self._searchMode = searchMode
        self._optimizationMode = optimizationMode
        self._systematicVariation = systematicVariation

        # Construct info string of module
        self._moduleInfoString = "%s_%s_%s"%(era, searchMode, optimizationMode)

        # Obtain dataset manager
        self._dsetMgrCreator = dataset.readFromMulticrabCfg(directory=multicrabDir)
        self._dsetMgr = self._dsetMgrCreator.createDatasetManager(dataEra=era,searchMode=searchMode,optimizationMode=optimizationMode,systematicVariation=systematicVariation)

        # Do the usual normalisation
        self._dsetMgr.updateNAllEventsToPUWeighted()
        self._dsetMgr.loadLuminosities()
        plots.mergeRenameReorderForDataMC(self._dsetMgr)
        self._dsetMgr.merge("EWK", opts.ewkDatasets)

        # Obtain luminosity
        self._luminosity = self._dsetMgr.getDataset("Data").getLuminosity()
        return
        
    def debug(self):
        self._dsetMgr.printDatasetTree()
        print "Luminosity = %f 1/fb"%(self._luminosity / 1000.0)
        return

    def getModuleInfoString(self):
        return "%s_%s_%s" % (self._era, self._searchMode, self._optimizationMode)

    def buildModule(self, dataPath, ewkPath, normFactors, calculateQCDNormalizationSyst, normDataSrc=None, normEWKSrc=None):
        
        # Create containers for results
        Verbose("Create containers for results", True)
        myModule = pseudoMultiCrabCreator.PseudoMultiCrabModule(self._dsetMgr,
                                                                self._era,
                                                                self._searchMode,
                                                                self._optimizationMode,
                                                                self._systematicVariation)
        Verbose("Obtaining results", True)
        self._nominalResult = qcdInvertedResult.QCDInvertedResultManager(dataPath,
                                                                         ewkPath,
                                                                         self._dsetMgr,
                                                                         self._luminosity,
                                                                         self.getModuleInfoString(),
                                                                         normFactors,
                                                                         calculateQCDNormalizationSyst,
                                                                         opts.normDataSrc,
                                                                         opts.normEwkSrc,
                                                                         self._opts.useInclusiveNorm,
                                                                         opts.verbose)
        # Store results
        myModule.addPlots(self._nominalResult.getShapePlots(),
                          self._nominalResult.getShapePlotLabels())
        self._outputCreator.addModule(myModule)
    
    def buildQCDNormalizationSystModule(self, dataPath, ewkPath):
        # Up variation of QCD normalization (i.e. ctrl->signal region transition)
        # Note that only the source histograms for the shape uncert are stored
        # because the result must be calculated after rebinning
        # (and rebinning is no longer done here for flexibility reasons)
        mySystModule = pseudoMultiCrabCreator.PseudoMultiCrabModule(self._dsetMgr,
                                                                    self._era,
                                                                    self._searchMode,
                                                                    self._optimizationMode,
                                                                    "SystVarQCDNormSource")
        mySystModule.addPlots(self._nominalResult.getQCDNormalizationSystPlots(),
                              self._nominalResult.getQCDNormalizationSystPlotLabels())
        self._outputCreator.addModule(mySystModule)

    def buildQCDQuarkGluonWeightingSystModule(self, dataPath, ewkPath, normFactorsUp, normFactorsDown, normalizationPoint):
        # Up variation of fake weighting
        mySystModulePlus = pseudoMultiCrabCreator.PseudoMultiCrabModule(self._dsetMgr,
                                                                        self._era,
                                                                        self._searchMode,
                                                                        self._optimizationMode,
                                                                        "SystVarFakeWeightingPlus")
        self._fakeWeightingPlusResult = qcdInvertedResult.QCDInvertedResultManager(dataPath, 
                                                                                   ewkPath,
                                                                                   self._dsetMgr,
                                                                                   self._luminosity,
                                                                                   self.getModuleInfoString(),
                                                                                   normFactorsUp,
                                                                                   optionCalculateQCDNormalizationSyst=False,
                                                                                   optionUseInclusiveNorm=self._opts.useInclusiveNorm)
        myModule.addPlots(self._fakeWeightingPlusResult.getShapePlots(),
                          self._fakeWeightingPlusResult.getShapePlotLabels())
        self._outputCreator.addModule(mySystModulePlus)
        # Down variation of fake weighting
        mySystModuleMinus = pseudoMultiCrabCreator.PseudoMultiCrabModule(dself._dsetMgr,
                                                                         self._era,
                                                                         self._searchMode,
                                                                         self._optimizationMode,
                                                                         "SystVarFakeWeightingMinus")
        self._fakeWeightingMinusResult = qcdInvertedResult.QCDInvertedResultManager(dataPath, 
                                                                                    ewkPath,
                                                                                    self._dsetMgr,
                                                                                    self._myLuminosity,
                                                                                    self.getModuleInfoString(),
                                                                                    normFactorsDown,
                                                                                    optionCalculateQCDNormalizationSyst=False)
        myModule.addPlots(self._fakeWeightingMinusResult.getShapePlots(),
                          self._fakeWeightingMinusResult.getShapePlotLabels())
        self._outputCreator.addModule(mySystModuleMinus)
        return

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

def getAvgProcessTimeForOneModule(myGlobalStartTime, myTotalModules):
    return (time.time()-myGlobalStartTime)/float(myTotalModules)

def getTotalElapsedTime(myGlobalStartTime):
    return (time.time()-myGlobalStartTime)

def printTimeEstimate(globalStart, localStart, nCurrent, nAll):
    myLocalTime   = time.time()
    myLocalDelta  = myLocalTime - localStart
    myGlobalDelta = myLocalTime - globalStart
    myEstimate    = myGlobalDelta / float(nCurrent) * float(nAll-nCurrent)
    
    # MAke estimate
    s = "%02d:" % (myEstimate/60)
    myEstimate -= int(myEstimate/60)*60
    s += "%02d"%(myEstimate)
    
    # Print info
    Print("Module finished in: %.1f seconds" % (myLocalDelta), True)
    Print("Estimated time to complete: %s" %  (s), False)
    return


def getModuleInfoString(dataEra, searchMode, optimizationMode):
    moduleInfoString = "%s_%s" % (dataEra, searchMode)
    if len(optimizationMode) > 0:
        moduleInfoString += "_%s" % (optimizationMode)
    return moduleInfoString


def getSourceFileName(dirName, fileName):
    src = os.path.join(dirName, fileName)
    if not os.path.exists(src):
        msg = "Normalisation factors ('%s') not found!\nRun script \"plotQCD_Fit.py\" to auto-generate the normalization factors python file." % src
        raise Exception(ShellStyles.ErrorLabel() + msg)
    else:
        Verbose("Found src file for normalization factors:\n\t%s" % (src), True)
    return src


def  getNormFactorFileList(dirName, fileBaseName):
    scriptList = []

    # For-loop: All items (files/dir) in directory
    for item in os.listdir(dirName):
        fullPath =  os.path.join(dirName, item)

        # Skip directories
        if os.path.isdir(fullPath):
            continue

        # Find files matching the script "Base" name (without moduleInfoStrings)
        if item.startswith((fileBaseName).replace("%s.py", "")):
            if item.endswith(".py"):
                scriptList.append(item)

    if len(scriptList) < 1:
        msg = "ERROR! Found no normalization info files under dir %s" % dirName
        raise Exception(msg)
    else:
        Print("Found %s norm-factor file(s):\n\t%s" % (  len(scriptList), "\n\t".join(os.path.join([os.path.join(dirName, s) for s in scriptList]))), True)
    return scriptList


def importNormFactors(era, searchMode, optimizationMode, multicrabDirName):
    '''
    Imports the auto-generates  QCDInvertedNormalizationFactors.py file, which is 
    created by the plotting/fitting templates script  (plotQCD_Fit.py)
    
    This containsthe results  of fitting to the Baseline Data the templates m_{jjb} 
    shapes from the QCD (Inverted Data) and EWK (Baseline MC).                                                                                                                               
 
    Results include the fit details for each shape and the QCD NormFactor for moving 
    from the ControlRegion (CR) to the Signal Region (SR).
    
    The aforementioned python file and a folder with the histogram ROOT files and the individual                                                                                                                         
    fits. The foler name will be normalisationPlots/<OptsMode> and will be placed inside the
    <pseudomulticrab_dir>. The autogenerated file file be place in the cwd (i.e. work/)
    '''
    # Find candidates for normalisation scripts
    scriptList = getNormFactorFileList(dirName=multicrabDirName, fileBaseName=opts.normFactorsSrc)

    # Create a string with the module information used
    moduleInfoString = getModuleInfoString(era, searchMode, optimizationMode)

    # Construct source file name
    src = getSourceFileName(multicrabDirName, opts.normFactorsSrc % moduleInfoString)

    # Check if normalization coefficients are suitable for the choses era
    Verbose("Reading normalisation factors from:\n\t%s" % src, True)

    # Split the path to get just the file name of src
    pathList = src.replace(".py","").split("/")

    # Insert the directory where the normFactor files reside into the path so that they are found
    if len(pathList) > 1:
        cwd = os.getenv("PWD")
        # Get directories to src in a list [i.e. remove the last entry (file-name) from the pathList]
        dirList = map(str, pathList[:(len(pathList)-1)])
        srcDir   = "/".join(dirList)
        sys.path.insert(0, os.path.join(cwd, srcDir))

    # Import the (normFactor) src file
    normFactorsImport = __import__(os.path.basename("/".join(pathList)))
    
    # Get the function definition
    myNormFactorsSafetyCheck = getattr(normFactorsImport, "QCDInvertedNormalizationSafetyCheck")

    Verbose("Check that the era=%s, searchMode=%s, optimizationMode=%s info matches!" % (era, searchMode, optimizationMode) )
    myNormFactorsSafetyCheck(era, searchMode, optimizationMode)

    # Obtain normalization factors
    myNormFactorsImport = getattr(normFactorsImport, "QCDNormalization")
    # myNormFactorsImportSystVarFakeWeightingDown = getattr(normFactorsImport, "QCDPlusEWKFakeTausNormalizationSystFakeWeightingVarDown") #FIXME
    # myNormFactorsImportSystVarFakeWeightingUp   = getattr(normFactorsImport, "QCDPlusEWKFakeTausNormalizationSystFakeWeightingVarUp")   #FIXME

    myNormFactors = {}
    myNormFactors["nominal"] = myNormFactorsImport
    # myNormFactors["FakeWeightingDown"] = myNormFactorsImportSystVarFakeWeightingDown # FIXME 
    # myNormFactors["FakeWeightingUp"]   = myNormFactorsImportSystVarFakeWeightingUp   # FIXME
    return myNormFactors


def main():
    
    # Object for selecting data eras, search modes, and optimization modes
    myModuleSelector = analysisModuleSelector.AnalysisModuleSelector()

    # Obtain multicrab directory
    myMulticrabDir = "."
    if opts.mcrab != None:
        myMulticrabDir = opts.mcrab
    if not os.path.exists("%s/multicrab.cfg" % myMulticrabDir):
        raise Exception(ShellStyles.ErrorLabel()+"No multicrab directory found at path '%s'! Please check path or specify it with --mcrab!"%(myMulticrabDir)+ShellStyles.NormalStyle())
    if len(opts.shape) == 0:
        raise Exception(ShellStyles.ErrorLabel()+"Provide a shape identifierwith --shape (for example MT)!"+ShellStyles.NormalStyle())

    # Set EWK source depending on calculation mode
    if opts.qcdonly:
        _generalOptions["EWKsource"] = _generalOptions["ewkSourceForQCDOnly"] #alex
    else:
        _generalOptions["EWKsource"] = _generalOptions["ewkSourceForQCDPlusFakeTaus"] #alex

    # Obtain dsetMgrCreator and register it to module selector
    dsetMgrCreator = dataset.readFromMulticrabCfg(directory=myMulticrabDir)

    # Obtain systematics names
    mySystematicsNamesRaw = dsetMgrCreator.getSystematicVariationSources()
    mySystematicsNames    = []
    for item in mySystematicsNamesRaw:
        mySystematicsNames.append("%sPlus" % item)
        mySystematicsNames.append("%sMinus"% item)
    if opts.test:
        mySystematicsNames = [] #[mySystematicsNames[0]] #FIXME

    # Set the primary source 
    myModuleSelector.setPrimarySource(label=opts.analysisName, dsetMgrCreator=dsetMgrCreator)

    # Select modules
    myModuleSelector.doSelect(opts)

    # Loop over era/searchMode/optimizationMode combos
    myDisplayStatus = True
    myTotalModules  = myModuleSelector.getSelectedCombinationCount() * (len(mySystematicsNames)+1) * len(opts.shape)
    Verbose("Found %s modules in total" % (myTotalModules), True)

    count, nEras, nSearchModes, nOptModes, nSysVars = myModuleSelector.getSelectedCombinationCountIndividually()
    if nSysVars > 0:
        msg = "Will run over %d modules (%d eras x %d searchModes x %d optimizationModes x %d systematic variations)" % (count, nEras, nSearchModes, nOptModes, nSysVars)
    else:
        msg = "Will run over %d modules (%d eras x %d searchModes x %d optimizationModes)" % (count, nEras, nSearchModes, nOptModes)
    Print(msg, True)

    # Create pseudo-multicrab creator
    myOutputCreator = pseudoMultiCrabCreator.PseudoMultiCrabCreator(opts.analysisName, myMulticrabDir)

    # Make time stamp for start time
    myGlobalStartTime = time.time()

    n = 0
    # For-loop: All Shapes
    for shapeType in opts.shape:
        _generalOptions["normalizationDataSource"] = "ForDataDrivenCtrlPlots"
        _generalOptions["normalizationEWKSource"]  = "ForDataDrivenCtrlPlots"

        # Initialize
        myOutputCreator.initialize(shapeType)
        
        msg = "Creating dataset for shape \"%s\"%s" % (shapeType, ShellStyles.NormalStyle())
        Verbose(ShellStyles.HighlightStyle() + msg, True)

        # For-Loop over era, searchMode, and optimizationMode options
        for era in myModuleSelector.getSelectedEras():
            for searchMode in myModuleSelector.getSelectedSearchModes():
                for optimizationMode in myModuleSelector.getSelectedOptimizationModes():

                    # Obtain normalization factors
                    myNormFactors = importNormFactors(era, searchMode, optimizationMode, opts.mcrab)

                    # Nominal module
                    myModuleInfoString = getModuleInfoString(era, searchMode, optimizationMode)
                    n += 1

                    # Inform user of what is being processes
                    msg = "Module %d/%d: %s/%s%s" % (n, myTotalModules, myModuleInfoString, shapeType, ShellStyles.NormalStyle())
                    Print(ShellStyles.CaptionStyle() + msg, True)

                    # Keep time
                    myStartTime = time.time()

                    # Create dataset manager with given settings
                    nominalModule = ModuleBuilder(opts, myOutputCreator)
                    nominalModule.createDsetMgr(myMulticrabDir, era, searchMode, optimizationMode)
                    
                    if (n == 1):
                        if opts.verbose:
                            nominalModule.debug()
                     
                    doQCDNormalizationSyst=False #FIXME - Systematics
                    Print("Building nominal module [calculateQCDNormalizationSyst = %s]" % (doQCDNormalizationSyst), True)
                    nominalModule.buildModule(opts.dataSrc, opts.ewkSrc, myNormFactors["nominal"], doQCDNormalizationSyst, opts.normDataSrc, opts.normEwkSrc)

                    if len(mySystematicsNames) > 0:
                        Print("Adding QCD normalization systematics (iff also other systematics  present) ", True)
                        nominalModule.buildQCDNormalizationSystModule(opts.dataSrc, opts.ewkSrc)

                    # FIXME: add quark gluon weighting systematics!
                    if 0: 
                        Print("Adding Quark/Gluon weighting systematics", True)
                        nominalModule.buildQCDQuarkGluonWeightingSystModule(opts.dataSrc,
                                                                            opts.ewkSrc,
                                                                            myNormFactors["FakeWeightingUp"],
                                                                            myNormFactors["FakeWeightingDown"],
                                                                            calculateQCDNormalizationSyst=False,
                                                                            normDataSrc=_generalOptions["normalizationDataSource"],
                                                                            normEWKSrc=_generalOptions["normalizationEWKSource"])

                    Verbose("Deleting nominal module", True)
                    nominalModule.delete()

                    Verbose("Printing time estimate", True)
                    printTimeEstimate(myGlobalStartTime, myStartTime, n, myTotalModules)

                    Verbose("Now do the rest of systematics variations", True)
                    for syst in mySystematicsNames:
                        n += 1
                        print ShellStyles.CaptionStyle()+"Analyzing systematics variations %d/%d: %s/%s/%s%s"%(n,myTotalModules,myModuleInfoString,syst,shapeType,ShellStyles.NormalStyle())
                        myStartTime = time.time()
                        systModule  = ModuleBuilder(opts, myOutputCreator)
                        # Create dataset manager with given settings
                        systModule.createDsetMgr(myMulticrabDir, era, searchMode, optimizationMode, systematicVariation=syst)

                        # Build asystematics module
                        systModule.buildModule(opts.dataSrc, opts.ewkSrc, myNormFactors["nominal"], False, opts.normDataSrc, opts.normEwkSrc)
                        printTimeEstimate(myGlobalStartTime, myStartTime, n, myTotalModules)
                        systModule.delete()

        Verbose("Pseudo-multicrab ready for %s" % shapeType, True)

    # Create rest of pseudo multicrab directory
    myOutputCreator.silentFinalize() 
    
    # Print some timing statistics
    Print("Average processing time per module was %.1f s" % getAvgProcessTimeForOneModule(myGlobalStartTime, myTotalModules), True)
    Print("Total elapsed time was %.1f s" % getTotalElapsedTime(myGlobalStartTime), False)

    msg = "SUCCESS: Created pseudo-multicrab directory for \"%s\":" % (shapeType)
    Print(ShellStyles.SuccessStyle() + msg + ShellStyles.NormalStyle(), True)
    Print(myOutputCreator.getDirName(), False)

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
    global opts
    ANALYSISNAME   = "FakeBMeasurement"
    EWKDATASETS    = ["TT", "WJetsToQQ_HT_600ToInf", "DYJetsToQQHT", "SingleTop", "TTWJetsToQQ", "TTZToQQ", "Diboson", "TTTT"]
    SEARCHMODES    = ["80to1000"]
    DATAERAS       = ["Run2016"]
    OPTMODE        = None
    BATCHMODE      = True
    PRECISION      = 3
    INTLUMI        = -1.0
    SUBCOUNTERS    = False
    LATEX          = False
    MCONLY         = False
    MERGEEWK       = False
    URL            = False
    NOERROR        = True
    SAVEDIR        = "/publicweb/a/aattikis/FakeBMeasurement/"
    VERBOSE        = False
    VARIATIONS     = False
    TEST           = True
    FACTOR_SRC     = "QCDInvertedNormalizationFactors_%s.py"
    DATA_SRC       = "ForDataDrivenCtrlPlots"
    EWK_SRC        = "ForDataDrivenCtrlPlots"
    NORM_DATA_SRC  = "ForDataDrivenCtrlPlots"
    NORM_EWK_SRC   = "ForDataDrivenCtrlPlots"
    INCLUSIVE_ONLY = True
    MULTICRAB      = None

    # Define the available script options
    parser = OptionParser(usage="Usage: %prog [options]", add_help_option=True, conflict_handler="resolve")

    parser.add_option("-m", "--mcrab", dest="mcrab", action="store",# required=True,
                      help="Path to the multicrab directory for input [default: %s]" % (MULTICRAB) )

    parser.add_option("--inclusiveOnly", dest="useInclusiveNorm", action="store_true", default=INCLUSIVE_ONLY, 
                      help="Use only inclusive weight instead of binning [default: %s]" % (INCLUSIVE_ONLY) )
    
    parser.add_option("--normFactorsSrc", dest="normFactorsSrc", action="store", default=FACTOR_SRC,
                      help="The python file (auto-generated) containing the normalisation factors. [default: %s]" % FACTOR_SRC)

    parser.add_option("-l", "--list", dest="listVariations", action="store_true", default=VARIATIONS, 
                      help="Print a list of available variations [default: %s]" % VARIATIONS)

    parser.add_option("--shape", dest="shape", action="store", default=["TrijetMass"], 
                      help="shape identifiers") # unknown use

    parser.add_option("--qcdonly", dest="qcdonly", action="store_true", default=False, 
                      help="Calculate QCD-only case instead of QCD+EWK fakes") # unknown use

    parser.add_option("--test", dest="test", action="store_true", default=TEST, 
                      help="Make short test by limiting number of syst. variations [default: %s]" % TEST)

    parser.add_option("-o", "--optMode", dest="optimizationMode", type="string", default=OPTMODE, 
                      help="The optimization mode when analysis variation is enabled [default: %s]" % OPTMODE)

    parser.add_option("-b", "--batchMode", dest="batchMode", action="store_false", default=BATCHMODE, 
                      help="Enables batch mode (canvas creation does NOT generate a window) [default: %s]" % BATCHMODE)

    parser.add_option("--ewkDatasets", dest="ewkDatasets", default=EWKDATASETS,
                      help="EWK Datsets to merge [default: %s]" % ", ".join(EWKDATASETS) )
    
    parser.add_option("--analysisName", dest="analysisName", type="string", default=ANALYSISNAME,
                      help="Override default analysisName [default: %s]" % ANALYSISNAME)

    parser.add_option("--mcOnly", dest="mcOnly", action="store_true", default=MCONLY,
                      help="Plot only MC info [default: %s]" % MCONLY)

    parser.add_option("--intLumi", dest="intLumi", type=float, default=INTLUMI,
                      help="Override the integrated lumi [default: %s]" % INTLUMI)

    parser.add_option("--searchMode", dest="searchMode", default=SEARCHMODES,
                      help="Override default searchMode [default: %s]" % ", ".join(SEARCHMODES) )

    parser.add_option("--dataEra", dest="era", default=DATAERAS, 
                      help="Override default dataEra [default: %s]" % ", ".join(DATAERAS) )

    parser.add_option("--mergeEWK", dest="mergeEWK", action="store_true", default=MERGEEWK, 
                      help="Merge all EWK samples into a single sample called \"EWK\" [default: %s]" % MERGEEWK)

    parser.add_option("--saveDir", dest="saveDir", type="string", default=SAVEDIR, 
                      help="Directory where all pltos will be saved [default: %s]" % SAVEDIR)

    parser.add_option("--url", dest="url", action="store_true", default=URL, 
                      help="Don't print the actual save path the histogram is saved, but print the URL instead [default: %s]" % URL)
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=VERBOSE, 
                      help="Enables verbose mode (for debugging purposes) [default: %s]" % VERBOSE)

    parser.add_option("-i", "--includeOnlyTasks", dest="includeOnlyTasks", action="store", 
                      help="List of datasets in mcrab to include")

    parser.add_option("-e", "--excludeTasks", dest="excludeTasks", action="store", 
                      help="List of datasets in mcrab to exclude")

    parser.add_option("--dataSrc", dest="dataSrc", action="store", default=DATA_SRC,
                      help="Source of Data histograms [default: %s" % (DATA_SRC) )

    parser.add_option("--ewkSrc", dest="ewkSrc", action="store", default=EWK_SRC,
                      help="Source of EWK histograms [default: %s" % (EWK_SRC) )

    parser.add_option("--normDataSrc", dest="normDataSrc", action="store", default=NORM_DATA_SRC,
                      help="Source of Data normalisation [default: %s" % (NORM_DATA_SRC) )
                      
    parser.add_option("--normEwkSrc", dest="normEwkSrc", action="store", default=NORM_EWK_SRC,
                      help="Source of EWK normalisation [default: %s" % (NORM_EWK_SRC) )
                      
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
    main()

    if not opts.batchMode:
        raw_input("=== makePseudoMulticrab.py: Press any key to quit ROOT ...")
