#================================================================================================  
# Import modules
#================================================================================================  
import os
import time
import copy
import json
import re
import sys
import socket
import datetime

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

import datasets as datasetsTest
import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux
import HiggsAnalysis.NtupleAnalysis.tools.git as git
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles

#================================================================================================  
# Global Definitions
#================================================================================================  
_debugMode = False
_debugPUreweighting = False
_debugMemoryConsumption = False
sh_Error   = ShellStyles.ErrorStyle()
sh_Success = ShellStyles.SuccessStyle()
sh_Note    = ShellStyles.HighlightAltStyle()
sh_Normal  = ShellStyles.NormalStyle()

#================================================================================================
# Function Definition
#================================================================================================
def Verbose(msg, printHeader=False):
    '''
    Calls Print() only if verbose options is set to true.
    '''
    if not _debugMode:
        return
    Print(msg, printHeader)
    return

def Print(msg, printHeader=True):
    '''
    Simple print function. If verbose option is enabled prints, otherwise does nothing.                                                                                      
    '''
    fName = __file__.split("/")[-1]
    if printHeader:
        print "=== ", fName
    print "\t", msg
    return

def File(fname):
    fullpath = os.path.join(aux.higgsAnalysisPath(), fname)
    if not os.path.exists(fullpath):
        raise Exception("The file %s does not exist" % self._fullpath)
    return fullpath    

#================================================================================================
# Class Definition
#================================================================================================
class PSet:
    def __init__(self, **kwargs):
        self.__dict__["_data"] = copy.deepcopy(kwargs)

    def clone(self, **kwargs):
        pset = PSet(**self._data)
        for key, value in kwargs.iteritems():
            setattr(pset, key, value)
        return pset

    def __getattr__(self, name):
        return self._data[name]

    def __hasattr__(self, name):
        return name in self._data.keys()

    def __setattr__(self, name, value):
        self.__dict__["_data"][name] = value

    def _asDict(self):
        data = {}
        for key, value in self._data.iteritems():
            if isinstance(value, PSet):
                # Support for json dump of PSet
                data[key] = value._asDict()
            elif isinstance(value, list):
                # Support for json dump of list of PSets
                myList = []
                for item in value:
                    if isinstance(item, PSet):
                        myList.append(item._asDict())
                    else:
                        myList.append(item)
                data[key] = myList
            else:
                data[key] = value
        return data

    def __str__(self):
        return self.serialize_()

    def __repr__(self):
        return self.serialize_()

    def serialize_(self):
        return json.dumps(self._asDict(), sort_keys=True, indent=2)

#================================================================================================
# Class Definition
#================================================================================================
class Analyzer:
    def __init__(self, className, **kwargs):
        self.__dict__["_className"] = className
        silentStatus = True
        if "silent" in kwargs:
            silentStatus = kwargs["silent"]
            del kwargs["silent"]
        if "config" in kwargs:
            if isinstance(kwargs["config"], PSet):
                self.__dict__["_pset"] = kwargs["config"]
            else:
                raise Exception("The keyword config should be used only for providing the parameters as a PSet!")
        else:
            self.__dict__["_pset"] = PSet(**kwargs)
        if not silentStatus:
            print "Configuration parameters:"
            print self.__dict__["_pset"]
        return

    def __getattr__(self, name):
        return getattr(self._pset, name)

    def __hasattr__(self, name):
        return hasattr(self._pset, name)

    def __setattr__(self, name, value):
        print "%s = %s " % (name, value)
        setattr(self.__dict__["_pset"], name, value)

    def exists(self, name):
        return name in self._pset._asDict()

    def className_(self):
        return self.__dict__["_className"]

    def config_(self):
        return self.__dict__["_pset"].serialize_()

#================================================================================================
# Class Definition
#================================================================================================
class AnalyzerWithIncludeExclude:
    def __init__(self, analyzer, **kwargs):
        self._analyzer = analyzer
        if len(kwargs) > 0 and (len(kwargs) != 1 or not ("includeOnlyTasks" in kwargs or "excludeTasks" in kwargs)):
            raise Exception("AnalyzerWithIncludeExclude expects exactly 1 keyword argument, which is 'includeOnlyTasks' or 'excludeTasks'")
        self._includeExclude = {}
        self._includeExclude.update(kwargs)

    def getAnalyzer(self):
        return self._analyzer

    def runForDataset_(self, datasetName):
        if len(self._includeExclude) == 0:
            return True
        tasks = aux.includeExcludeTasks([datasetName], **(self._includeExclude))
        return len(tasks) == 1

#================================================================================================
# Class Definition
#================================================================================================
class DataVersion:
    def __init__(self, dataVersion):
        self._version = dataVersion
        self._isData = "data" in self._version
        self._isMC = "mc" in self._version
        return

    def __str__(self):
        return self._version

    def isData(self):
        return self._isData

    def isMC(self):
        return self._isMC

    def is53X(self):
        return "53X" in self._version

    def is74X(self):
        return "74X" in self._version

    def is84X(self):
        return "84X" in self._version

    def isS10(self):
        return self._isMC() and "S10" in self._version

#================================================================================================
# Class Definition
#================================================================================================
class Dataset:
    def __init__(self, name, files, dataVersion, lumiFile, pileup, nAllEvents):
        self._name = name
        self._files = files
        self._dataVersion = DataVersion(dataVersion)
        self._lumiFile = lumiFile
        self._pileup = pileup
        self._nAllEvents = nAllEvents
        return

    def getName(self):
        return self._name

    def getFileNames(self):
        return self._files

    def getDataVersion(self):
        return self._dataVersion

    def getLumiFile(self):
        return self._lumiFile

    def getPileUp(self,direction):
        if direction=="plus":
            return self._pileup["up"]
        elif direction=="minus":
            return self._pileup["down"]
        else:
            return self._pileup["nominal"]
      
    def getNAllEvents(self):
        return self._nAllEvents

