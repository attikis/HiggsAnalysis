'''
\package PseudoMultiCrabCreator

DESCRIPTION::
Used for creating a root file and proper directory structure to fool the dataset.py to think
 it is a genuine multicrab directory

USE CASES: 
Converterting QCD/FakeB/EwkGenuineB measurement results to readable format for the datacard generator
 
AUTHOR: 
Lauri A. Wendland
'''

#================================================================================================
# Imports
#================================================================================================
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys
import os
import shutil
from math import sqrt

import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset

#================================================================================================
# Clas definition
#================================================================================================
class PseudoMultiCrabCreator:
    ## Constructor
    # title is a string that goes to the multicrab directory name
    def __init__(self, title, inputMulticrabDir, verbose=False):
        suffix = ""
        s = inputMulticrabDir.split("_")
        if s[len(s)-1].endswith("pr") or s[len(s)-1].endswith("prong"):
            suffix = "_"+s[len(s)-1]
        self._verbose = verbose
        self._title = title+suffix
        self._mySubTitles = []
        self._modulesList = [] # List of PseudoMultiCrabModule objects
        self._inputMulticrabDir = inputMulticrabDir
        self._myBaseDir = None
        self._energy = None
        self._dataVersion = None
        #self._codeVersion = None
        return

    def Print(self, msg, printHeader=False):
        fName = __file__.split("/")[-1].replace("pyc", "py")
        if printHeader==True:
            print "===", fName
            print "\t", msg
        else:
            print "\t", msg
        return

    def Verbose(self, msg, printHeader=True):
        if not self._verbose:
            return
        self.Print(msg, printHeader)
        return

    def addModule(self, module):
        if self._energy == None:
            self._energy = module._energy
            self._dataVersion = module._dataVersion.Clone()
            #self._codeVersion = module._codeVersion.Clone()
            self._writeRootFileToDisk(self._currentSubTitle)
            self._dataVersion = None # No need to delete from gDirectory, since they were saved to disk already
            #self._codeVersion = None

        # Open root file
        myFilename = "%s/%s/res/histograms-%s.root" % (self._myBaseDir,self._title+self._mySubTitles[-1],self._title+self._mySubTitles[-1])
        myRootFile = None
        if os.path.exists(myFilename):
            myRootFile = ROOT.TFile(myFilename,"UPDATE")
        else:
            myRootFile = ROOT.TFile(myFilename,"CREATE")

        # Write module
        module.writeModuleToRootFile(myRootFile)
        myRootFile.Write()
        myRootFile.Close()
        module.delete()
        return

    def _createBaseDirectory(self, prefix):
        if self._myBaseDir != None:
            return
        # Create directory structure
        self._myBaseDir = os.path.join(self._inputMulticrabDir, "%s%s" % (prefix, self._title) )
        if os.path.exists(self._myBaseDir):
            shutil.rmtree(self._myBaseDir)

        self.Verbose("Creating dir %s" % (self._myBaseDir), True)
        os.mkdir(self._myBaseDir)
        return

    def initialize(self, subTitle, prefix="pseudoMulticrab_"):
        self._energy = None
        self._dataVersion = None
        #self._codeVersion = None
        self._createBaseDirectory(prefix)
        self._mySubTitles.append(subTitle)
        self._currentSubTitle = subTitle

        datasetDir = os.path.join(self._myBaseDir, self._title + subTitle)
        resDir = os.path.join(datasetDir, "res")

        self.Verbose("Creating dir %s" % (datasetDir), True)
        os.mkdir(datasetDir)

        self.Verbose("Creating sub-dir %s" % (resDir), False)
        os.mkdir(resDir)
        return

    def finalize(self, silent=False):
        '''
        Copy lumi.json file from input multicrab directory

        os.system("cp %s/lumi.json %s"%(self._inputMulticrabDir, self._myBaseDir))
        '''
        # Create multicrab.cfg
        filePath = os.path.join(self._myBaseDir, "multicrab.cfg")
        f = open(filePath, "w")
        f.write("# Ultimate pseudo-multicrab for fooling dataset.py, created by pseudoMultiCrabCreator.py\n")
    
        for item in self._mySubTitles:
            f.write("[%s]\n" % (self._title+item) )
        f.close()

        # Inform user ?
        msg = "Created pseudo-multicrab directory %s" % (ShellStyles.SuccessStyle()  + self._myBaseDir + ShellStyles.NormalStyle() )
        if silent == False:
            self.Print(msg, True)
        return

    def silentFinalize(self):
        '''
        Copy lumi.json file from input multicrab directory
        '''
        self.finalize(silent=True)
        return

    def getDirName(self):
        return self._myBaseDir

    def _writeRootFileToDisk(self, subTitle):
        # Open root file
        myRootFile = ROOT.TFile("%s/%s/res/histograms-%s.root"%(self._myBaseDir,self._title+self._mySubTitles[-1],self._title+self._mySubTitles[-1]),"UPDATE")
        # Write modules
        #for m in self._modulesList:
        #    m.writeModuleToRootFile(myRootFile)
        # Create config info histogram

        myRootFile.cd("/")
        myConfigInfoDir = myRootFile.mkdir("configInfo")
        hConfigInfo = ROOT.TH1F("configinfo","configinfo",2,0,2)
        hConfigInfo.GetXaxis().SetBinLabel(1,"control")
        hConfigInfo.SetBinContent(1, 1)
        hConfigInfo.GetXaxis().SetBinLabel(2,"energy")
        hConfigInfo.SetBinContent(2, self._energy)
        #hConfigInfo.GetXaxis().SetBinLabel(3,"luminosity")
        #hConfigInfo.SetBinContent(3, 1)
        hConfigInfo.SetDirectory(myConfigInfoDir)
        # Write a copy of data version and code version
        myConfigInfoDir.Add(self._dataVersion)
        #myConfigInfoDir.Add(self._codeVersion)
        # Write and close the root file
        myRootFile.Write()
        myRootFile.Close()
        return

