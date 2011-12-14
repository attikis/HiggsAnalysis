import FWCore.ParameterSet.Config as cms
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion
import FWCore.ParameterSet.VarParsing as VarParsing

#dataVersion = "39Xredigi"
#dataVersion = "39Xdata"
#dataVersion = "311Xredigi"
dataVersion = "42Xmc"

################################################################################

# Command line arguments (options) and DataVersion object
options = VarParsing.VarParsing()
options.register("WDecaySeparate",
                 0,
                 options.multiplicity.singleton,
                 options.varType.int,
                 "Separate W decays from MC information")
options, dataVersion = getOptionsDataVersion(dataVersion, options, useDefaultSignalTrigger=False)

#options.doPat=1

process = cms.Process("HChMuonAnalysis")

#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(2000) )
#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10000) )
#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string(dataVersion.getGlobalTag())

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(
        # For testing in lxplus
        #dataVersion.getAnalysisDefaultFileCastor()
        # For testing in jade
        #dataVersion.getAnalysisDefaultFileMadhatter()
    "/store/group/local/HiggsChToTauNuFullyHadronic/tauembedding/CMSSW_4_2_X/TTJets_TuneZ2_Summer11_1/TTJets_TuneZ2_7TeV-madgraph-tauola/Summer11_PU_S4_START42_V11_v1_AODSIM_tauembedding_skim_v13_2/6ce8de2c5b6c0c9ed414998577b7e28d/skim_982_1_xgs.root"
  )
)

################################################################################

process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChCommon_cfi")
#process.options.wantSummary = cms.untracked.bool(True)
process.MessageLogger.cerr.FwkReport.reportEvery = 5000
process.MessageLogger.categories.append("TauIsolationSelector")

# Uncomment the following in order to print the counters at the end of
# the job (note that if many other modules are being run in the same
# job, their INFO messages are printed too)
#process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")

# Fragment to run PAT on the fly if requested from command line
from HiggsAnalysis.HeavyChHiggsToTauNu.HChPatTuple import addPatOnTheFly
from PhysicsTools.PatAlgos.tools.coreTools import removeSpecificPATObjects
patArgs = {"doPatTrigger": False,
#           "doPatTaus": False,
#           "doHChTauDiscriminators": False,
           "doPatElectronID": True,
           "doTauHLTMatching": False,
           "doPatMuonPFIsolation": True,
           }
process.commonSequence, additionalCounters = addPatOnTheFly(process, options, dataVersion, plainPatArgs=patArgs)
#process.commonSequence.remove(process.goodPrimaryVertices10)
if options.doPat == 0:
    process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChPrimaryVertex_cfi")
    process.commonSequence *= (
        process.goodPrimaryVertices *
        process.goodPrimaryVertices10
    )

from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import *
# Pileup weights
import HiggsAnalysis.HeavyChHiggsToTauNu.HChSignalAnalysisParameters_cff as param
process.pileupWeightEPS = cms.EDProducer("HPlusVertexWeightProducer",
    alias = cms.string("pileupWeightEPS"),
)
process.pileupWeightRun2011AnoEPS = process.pileupWeightEPS.clone(
    alias = "pileupWeightRun2011AnoEPS"
)
process.pileupWeightRun2011A = process.pileupWeightEPS.clone(
    alias = "pileupWeightRun2011A"
)
param.setPileupWeightFor2011(dataVersion, era="EPS")
insertPSetContentsTo(param.vertexWeight.clone(), process.pileupWeightEPS)
param.setPileupWeightFor2011(dataVersion, era="Run2011A-EPS")
insertPSetContentsTo(param.vertexWeight.clone(), process.pileupWeightRun2011AnoEPS)
param.setPileupWeightFor2011(dataVersion, era="Run2011A")
insertPSetContentsTo(param.vertexWeight.clone(), process.pileupWeightRun2011A)

process.commonSequence *= (
    process.pileupWeightEPS *
    process.pileupWeightRun2011AnoEPS *
    process.pileupWeightRun2011A
)
    
# Add the muon selection counters, as this is done after the skim
import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.muonSelectionPF_cff as MuonSelection
additionalCounters.extend(MuonSelection.muonSelectionCounters)

