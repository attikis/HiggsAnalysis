# For miniAOD instructions see: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2015 

import FWCore.ParameterSet.Config as cms
import HiggsAnalysis.MiniAOD2TTree.tools.git as git #HiggsAnalysis.HeavyChHiggsToTauNu.tools.git as git
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion

process = cms.Process("TTreeDump")

dataVersion = "74Xmc"

options, dataVersion = getOptionsDataVersion(dataVersion)
print dataVersion

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10000)
)

process.load("FWCore/MessageService/MessageLogger_cfi")
process.MessageLogger.categories.append("TriggerBitCounter")
process.MessageLogger.cerr.FwkReport.reportEvery = 10000 # print the event number for every 100th event
process.MessageLogger.cerr.TriggerBitCounter = cms.untracked.PSet(limit = cms.untracked.int32(10)) # print max 100 warnings

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
       '/store/mc/RunIISpring15DR74/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/Asympt25ns_MCRUN2_74_V9-v1/00000/022B08C4-C702-E511-9995-D4856459AC30.root',
    )
)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, cms.string(dataVersion.getGlobalTag()), '')
process.GlobalTag = GlobalTag(process.GlobalTag, str(dataVersion.getGlobalTag()), '')
print "GlobalTag="+dataVersion.getGlobalTag()

# Set up electron ID (VID framework)
# https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2
from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
# define which IDs we want to produce and add them to the VID producer
for idmod in ['RecoEgamma.ElectronIdentification.Identification.mvaElectronID_PHYS14_PU20bx25_nonTrig_V1_cff']:
    setupAllVIDIdsInModule(process, idmod, setupVIDElectronSelection)

# Set up HBHE noise filter
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2
process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
process.HBHENoiseFilterResultProducer.minZeros = cms.int32(99999)

process.ApplyBaselineHBHENoiseFilter = cms.EDFilter('BooleanFlagFilter',
   inputLabel = cms.InputTag('HBHENoiseFilterResultProducer','HBHENoiseFilterResult'),
   reverseDecision = cms.bool(False)
)
METNoiseFilterSource = "TriggerResults::RECO"
if dataVersion.isMC():
    METNoiseFilterSource = "TriggerResults::PAT"

# Set up MET uncertainties - FIXME: does not work at the moment
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#MET_Systematics_Tools
#import PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties as metUncertaintyTools
#metUncertaintyTools.runMETCorrectionsAndUncertainties(process=process, 
                                                      #metType="PF",
                                                      #correctionLevel=["T0","T1","Txy"], # additional options: Smear 
                                                      #computeUncertainties=True,
                                                      #produceIntermediateCorrections=False,
                                                      #addToPatDefaultSequence=True,
                                                      #jetCollection=cms.InputTag("slimmedJets"),
                                                      #jetCollectionUnskimmed=cms.InputTag("slimmedJets"),
                                                      #electronCollection="",
                                                      #muonCollection="",
                                                      #tauCollection="",
                                                      #pfCandCollection=cms.InputTag("packedPFCandidates"),
                                                      #onMiniAOD=True,
                                                      #postfix="Type01xy")