#================================================================================================
# Clas definition
#================================================================================================
class PseudoMultiCrabModule:
    ## Constructor
    def __init__(self, dsetMgr, era, searchMode, optimizationMode, systematicsVariation=None, analysisName="signalAnalysis", verbose=False):
        self._verbose = verbose
        self._moduleName = "%s_%s_%s" % (analysisName, searchMode, era)
        if optimizationMode != "" and optimizationMode != None:
            self._moduleName += "_%s" % optimizationMode
        if systematicsVariation != None:
            self._moduleName += "_%s" % systematicsVariation
        self._shapes = [] # Shape histograms
        self._dataDrivenControlPlots = [] # Data driven control plot histograms
        self._counters = {} # Dictionary for counter values to be stored
        self._counterUncertainties = {} # Dictionary for counter values to be stored
        self._hCounters = None
        self._luminosity = self.GetLuminosity(dsetMgr)
        self._energy = self.GetEnergy(dsetMgr)
        self._counters["luminosity"] = self._luminosity
        self._counterUncertainties["luminosity"] = 0

        # Copy splittedBinInfo (for self-documenting)
        self._hSplittedBinInfo = dsetMgr.getDataset("Data").getDatasetRootHisto("SplittedBinInfo").getHistogram().Clone()
        myControlValue = self._hSplittedBinInfo.GetBinContent(1)
        for i in range(1,self._hSplittedBinInfo.GetNbinsX()+1):
            self._hSplittedBinInfo.SetBinContent(i, self._hSplittedBinInfo.GetBinContent(i)/myControlValue)
        self._hSplittedBinInfo.SetName("SplittedBinInfo")
       
        # Copy parameter set information
        #(objs, realNames) = dsetMgr.getDataset("Data").datasets[0].getRootObjects("parameterSet")
        #self._psetInfo = objs[0].Clone()

        # Copy data version and set it to pseudo
        #objs = None
        #realNames = None
        #if isinstance(dsetMgr.getDataset("Data"), dataset.Dataset):
        #    (objs, realNames) = dsetMgr.getDataset("Data").getRootObjects("../configInfo/dataVersion")
        #else:
        #    (objs, realNames) = dsetMgr.getDataset("Data").datasets[0].getRootObjects("../configInfo/dataVersion")
        #self._dataVersion = objs[0].Clone()
        self._dataVersion = self.GetDataVersion(dsetMgr)
        self._dataVersion.SetTitle("pseudo")

        # Copy code version
        #if isinstance(dsetMgr.getDataset("Data"), dataset.Dataset):
            #(objs, realNames) = dsetMgr.getDataset("Data").getRootObjects("../configInfo/codeVersion")
        #else:
            #(objs, realNames) = dsetMgr.getDataset("Data").datasets[0].getRootObjects("../configInfo/codeVersion")
        #self._codeVersion = objs[0].Clone()
        return

    def Print(self, msg, printHeader=False):
        fName = __file__.split("/")[-1].replace("pyc", "py")
        if printHeader==True:
            print "===", fName
            print "\t", msg
        else:
            print "\t", msg
        return

    def Verbose(self, msg, printHeader=True):
        if not self._verbose:
            return
        self.Print(msg, printHeader)
        return

    def GetEnergy(self, dsetMgr):
        '''
        Obtain luminosity information 
        from the dataset manager
        '''
        if isinstance(dsetMgr.getDataset("Data"), dataset.Dataset):
            myEnergy = dsetMgr.getDataset("Data").getEnergy()
        else:
            myEnergy = dsetMgr.getDataset("Data").datasets[0].getEnergy()
        msg = "Centre-of-Mass energy is %s TeV" % (ShellStyles.NoteStyle() + myEnergy + ShellStyles.NormalStyle())
        self.Verbose(msg, True)
        return float(myEnergy)

    def GetLuminosity(self, dsetMgr):
        '''
        Obtain luminosity information from the
        dataset manager by looping over all data 
        datasets
        '''
        myLuminosity = 0.0
        myDataDatasets = dsetMgr.getDataDatasets()
        for d in myDataDatasets:
            myLuminosity += d.getLuminosity()
            
        msg = "Integrated luminosity is %s%.3f%s" % (ShellStyles.NoteStyle(), myLuminosity, ShellStyles.NormalStyle())
        self.Verbose(msg, True)
        return myLuminosity

    def GetDataVersion(self, dsetMgr):
        '''
        Copy data version and set it to pseudo
        '''
        objs = None
        realNames = None
        if isinstance(dsetMgr.getDataset("Data"), dataset.Dataset):
            (objs, realNames) = dsetMgr.getDataset("Data").getRootObjects("../configInfo/dataVersion")
        else:
            (objs, realNames) = dsetMgr.getDataset("Data").datasets[0].getRootObjects("../configInfo/dataVersion")
        dataVersion = objs[0].Clone()

        msg = "The data-version is %s" % (ShellStyles.NoteStyle() + dataVersion.GetTitle() + ShellStyles.NormalStyle())
        self.Verbose(msg, True)
        return dataVersion

    def delete(self):
        if False:
            # Once the objects are written to file, they are erased from the list
            for h in self._shapes:
                h.Delete()
            for h in self._dataDrivenControlPlots:
                h.Delete()
            self._counters = None
            self._counterUncertainties = None
            self._hSplittedBinInfo.Delete()
            self._dataVersion.Delete()
            #self._codeVersion.Delete()
        ROOT.gDirectory.GetList().Delete()
        return

    def addShape(self, shapeHisto, plotName):
        self._shapes.append(shapeHisto.Clone(plotName))
        myValue = 0.0
        myUncert = 0.0
        for i in range(1, shapeHisto.GetNbinsX()+1):
            myValue += shapeHisto.GetBinContent(i)
            myUncert += shapeHisto.GetBinError(i)**2
        self._counters[plotName] = myValue
        self._counterUncertainties[plotName] = sqrt(myUncert)
        return

    def addDataDrivenControlPlot(self, histo, name):
        self._dataDrivenControlPlots.append(histo.Clone(name))
        return

    def addDataDrivenControlPlots(self, histoList, labelList):
        for i in range(0,len(histoList)):
            h = histoList[i].Clone()
            h.SetTitle(labelList[i])
            h.SetName(labelList[i])
            self._dataDrivenControlPlots.append(h)
        return

    def addPlots(self, plots, labels):
        '''
        Adds all plots in one go from the QCDPlotContainer object
        '''
        for i in range(len(labels)):
            h = plots[i]
            plotName = labels[i]
            if plotName.startswith("shape"):
                myValue = 0.0
                myUncert = 0.0
                for i in range(1, h.GetNbinsX()+1):
                    myValue += h.GetBinContent(i)
                    myUncert += h.GetBinError(i)**2
                self._counters[plotName] = myValue
                self._counterUncertainties[plotName] = sqrt(myUncert)
            h.SetName(plotName)
            self._dataDrivenControlPlots.append(h)
        return

    def writeModuleToRootFile(self, rootfile):
        # Create module directory
        rootfile.cd("/")
        myModuleDir = rootfile.mkdir(self._moduleName)
        # Save shape information
        for h in self._shapes:
            h.SetDirectory(myModuleDir)
        # Save data-driven control plots
        myDDPlotsDirName = "ForDataDrivenCtrlPlots"
        myDDPlotsDir = myModuleDir.mkdir(myDDPlotsDirName)
        for h in self._dataDrivenControlPlots:
            h.SetDirectory(myDDPlotsDir)
        
        # Save counter histogram
        myCounterDir = myModuleDir.mkdir("counters")
        myWeightedCounterDir = myCounterDir.mkdir("weighted")
        self._hCounters = ROOT.TH1F("counter","counter",len(self._counters),0,len(self._counters))
        i = 1
        for key in self._counters.keys():
            self._hCounters.GetXaxis().SetBinLabel(i, key)
            i += 1
            self._hCounters.SetBinContent(i, self._counters[key])
            self._hCounters.SetBinError(i, self._counterUncertainties[key])
        self._hCounters.SetDirectory(myWeightedCounterDir)
        # Save splittedBinInfo
        self._hSplittedBinInfo.SetDirectory(myModuleDir)
        # Save parameter set, code version and data version
        #myModuleDir.Add(self._psetInfo)
        # Create config info for the module
        myConfigInfoDir = myModuleDir.mkdir("configInfo")
        self._hConfigInfo = ROOT.TH1F("configinfo","configinfo",2,0,2) # Have to store the histogram to keep it alive for writing        self._hConfigInfo.GetXaxis().SetBinLabel(1,"control")
        self._hConfigInfo.GetXaxis().SetBinLabel(1,"control")
        self._hConfigInfo.SetBinContent(1, 1)
        #self._hConfigInfo.GetXaxis().SetBinLabel(2,"energy")
        #self._hConfigInfo.SetBinContent(2, self._energy)
        self._hConfigInfo.GetXaxis().SetBinLabel(2,"luminosity")
        self._hConfigInfo.SetBinContent(2, self._luminosity)
        self._hConfigInfo.SetDirectory(myConfigInfoDir)
        myConfigInfoDir.Add(self._dataVersion)
        #myConfigInfoDir.Add(self._codeVersion)
        #.SetDirectory(rootfile)
        #self._codeVersion.SetDirectory(rootfile)
        return