# Add configuration information to histograms.root
process.infoPath = addConfigInfo(process, options, dataVersion)

################################################################################

process.firstPrimaryVertex = cms.EDProducer("HPlusFirstVertexSelector",
    src = cms.InputTag("offlinePrimaryVertices")
)
process.commonSequence *= process.firstPrimaryVertex

import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.customisations as customisations
muons = customisations.addMuonIsolationEmbedding(process, process.commonSequence, "selectedPatMuons")

import HiggsAnalysis.HeavyChHiggsToTauNu.HChGlobalElectronVetoFilter_cfi as ElectronVeto
process.eveto = cms.EDFilter("HPlusGlobalElectronVetoFilter",
    GlobalElectronVeto = param.GlobalElectronVeto.clone(),
    filter = cms.bool(False)
)
process.commonSequence *= process.eveto

process.preselectedMuons = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag(muons),
    cut = cms.string(
        "isGlobalMuon() && isTrackerMuon()"
        "&& muonID('GlobalMuonPromptTight')"
        "&& innerTrack().numberOfValidHits() > 10"
        "&& innerTrack().hitPattern().pixelLayersWithMeasurement() >= 1"
        "&& numberOfMatches() > 1"
    )
)
process.preselectedMuons40 = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("preselectedMuons"),
    cut = cms.string("pt() > 40 && abs(eta) < 2.1")
)
process.preselectedMuons40Filter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("preselectedMuons40"),
    minNumber = cms.uint32(1)
)
process.preselectedMuons40Count = cms.EDProducer("EventCountProducer")
process.commonSequence *= (
    process.preselectedMuons *
    process.preselectedMuons40 *
    process.preselectedMuons40Filter *
    process.preselectedMuons40Count
)
additionalCounters.append("preselectedMuons40Count")

process.preselectedJets = cms.EDFilter("PATJetSelector",
    src = cms.InputTag("goodJets"),
    cut = cms.string(
    "pt() > 30 && abs(eta()) < 2.4"
    "&& numberOfDaughters() > 1 && chargedEmEnergyFraction() < 0.99"
    "&& neutralHadronEnergyFraction() < 0.99 && neutralEmEnergyFraction < 0.99"
    "&& chargedHadronEnergyFraction() > 0 && chargedMultiplicity() > 0" # eta < 2.4, so don't need the requirement here
    ),
)
process.preselectedJetsFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("preselectedJets"),
    minNumber = cms.uint32(3)
)
process.preselectedJetsCount = cms.EDProducer("EventCountProducer")
process.commonSequence *= (
    process.preselectedJets *
#    process.preselectedJetsFilter * 
    process.preselectedJetsCount
)
additionalCounters.append("preselectedJetsCount")

# Configuration
import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.muonAnalysis as muonAnalysis
ntuple = cms.EDAnalyzer("HPlusMuonNtupleAnalyzer",
    patTriggerEvent = cms.InputTag("patTriggerEvent"),
    genParticleSrc = cms.InputTag("genParticles"),
    muonSrc = cms.InputTag("preselectedMuons"),
    muonFunctions = cms.PSet(
        dB = cms.string("dB()")
        #name = cms.string("function")
    ),
    jetSrc = cms.InputTag("preselectedJets"),
    jetFunctions = cms.PSet(
        tche = cms.string("bDiscriminator('trackCountingHighEffBJetTags')"),
    ),
    mets = cms.PSet(
        caloMet_p4 = cms.InputTag("met"),
        caloMetNoHF_p4 = cms.InputTag("metNoHF"),
        pfMet_p4 = cms.InputTag("pfMet"),
    ),
    doubles = cms.PSet(
        pileupWeightEPS = cms.InputTag("pileupWeightEPS"),
        weightPileup_Run2011AnoEPS = cms.InputTag("pileupWeightRun2011AnoEPS"),
        weightPileup_Run2011A = cms.InputTag("pileupWeightRun2011A")
    ),
    bools = cms.PSet(
        ElectronVetoPassed = cms.InputTag("eveto")
    ),
)
#isolations = muonAnalysis.isolations.keys()
isolations = ["trackIso", "caloIso", "pfChargedIso", "pfNeutralIso", "pfGammaIso", "tauTightIc04ChargedIso", "tauTightIc04GammaIso"]
#print isolations
for name in isolations:
    setattr(ntuple.muonFunctions, name, cms.string(muonAnalysis.isolations[name]))