#================================================================================================
# Class Definition
#================================================================================================
class Process:
    def __init__(self, outputPrefix="analysis", outputPostfix="", maxEvents={}):
        ROOT.gSystem.Load("libHPlusAnalysis.so")
        self._verbose = _debugMode
        self._outputPrefix  = outputPrefix
        self._outputPostfix = outputPostfix
        self._datasets = []
        self._analyzers = {}
        self._maxEvents = maxEvents
        self.datasetsData = [] # used only for PU-reweighting
        self._options = PSet()
        return
    
    def Verbose(self, msg, printHeader=False):
        '''
        Calls Print() only if verbose options is set to true.
        '''
        if not self._verbose:
            return
        self.Print(msg, printHeader)
        return

    def Print(self, msg, printHeader=True):
        '''
        Simple print function. If verbose option is enabled prints, otherwise does nothing.                                                                                      
        '''
        fName = __file__.split("/")[-1].replace(".pyc", ".py")
        if printHeader:
            print "=== ", fName
        print "\t", msg
        return

    def ConvertSymLinks(fileList):
        '''
        Takes as argument a list of files.
        If any of those are (EOS) symbolic links
        this will append the correct prefix for 
        accessing them on EOS.
        '''
        Verbose("ConvertSymLinks()", True)
        HOST = socket.gethostname()
        bUseSymLinks = False

        if "fnal" in HOST:
            prefix = "root://cmseos.fnal.gov//"
        elif "lxplus" in HOST:
            prefix = "root://eoscms.cern.ch//"
        else:
            prefix = ""
            
        # If the file is symbolic link store the target path
        for i, f in enumerate(fileList):
            if not os.path.islink(f):
                continue
            bUseSymLinks = True
            fileList[i] = prefix + os.path.realpath(f)

        if bUseSymLinks:
            self.Print("SymLinks detected. Appending prefix \"%s\" to all ROOT file paths" % (prefix) )
        return fileList


    def addDataset(self, name, files=None, dataVersion=None, lumiFile=None):
        Verbose("addDataset()", True)
        if files is None:
            files = datasetsTest.getFiles(name)

        prec = dataset.DatasetPrecursor(name, files)
        if dataVersion is None:
            dataVersion = prec.getDataVersion()
        #get pileup
        pileUp = {}
        pileUp["nominal"]=prec.getPileUp("nominal")
        pileUp["up"]=prec.getPileUp("up")
        pileUp["down"]=prec.getPileUp("down")

        nAllEvents = prec.getNAllEvents()
        prec.close()
        self._datasets.append( Dataset(name, files, dataVersion, lumiFile, pileUp, nAllEvents) )
        return

    def addDatasets(self, names):
        '''
        No explicit files possible here
        '''
        Verbose("addDataset()", True)
        for name in names:
            self.addDataset(name)
        return
        
    def addDatasetsFromMulticrab(self, directory, *args, **kwargs):
        '''
        kwargs for 'includeOnlyTasks' or 'excludeTasks' to set the datasets over which this analyzer is processed, default is all datasets
        '''
        Verbose("addDatasetsFromMulticrab()", True)
        blacklist = []
        if "blacklist" in kwargs.keys():
            if isinstance(kwargs["blacklist"], str):
                blacklist.append(kwargs["blacklist"])
            elif isinstance(kwargs["blacklist"], list):
                blacklist.extend(kwargs["blacklist"])
            else:
                raise Exception("Unsupported input format!")
            del kwargs["blacklist"]

        whitelist = []
        if "whitelist" in kwargs.keys():
            if isinstance(kwargs["whitelist"], str):
                whitelist.append(kwargs["whitelist"])
            elif isinstance(kwargs["whitelist"], list):
                whitelist.extend(kwargs["whitelist"])
            else:
                raise Exception("Unsupported input format!")
            del kwargs["whitelist"]

        dataset._optionDefaults["input"] = "histograms-*.root" #"miniaod2tree*.root"
        dsetMgrCreator = dataset.readFromMulticrabCfg(directory=directory, *args, **kwargs)
        dsets = dsetMgrCreator.getDatasetPrecursors()
        # Check if data datasets included
        for i, d in enumerate(dsets, 1):
            if d.isData():
                self.datasetsData.append(d)
        dsetMgrCreator.close()

        # Create a manager with data datasets (to enable PU reweighting even if not running with data)
        if len(self.datasetsData) < 1:
            dsetMgrCreator_tmp = dataset.readFromMulticrabCfg(directory=directory)
            dsets_tmp = dsetMgrCreator_tmp.getDatasetPrecursors()
            for i, d in enumerate(dsets_tmp, 1):
                if d.isData():
                    self.datasetsData.append(d)
            dsetMgrCreator_tmp.close()
        self.Print("Pileup reweighting will be done according to the sum of:\n\t%s" % (sh_Note + "\n\t".join([d.getName() for d in self.datasetsData]) + sh_Normal), True)


        if len(whitelist) > 0:
            for dset in dsets:
                isOnWhiteList = False
                for item in whitelist:
                    if dset.getName().startswith(item):
                        isOnWhiteList = True
                if not isOnWhiteList:
                    blacklist.append(dset.getName())

        for dset in dsets:
            isOnBlackList = False
            for item in blacklist:
                if dset.getName().startswith(item):
                    isOnBlackList = True
            if isOnBlackList:
                self.Print("Ignoring dataset because of black/whitelist options: '%s' ..." % dset.getName(), True)
            else:
                self.addDataset(dset.getName(), dset.getFileNames(), dataVersion=dset.getDataVersion(), lumiFile=dsetMgrCreator.getLumiFile())
        return

    def getDatasets(self):
        return self._datasets

    def setDatasets(self, datasets):
        self._datasets = datasets

    def getRuns(self):
        runmin = -1
        runmax = -1
        run_re = re.compile("\S+_Run20\S+_(?P<min>\d\d\d\d\d\d)_(?P<max>\d\d\d\d\d\d)")
        for d in self._datasets:
            if d.getDataVersion().isData():
                match = run_re.search(d.getName())
                if match:
                    min_ = int(match.group("min"))
                    max_ = int(match.group("max"))
                    if runmin < 0:
                        runmin = min_
                    else:
                        if min_ < runmin:
                            runmin = min_
                    if max_ > runmax:
                        runmax = max_
        return runmin,runmax

    def addAnalyzer(self, name, analyzer, **kwargs):
        Verbose("addAnalyzer()", True)
        if self.hasAnalyzer(name):
            raise Exception("Analyzer '%s' already exists" % name)
        self._analyzers[name] = AnalyzerWithIncludeExclude(analyzer, **kwargs)
        return

    def getAnalyzer(self, name):
        if not self.hasAnalyzer(name):
            raise Exception("Analyzer '%s' does not exist" % name)
        return self._analyzers[name].getAnalyzer()

    def removeAnalyzer(self, name):
        if not self.hasAnalyzer(name):
            raise Exception("Analyzer '%s' does not exist" % name)
        del self._analyzers[name]

    def hasAnalyzer(self, name):
        return name in self._analyzers

    def addOptions(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self._options, key, value)

    def isTTbarDataset(self, dset):
        if not dset.getName().startswith("TT"):
            return False
        ignoreList = ["TTZToQQ", "TTWJetsToQQ", "TTTT"]
        if dset.getName() in ignoreList:
            return False
        return True
        
    def run(self, proof=False, proofWorkers=None):
        outputDir = self._outputPrefix+"_"+time.strftime("%y%m%d_%H%M%S")
        if self._outputPostfix != "":
            outputDir += "_"+self._outputPostfix

        # Create output directory
        os.mkdir(outputDir)
        self.Print("Created output directory %s" % (sh_Note + outputDir + sh_Normal), True)

        multicrabCfg = os.path.join(outputDir, "multicrab.cfg")
        f = open(multicrabCfg, "w")
        # For-loop: All datasets to be ran
        for dset in self._datasets:
            f.write("[%s]\n\n" % dset.getName())
        f.close()

        # Copy/merge lumi files
        lumifiles = set([d.getLumiFile() for d in self._datasets])
        lumidata = {}
        for fname in lumifiles:
            if not os.path.exists(fname):
                continue
            f = open(fname)
            data = json.load(f)
            f.close()
            for k in data.keys():
                if k in lumidata:
                    msg  = "Luminosity JSON file %s has a dataset (%s) for which the luminosity has already been loaded. " % (fname, k) 
                    msg += "Please check the luminosity JSON files:\n%s" % ("\n".join(lumifiles))
                    raise Exception(sh_Error + msg + sh_Normal)
            lumidata.update(data)
        if len(lumidata) > 0:
            # Add run range in a json file, if runMin and runMax in pset
            rrdata = {}
            for aname, analyzerIE in self._analyzers.iteritems():
                ana = analyzerIE.getAnalyzer()
                if hasattr(ana, "__call__"):
                    for dset in self._datasets:
                        if dset.getDataVersion().isData():
                            ana = ana(dset.getDataVersion())
                            if ana.__getattr__("runMax") > 0:
                                rrdata[aname] = "%s-%s"%(ana.__getattr__("runMin"),ana.__getattr__("runMax"))
                                #lumidata[aname] = ana.__getattr__("lumi")
                                break
            if len(rrdata) > 0:
                f = open(os.path.join(outputDir, "runrange.json"), "w")
                json.dump(rrdata, f, sort_keys=True, indent=2)
                f.close()

            # Create the luminosity JSON file
            f = open(os.path.join(outputDir, "lumi.json"), "w")
            json.dump(lumidata, f, sort_keys=True, indent=2)
            self.Verbose("Created luminosity json file %s" % (sh_Note + f.name + sh_Normal), True)
            f.close()

        # Setup proof if asked
        _proof = None
        if proof:
            opt = ""
            if proofWorkers is not None:
                opt = "workers=%d"%proofWorkers
            _proof = ROOT.TProof.Open(opt)
            _proof.Exec("gSystem->Load(\"libHPlusAnalysis.so\");")

        # Init timing counters
        realTimeTotal = 0
        cpuTimeTotal = 0
        readMbytesTotal = 0
        callsTotal = 0

        # Print the datasets that will be run on!
        self.Print("Will process %d datasets in total:" % (len(self._datasets) ), True)
        for i, d in enumerate(self._datasets, 1):
            self.Print("%d) %s" % (i, sh_Note + d.getName() + sh_Normal), i==0)

        # Process over datasets
        ndset = 0
        for i, dset in enumerate(self._datasets, 1):
            hPUs = self._getDataPUhistos()
            # Initialize
            ndset += 1
            inputList = ROOT.TList()
            nanalyzers = 0
            anames = []
            usePUweights = False
            useTopPtCorrection = False
            nAllEventsPUWeighted = 0.0
            for aname, analyzerIE in self._analyzers.iteritems():
                if analyzerIE.runForDataset_(dset.getName()):
                    nanalyzers += 1
                    analyzer = analyzerIE.getAnalyzer()
                    if hasattr(analyzer, "__call__"):
                        analyzer = analyzer(dset.getDataVersion())
                        if analyzer is None:
                            raise Exception("Analyzer %s was specified as a function, but returned None" % aname)
                        if not isinstance(analyzer, Analyzer):
                            raise Exception("Analyzer %s was specified as a function, but returned object of %s instead of Analyzer" % (aname, analyzer.__class__.__name__))
                    inputList.Add(ROOT.TNamed("analyzer_"+aname, analyzer.className_()+":"+analyzer.config_()))
                    # ttbar status for top pt corrections
                    ttbarStatus = "0"
                    useTopPtCorrection = analyzer.exists("useTopPtWeights") and analyzer.__getattr__("useTopPtWeights")
                    #useTopPtCorrection = useTopPtCorrection and dset.getName().startswith("TT")
                    useTopPtCorrection = useTopPtCorrection and self.isTTbarDataset(dset)
                    if useTopPtCorrection:
                        ttbarStatus = "1"
                    inputList.Add(ROOT.TNamed("isttbar", ttbarStatus))
                    # intermediate H+ status for reweighting the NoNeutral samples
                    intermediateStatus = "0"
                    if dset.getName().find("IntermediateMassNoNeutral") > 0:
                        intermediateStatus = "1"
                    inputList.Add(ROOT.TNamed("isIntermediateNoNeutral", intermediateStatus))

                    # Pileup reweighting
                    self.Verbose("Getting pileup reweighting weights", True)
                    (puAllEvents, puStatus) = self._parsePUweighting(dset, analyzer, aname, hPUs, inputList)
                    nAllEventsPUWeighted += puAllEvents
                    usePUweights = puStatus
                    # Sum skim counters (from ttree)
                    hSkimCounterSum = self._getSkimCounterSum(dset.getFileNames())
                    inputList.Add(hSkimCounterSum)
                    # Add name
                    anames.append(aname)
            if nanalyzers == 0:
                self.Print("Skipping %s, no analyzers" % dset.getName(), True)
                continue                            

            self.Print("Processing dataset (%d/%d)" % (ndset, len(self._datasets) ))
            align= "{:<23} {:<1} {:<60}"
            info = {}
            info["Dataset"] = dset.getName()
            if dset.getDataVersion().isData():
                lumivalue = "--- not available in lumi.json (or lumi.json not available) ---"
                if dset.getName() in lumidata.keys():
                    lumivalue = lumidata[dset.getName()]
                info["Luminosity"] = str(lumivalue) + " fb-1"
            info["UsePUweights"] = usePUweights
            info["UseTopPtCorrection"] = useTopPtCorrection
            for key in info:
                self.Print(align.format(key, ":", info[key]), False)

            # Create dir for dataset ROOTT files   
            resDir = os.path.join(outputDir, dset.getName(), "res")
            resFileName = os.path.join(resDir, "histograms-%s.root"%dset.getName())
            os.makedirs(resDir)

            tchain = ROOT.TChain("Events")
            # For-loop: All file names for dataset
            for f in dset.getFileNames():
                tchain.Add(f)
            tchain.SetCacheLearnEntries(1000);
            tchain.SetCacheSize(10000000) # Set cache size to 10 MB (somehow it is not automatically set contrary to ROOT docs)

            tselector = ROOT.SelectorImpl()

            # FIXME: TChain.GetEntries() is needed only to give a time
            # estimate for the analysis. If this turns out to be slow,
            # we could store the number of events along the file names
            # (whatever is the method for that)
            inputList.Add(ROOT.TNamed("entries", str(tchain.GetEntries())))
            if dset.getDataVersion().isMC():
                inputList.Add(ROOT.TNamed("isMC", "1"))
            else:
                inputList.Add(ROOT.TNamed("isMC", "0"))
            inputList.Add(ROOT.TNamed("options", self._options.serialize_()))
            inputList.Add(ROOT.TNamed("printStatus", "1"))

            if _proof is not None:
                tchain.SetProof(True)
                inputList.Add(ROOT.TNamed("PROOF_OUTPUTFILE_LOCATION", resFileName))
            else:
                inputList.Add(ROOT.TNamed("OUTPUTFILE_LOCATION", resFileName))

            tselector.SetInputList(inputList)

            readBytesStart = ROOT.TFile.GetFileBytesRead()
            readCallsStart = ROOT.TFile.GetFileReadCalls()
            timeStart = time.time()
            clockStart = time.clock()

            # Determine how many events to run on for given dataset
            if len(self._maxEvents.keys()) > 0:
                key = ""
                for k in self._maxEvents.keys():
                    if k.lower() == "all":
                        key = k
                        break
                    maxEv_re = re.compile(k)
                    match = maxEv_re.search(dset.getName())
                    if match:
                        key = k
                        break
                if key == "":
                    tchain.Process(tselector)
                else:
                    maxEvts  = self._maxEvents[key]
                    if maxEvts == -1:
                        tchain.Process(tselector)
                    else:
                        tchain.SetCacheEntryRange(0, self._maxEvents[key])
                        tchain.Process(tselector, "", self._maxEvents[key])
            else:
                tchain.Process(tselector)
            if _debugMemoryConsumption:
                print "    MEMDBG: TChain cache statistics:"
                tchain.PrintCacheStats()
            
            # Obtain Nall events for top pt corrections
            NAllEventsTopPt = 0
            if useTopPtCorrection:
                for inname in dset.getFileNames():
                    fIN = ROOT.TFile.Open(inname)
                    h = fIN.Get("configInfo/topPtWeightAllEvents")
                    if h != None:
                        binNumber = 2 # nominal
                        if hasattr(analyzer, "topPtSystematicVariation"):
                            variation = getattr(analyzer, "topPtSystematicVariation")
                            if variation == "minus":
                                binNumber = 0
                            # FIXME: The bin is to be added to the ttrees
                            #elif variation == "plus":
                                #binNumber = 3
                                #if not h.GetXaxis().GetBinLabel().endsWith("Plus"):
                                    #raise Exception("This should not happen")
                        if binNumber > 0:
                            NAllEventsTopPt += h.GetBinContent(binNumber)
                    else:
                        raise Exception("Warning: Could not obtain N(AllEvents) for top pt reweighting")
                    ROOT.gROOT.GetListOfFiles().Remove(fIN)
                    fIN.Close()

            # Write configInfo
            fIN = ROOT.TFile.Open(dset.getFileNames()[0])
            cinfo = fIN.Get("configInfo/configinfo")
            tf = ROOT.TFile.Open(resFileName, "UPDATE")
            configInfo = tf.Get("configInfo")
            if configInfo == None:
                configInfo = tf.mkdir("configInfo")
            configInfo.cd()
            dv = ROOT.TNamed("dataVersion", str(dset.getDataVersion()))
            dv.Write()
            dv.Delete()
            cv = ROOT.TNamed("codeVersionAnalysis", git.getCommitId())
            cv.Write()
            cv.Delete()
            if not cinfo == None:
                # Add more information to configInfo
                n = cinfo.GetNbinsX()
                cinfo.SetBins(n+3, 0, n+3)
                cinfo.GetXaxis().SetBinLabel(n+1, "isData")
                cinfo.GetXaxis().SetBinLabel(n+2, "isPileupReweighted")
                cinfo.GetXaxis().SetBinLabel(n+3, "isTopPtReweighted")
                # Add "isData" column
                if not dset.getDataVersion().isMC():
                    cinfo.SetBinContent(n+1, cinfo.GetBinContent(1))
                # Add "isPileupReweighted" column
                if usePUweights:
                    cinfo.SetBinContent(n+2, nAllEventsPUWeighted / nanalyzers)
                # Add "isTopPtReweighted" column
                if useTopPtCorrection:
                    cinfo.SetBinContent(n+3, NAllEventsTopPt)
                # Write
                cinfo.Write()
                ROOT.gROOT.GetListOfFiles().Remove(fIN);
                fIN.Close()

            # Memory management
            configInfo.Delete()
            ROOT.gROOT.GetListOfFiles().Remove(tf);
            tf.Close()
            for item in inputList:
                if isinstance(item, ROOT.TObject):
                    item.Delete()
            inputList = None
            if hSkimCounterSum != None:
                hSkimCounterSum.Delete()
            if _debugMemoryConsumption:
                print "      MEMDBG: gDirectory", ROOT.gDirectory.GetList().GetSize()
                print "      MEMDBG: list ", ROOT.gROOT.GetList().GetSize()
                print "      MEMDBG: globals ", ROOT.gROOT.GetListOfGlobals().GetSize()
                #for item in ROOT.gROOT.GetListOfGlobals():
                    #print item.GetName()
                print "      MEMDBG: files", ROOT.gROOT.GetListOfFiles().GetSize()
                #for item in ROOT.gROOT.GetListOfFiles():
                #    print "          %d items"%item.GetList().GetSize()
                print "      MEMDBG: specials ", ROOT.gROOT.GetListOfSpecials().GetSize()
                for item in ROOT.gROOT.GetListOfSpecials():
                    print "          "+item.GetName()
                
                #gDirectory.GetList().Delete();
                #gROOT.GetList().Delete();
                #gROOT.GetListOfGlobals().Delete();
                #TIter next(gROOT.GetList());
                #while (TObject* o = dynamic_cast<TObject*>(next())) {
                  #o.Delete();
                #}
            
            # Performance and information
            timeStop = time.time()
            clockStop = time.clock()
            readCallsStop = ROOT.TFile.GetFileReadCalls()
            readBytesStop = ROOT.TFile.GetFileBytesRead()

            calls = ""
            if _proof is not None:
                tchain.SetProof(False)
                queryResult = _proof.GetQueryResult()
                cpuTime = queryResult.GetUsedCPU()
                readMbytes = queryResult.GetBytes()/1024/1024
            else:
                cpuTime = clockStop-clockStart
                readMbytes = float(readBytesStop-readBytesStart)/1024/1024
                calls = " (%d calls)" % (readCallsStop-readCallsStart)
            realTime = timeStop-timeStart

            # Print usage stats in user-friendly formatting
            self.PrintStats(readCallsStop, readCallsStart, cpuTime, realTime, readMbytes)

            # Time accumulation
            realTimeTotal   += realTime
            cpuTimeTotal    += cpuTime
            readMbytesTotal += readMbytes

        # Total time stats
        self.PrintStatsTotal(readMbytes, cpuTimeTotal, realTimeTotal, readMbytesTotal)

        # Inform user of location of results
        self.Print("Results are in %s" % (sh_Success + outputDir + sh_Normal), True)
        return outputDir
    
    def PrintStatsTotal(self, readMbytes, cpuTimeTotal, realTimeTotal, readMbytesTotal):
        '''
        Print usage stats (total) in user-friendly formatting
        '''
        if len(self._datasets) < 2:
            return
        self.Print("Processed all %d datasets" % (len(self._datasets)), True)
        align = "{:<15} {:<1} {:<30}"
        total = {}
        total["CPU time"]     = "%.1f" % cpuTimeTotal  + " s (%.1f %% of real time)" % (cpuTimeTotal/realTimeTotal*100)
        total["Read size"]    = "%.1f" % (readMbytesTotal) + " MB"
        total["Read speed"]   = "%.1f" % (readMbytes/realTimeTotal) + " MB/s"
        dt = str(datetime.timedelta(seconds=round(realTimeTotal))) + " (h:mm:ss)"
        total["Real time"] = "%s"   % (sh_Note + dt + sh_Normal)
        # total["Real time"]    = "%.1f" % realTimeTotal + " s"
        for key in total:
            self.Print(align.format(key, ":", total[key]), False)
        return

    def PrintStats(self, readCallsStop, readCallsStart, cpuTime, realTime, readMbytes):
        '''
        Print usage stats in user-friendly formatting
        '''
        align= "{:<23} {:<1} {:<60}"
        info = {}
        info["Read Calls"]   = "%s"   % (readCallsStop-readCallsStart)
        info["CPU time"]     = "%.1f" % cpuTime  + " s"
        info["Read Percent"] = "%.1f" % (cpuTime/realTime*100) + " %"
        info["Read Size"]    = "%.1f" % (readMbytes) + " MB"
        info["Read Speed"]   = "%.1f" % (readMbytes/realTime) + " MB/s"
        dt = str(datetime.timedelta(seconds=round(realTime))) + " (h:mm:ss)"
        info["Real time"] = "%s"   % (sh_Note + dt + sh_Normal)
        # info["Real time"]    = "%.1f" % realTime + " s"
        for key in info:
            self.Print(align.format(key, ":", info[key]), False)
        return

    def _getDataPUhistos(self):
        '''
        Get data PU distributions from data
        This is done every time for a dataset since memory management is simpler to handle
        if all the histograms in memory are deleted after reading a dataset is finished

        Returns PU histograms for data
        '''
        hPUs = {}
        count= 0
        for aname, analyzerIE in self._analyzers.iteritems():
            count+=1
            hPU = None            
            direction="nominal"
            analyzer = analyzerIE.getAnalyzer()

            if hasattr(analyzer,"usePileupWeights"):
                usePUweights = analyzer.__getattr__("usePileupWeights")
                if not usePUweights:
                    continue

            if hasattr(analyzer, "PUWeightSystematicVariation"):
                direction=getattr(analyzer, "PUWeightSystematicVariation")

            # For-loop: All data datasets
            for i, dset in enumerate(self.datasetsData, 1):
                if analyzerIE.runForDataset_(dset.getName()):
                    if hPU is None:
                        hPU = dset.getPileUp(direction).Clone()
                    else:
                        hPU.Add(dset.getPileUp(direction))

            # Determine PU histo name postfix 
            if hPU != None:
                if direction == "plus":
                    direction_postfix="Up"
                elif direction == "minus":
                    direction_postfix = "Down"
                else:
                    direction_postfix = ""

                # Set the histogram name
                hPU.SetName("PileUpData"+direction_postfix)
                hPU.SetDirectory(None)
                hPUs[aname] = hPU
                self.Verbose("Saving PU direction \"%s\" for aname \"%s\". Mean = %s" % (direction, aname, hPUs[aname].GetMean() ), True)
                # self.Verbose("Determined PU spectrum from data to have mean %.1f" % (hPUs[aname].GetMean()), True)
            else:
                raise Exception("Cannot determine PU spectrum for data!")
        return hPUs

    def _getDataPUhistos_ORIGINAL(self): # for backwards compatibility while in transition
        '''
        Get data PU distributions from data
        This is done every time for a dataset since memory management is simpler to handle
        if all the histograms in memory are deleted after reading a dataset is finished

        Returns PU histograms for data
        '''
        hPUs = {}
        for aname, analyzerIE in self._analyzers.iteritems():
            hPU = None
            direction="nominal"
            analyzer = analyzerIE.getAnalyzer()
            if hasattr(analyzer,"usePileupWeights"):
                usePUweights = analyzer.__getattr__("usePileupWeights")
                if not usePUweights:
                    continue
            # iro
            if hasattr(analyzer, "PUWeightSystematicVariation"):
                direction=getattr(analyzer, "PUWeightSystematicVariation")

            for i, dset in enumerate(self._datasets, 1):
                self.Print("dataset = %s" % (dset.getName()), i==1)
                if dset.getDataVersion().isData() and analyzerIE.runForDataset_(dset.getName()):
                    if hPU is None:
                        hPU = dset.getPileUp(direction).Clone()
                    else:
                        hPU.Add(dset.getPileUp(direction))
            if hPU != None:
                if direction == "plus":
                    direction_postfix="Up"
                elif direction == "minus":
                    direction_postfix = "Down"
                else:
                    direction_postfix = ""
                hPU.SetName("PileUpData"+direction_postfix)
                hPU.SetDirectory(None)
                hPUs[aname] = hPU
