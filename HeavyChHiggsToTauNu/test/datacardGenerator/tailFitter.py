#! /usr/bin/env python

import os
import glob
import sys
import inspect
from optparse import OptionParser
import array

import HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.TailFitter as TailFitter
import HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.TableProducer as TableProducer
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.CommonLimitTools as limitTools
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux as aux
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset import RootHistoWithUncertainties
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
import HiggsAnalysis.HeavyChHiggsToTauNu.qcdCommon.systematicsForMetShapeDifference as systematicsForMetShapeDifference

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True) # no flashing canvases

_myOriginalDir = "originalDatacards"

def _isSignal(label):
    return label.startswith("HH") or label.startswith("HW") or label.startswith("Hp")

# Return info of column names from datacard file
def parseColumnNames(lines):
    for l in lines:
        mySplit = l.split()
        if mySplit[0] == "process":
            return mySplit[1:]
    raise Exception("This line should never be reached")

# Return info of nuisances from datacard file
def parseNuisanceNames(lines, columnNames):
    myNames = []
    myStatus = False
    for l in lines:
        mySplit = l.split()
        if myStatus and len(mySplit) > 1 and not "statBin" in mySplit[0]:
            # store info
            myDict = {}
            myDict["name"] = mySplit[0]
            myDict["distribution"] = mySplit[1]
            for i in range(2,len(mySplit)):
                myDict[columnNames[i-2]] = mySplit[i]
            myNames.append(myDict)
        if mySplit[0] == "rate":
            # store rate
            myStatus = True
            myDict = {}
            myDict["name"] = "rate"
            myDict["distribution"] = "rate"
            for i in range(1,len(mySplit)):
                myDict[columnNames[i-1]] = mySplit[i]
            myNames.append(myDict)
        if mySplit[0] == "process":
            # store process lines (for formatting only
            myDict = {}
            myDict["name"] = "process"
            myDict["distribution"] = "process"
            for i in range(1,len(mySplit)):
                myDict[columnNames[i-1]] = mySplit[i]
            myNames.append(myDict)
    if len(myNames) == 0:
        raise Exception("No nuisances found!")
    return myNames

def checkSettings(config):
    def checkFitFunc(settings, name):
        myFuncList = []
        for name, obj in inspect.getmembers(TailFitter):
            if inspect.isclass(obj):
                myFuncList.append(name)
        if not "fitfunc" in settings.keys():
            raise Exception(ErrorLabel()+"Fit function ('fitfunc') is not defined for '%s'! Options are (see TailFitter.py): %s"%(name,", ".join(map(str,myFuncList))))
        if not settings["fitfunc"] in myFuncList:
            raise Exception(ErrorLabel()+"Fit function ('%s') is unknown for '%s'! Options are (see TailFitter.py): %s"%(settings["fitfunc"],name,", ".join(map(str,myFuncList))))

    # binning
    if not hasattr(config, "finalBinning"):
        raise Exception(ErrorLabel()+"Dictionary 'finalBinning' missing from settings! Please add!")
    # QCD
    if not hasattr(config, "QCD"):
        raise Exception(ErrorLabel()+"Dictionary 'QCD' with settings for QCD is missing from settings! Please add!")
    checkFitFunc(config.QCD,"QCD")
    # Embedding
    if not hasattr(config, "EWKTau"):
        raise Exception(ErrorLabel()+"Dictionary 'EWKTau' with settings for EWK+tt with taus is missing from settings! Please add!")
    checkFitFunc(config.EWKTau,"EWKTau")
    # EWK+tt fakes
    if not hasattr(config, "EWKFake"):
        raise Exception(ErrorLabel()+"Dictionary 'EWKFake' with settings for EWK+tt misidentified taus is missing from settings! Please add!")
    checkFitFunc(config.EWKFake,"EWKFake")

def getAndRebinRateHisto(columnName, rootFile, binlist):
    myName = "%s_fineBinning"%columnName
    hOriginal = rootFile.Get(myName)
    if hOriginal == None:
        raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%myName)
    myArray = array.array("d",binlist)
    h = hOriginal.Rebin(len(myArray)-1, "", myArray)
    hOriginal.Delete()
    h.SetTitle(columnName)
    h.SetName(columnName)
    return h