addAnalysis(process, "muonNtuple", ntuple,
            preSequence=process.commonSequence,
            additionalCounters=additionalCounters,
            signalAnalysisCounters=False)
process.muonNtupleCounters.printMainCounter = True

# Replace all event counters with the weighted one
eventCounters = []
for label, module in process.producers_().iteritems():
    if module.type_() == "EventCountProducer":
        eventCounters.append(label)
prototype = cms.EDProducer("HPlusEventCountProducer",
    weightSrc = cms.InputTag("pileupWeightRun2011A")
)
for label in eventCounters:
    process.globalReplace(label, prototype.clone())



# def createAnalysis(name, postfix="", weightSrc=None, **kwargs):
#     wSrc = weightSrc
#     if dataVersion.isData():
#         wSrc = None
#     def create(**kwargs):
#         muonAnalysis.createAnalysis(process, dataVersion, additionalCounters, name=name,
#                                     trigger=trigger, jets="goodJets", met="pfMet",
#                                     weightSrc = wSrc,
#                                     **kwargs)

#     prefix = name+postfix
#     create(prefix=prefix, **kwargs)
#     if not "doIsolationWithTau" in kwargs:
#         for iso in [
# #            "VLoose",
# #            "Loose",
# #            "Medium",
# #            "Tight",
# #            "TightSc015",
# #            "TightSc02",
#             "TightIc04",
# #            "TightSc015Ic04",
# #            "TightSc02Ic04",
#             ]:
#             create(prefix=prefix+"IsoTauLike"+iso, doMuonIsolation=True, muonIsolation="tau%sIso"%iso, muonIsolationCut=0.5, **kwargs)

# #         for iso in [
# #             "Tight",
# #             "TightSc0",
# #             "TightSc0Ic04",
# #             "TightSc0Ic04Noq",
# #             create(prefix=prefix+"IsoTauLikeRel"+iso, doMuonIsolation=True, muonIsolation="tau%sIsoRel"%iso, muonIsolationCut=

# #    if not "doIsolationWithTau" in kwargs:
# #        for iso in [
# #            "VLoose",
# #            "Loose",
# #            "Medium",
# #            "Tight",
# #            ]:
# #            create(prefix=prefix+"IsoTau"+iso, doIsolationWithTau=True, isolationWithTauDiscriminator="by%sIsolation"%iso, **kwargs)
        
#     create(prefix=prefix+"Aoc", afterOtherCuts=True, **kwargs)

# def createAnalysis2(**kwargs):
# #    createAnalysis("topMuJetRefMet", doIsolationWithTau=False, **kwargs)

#     args = {}
#     args.update(kwargs)
#     postfix = kwargs.get("postfix", "")
#     for pt, met, njets in [
# #        (30, 20, 2),
# #        (30, 20, 3),
# #        (40, 20, 2),
#         (40, 20, 3)
#         ]:
#         args["postfix"] = "Pt%dMet%dNJets%d%s" % (pt, met, njets, postfix)
#         args["muonPtCut"] = pt
#         args["metCut"] = met
#         args["njets"] = njets
#         createAnalysis("muonSelectionPF", **args)

# createAnalysis2(muons=muons, allMuons=muons)
# createAnalysis2(muons=muons, allMuons=muons, weightSrc="vertexWeight", postfix="VertexWeight")
# #createAnalysis2(muons=muons, allMuons=muons, weightSrc="pileupWeight", postfix="PileupWeight")
# #createAnalysis2(muons="tightMuonsZ")

# # process.out = cms.OutputModule("PoolOutputModule",
# #     fileName = cms.untracked.string('foo.root'),
# #     outputCommands = cms.untracked.vstring(["keep *_*MuonVeto*_*_*"])
# # )
# # process.endPath = cms.EndPath(
# #     process.out
# # )