#                #Debug prints:
#                sys.stderr.write("_getDataPUhistos saves direction ")
#                sys.stderr.write(direction)
#                sys.stderr.write(" histograms for aname ")
#                sys.stderr.write(aname)
#                sys.stderr.write(", mean =")
#                sys.stderr.write(str(hPUs[aname].GetMean()))
#                sys.stderr.write("\n")
            else:
                raise Exception("Cannot determine PU spectrum for data!")
        return hPUs
 
    def _parsePUweighting(self, dset, analyzer, aname, hDataPUs, inputList):
        '''
        Obtains PU histogram for MC
        Returns tuple of N(all events PU weighted) and status of enabling PU weights
        '''
        Verbose("_parsePUweighting()", True)

        if not dset.getDataVersion().isMC():
            return (0.0, False)
        hPUMC = None
        nAllEventsPUWeighted = 0.0
        if aname in hDataPUs.keys():
#            if _debugPUreweighting:
#                for k in range(hDataPUs[aname].GetNbinsX()):
#                    print "DEBUG(PUreweighting,aname=%s): dataPU:%d:%f"%(aname,k+1, hDataPUs[aname].GetBinContent(k+1))
            inputList.Add(hDataPUs[aname])
        else:
            n = 100
            hFlat = ROOT.TH1F("dummyPU"+aname,"dummyPU"+aname,n,0,n)
            hFlat.SetName("PileUpData")
            for k in range(n):
                hFlat.Fill(k+1, 1.0/n)
            inputList.Add(hFlat)
            hDataPUs[aname] = hFlat
        if dset.getPileUp("nominal") == None:
            raise Exception("Error: pileup spectrum is missing from dataset! Please switch to using newest multicrab!")
        hPUMC = dset.getPileUp("nominal").Clone()
        hPUMC.SetDirectory(None)

        # Sanity checks: Integral and Binning
        if hDataPUs[aname].Integral() == 0.0:
            raise Exception("hDataPUs[%s].Integral() = %s! Make sure that the histogram \"configInfo/pileup\" of dataset \"%s\" is not empty!" % (aname, hDataPUs[aname].Integral(), dset.getName()) )
        else:
            Verbose("hDataPUs[%s].GetMean() =  %s" % (aname, hDataPUs[aname].GetMean() ), False)
        if hPUMC.GetNbinsX() != hDataPUs[aname].GetNbinsX():
            raise Exception("Pileup histogram dimension mismatch! data nPU has %d bins and MC nPU has %d bins, for dataset \"%s\"!" % (hDataPUs[aname].GetNbinsX(), hPUMC.GetNbinsX(), dset.getName()) )
        else:
            Verbose("hPUMC.GetMean() =  %s" % (hPUMC.GetMean() ), False)

        hPUMC.SetName("PileUpMC")
