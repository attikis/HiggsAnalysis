import FWCore.ParameterSet.Config as cms
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion
import FWCore.ParameterSet.VarParsing as VarParsing

#dataVersion = "39Xredigi"
#dataVersion = "39Xdata"
#dataVersion = "311Xredigi"
dataVersion = "44XmcS6"

PF2PATVersion = "PFlow"

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
#    "/store/group/local/HiggsChToTauNuFullyHadronic/tauembedding/CMSSW_4_2_X/TTJets_TuneZ2_Summer11_1/TTJets_TuneZ2_7TeV-madgraph-tauola/Summer11_PU_S4_START42_V11_v1_AODSIM_tauembedding_skim_v13_2/6ce8de2c5b6c0c9ed414998577b7e28d/skim_982_1_xgs.root"
#        "file:skim.root"
        "/store/group/local/HiggsChToTauNuFullyHadronic/tauembedding/CMSSW_4_4_X/TTJets_TuneZ2_Fall11/TTJets_TuneZ2_7TeV-madgraph-tauola/Tauembedding_skim_v44_1_TTJets_TuneZ2_Fall11//2f6341f5a210122b891e378fe7516bcf/skim_1001_1_qUS.root"
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
           }
process.commonSequence, additionalCounters = addPatOnTheFly(process, options, dataVersion, patArgs=patArgs)
#process.commonSequence.remove(process.goodPrimaryVertices10)
# if options.doPat == 0:
#     process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChPrimaryVertex_cfi")
#     process.commonSequence *= (
#         process.goodPrimaryVertices *
#         process.goodPrimaryVertices10
#     )

from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import *
# Pileup weights
import HiggsAnalysis.HeavyChHiggsToTauNu.HChSignalAnalysisParameters_cff as param
param.changeCollectionsToPF2PAT(PF2PATVersion)
puWeights = [
    ("Run2011A", "Run2011A"),
    ("Run2011B", "Run2011B"),
    ("Run2011A+B", "Run2011AB")
    ]
for era, name in puWeights:
    modname = "pileupWeight"+name
    setattr(process, modname, cms.EDProducer("HPlusVertexWeightProducer",
        alias = cms.string(modname),
    ))
    param.setPileupWeight(dataVersion, process=process, commonSequence=process.commonSequence, era=era)
    insertPSetContentsTo(param.vertexWeight.clone(), getattr(process, modname))
    process.commonSequence *= getattr(process, modname)
    
# Add the muon selection counters, as this is done after the skim
import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.muonSelectionPF as MuonSelection
additionalCounters.extend(MuonSelection.getMuonSelectionCountersForEmbedding(PF2PATVersion))

# Add configuration information to histograms.root
process.infoPath = addConfigInfo(process, options, dataVersion)

################################################################################

process.firstPrimaryVertex = cms.EDProducer("HPlusFirstVertexSelector",
    src = cms.InputTag("offlinePrimaryVertices")
)
process.commonSequence *= process.firstPrimaryVertex

import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.customisations as customisations
customisations.PF2PATVersion = PF2PATVersion
muons = "selectedPatMuons"+PF2PATVersion
#muons = customisations.addMuonIsolationEmbedding(process, process.commonSequence, muons)
isolation = customisations.constructMuonIsolationOnTheFly(muons)
muons = muons+"Iso"
setattr(process, muons, isolation)
process.commonSequence *= isolation

import HiggsAnalysis.HeavyChHiggsToTauNu.HChGlobalElectronVetoFilter_cfi as ElectronVeto
process.eveto = ElectronVeto.hPlusGlobalElectronVetoFilter.clone(
    filter = False
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
    src = cms.InputTag("goodJets"+PF2PATVersion),
    cut = cms.string(customisations.jetSelection)
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
        dB = cms.string("dB()"),
        pfChargedHadrons = cms.string("chargedHadronIso()"),
        pfNeutralHadrons = cms.string("neutralHadronIso()"),
        pfPhotons = cms.string("photonIso()"),
        pfPUChargedHadrons = cms.string("puChargedHadronIso()"),
        
        pfChargedHadrons_01to04 = cms.string("userFloat('ontheflyiso_pfChargedHadrons')"),
        pfNeutralHadrons_01to04 = cms.string("userFloat('ontheflyiso_pfNeutralHadrons')"),
        pfPhotons_01to04 = cms.string("userFloat('ontheflyiso_pfPhotons')"),
        pfPUChargedHadrons_01to04 = cms.string("userFloat('ontheflyiso_pfPUChargedHadrons')"),

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
    doubles = cms.PSet(),
    bools = cms.PSet(
        ElectronVetoPassed = cms.InputTag("eveto")
    ),
)
for era, name in puWeights:
    setattr(ntuple.doubles, "weightPileup_"+name, cms.InputTag("pileupWeight"+name))

#isolations = muonAnalysis.isolations.keys()
isolations = ["trackIso", "caloIso", "pfChargedIso", "pfNeutralIso", "pfGammaIso", "tauTightIc04ChargedIso", "tauTightIc04GammaIso"]
#print isolations
for name in isolations:
    setattr(ntuple.muonFunctions, name, cms.string(muonAnalysis.isolations[name]))
userFloats = []
for name in ["pfNeutralHadrons", "pfChargedAll", "pfPUChargedHadrons", "pfPhotons", "pfChargedHadrons"]:
    userFloats.extend(["iso01to04_"+name, "iso01to03_"+name])
for name in userFloats:
    setattr(ntuple.muonFunctions, name, cms.string("userFloat('%s')" % name))


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