def getAndRebinNuisanceHistos(columnName, rootFile, nuisanceInfo, binlist):
    myHistograms = []
    mySuffixes = ["Up_fineBinning","Down_fineBinning"]
    # Loop over nuisance info
    for n in nuisanceInfo:
        if n["distribution"] == "shape" and n[columnName] == "1" and not "QCD_metshape" in n["name"]:
            for suffix in mySuffixes:
                myName = "%s_%s%s"%(columnName,n["name"],suffix)
                hOriginal = rootFile.Get(myName)
                if hOriginal == None:
                    raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%myName)
                myArray = array.array("d",binlist)
                h = hOriginal.Rebin(len(myArray)-1, "", myArray)
                hOriginal.Delete()
                h.SetTitle(myName.replace("_fineBinning",""))
                h.SetName(myName.replace("_fineBinning",""))
                myHistograms.append(h)
    return myHistograms

def getAndRebinQCDShapeNuisanceHistos(columnName, rootFile, hRate, nuisanceInfo, binlist):
    if not "QCD" in columnName:
        return []
    myHistograms = []
    # Loop over nuisance info
    for n in nuisanceInfo:
        if n["distribution"] == "shape" and n[columnName] == "1" and "QCD_metshape" in n["name"]:
            # Obtain numerator and denominator
            myNumName = "%s_QCD_metshapeSource_Numerator"%(columnName)
            myDenomName = "%s_QCD_metshapeSource_Denominator"%(columnName)
            hNum = rootFile.Get(myNumName)
            if hNum == None:
                raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%myNumName)
            hDenom = rootFile.Get(myDenomName)
            if hDenom == None:
                raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%myDenomName)
            myArray = array.array("d",binlist)
            hDenomRebinned = hDenom.Rebin(len(myArray)-1, "", myArray)
            hNumRebinned = hNum.Rebin(len(myArray)-1, "", myArray)
            hDenom.Delete()
            hNum.Delete()
            # Create output histograms
            hUp = aux.Clone(hRate, "%s_QCD_metshapeUp"%columnName)
            hDown = aux.Clone(hRate, "%s_QCD_metshapeDown"%columnName)
            hUp.Reset()
            hDown.Reset()
            # Calculate
            systematicsForMetShapeDifference.createSystHistograms(hRate, hUp, hDown, hNumRebinned, hDenomRebinned)
            myHistograms.append(hUp)
            myHistograms.append(hDown)
    return myHistograms

## Calculates the shape nuisance histogram for the new binning
## Basic principle: keep relative uncertainty constant between unfitted and fitted distributions
def updateNuisanceTail(hOriginalShape, hFittedShape, rootFile, histoName):
    myList = []
    myPostfixes = ["Up","Down"]
    for postfix in myPostfixes:
        # Obtain original nuisance histogram
        hOriginalNuisance = rootFile.Get(histoName+postfix)
        if hOriginalNuisance == None:
            raise Exception(ErrorLabel()+"Cannot open histogram '%s'!"%(histoName+postfix))
        # Sanity check
        if hOriginalShape.GetNbinsX() != hOriginalNuisance.GetNbinsX():
            raise Exception("This should not happen")
        # Prepare new histogram
        hNewNuisance = aux.Clone(hFittedShape, histoName+postfix)
        hNewNuisance.Reset()
        # Loop over final histogram bins
        for i in range(1,hFittedShape.GetNbinsX()+1):
            myOriginalBin = hOriginalShape.GetXaxis().FindBin(hFittedShape.GetXaxis().GetBinLowEdge(i)+0.0001)
            myOriginalBinUpEdge = hOriginalShape.GetXaxis().FindBin(hFittedShape.GetXaxis().GetBinUpEdge(i)-0.0001)
            if myOriginalBin != myOriginalBinUpEdge:
                raise Exception(ErrorLabel()+"final rebinning boundaries at %d-%d do not match to original histogram (needed for shape nuisance scaling)!"%(hFittedShape.GetXaxis().GetBinLowEdge(i),hFittedShape.GetXaxis().GetBinUpEdge(i)))
            # Original relative uncertainty (if ambiguous, leave as None, i.e. perform no scaling
            myOriginalDelta = None
            if abs(hOriginalNuisance.GetBinContent(myOriginalBin)) < 0.00001:
                myOriginalDelta = None
            elif abs(hOriginalShape.GetBinContent(myOriginalBin)) < 0.00001:
                myOriginalDelta = None
            else:
                myOriginalDelta = hOriginalNuisance.GetBinContent(myOriginalBin) / hOriginalShape.GetBinContent(myOriginalBin)
            #print i, myOriginalBin, myOriginalDelta, hOriginalNuisance.GetBinContent(myOriginalBin), hOriginalShape.GetBinContent(myOriginalBin)
            # Calculate new variation counts
            myNewVariation = None
            if myOriginalDelta == None:
                # scale by bin width difference
                myNewVariation = hOriginalNuisance.GetBinContent(myOriginalBin) * hFittedShape.GetXaxis().GetBinWidth(i) / hOriginalNuisance.GetXaxis().GetBinWidth(myOriginalBin)
            else:
                myNewVariation = myOriginalDelta * hFittedShape.GetBinContent(i)
            #print i, myNewVariation, hFittedShape.GetBinContent(i)
            # Store
            hNewNuisance.SetBinContent(i, myNewVariation)
            hNewNuisance.SetBinError(i, 0.0)
        # Finalize
        hOriginalNuisance.Delete()
        hNewNuisance.SetTitle(histoName+postfix)
        myList.append(hNewNuisance)
    return myList