#        if _debugPUreweighting:
#            for k in range(hPUMC.GetNbinsX()):
#                print "Debug(PUreweighting): MCPU:%d:%f"%(k+1, hPUMC.GetBinContent(k+1))
        inputList.Add(hPUMC)

        if analyzer.exists("usePileupWeights"):
            usePUweights = analyzer.__getattr__("usePileupWeights")           
            if _debugPUreweighting:
                Print("Debug(PUreweighting,aname=%s): hDataPUs[aname].Integral(): %f"%(aname,hDataPUs[aname].Integral()), True)
                Print("Debug(PUreweighting,aname=%s): hDataPUs[aname].Mean(): %f"%(aname,hDataPUs[aname].GetMean()), True)

            # Apply PU-reweighting
            factor = hPUMC.Integral() / hDataPUs[aname].Integral()
            for k in range(0, hPUMC.GetNbinsX()+2):
                if hPUMC.GetBinContent(k) > 0.0:
                    w = hDataPUs[aname].GetBinContent(k) / hPUMC.GetBinContent(k) * factor
                    nAllEventsPUWeighted += w * hPUMC.GetBinContent(k)
            if _debugPUreweighting:
                Print("Debug(PUreweighting, aname=%s): normalization factor: %f"%(aname,factor), True)
                Print("Debug(PUreweighting, aname=%s): nAllEventsPUWeighted: %f"%(aname,nAllEventsPUWeighted), True)

        return (nAllEventsPUWeighted, usePUweights)

 
    def _getSkimCounterSum(self, datasetFilenameList):
        '''
        Sums the skim counters from input files and returns a pset containing them 
        '''
        Verbose("_getSkimCounterSum()", True)

        hSkimCounterSum = None
        for inname in datasetFilenameList:
            fIN = ROOT.TFile.Open(inname)
            hSkimCounters = fIN.Get("configInfo/SkimCounter")
            if hSkimCounterSum == None:
                hSkimCounterSum = hSkimCounters.Clone()
                hSkimCounterSum.SetDirectory(None) # Store the histogram to memory TDirectory, not into fIN
            else:
                hSkimCounterSum.Add(hSkimCounters)
            hSkimCounters.Delete()
            fIN.Close()
        if hSkimCounterSum == None:
            # Construct an empty histogram
            hSkimCounterSum = ROOT.TH1F("SkimCounter","SkimCounter",1,0,1)
        else:
            # Format bin labels
            for i in range(hSkimCounterSum.GetNbinsX()):
                hSkimCounterSum.GetXaxis().SetBinLabel(i+1, "ttree: %s"%hSkimCounterSum.GetXaxis().GetBinLabel(i+1))
        hSkimCounterSum.SetName("SkimCounter")
        return hSkimCounterSum

