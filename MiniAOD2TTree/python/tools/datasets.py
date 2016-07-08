lumiMask = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-275125_13TeV_PromptReco_Collisions16_JSON.txt"

#================================================================================================ 
# Class Definition
#================================================================================================ 
class Dataset:
    def __init__(self, url, dbs="global", dataVersion="80Xmc", dasQuery="", lumiMask=lumiMask):
        self.URL = url
        self.DBS = dbs
        self.dataVersion = dataVersion
        self.lumiMask = lumiMask
        self.DASquery = dasQuery

    def isData(self):
        if "data" in self.dataVersion:
            return True
        return False

#================================================================================================ 
# Dataset definition
#================================================================================================ 
datasetsTauData = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FTau%2FRun2016*-PromptReco-v2%2FMINIAOD"
datasetsTauData.append(Dataset('/Tau/Run2016B-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))
datasetsTauData.append(Dataset('/Tau/Run2016C-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))


datasetsJetHTData = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FJetHT%2FRun2016*-PromptReco-v2%2FMINIAOD"
datasetsJetHTData.append(Dataset('/JetHT/Run2016B-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))
datasetsJetHTData.append(Dataset('/JetHT/Run2016C-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))


datasetsMuonData = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FSingleMuon%2FRun2016*-PromptReco-v2%2FMINIAOD"
datasetsMuonData.append(Dataset('/SingleMuon/Run2016B-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))
datasetsMuonData.append(Dataset('/SingleMuon/Run2016C-PromptReco-v2/MINIAOD', dataVersion="80Xdata", dasQuery=das))


datasetsTop = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FTT_TuneCUETP8M1_13TeV-powheg-pythia8%2FRunII*16MiniAODv2-*%2FMINIAODSIM"
datasetsTop.append(Dataset('/TT_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14_ext3-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))


datasetsDY = []


datasetsWJets = []


datasetsDiboson = []


datasetsQCD = []


datasetsSignalTauNu = []
das = "https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FChargedHiggs_TTToHplusBWB_HplusToTauNu_M-*%2FRunII*16MiniAODv2-*%2FMINIAODSIM"
datasetsSignalTauNu.append(Dataset('/ChargedHiggs_TTToHplusBWB_HplusToTauNu_M-120_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))


datasetsSignalTB = []
das = " https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FChargedHiggs_HplusTB_HplusToTB_M-*%2FRunII*16MiniAODv2-*%2FMINIAODSIMa"
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-180_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-200_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-220_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-250_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-300_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-350_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-400_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))
datasetsSignalTB.append(Dataset('/ChargedHiggs_HplusTB_HplusToTB_M-500_13TeV_amcatnlo_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM', dataVersion="80Xmc", dasQuery=das))


#================================================================================================ 
# Dataset Grouping
#================================================================================================ 
tauLegDatasets = []
tauLegDatasets.extend(datasetsMuonData)
tauLegDatasets.extend(datasetsDY)
# tauLegDatasets.extend(datasetsWJets)
# tauLegDatasets.extend(datasetsQCDMuEnriched)
# tauLegDatasets.extend(datasetsH125)


metLegDatasets = []
metLegDatasets.extend(datasetsTauData)
metLegDatasets.extend(datasetsDY)
metLegDatasets.extend(datasetsTop)
metLegDatasets.extend(datasetsWJets)
metLegDatasets.extend(datasetsQCD)


signalAnalysisDatasets = []
signalAnalysisDatasets.extend(datasetsTauData)
signalAnalysisDatasets.extend(datasetsDY)
signalAnalysisDatasets.extend(datasetsTop)
signalAnalysisDatasets.extend(datasetsWJets)
signalAnalysisDatasets.extend(datasetsDiboson)
signalAnalysisDatasets.extend(datasetsQCD)
signalAnalysisDatasets.extend(datasetsSignalTauNu)
signalAnalysisDatasets.extend(datasetsSignalTB)


hplus2tbAnalysisDatasets = []
hplus2tbAnalysisDatasets.extend(datasetsJetHTData)
hplus2tbAnalysisDatasets.extend(datasetsSignalTB)
# hplus2tbAnalysisDatasets.extend(datasetsDYToQQ)
# hplus2tbAnalysisDatasets.extend(datasetsQCD)   
## hplus2tbAnalysisDatasets.extend(datasetsQCDbEnriched)
## hplus2tbAnalysisDatasets.extend(datasetsQCDbGenFilter)
## hplus2tbAnalysisDatasets.extend(datasetsQCDHTBins)
hplus2tbAnalysisDatasets.extend(datasetsTop)
## h plus2tbAnalysisDatasets.extend(datasetsTT)
## hplus2tbAnalysisDatasets.extend(datasetsGGJets)
## hplus2tbAnalysisDatasets.extend(datasetsGJets)
## hplus2tbAnalysisDatasets.extend(datasetsTGJets)
## hplus2tbAnalysisDatasets.extend(datasetsTTGJets)     
## hplus2tbAnalysisDatasets.extend(datasetsTTJets)
## hplus2tbAnalysisDatasets.extend(datasetsTTJetsHT)    
# hplus2tbAnalysisDatasets.extend(datasetsTTWJets)
# hplus2tbAnalysisDatasets.extend(datasetsTTZJets)
# hplus2tbAnalysisDatasets.extend(datasetsTTWJetsToQQ)  
# hplus2tbAnalysisDatasets.extend(datasetsTTTT)  
# hplus2tbAnalysisDatasets.extend(datasetsTTZToQQ)
# hplus2tbAnalysisDatasets.extend(datasetsWJetsToQQ)    
# hplus2tbAnalysisDatasets.extend(datasetsZJetsToQQ)    
# hplus2tbAnalysisDatasets.extend(datasetsDiboson) #    
## hplus2tbAnalysisDatasets.extend(datasetsDibosonG)    
## hplus2tbAnalysisDatasets.extend(datasetsWWTo4Q)
## hplus2tbAnalysisDatasets.extend(datasetsZZTo4Q)
# hplus2tbAnalysisDatasets.extend(datasetsttbb)  
# hplus2tbAnalysisDatasets.extend(datasetsTriboson) 


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

        analyses = ["SignalAnalysis", "Hplus2tbAnalysis", "TauLeg", "METLeg"]
        if self.analysis not in analyses:
            raise Exception("Unknown analysis \"%s\". Please select one of the following:\n" % ("\n".join(analyses) ) )

        self.GroupDict["SignalAnalysis"]   = signalAnalysisDatasets
        self.GroupDict["Hplus2tbAnalysis"] = hplus2tbAnalysisDatasets
        self.GroupDict["TauLeg"]           = tauLegDatasets
        self.GroupDict["METLeg"]           = metLegDatasets
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
