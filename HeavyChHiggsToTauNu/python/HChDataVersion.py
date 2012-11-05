# The purpose of default files is testing only. For production
# processing use either CRAB or explicit file names in PoolSource

# triggerProcess:  the process containing the HLT information
# patCastor:         default input file for PATtuple at castor
# patMadhatter:      default input file for PATtuple at madhatter
# analysisCastor:    default input file for analysis at castor
# analysisMadhatter: default input file for analysis at madhatter
config = {
    "42Xdata": {
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
#        "signalTrigger": "HLT_MediumIsoPFTau35_Trk20_MET60_v1"
#        "patCastor": "",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/Tau/Run2011A-PromptReco-v4/AOD/FCF1CBDD-878F-E011-885B-003048F118D4.root",
#        "patMadhatter": "file:/mnt/flustre/mkortela/data/SingleMu/PromptReco-v4/AOD/F2B6FB32-7AA3-E011-BCAF-BCAEC5329710.root",
#        "analysisCastor": "",
        "analysisMadhatter": "/store/group/local/HiggsChToTauNuFullyHadronic/pattuples/CMSSW_4_2_X/Tau_173236-173692_Prompt/Tau/Run2011A_PromptReco_v6_AOD_173236_pattuple_v20_test1/ffd00eb3f262c07dc29d261d6126a908/pattuple_11_1_tdz.root",
    },
    "42XmcS3": {
        "simProcess": "HLT",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "signalTrigger": "HLT_IsoPFTau35_Trk20_MET45_v2",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/TT_TuneZ2_7TeV-pythia6-tauola/Summer11-PU_S3_START42_V11-v1/AODSIM/84A5EB09-0A77-E011-A8C3-00266CF252D4.root",
#        "patMadhatter": "file:/mnt/flustre/mkortela/data/QCD_Pt-170to300_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM/FE47C9F3-C97D-E011-B103-003048670B66.root",
    },
    "42XmcS4": {
        "simProcess": "HLT",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "signalTrigger": "HLT_IsoPFTau35_Trk20_MET45_v2",
#        "patMadhatter": "/store/mc/Summer11/WJetsToLNu_TuneZ2_7TeV-madgraph-tauola/AODSIM/PU_S4_START42_V11-v1/0000/0428EC7E-F199-E011-B474-002618943861.root",
        "patMadhatter": "file:/mnt/flustre/mkortela/data//TTJets_TuneZ2_7TeV-madgraph-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM/F498AD1D-8298-E011-BFB9-003048678F92.root",
        "analysisMadhatter": "/store/group/local/HiggsChToTauNuFullyHadronic/pattuples/CMSSW_4_2_X/TTToHplusBWB_M120_Summer11/TTToHplusBWB_M-120_7TeV-pythia6-tauola/Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v20_test1/88557732962dcf8166a136160b7c6f9d/pattuple_10_1_5mL.root"
    },
    "42XmcS6": {
        "simProcess": "HLT",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "signalTrigger": "HLT_MediumIsoPFTau35_Trk20_MET60_v1",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/TTToHplusBWB_M-120_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM/A87958F4-92F3-E011-9CBC-0018F3D0966C.root",
    },
    "44Xdata": {
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
#        "signalTrigger": "HLT_IsoPFTau35_Trk20_MET60_v2",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/Tau/Run2011A-08Nov2011-v1/AOD/E8B13C66-A70B-E111-B8C5-001EC9B09F59.root"
    },
    "44Xmc_highPU": {
        "simProcess": "SIM",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "signalTrigger": "HLT_MediumIsoPFTau35_Trk20_MET60_v6",
        #"patMadhatter": "file:/mnt/flustre/mkortela/data/TTToHplusBWB_M-120_7TeV-pythia6-tauola/Fall11-PU_S6_START44_V9B-v1/AODSIM/28ACFF78-0237-E111-97C7-00261894397B.root"
        #"patMadhatter": "file:/mnt/flustre/mkortela/data//QCD_Pt-170to300_TuneZ2_7TeV_pythia6/Fall11-PU_S6_START44_V9B-v1/AODSIM/F468E7CF-C029-E111-BDA8-003048D47750.root"
    },
    "44XmcS6": {
        "simProcess": "HLT",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "signalTrigger": "HLT_MediumIsoPFTau35_Trk20_MET60_v1",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/TTToHplusBWB_M-120_7TeV-pythia6-tauola/Fall11-PU_S6_START44_V9B-v1/AODSIM/28ACFF78-0237-E111-97C7-00261894397B.root", 
        "analysisMadhatter": "/store/group/local/HiggsChToTauNuFullyHadronic/pattuples/CMSSW_4_4_X/TTJets_TuneZ2_7TeV-madgraph-tauola/Fall11_PU_S6_START44_V9B_v1_AODSIM_pattuple_v44_4/f16be938188c46248667b60f0c9e7452/pattuple_7_1_ozc.root", # TTJets, v44_4
    },
    "44XmcAve32": {
        "simProcess": "SIM",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "globalTag": "START44_V13::All",
        "signalTrigger": "HLT_MediumIsoPFTau35_Trk20_MET60_v1",
        "patMadhatter": "file:/mnt/flustre/slehti/Fall11_TTToHplusBWB_M-90_7TeV-pythia6-tauola_B2AD85E1-D520-E111-B5AC-001A928116EA.root",
    },
    "53Xdata13Jul2012": {"triggerProcess": "HLT", "recoProcess": "RECO",
        "globalTag": "FT_53_V6_AN2::All",
#        "signalTrigger": ["HLT_QuadJet80_v2", "HLT_QuadJet75_55_38_20_BTagIP_VBF_v3", "HLT_QuadPFJet75_55_38_20_BTagCSV_VBF_v4"],
#        "patMadhatter": "file:/mnt/flustre/mkortela/data/MultiJet/Run2012A-13Jul2012-v1/AOD/F4740DF9-26D6-E111-9BA6-003048FFD71E.root", # run 191700
    },
    "53Xdata06Aug2012": {"triggerProcess": "HLT", "recoProcess": "RECO",
        "globalTag": "FT_53_V6C_AN2::All",
    },
    "53Xdata24Aug2012": {
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "globalTag": "FT_53_V10_AN2::All",
#        "signalTrigger": "HLT_LooseIsoPFTau35_Trk20_Prong1_MET70_v7",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/Tau/Run2012C-24Aug2012-v1/AOD/02698B5A-A0EE-E111-B4FB-0025901D4AF4.root",
    },
    "53XdataPromptCv2": {"triggerProcess": "HLT", "recoProcess": "RECO",
        "globalTag": "GR_P_V41_AN2::All",
    },
    "53XdataPromptDv1": {"triggerProcess": "HLT", "recoProcess": "RECO",
        "globalTag": "GR_P_V42_AN2::All",
    },
    "53XmcS10": {
        "simProcess": "SIM",
        "triggerProcess": "HLT",
        "recoProcess": "RECO",
        "globalTag": "START53_V7F::All",
        "signalTrigger": "HLT_LooseIsoPFTau35_Trk20_Prong1_MET70_v6",
        "patMadhatter": "file:/mnt/flustre/mkortela/data/TTToHplusBWB_M-120_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM/E6FBC572-20F5-E111-9CBD-00215E21DC60.root",
        "analysisMadhatter": "/store/group/local/HiggsChToTauNuFullyHadronic/pattuples/CMSSW_5_3_X/TTToHplusBWB_M120_Summer12/TTToHplusBWB_M-120_8TeV-pythia6-tauola/Summer12_DR53X_PU_S10_START53_V7A_v1_AODSIM_pattuple_v53_1_test1/cad8d1056ca20d363262a3efa1d97a74/pattuple_9_1_sH1.root"
    }
}