def addNuisanceForIndividualColumn(columnNames,nuisanceInfo,currentColumn,nuisanceName):
    myDict = {}
    myDict["name"] = nuisanceName.replace("Up","").replace("Down","").replace("%s_%s"%(currentColumn,currentColumn),currentColumn)
    myDict["distribution"] = "shape"
    for cc in columnNames:
        if currentColumn == cc:
            myDict[cc] = "1"
        else:
            myDict[cc] = "-"
    nuisanceInfo.append(myDict)

def addBinByBinStatUncert(currentColumn, hRate, columnNames, nuisanceInfo, fitmin=None, fitmax=None):
    if fitmin == None:
        fitmin = hRate.GetXaxis().GetBinLowEdge(1)
    if fitmax == None:
        fitmax = hRate.GetXaxis().GetBinUpEdge(hRate.GetNbinsX())
    print "... Adding bin-by-bin stat. uncert '%s' for range %d-%d"%(currentColumn,fitmin,fitmax)
    myStatHistograms = TableProducer.createBinByBinStatUncertHistograms(hRate, fitmin, fitmax)
    myHistogramCache.extend(myStatHistograms)
    # Add bin-by-bin stat. nuisances to nuisance table
    for h in myStatHistograms:
        if h.GetTitle().endswith("Up"):
            myName = h.GetTitle().replace("%s_%s"%(currentColumn,currentColumn),currentColumn)
            addNuisanceForIndividualColumn(columnNames,nuisanceInfo,currentColumn,myName)
    return myStatHistograms

def createDatacardOutput(originalCardLines, columnNames, nuisanceInfo):
    myOutput = ""
    myProcessLinePassed = False
    for l in originalCardLines:
        # write header lines
        if "Description" in l:
            myOutput += l.replace("Description:", "Description: TAILFITTED")
        else:
            mySplit = l.split()
            if mySplit[0] == "process":
                myProcessLinePassed = True
            if not myProcessLinePassed:
                myOutput += l
    # Create tables
    myProcessTable = []
    myRateTable = []
    myNuisanceTable = []
    myStatTable = []
    for n in nuisanceInfo:
        myRow = []
        # add first two entries
        if n["name"] == "rate" or n["name"] == "process":
            myRow.append(n["name"])
            myRow.append("")
        else:
            myRow.append(n["name"])
            myRow.append(n["distribution"])
        # add data from columns
        for c in columnNames:
            myRow.append(n[c])
        # store
        if n["name"] == "rate":
            myRateTable.append(myRow)
        elif n["name"] == "process":
            myProcessTable.append(myRow)
        elif "statBin" in n["name"]:
            myStatTable.append(myRow)
        else:
            myNuisanceTable.append(myRow)
    # Create table
    myWidths = []
    TableProducer.calculateCellWidths(myWidths, myProcessTable)
    TableProducer.calculateCellWidths(myWidths, myRateTable)
    TableProducer.calculateCellWidths(myWidths, myNuisanceTable)
    TableProducer.calculateCellWidths(myWidths, myStatTable)
    for i in range(0,len(myWidths)):
        if myWidths[i] < 9:
            myWidths[i] = 9
    mySeparatorLine = TableProducer.getSeparatorLine(myWidths)
    myOutput += TableProducer.getTableOutput(myWidths, myProcessTable)
    myOutput += mySeparatorLine
    myOutput += TableProducer.getTableOutput(myWidths, myRateTable)
    myOutput += mySeparatorLine
    myOutput += TableProducer.getTableOutput(myWidths, myNuisanceTable)
    myOutput += mySeparatorLine
    myOutput += TableProducer.getTableOutput(myWidths, myStatTable)
    myOutput += mySeparatorLine
    return myOutput