if __name__ == "__main__":
    import unittest
    class TestPSet(unittest.TestCase):
        def testConstruct(self):
            d = {"foo": 1, "bar": 4}
            a = PSet(**d)
            self.assertEqual(a.foo, 1)
            self.assertEqual(a.bar, 4)
            d["foo"] = 5
            self.assertEqual(a.foo, 1)

        def testClone(self):
            a = PSet(foo=1, bar=4)
            b = a.clone()
            self.assertEqual(b.foo, a.foo)
            self.assertEqual(b.bar, a.bar)
            a.foo = 5
            self.assertEqual(a.foo, 5)
            self.assertEqual(b.foo, 1)

            c = a.clone(foo=10, xyzzy=42)
            self.assertEqual(a.foo, 5)
            self.assertEqual(c.foo, 10)
            self.assertEqual(c.xyzzy, 42)

        def testRecursive(self):
            a = PSet(foo=1, bar=PSet(a=4, b="foo"))
            self.assertEqual(a.foo, 1)
            self.assertEqual(a.bar.a, 4)
            self.assertEqual(a.bar.b, "foo")

        def testSet(self):
            a = PSet()
            a.foo = 1
            a.bar = "foo"

            setattr(a, "xyzzy", 42)

            self.assertEqual(a.foo, 1)
            self.assertEqual(a.bar, "foo")
            self.assertEqual(a.xyzzy, 42)

        def testSerialize(self):
            a = PSet(foo=1, bar=PSet(a=0.5, b="foo"))
            a.xyzzy = 42
            setattr(a, "fred", 56)
            self.assertEqual(a.serialize_(), """{
  "bar": {
    "a": 0.5, 
    "b": "foo"
  }, 
  "foo": 1, 
  "fred": 56, 
  "xyzzy": 42
}""")
        def testSerializeListOfPSet(self):
            a = PSet(foo=1, bar=[PSet(a=0.5),PSet(a=0.7)])
            self.assertEqual(a.serialize_(), """{
  "bar": [
    {
      "a": 0.5
    }, 
    {
      "a": 0.7
    }
  ], 
  "foo": 1
}""")

    class TestFile(unittest.TestCase):
        def testConstruct(self):
            f = File("NtupleAnalysis/python/main.py")
            self.assertEqual(f, os.path.join(aux.higgsAnalysisPath(), "NtupleAnalysis/python/main.py"))
            self.assertRaises(Exception, File, "NtupleFoo")

        def testSerialize(self):
            a = PSet(foo=File("NtupleAnalysis/python/main.py"))
            self.assertEqual(a.serialize_(), """{
  "foo": "%s/NtupleAnalysis/python/main.py"
}""" % aux.higgsAnalysisPath())

    class TestAnalyzer(unittest.TestCase):
        def testConstruct(self):
            a = Analyzer("Foo", foo=1, bar="plop", xyzzy = PSet(fred=42))
            self.assertEqual(a.className_(), "Foo")
            self.assertEqual(a.foo, 1)
            self.assertEqual(a.bar, "plop")
            self.assertEqual(a.xyzzy.fred, 42)
            self.assertEqual(a.config_(), """{
  "bar": "plop", 
  "foo": 1, 
  "xyzzy": {
    "fred": 42
  }
}""")

        def testModify(self):
            a = Analyzer("Foo", foo=1)
            self.assertEqual(a.foo, 1)

            a.bar = "plop"
            a.foo = 2
            setattr(a, "xyzzy", PSet(a=10))
            self.assertEqual(a.foo, 2)
            self.assertEqual(a.bar, "plop")
            self.assertEqual(a.xyzzy.a, 10)
            self.assertEqual(a.config_(), """{
  "bar": "plop", 
  "foo": 2, 
  "xyzzy": {
    "a": 10
  }
}""")

            a.xyzzy.a = 20
            self.assertEqual(a.xyzzy.a, 20)

            setattr(a, "xyzzy", 50.0)
            self.assertEqual(a.xyzzy, 50.0)

    class TestAnalyzerWithIncludeExclude(unittest.TestCase):
        def testIncludeExclude(self):
            a = AnalyzerWithIncludeExclude(None, includeOnlyTasks="Foo")
            self.assertEqual(a.runForDataset_("Foo"), True)
            self.assertEqual(a.runForDataset_("Bar"), False)
            self.assertEqual(a.runForDataset_("Foobar"), True)

            a = AnalyzerWithIncludeExclude(None, excludeTasks="Foo")
            self.assertEqual(a.runForDataset_("Foo"), False)
            self.assertEqual(a.runForDataset_("Bar"), True)
            self.assertEqual(a.runForDataset_("Foobar"), False)

    class TestProcess(unittest.TestCase):
        #Does not work anymore, since addDataset calls DatasetPrecursor, which fails to open foo1.root since it does not exist
        #def testDataset(self):
            #p = Process()
            #p.addDataset("Foo", ["foo1.root", "foo2.root"], dataVersion="data")
            #p.addDataset("Test", dataVersion="mc")

            #self.assertEqual(len(p._datasets), 2)
            #self.assertEqual(p._datasets[0].getName(), "Foo")
            #self.assertEqual(len(p._datasets[0].getFileNames()), 2)
            #self.assertEqual(p._datasets[0].getFileNames(), ["foo1.root", "foo2.root"])
            #self.assertEqual(p._datasets[1].getName(), "Test")
            #self.assertEqual(len(p._datasets[1].getFileNames()), 2)
            #self.assertEqual(p._datasets[1].getFileNames(), ["testfile1.root", "testfile2.root"])

        def testAnalyzer(self):
            p = Process()
            p.addAnalyzer("Test1", Analyzer("FooClass", foo=1))
            p.addAnalyzer("Test2", Analyzer("FooClass", foo=2))

            self.assertEqual(len(p._analyzers), 2)
            self.assertTrue(p.hasAnalyzer("Test1"))
            self.assertTrue(p.hasAnalyzer("Test2"))
            self.assertFalse(p.hasAnalyzer("Test3"))

            self.assertEqual(p.getAnalyzer("Test1").foo, 1)
            self.assertEqual(p.getAnalyzer("Test2").foo, 2)

            p.removeAnalyzer("Test2")
            self.assertEqual(len(p._analyzers), 1)
            self.assertTrue(p.hasAnalyzer("Test1"))
            self.assertFalse(p.hasAnalyzer("Test2"))

        def testOptions(self):
            p = Process()
            p.addOptions(Foo = "bar", Bar = PSet(x=1, y=2.0))

            self.assertEqual(p._options.Foo, "bar")
            self.assertEqual(p._options.Bar.x, 1)
            self.assertEqual(p._options.Bar.y, 2)

            p.addOptions(Foo = "xyzzy", Plop = PSet(x=1, b=3))

            self.assertEqual(p._options.Foo, "xyzzy")
            self.assertEqual(p._options.Plop.x, 1)
            self.assertEqual(p._options.Plop.b, 3)

        def testSelectorImpl(self):
            t = ROOT.SelectorImpl()

            # dummy test
            self.assertEqual(isinstance(t, ROOT.TSelector), True)

    unittest.main()
