import FWCore.ParameterSet.Config as cms
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion

dataVersion = "44XmcS6"

options, dataVersion = getOptionsDataVersion(dataVersion, useDefaultSignalTrigger=False)

process = cms.Process("TauEmbeddingAnalysis")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string(dataVersion.getGlobalTag())

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(
        "file:/mnt/flustre/mkortela/data/TTJets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START44_V9B-v1/AODSIM/7EE6381E-D036-E111-9BF5-002354EF3BDF.root"
    )
)

process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChCommon_cfi")

additionalCounters = []
# Add configuration information to histograms.root
import HiggsAnalysis.HeavyChHiggsToTauNu.HChTools as HChTools
process.infoPath = HChTools.addConfigInfo(process, options, dataVersion)

# do PAT muon stuff
#doRecoMuon = False
doRecoMuon = True
doRecoMuonScaleCorrection = True
process.commonSequence = cms.Sequence()
if doRecoMuon:
    # Gen-level filtering
    process.allEvents = cms.EDProducer("EventCountProducer")
    process.genMuons = cms.EDFilter("GenParticleSelector",
        src = cms.InputTag("genParticles"),
        cut = cms.string("abs(pdgId()) == 13 && pt() > 40 && abs(eta()) < 2.1 && abs(mother().pdgId()) != 13")
    )
    process.genMuonsFilter = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag("genMuons"),
        minNumber = cms.uint32(1),
    )
    process.genMuonsCount = cms.EDProducer("EventCountProducer")
    process.commonSequence += (
        process.allEvents +
        process.genMuons +
        process.genMuonsFilter +
        process.genMuonsCount
    )
    additionalCounters.extend(["allEvents", "genMuonsCount"])

    # PAT muons
    options.doPat = 1
    from HiggsAnalysis.HeavyChHiggsToTauNu.HChPatTuple import addPatOnTheFly
    process.fooSequenceSequence, fooCounters = addPatOnTheFly(process, options, dataVersion)
    process.patMuons.userData.userFloats.src = []
    process.selectedPatMuons.src = "patMuons"
    process.selectedPatMuons.cut = ""
    process.commonSequence += (
        process.pfParticleSelectionSequence +
        process.muIsoSequence +
        process.makePatMuons +
        process.selectedPatMuons
    )

    # MuScleFit correction
    # https://twiki.cern.ch/twiki/bin/view/CMSPublic/MuScleFitCorrections2012
    if doRecoMuonScaleCorrection:
        process.muscleMuons = cms.EDProducer("MuScleFitPATMuonCorrector", 
            src = cms.InputTag("selectedPatMuons"), 
            debug = cms.bool(False), 
            identifier = cms.string("Fall11_START44"), 
            applySmearing = cms.bool(False), 
            fakeSmearing = cms.bool(False)
        )
        process.commonSequence += process.muscleMuons

    # muon selection
    import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.muonSelectionPF as MuonSelection
    MuonSelection.addMuonSelectionForEmbedding(process)
    process.commonSequence += (
#        process.muonSelectionAllEvents +
        process.tightMuons
#        process.tightMuonsFilter +
#        process.muonSelectionMuons
    )
#    additionalCounters.extend(["muonSelectionAllEvents", "muonSelectionMuons"])
    if doRecoMuonScaleCorrection:
        process.tightMuons.src = "muscleMuons"

    process.load("HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.PFEmbeddingSource_cff")
    process.commonSequence += (
        process.tightenedMuons
#        process.tightenedMuonsFilter +
#        process.tightenedMuonsCount
    )
#    additionalCounters.append("tightenedMuonsCount")


# Configuration
import HiggsAnalysis.HeavyChHiggsToTauNu.HChSignalAnalysisParameters_cff as param
analyzer = cms.EDAnalyzer("HPlusEmbeddingDebugMuonAnalyzer",
    muonSrc = cms.untracked.InputTag("tightenedMuons"),
    jetSrc = cms.untracked.InputTag("goodJets"),
    genSrc = cms.untracked.InputTag("genParticles"),
    recoMuon = cms.untracked.bool(doRecoMuon),
    recoJets = cms.untracked.bool(False),

    muonPtCut = cms.untracked.double(41),
    muonEtaCut = cms.untracked.double(2.1),

    embeddingMuonEfficiency = param.embeddingMuonEfficiency.clone(
        mode = "mcEfficiency"
    ),

    eventCounter = param.eventCounter.clone(),
    histogramAmbientLevel = cms.untracked.string("Informative"),
)

HChTools.addAnalysis(process, "debugAnalyzer", analyzer,
                     preSequence=process.commonSequence,
                     additionalCounters=additionalCounters)
process.debugAnalyzer.eventCounter.printMainCounter = True

f = open("configDumpEmbeddingDebugMuonAnalysisAOD.py", "w")
f.write(process.dumpPython())
f.close()