def printSummaryInfo(columnNames, myNuisanceInfo, cachedHistos):
    def addOrReplace(dictionary, key, newItem):
        if dictionary[key] == None:
            dictionary[key] = newItem.Clone()
        else:
            dictionary[key].Add(newItem)

    def getHisto(cachedHistos,name):
        for h in cachedHistos:
            if h.GetName() == name:
                return h
        raise Exception("Cannot find histogram '%s'!"%name)

    # Create for each column a root histo with uncertainties
    myDict = {}
    myDict["Hp"] = None
    myDict["QCD"] = None
    myDict["EWKtau"] = None
    myDict["EWKfakes"] = None
    myTotal = None
    for c in columnNames:
        hRate = aux.Clone(getHisto(cachedHistos, c))
        myRHWU = RootHistoWithUncertainties(hRate)
        for n in myNuisanceInfo:
            # Add shape uncertainties
            if n["distribution"] == "shape" and n[c] == 1 and "statBin" not in n["name"]:
                hUp = aux.Clone(getHisto(cachedHistos, "%s_%sUp"%(c,n["name"])))
                hDown = aux.Clone(getHisto(cachedHistos, "%s_%sDown"%(c,n["name"])))
                myRHWU.addShapeUncertaintyFromVariation(n["name"], hUp, hDown)
            # Add constant uncertainties
            elif n["name"] != "rate" and n["name"] != "process" and n[c] != "-":
                diffUp = 0.0
                diffDown = 0.0
                if "/" in n[c]:
                    mySplit = n[c].split("/")
                    diffDown = float(mySplit[0])-1.0
                    diffUp = float(mySplit[1])-1.0
                else:
                    diffDown = float(n[c])
                    diffUp = float(n[c])
                myRHWU.addNormalizationUncertaintyRelative(n["name"], diffUp, diffDown)
        # Store column info
        _myBr = 0.01
        myAddToTotalStatus = False
        if c.startswith("HH"):
            myRHWU.Scale(_myBr**2)
            addOrReplace(myDict, "Hp", myRHWU)
        elif c.startswith("HW"):
            myRHWU.Scale(2.0*_myBr*(1.0-_myBr))
            addOrReplace(myDict, "Hp", myRHWU)
        elif c.startswith("Hp"):
            addOrReplace(myDict, "Hp", myRHWU)
        elif c == "EWK_Tau":
            addOrReplace(myDict, "EWKtau", myRHWU)
            myAddToTotalStatus = True
        elif c.endswith("faketau"):
            addOrReplace(myDict, "EWKfakes", myRHWU)
            myAddToTotalStatus = True
        elif c.startswith("QCD"):
            addOrReplace(myDict, "QCD", myRHWU)
            myAddToTotalStatus = True
        else:
            myDict[c] = myRHWU
            myAddToTotalStatus = True
        if myAddToTotalStatus:
            if myTotal == None:
                myTotal = myRHWU.Clone()
            else:
                myTotal.Add(myRHWU)

    myDict["Totalbkg"] = myTotal
    # Make table
    print "\nEvent yields:"
    myTotal = None
    for item in myDict.keys():
        if myDict[item] != None:
            myDict[item].makeFlowBinsVisible()
            rate = myDict[item].getRate()
            stat = myDict[item].getRateStatUncertainty()
            (systUp,systDown) = myDict[item].getRateSystUncertainty()
            print "%10s: %.1f +- %.1f (stat.) + %.1f - %.1f (syst.)"%(item,rate,stat,systUp,systDown)
    print ""