# Set up tree dumper
process.dump = cms.EDFilter('MiniAOD2TTreeFilter',
    OutputFileName = cms.string("miniaod2tree.root"),
    CodeVersion = cms.string(git.getCommitId()),
    DataVersion = cms.string(str(dataVersion.version)),
    CMEnergy = cms.int32(13),
    Skim = cms.PSet(
	Counters = cms.VInputTag(
	    "skimCounterAll",
	    "skimCounterMETFilters",
            "skimCounterPassed"
        ),
    ),
    EventInfo = cms.PSet(
	PileupSummaryInfoSrc = cms.InputTag("addPileupInfo"),
	LHESrc = cms.InputTag("externalLHEProducer"),
	OfflinePrimaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices"),
    ),
    Trigger = cms.PSet(
	TriggerResults = cms.InputTag("TriggerResults::HLT"),
	TriggerBits = cms.vstring(
            "HLT_LooseIsoPFTau50_Trk30_eta2p1_MET80_v",
            "HLT_LooseIsoPFTau50_Trk30_eta2p1_MET80_JetIdCleaned_v",
            "HLT_LooseIsoPFTau50_Trk30_eta2p1_MET120_v",
            "HLT_LooseIsoPFTau50_Trk30_eta2p1_MET120_JetIdCleaned_v",
        ),
	L1Extra = cms.InputTag("l1extraParticles:MET"),
	TriggerObjects = cms.InputTag("selectedPatTrigger"),
	filter = cms.untracked.bool(False)
    ),
    METNoiseFilter = cms.PSet(
        triggerResults = cms.InputTag(METNoiseFilterSource),
        printTriggerResultsList = cms.untracked.bool(False),
        filtersFromTriggerResults = cms.vstring(
            "Flag_CSCTightHaloFilter",
            "Flag_goodVertices",
            "Flag_eeBadScFilter",
        ),
    ),
    Taus = cms.VPSet(
        cms.PSet(
            branchname = cms.untracked.string("Taus"),
            src = cms.InputTag("slimmedTaus"),
            discriminators = cms.vstring(
                #"againstElectronLoose",
                "againstElectronLooseMVA5",
                "againstElectronMVA5category",
                #"againstElectronMVA5raw",
                #"againstElectronMedium",
                "againstElectronMediumMVA5",
                #"againstElectronTight",
                "againstElectronTightMVA5",
                "againstElectronVLooseMVA5",
                "againstElectronVTightMVA5",
                #"againstMuonLoose",
                #"againstMuonLoose2",
                "againstMuonLoose3",
                #"againstMuonLooseMVA",
                #"againstMuonMVAraw",
                #"againstMuonMedium",
                #"againstMuonMedium2",
                #"againstMuonMediumMVA",
                #"againstMuonTight",
                #"againstMuonTight2",
                "againstMuonTight3",
                #"againstMuonTightMVA",
                "byCombinedIsolationDeltaBetaCorrRaw3Hits",
                "byIsolationMVA3newDMwLTraw",
                "byIsolationMVA3newDMwoLTraw",
                "byIsolationMVA3oldDMwLTraw",
                "byIsolationMVA3oldDMwoLTraw",
                "byLooseCombinedIsolationDeltaBetaCorr3Hits",
                "byLooseIsolationMVA3newDMwLT",
                "byLooseIsolationMVA3newDMwoLT",
                "byLooseIsolationMVA3oldDMwLT",
                "byLooseIsolationMVA3oldDMwoLT",
                "byMediumCombinedIsolationDeltaBetaCorr3Hits",
                "byMediumIsolationMVA3newDMwLT",
                "byMediumIsolationMVA3newDMwoLT",
                "byMediumIsolationMVA3oldDMwLT",
                "byMediumIsolationMVA3oldDMwoLT",
                "byTightCombinedIsolationDeltaBetaCorr3Hits",
                "byTightIsolationMVA3newDMwLT",
                "byTightIsolationMVA3newDMwoLT",
                "byTightIsolationMVA3oldDMwLT",
                "byTightIsolationMVA3oldDMwoLT",
                "byVLooseIsolationMVA3newDMwLT",
                "byVLooseIsolationMVA3newDMwoLT",
                "byVLooseIsolationMVA3oldDMwLT",
                "byVLooseIsolationMVA3oldDMwoLT",
                "byVTightIsolationMVA3newDMwLT",
                "byVTightIsolationMVA3newDMwoLT",
                "byVTightIsolationMVA3oldDMwLT",
                "byVTightIsolationMVA3oldDMwoLT",
                "byVVTightIsolationMVA3newDMwLT",
                "byVVTightIsolationMVA3newDMwoLT",
                "byVVTightIsolationMVA3oldDMwLT",
                "byVVTightIsolationMVA3oldDMwoLT",
                "chargedIsoPtSum",
                "decayModeFinding",
                "decayModeFindingNewDMs",
                "neutralIsoPtSum",
                "puCorrPtSum"
	    ),
            filter = cms.untracked.bool(False),
            jetSrc = cms.InputTag("slimmedJets"), # made from ak4PFJetsCHS
            TESvariation = cms.untracked.double(0.03),
            TESvariationExtreme = cms.untracked.double(0.10)
        )
    ),
    Electrons = cms.VPSet(
        cms.PSet(
            branchname = cms.untracked.string("Electrons"),
            src = cms.InputTag("slimmedElectrons"),
            rhoSource = cms.InputTag("fixedGridRhoFastjetAll"), # for PU mitigation in isolation
            IDprefix = cms.string("egmGsfElectronIDs"),
            discriminators = cms.vstring("mvaEleID-PHYS14-PU20bx25-nonTrig-V1-wp80",
                                         "mvaEleID-PHYS14-PU20bx25-nonTrig-V1-wp90")
        )
    ),
    Muons = cms.VPSet(   
        cms.PSet(
            branchname = cms.untracked.string("Muons"),   
            src = cms.InputTag("slimmedMuons"),    
            discriminators = cms.vstring() 
        )   
    ),
    Jets = cms.VPSet(      
        cms.PSet(
            branchname = cms.untracked.string("Jets"),       
            src = cms.InputTag("slimmedJets"), # made from ak4PFJetsCHS
            discriminators = cms.vstring(
                "pfJetBProbabilityBJetTags",
                "pfJetProbabilityBJetTags",
                #"trackCountingHighPurBJetTags", 
                #"trackCountingHighEffBJetTags",
                #"simpleSecondaryVertexHighEffBJetTags",
                #"simpleSecondaryVertexHighPurBJetTags",
                "pfCombinedSecondaryVertexBJetTags",
                "pfCombinedInclusiveSecondaryVertexBJetTags",
                #"combinedInclusiveSecondaryVertexV2BJetTags", # for 72x
                "pfCombinedInclusiveSecondaryVertexV2BJetTags", # for 74x
                "pfCombinedMVABJetTag",
            ),
	    userFloats = cms.vstring(
		"pileupJetId:fullDiscriminant"
	    ),
        )
    ),
    METs = cms.VPSet(
        cms.PSet(
            branchname = cms.untracked.string("MET_Type1"),
            src = cms.InputTag("slimmedMETs")
        ),
    ),
    GenWeights = cms.VPSet(
        cms.PSet(
            branchname = cms.untracked.string("GenWeights"),
            src = cms.InputTag("generator"),
            filter = cms.untracked.bool(False)
        )
    ),
    GenJets = cms.VPSet(      
        cms.PSet(
            branchname = cms.untracked.string("GenJets"),
            src = cms.InputTag("slimmedGenJets"), # ak4
        )
    ),
    GenParticles = cms.VPSet(      
        cms.PSet(
            branchname = cms.untracked.string("genParticles"),
            src = cms.InputTag("prunedGenParticles"),
            saveAllGenParticles = cms.untracked.bool(False),
            saveGenElectrons = cms.untracked.bool(True),
            saveGenMuons = cms.untracked.bool(True),
            saveGenTaus = cms.untracked.bool(True),
            saveGenNeutrinos = cms.untracked.bool(True),
            saveTopInfo = cms.untracked.bool(True),
            saveWInfo = cms.untracked.bool(True),
            saveHplusInfo = cms.untracked.bool(True),
        )
    ),
    Tracks =  cms.VPSet(      
        cms.PSet(
            branchname = cms.untracked.string("PFcandidates"),
            src = cms.InputTag("packedPFCandidates"),
            ptCut = cms.untracked.double(0.0), # pt < value
            etaCut = cms.untracked.double(2.5), # abs(eta) < value
        )
    ),
)

process.load("HiggsAnalysis.MiniAOD2TTree.SignalAnalysisSkim_cfi")

process.skimCounterAll        = cms.EDProducer("EventCountProducer")
process.skimCounterMETFilters = cms.EDProducer("EventCountProducer")
process.skimCounterPassed     = cms.EDProducer("EventCountProducer")

# module execution
process.runEDFilter = cms.Path(process.skimCounterAll*
                               process.HBHENoiseFilterResultProducer* #Produces HBHE bools
                               process.ApplyBaselineHBHENoiseFilter*  #Reject HBHE noise events
                               process.skimCounterMETFilters*
                               process.skim*
                               process.skimCounterPassed*
                               process.egmGsfElectronIDSequence*
                               process.dump)

#process.output = cms.OutputModule("PoolOutputModule",
   #outputCommands = cms.untracked.vstring(
       #"keep *",
   #),
   #fileName = cms.untracked.string("CMSSW.root")
#)
#process.out_step = cms.EndPath(process.output)