class DataVersion:
    def __init__(self, dataVersion):
        if dataVersion == "42Xmc":
            dataVersion = "42XmcS4"
        if not dataVersion in config:
            names = config.keys()
            names.sort()
            raise Exception("Unknown dataVersion '%s',  allowed versions are %s" % (dataVersion, ", ".join(names)))

        conf = config[dataVersion]

        self.trigger = conf["triggerProcess"]
        self.recoProcess = conf.get("recoProcess", None)
        self.simProcess = conf.get("simProcess", None)
        self.version = dataVersion
        self.globalTag = conf["globalTag"]

        for f in ["patCastor", "patMadhatter", "analysisCastor", "analysisMadhatter"]:
            if f in conf:
                setattr(self, f, conf[f])

        # Collision data
        if "data" in dataVersion:
            self.is_data = True

        # MC
        else:
            self.is_data = False
                
            try:
                self.signalTrigger = conf["signalTrigger"]
            except KeyError:
                pass
                
    def isData(self):
        return self.is_data

    def isMC(self):
        return not self.is_data

    def isS4(self):
        return self.isMC() and ("S4" in self.version)

    def isS6(self):
        return self.isMC() and "S6" in self.version

    def isS10(self):
        return self.isMC() and "S10" in self.version

    def isHighPU(self):
        return self.isMC() and "highPU" in self.version

    def is53X(self):
        return "53X" in self.version

    def getTriggerProcess(self):
        return self.trigger

    def getDefaultSignalTrigger(self):
        # The trigger names in data can change so often that encoding
        # it in the dataVersion is not flexible enough
        if self.isData():
            raise Exception("Default signal trigger is available only for MC")
        return self.signalTrigger

    def getRecoProcess(self):
        if not self.recoProcess:
            raise Exception("Reco process name is not available for %s" % self.version)
        return self.recoProcess

    def getSimProcess(self):
        if not self.simProcess:
            raise Exception("Sim process name is not available for %s" % self.version)
        return self.simProcess

    def getGlobalTag(self):
        return self.globalTag

    def getPatDefaultFileCastor(self):
        if not hasattr(self, "patCastor"):
            print "No default file for PAT in CASTOR for dataVersion "+self.version
            return ""
        return self.patCastor

    def getPatDefaultFileMadhatter(self, dcap=False):
        if not hasattr(self, "patMadhatter"):
            print "No default file for PAT in madhatter for dataVersion "+self.version
            return ""
        if dcap and self.patMadhatter.find("/store") == 0:
            return "dcap://madhatter.csc.fi:22125/pnfs/csc.fi/data/cms"+self.patMadhatter
        else:
            return self.patMadhatter

    def getAnalysisDefaultFileCastor(self):
        if not hasattr(self, "analysisCastor"):
            print "No default file for analysis in CASTOR for dataVersion "+self.version+ ". Perhaps you could copy one there?"
            return ""
        return self.analysisCastor

    def getAnalysisDefaultFileMadhatter(self, dcap=False):
        if not hasattr(self, "analysisMadhatter"):
            print "No default file for analysis in madhatter for dataVersion "+self.version
            return ""
        if dcap and self.analysisMadhatter.find("/store") == 0:
            return "dcap://madhatter.csc.fi:22125/pnfs/csc.fi/data/cms"+self.analysisMadhatter
        else:
            return self.analysisMadhatter