if __name__ == "__main__":
    parser = OptionParser(usage="Usage: %prog [options]",add_help_option=False,conflict_handler="resolve")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Print more information")
    parser.add_option("-x", "--settings", dest="settings", action="store", help="Name (incl. path) of the settings file to be used as an input")
    (opts, args) = parser.parse_args()

    # Check that input arguments are sufficient
    if opts.settings == None:
        raise Exception(ErrorLabel()+"Please provide input parameter file with -x or --params !")

    # Load settings
    print "Loading settings:",opts.settings
    if not os.path.exists(opts.settings):
        raise Exception(ErrorLabel()+"Cannot find settings file '%s'!"%opts.settings)
    os.system("python %s"%opts.settings) # Catch any errors in the input datacard
    config = aux.load_module(opts.settings)
    checkSettings(config)
    myFitSettingsList = [config.QCD, config.EWKTau, config.EWKFake, config.EWKTauMC]

    # Copy unfitted cards for provenance information if necessary
    if not os.path.exists(_myOriginalDir):
        os.mkdir(_myOriginalDir)
        os.system("mv *.txt %s/."%_myOriginalDir)
        os.system("mv *.root %s/."%_myOriginalDir)
        print "Moved original datacards as provenance info to %s"%_myOriginalDir
    else:
        items = glob.glob("*.txt")
        if len(items):
            os.system("rm *.txt")
        items = glob.glob("*.root")
        if len(items):
            os.system("rm *.root")

    # Find datacards
    myLimitSettings = limitTools.GeneralSettings(_myOriginalDir,[])
    massPoints = myLimitSettings.getMassPoints(limitTools.LimitProcessType.TAUJETS)
    myDatacardPattern = myLimitSettings.getDatacardPattern(limitTools.LimitProcessType.TAUJETS)
    myRootfilePattern = myLimitSettings.getRootfilePattern(limitTools.LimitProcessType.TAUJETS)

    # Loop over mass points
    for m in massPoints:
        myHistogramCache = []
        # Obtain luminosity
        myLuminosity = float(limitTools.readLuminosityFromDatacard(_myOriginalDir, "%s"%myDatacardPattern%m))
        # Obtain root file
        myRootFile = ROOT.TFile.Open("%s/%s"%(_myOriginalDir, myRootfilePattern%m))
        # Obtain datacard
        myOriginalCardFile = open("%s/%s"%(_myOriginalDir, myDatacardPattern%m))
        myOriginalCardLines = myOriginalCardFile.readlines()
        myOriginalCardFile.close()
        # Obtain column and nuisance info
        myColumnNames = parseColumnNames(myOriginalCardLines)
        myNuisanceInfo = parseNuisanceNames(myOriginalCardLines, myColumnNames)
        myFitParNuisanceInfo = None
        # Treat observation
        hObs = getAndRebinRateHisto("data_obs", myRootFile, config.finalBinning["shape"])
        myHistogramCache.append(hObs)
        # Loop over column names
        for c in myColumnNames:
            print HighlightStyle()+"Processing column %s for mass %s"%(c,m)+NormalStyle()
            if _isSignal(c) or c in config.Blacklist:
                print "... skipping fit (signal or blacklist)"
                # Obtain and rebin rate histo
                hRate = getAndRebinRateHisto(c, myRootFile, config.finalBinning["shape"])
                myHistogramCache.append(hRate)
                # Obtain and rebin nuisance histos
                hNuisances = getAndRebinNuisanceHistos(c, myRootFile, myNuisanceInfo, config.finalBinning["shape"])
                myHistogramCache.extend(hNuisances)
                # Treat QCD shape uncertainty separately (for testing only; one should use the tail fit for QCD)
                hNuisances = getAndRebinQCDShapeNuisanceHistos(c, myRootFile, hRate, myNuisanceInfo, config.finalBinning["shape"])
                myHistogramCache.extend(hNuisances)
                # Create bin-by-bin stat. histograms for fitted distribution and update the nuisance table
                myStatHistograms = addBinByBinStatUncert(c, hRate, myColumnNames, myNuisanceInfo)
                myHistogramCache.extend(myStatHistograms)
            else:
                # Not signal or blacklist, do fit
                hFineBinning = myRootFile.Get(c+"_fineBinning")
                hOriginalShape = myRootFile.Get(c)
                if hFineBinning == None:
                    raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%(c+"_fineBinning"))
                if hOriginalShape == None:
                    raise Exception(ErrorLabel()+"Cannot find histogram '%s'!"%(c))
                # Proceed
                myFitSettings = None
                for s in myFitSettingsList:
                    if s["id"] in c:
                        myFitSettings = s
                        print "... using fitfunc: %s and range %d-%d"%(s["fitfunc"],s["fitmin"],s["fitmax"])
                if myFitSettings == None:
                    raise Exception()
                myFitter = TailFitter.TailFitter(hFineBinning, c, m, myFitSettings["fitfunc"], myFitSettings["fitmin"], myFitSettings["fitmax"])
                # Obtain fitted rate with final binning
                myFittedRateHistograms = myFitter.getFittedRateHistogram(hFineBinning, config.finalBinning["shape"])
                myHistogramCache.extend(myFittedRateHistograms)
                # Update rate
                print hFineBinning.Integral(),hOriginalShape.Integral()
                for n in myNuisanceInfo:
                    if n["name"] == "rate":
                        n[c] = "%f"%myFittedRateHistograms[0].Integral()
                        print "... Updated rate because of fitting %.1f -> %.1f (diff=%f)"%(hFineBinning.Integral(), myFittedRateHistograms[0].Integral(), myFittedRateHistograms[0].Integral()/hFineBinning.Integral())
                # Update all those shape nuisances (update histograms only, no need to touch nuisance table)
                for n in myNuisanceInfo:
                    if n["distribution"] == "shape" and n[c] == "1":
                        print "... Updating shape nuisance '%s' tail"%n["name"]
                        myUpdatedNuisanceHistograms = updateNuisanceTail(hOriginalShape, myFittedRateHistograms[0], myRootFile, "%s_%s"%(c,n["name"]))
                        myHistogramCache.extend(myUpdatedNuisanceHistograms)
                # Obtain fit uncertainty histograms and add them to cache
                (huplist, hdownlist) = myFitter.calculateVariationHistograms(config.finalBinning["shape"])
                # Treat blancs (norm == 0)
                for i in range(0, len(huplist)):
                    if huplist[i].Integral() == 0:
                        for k in range(0, huplist[i].GetNbinsX()+2):
                            huplist[i].SetBinContent(k, myFittedRateHistograms[0].GetBinContent(k))
                    if hdownlist[i].Integral() == 0:
                        for k in range(0, hdownlist[i].GetNbinsX()+2):
                            hdownlist[i].SetBinContent(k, myFittedRateHistograms[0].GetBinContent(k))
                myHistogramCache.extend(huplist)
                myHistogramCache.extend(hdownlist)
                # Add fit parameter nuisances to nuisance table
                for hup in huplist:
                    addNuisanceForIndividualColumn(myColumnNames,myNuisanceInfo,c,hup.GetTitle())
                # Create bin-by-bin stat. histograms for fitted distribution and update the nuisance table
                myStatHistograms = addBinByBinStatUncert(c, myFittedRateHistograms[0], myColumnNames, myNuisanceInfo, 0.0, myFitSettings["fitmin"])
                myHistogramCache.extend(myStatHistograms)
                # Clear memory
                hFineBinning.Delete()
                hOriginalShape.Delete()
        # Print summary info
        printSummaryInfo(myColumnNames, myNuisanceInfo, myHistogramCache)
        # Histogram cache contains now all root files and nuisance table is now up to date
        # Create new root file and write
        myRootFilename = myRootfilePattern%m
        myRootFile = ROOT.TFile.Open(myRootFilename, "RECREATE")
        if myRootFile == None:
            raise Exception(ErrorLabel()+" Cannot open file '"+myRootFilename+"' for output!")
        for h in myHistogramCache:
            h.SetDirectory(myRootFile)
        myRootFile.Write()
        myRootFile.Close()
        # Create new datacard file and write
        myOutput = createDatacardOutput(myOriginalCardLines, myColumnNames, myNuisanceInfo)
        myFilename = myDatacardPattern%m
        myFile = open(myFilename, "w")
        myFile.write(myOutput)
        myFile.close()
        print "... Generated datacard files %s and %s"%(myFilename, myRootFilename)

