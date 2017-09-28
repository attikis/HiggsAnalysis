lumiMask = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Cert_294927-302654_13TeV_PromptReco_Collisions17_JSON.txt"


#================================================================================================ 
# Class Definition
#================================================================================================ 
import os

class Dataset:
    def __init__(self, url, dbs="global", dataVersion="80Xmc", dasQuery="", lumiMask=lumiMask, name=""):
        self.URL = url
        self.DBS = dbs
        self.dataVersion = dataVersion
        if not os.path.dirname(lumiMask):
            lumiMask = os.path.join(os.environ['CMSSW_BASE'],"src/HiggsAnalysis/MiniAOD2TTree/data",lumiMask)
        self.lumiMask = lumiMask
        self.DASquery = dasQuery
	self.name = name

    def isData(self):
        if "data" in self.dataVersion:
            return True
        return False

    def getName(self):
	return self.name


#================================================================================================ 
# Data
#================================================================================================ 
datasetsTauData = []
das = ""
datasetsTauData.append(Dataset('/Tau/Run2017A-PromptReco-v3/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsTauData.append(Dataset('/Tau/Run2017B-PromptReco-v2/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsTauData.append(Dataset('/Tau/Run2017C-PromptReco-v3/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsTauData.append(Dataset('/Tau/Run2017D-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))

datasetsJetHTData = []
das = ""


datasetsMuonData = []
das = ""
datasetsMuonData.append(Dataset('/SingleMuon/Run2017A-PromptReco-v3/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsMuonData.append(Dataset('/SingleMuon/Run2017B-PromptReco-v2/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsMuonData.append(Dataset('/SingleMuon/Run2017C-PromptReco-v3/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsMuonData.append(Dataset('/SingleMuon/Run2017D-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsMuonData.append(Dataset('/SingleMuon/Run2017E-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))


datasetsZeroBiasData = []
das = ""
#datasetsZeroBiasData.append(Dataset('/ZeroBias1/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias2/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias3/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias4/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias5/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias6/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias7/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias8/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
#datasetsZeroBiasData.append(Dataset('/ZeroBias9/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))
datasetsZeroBiasData.append(Dataset('/ZeroBias10/Run2017A-PromptReco-v1/MINIAOD', dataVersion="92Xdata", dasQuery=das, lumiMask=lumiMask))





#================================================================================================ 
# MC, 83X
#================================================================================================ 
datasetsSignalTB = []
das = ""


datasetsSignalTauNu = []



datasetsSingleTop = []


datasetsTop = []
das = ""
datasetsTop.append(Dataset('/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/PhaseISpring17MiniAOD-FlatPU28to62_90X_upgrade2017_realistic_v20-v1/MINIAODSIM', dataVersion="92Xmc", dasQuery=das)) # new tune


datasetsTTJets = []


datasetsDY = []
das = ""
#datasetsDY.append(Dataset('', dataVersion="83Xmc", dasQuery=das))


datasetsDYJetsToQQ = []


datasetsZprime = []


datasetsWJets = []


datasetsWJetsToQQ = []


datasetsZJetsToQQ = []


datasetsDiboson = []


datasetsDibosonToQQ = []


datasetsQCD = []


datasetsQCDMuEnriched = []


datasetsQCDbEnriched = []


datasetsQCD_HT_GenJets5 = []


datasetsQCD_HT_BGenFilter = []


datasetsQCD_HT = []


datasetsTTWJetsToQQ = []


datasetsTTTT = []


datasetsTTBB = []


datasetsTTZToQQ = []


datasetsNeutrino = []





#================================================================================================ 
# MC, Trigger Development
#================================================================================================ 
datasetsSignalTauNu_TRGdev = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FChargedHiggs_*%2*%2/RAWAODSIM"
datasetsSignalTauNu_TRGdev.append(Dataset('/ChargedHiggs_TTToHplusBWB_HplusToTauNu_M-80_13TeV_amcatnlo_pythia8/PhaseIFall16MiniAOD-FlatPU28to62HcalNZSRAW_PhaseIFall16_90X_upgrade2017_realistic_v6_C1-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTauNu_TRGdev.append(Dataset('/ChargedHiggs_TTToHplusBWB_HplusToTauNu_M-160_13TeV_amcatnlo_pythia8/PhaseIFall16MiniAOD-FlatPU28to62HcalNZSRAW_PhaseIFall16_90X_upgrade2017_realistic_v6_C1-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTauNu_TRGdev.append(Dataset('/ChargedHiggs_HplusTB_HplusToTauNu_M-200_13TeV_amcatnlo_pythia8/PhaseIFall16MiniAOD-FlatPU28to62HcalNZSRAW_PhaseIFall16_90X_upgrade2017_realistic_v6_C1-v2/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTauNu_TRGdev.append(Dataset('/ChargedHiggs_HplusTB_HplusToTauNu_M-500_13TeV_amcatnlo_pythia8/PhaseIFall16MiniAOD-FlatPU28to62HcalNZSRAW_PhaseIFall16_90X_upgrade2017_realistic_v6_C1-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTauNu_TRGdev.append(Dataset('/ChargedHiggs_HplusTB_HplusToTauNu_M-1000_13TeV_amcatnlo_pythia8/PhaseIFall16MiniAOD-FlatPU28to62HcalNZSRAW_PhaseIFall16_90X_upgrade2017_realistic_v6_C1-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))


#================================================================================================ 
# Dataset Grouping
#================================================================================================ 
tauLegDatasets = []
#tauLegDatasets.extend(datasetsZeroBiasData)
tauLegDatasets.extend(datasetsMuonData)
#tauLegDatasets.extend(datasetsDY)
#tauLegDatasets.extend(datasetsZprime)
# tauLegDatasets.extend(datasetsWJets_reHLT)
# tauLegDatasets.extend(datasetsQCDMuEnriched_reHLT)
# tauLegDatasets.extend(datasetsH125)


metLegDatasets = []
metLegDatasets.extend(datasetsTauData)
metLegDatasets.extend(datasetsDY)
metLegDatasets.extend(datasetsTop)
#metLegDatasets.extend(datasetsSingleTop)
metLegDatasets.extend(datasetsWJets)
metLegDatasets.extend(datasetsQCD)

l1Datasets = []
l1Datasets.extend(datasetsZeroBiasData)
l1Datasets.extend(datasetsNeutrino)
l1Datasets.extend(datasetsQCD)

signalAnalysisDatasets = []
signalAnalysisDatasets.extend(datasetsTauData)
#signalAnalysisDatasets.extend(datasetsDY) 
#signalAnalysisDatasets.extend(datasetsTop)
#signalAnalysisDatasets.extend(datasetsSingleTop)
#signalAnalysisDatasets.extend(datasetsWJets)  
#signalAnalysisDatasets.extend(datasetsDiboson)
#signalAnalysisDatasets.extend(datasetsQCD)
#signalAnalysisDatasets.extend(datasetsSignalTauNu)
#signalAnalysisDatasets.extend(datasetsSignalTB)
#signalAnalysisDatasets.extend(datasetsSignalTauNu_TRGdev)

#signalAnalysisDatasets.extend(datasetsDY_reHLT)
#signalAnalysisDatasets.extend(datasetsTop_reHLT)
#signalAnalysisDatasets.extend(datasetsWJets_reHLT)
#signalAnalysisDatasets.extend(datasetsDiboson_reHLT)
##signalAnalysisDatasets.extend(datasetsQCD_reHLT)
#signalAnalysisDatasets.extend(datasetsSignalTauNu_reHLT)
##signalAnalysisDatasets.extend(datasetsSignalTB_reHLT)


hplus2tbAnalysisDatasets = []
hplus2tbAnalysisDatasets.extend(datasetsJetHTData)
hplus2tbAnalysisDatasets.extend(datasetsSignalTB)
hplus2tbAnalysisDatasets.extend(datasetsTop)
hplus2tbAnalysisDatasets.extend(datasetsSingleTop)
hplus2tbAnalysisDatasets.extend(datasetsDYJetsToQQ)
hplus2tbAnalysisDatasets.extend(datasetsWJetsToQQ)
# hplus2tbAnalysisDatasets.extend(datasetsZJetsToQQ_reHLT) # PUMoriond17?
hplus2tbAnalysisDatasets.extend(datasetsDibosonToQQ)
# hplus2tbAnalysisDatasets.extend(datasetsQCD)
hplus2tbAnalysisDatasets.extend(datasetsQCD_HT)
hplus2tbAnalysisDatasets.extend(datasetsQCDbEnriched)
hplus2tbAnalysisDatasets.extend(datasetsTTWJetsToQQ)  
hplus2tbAnalysisDatasets.extend(datasetsTTTT) 
# hplus2tbAnalysisDatasets.extend(datasetsTTBB) # PUMoriond17?
hplus2tbAnalysisDatasets.extend(datasetsTTZToQQ)
# hplus2tbAnalysisDatasets.extend(datasetsQCDMuEnriched)
# hplus2tbAnalysisDatasets.extend(datasetsQCD_HT_BGenFilter) 
# hplus2tbAnalysisDatasets.extend(datasetsQCD_HT_GenJets5) 
# hplus2tbAnalysisDatasets.extend(datasetsTTJets) #-ve weights


#================================================================================================ 
# Class Definition
#================================================================================================ 
class DatasetGroup:
    def __init__(self, analysis):
        self.verbose   = False
        self.analysis  = analysis
        self.GroupDict = {}
        self.CreateGroups()

    def SetVerbose(verbose):
        self.verbose = verbose
        return


    def Verbose(self, msg, printHeader=False):
        '''
        Simple print function. If verbose option is enabled prints, otherwise does nothing.
        '''
        if not self.verbose:
            return
        self.Print(msg, printHeader)
        return


    def Print(self, msg, printHeader=True):
        '''
        Simple print function. If verbose option is enabled prints, otherwise does nothing.
        '''
        fName = __file__.split("/")[-1]
        cName = self.__class__.__name__
        name  = fName + ": " + cName
        if printHeader:
                print "=== ", name
        print "\t", msg
        return


    def CreateGroups(self):
        '''
        Create dataset grouping in a dictionary for easy access.
        '''

        analyses = ["SignalAnalysis", "Hplus2tbAnalysis", "TauLeg", "METLeg", "L1Study", "All"]
        if self.analysis not in analyses:
            raise Exception("Unknown analysis \"%s\". Please select one of the following: \"%s" % (self.analysis, "\", \"".join(analyses) + "\".") )

        self.GroupDict["SignalAnalysis"]   = signalAnalysisDatasets
        self.GroupDict["Hplus2tbAnalysis"] = hplus2tbAnalysisDatasets
        self.GroupDict["TauLeg"]           = tauLegDatasets
        self.GroupDict["METLeg"]           = metLegDatasets
        self.GroupDict["L1Study"]          = l1Datasets
        self.GroupDict["All"]              = signalAnalysisDatasets + hplus2tbAnalysisDatasets + metLegDatasets + metLegDatasets
        return


    def GetDatasetList(self):
        '''
        Return the dataset list according to the analysis name. 
        Uses pre-defined dictionary mapping: analysis->dataset list
        '''
        return self.GroupDict[self.analysis]


    def PrintDatasets(self, printHeader=False):
        '''
        Print all datasets for given analysis
        '''
        datasetList = self.GroupDict[self.analysis]

        if printHeader==True:
            self.Print("The datasets for analysis \"%s\" are:\n\t%s" % (self.analysis, "\n\t".join(str(d.URL) for d in datasetList) ), True)
        else:
            self.Print("\n\t".join(str(d.URL) for d in datasetList), False)
        return
