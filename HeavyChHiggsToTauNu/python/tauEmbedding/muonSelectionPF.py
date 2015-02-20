import FWCore.ParameterSet.Config as cms


# write as function , params: process and postfix

muonGlobalPtEta = "isGlobalMuon() && pt() > 35 && abs(eta()) < 2.1"

def getTightMuonsDefinition(postfix=""):
    src = "selectedPatMuons"
    if postfix != "":
        # Assume PF2PAT
        src = "selectedPatMuons"+postfix+"All"

    tightMuons = cms.EDFilter("PATMuonSelector",
        src = cms.InputTag(src),
        # Take out chi2<10 cut for testing TuneP cocktail
        cut = cms.string("%s && globalTrack().hitPattern().numberOfValidMuonHits() > 0" % muonGlobalPtEta)
#        cut = cms.string("%s && muonID('GlobalMuonPromptTight')" % muonGlobalPtEta)
#        "&& innerTrack().numberOfValidHits() > 10"
#        "&& innerTrack().hitPattern().pixelLayersWithMeasurement() >= 1"
#        "&& numberOfMatches() > 1"
#        "&& abs(dB()) < 0.02"
    #    "&& (isolationR03().emEt+isolationR03().hadEt+isolationR03().sumPt)/pt() < 0.05",
#        )
    )
    return tightMuons

def addMuonPreSelectionForEmbedding(process):
    sequence = cms.Sequence()

    process.muonPreSelectionAllEvents = cms.EDProducer("EventCountProducer")
    sequence *= process.muonPreSelectionAllEvents

    process.muonPreSelectionMuons = cms.EDFilter("CandPtrSelector",
        src = cms.InputTag(process.patMuons.muonSource.value()),
        cut = cms.string(muonGlobalPtEta)
    )
    sequence *= process.muonPreSelectionMuons

    process.muonPreSelectionMuonsFilter = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag("muonPreSelectionMuons"),
        minNumber = cms.uint32(1)
    )
    sequence *= process.muonPreSelectionMuonsFilter

    process.muonPreSelectionPassed = cms.EDProducer("EventCountProducer")
    sequence *= process.muonPreSelectionPassed

    return sequence

def addMuonSelectionForEmbedding(process, postfix=""):
    muonSelectionAllEvents = cms.EDProducer("EventCountProducer")
    setattr(process, "muonSelectionAllEvents"+postfix, muonSelectionAllEvents)
    
    ### Primary vertex
    muonFirstPrimaryVertex = cms.EDProducer("HPlusFirstVertexSelector",
        src = cms.InputTag("offlinePrimaryVertices")
    )
    setattr(process, "muonFirstPrimaryVertex"+postfix, muonFirstPrimaryVertex)
    
    muonGoodPrimaryVertex = cms.EDFilter("VertexSelector",
        filter = cms.bool(False),
        src = cms.InputTag("muonFirstPrimaryVertex"+postfix),
        cut = cms.string("!isFake && ndof > 4 && abs(z) < 24.0 && position.rho < 2.0")
    )
    setattr(process, "muonGoodPrimaryVertex"+postfix, muonGoodPrimaryVertex)
    
    muonPrimaryVertexFilter = cms.EDFilter("VertexCountFilter",
        src = cms.InputTag("muonGoodPrimaryVertex"+postfix),
        minNumber = cms.uint32(1),
        maxNumber = cms.uint32(999)
    )
    setattr(process, "muonPrimaryVertexFilter"+postfix, muonPrimaryVertexFilter)
    
    muonSelectionPrimaryVertex = cms.EDProducer("EventCountProducer")
    setattr(process, "muonSelectionPrimaryVertex"+postfix, muonSelectionPrimaryVertex)

    ### Tight muon ID, with slightly relaxed pT cut and without isolation
    tightMuons = getTightMuonsDefinition(postfix=postfix)
    setattr(process, "tightMuons"+postfix, tightMuons)
    
    #tightMuonsZ = cms.EDFilter("HPlusPATMuonViewVertexZSelector",
    #    src = cms.InputTag("tightMuons"),
    #    vertexSrc = cms.InputTag("muonGoodPrimaryVertex"),
    #    maxZ = cms.double(1.0)
    #)
    #setattr(process, "tightMuonsZ"+postfix, tightMuonsZ)
    
    tightMuonsFilter = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag("tightMuons"+postfix),
        minNumber = cms.uint32(1)
    )
    setattr(process, "tightMuonsFilter"+postfix, tightMuonsFilter)
    
    #tauEmbeddingMuons = cms.EDFilter("HPlusLargestPtPATMuonViewSelector",
    #tauEmbeddingMuons = cms.EDFilter("HPlusSmallestRelIsoPATMuonViewSelector",
    #    src = cms.InputTag("tightMuons"),
    #    filter = cms.bool(False),
    #    maxNumber = cms.uint32(1)
    #)
    ##tauEmbeddingMuons = cms.EDFilter("HPlusPATMuonViewVertexZSelector",
    #    src = cms.InputTag("tightMuons"),
    #    vertexSrc = cms.InputTag("muonGoodPrimaryVertex"),
    #    maxZ = cms.double(1.0)
    #)
    #setattr(process, "tauEmbeddingMuons"+postfix, tauEmbeddingMuons)
    # tauEmbeddingMuonsFilter = cms.EDFilter("PATCandViewCountFilter",
    #     src = cms.InputTag("tauEmbeddingMuons"),
    #     minNumber = cms.uint32(1),
    #     maxNumber = cms.uint32(1)
    # )
    #setattr(process, "tauEmbeddingMuonsFilter"+postfix, tauEmbeddingMuonsFilter)
    muonSelectionMuons = cms.EDProducer("EventCountProducer")
    setattr(process, "muonSelectionMuons"+postfix, muonSelectionMuons)

    ### Jet selection
    # As the muon selection is not yet final at this stage, do not
    # clean the jets from selected muon before counting them.

    #from PhysicsTools.PatAlgos.cleaningLayer1.jetCleaner_cfi import *
    #goodJets = cleanPatJets.clone(
    goodJets = cms.EDFilter("PATJetSelector",
        src = cms.InputTag("selectedPatJets"+postfix),
    #    preselection =
        cut = cms.string(
        "pt() > 20 && abs(eta()) < 2.4"
        "&& numberOfDaughters() > 1 && chargedEmEnergyFraction() < 0.99"
        "&& neutralHadronEnergyFraction() < 0.99 && neutralEmEnergyFraction < 0.99"
        "&& chargedHadronEnergyFraction() > 0 && chargedMultiplicity() > 0" # eta < 2.4, so don't need the requirement here
        ),
    #    checkOverlaps = cms.PSet(
    #        muons = cms.PSet(
    #            src                 = cms.InputTag("tauEmbeddingMuons"),
    #            algorithm           = cms.string("byDeltaR"),
    #            preselection        = cms.string(""),
    #            deltaR              = cms.double(0.1),
    #            checkRecoComponents = cms.bool(False),
    #            pairCut             = cms.string(""),
    #            requireNoOverlaps   = cms.bool(True),
    #        )
    #    )
    )
    setattr(process, "goodJets"+postfix, goodJets)
    
    goodJetFilter = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag("goodJets"+postfix),
        minNumber = cms.uint32(3)
    )
    setattr(process, "goodJetFilter"+postfix, goodJetFilter)
    
    muonSelectionJets = cms.EDProducer("EventCountProducer")
    setattr(process, "muonSelectionJets"+postfix, muonSelectionJets)

    # goodMet = cms.EDFilter("PATMETSelector",
    #     src = cms.InputTag("patMETsPF"),
    #     cut = cms.string("et() > 40")
    # )
    # setattr(process, "goodMet"+postfix, goodMet)
    # goodMetFilter = cms.EDFilter("CandViewCountFilter",
    #     src = cms.InputTag("goodMet"),
    #     minNumber = cms.uint32(1)
    # )
    # setattr(process, "goodMetFilter"+postfix, goodMetFilter)
    # muonSelectionMet = cms.EDProducer("EventCountProducer")
    # setattr(process, "muonSelectionMet"+postfix, muonSelectionMet)

    muonSelectionSequence = cms.Sequence(
        muonSelectionAllEvents
        * muonFirstPrimaryVertex * muonGoodPrimaryVertex * muonPrimaryVertexFilter * muonSelectionPrimaryVertex
        * tightMuons 
    #    * tightMuonsZ 
        * tightMuonsFilter
    #    * tauEmbeddingMuons 
    #    * tauEmbeddingMuonsFilter
        * muonSelectionMuons
        * goodJets      * goodJetFilter * muonSelectionJets
    #    * goodMet       * goodMetFilter * muonSelectionMet
    )
    return muonSelectionSequence
    

def getMuonPreSelectionCountersForEmbedding():
    return ["muonPreSelectionAllEvents",
            "muonPreSelectionPassed"]

def getMuonSelectionCountersForEmbedding(dataVersion, jetPostfixes=["", "Chs"]):
    muonSelectionCounters = [
        "muonSelectionAllEvents",
        "muonSelectionPrimaryVertex",
        "muonSelectionMuons"
        ]
    muonSelectionCounters.extend(["muonSelectionJets"+p for p in jetPostfixes])
    if dataVersion.isMC():
        for postfix in jetPostfixes:
            muonSelectionCounters.extend([
                    "muonSelectionJetsSmeared"+postfix, 
                    "muonSelectionJetsResDown"+postfix,
                    "muonSelectionJetsResUp"+postfix,
                    "muonSelectionJetsEnDown"+postfix,
                    "muonSelectionJetsEnUp"+postfix
            ])
    return muonSelectionCounters

def getMuonSelectionCountersForEmbeddingPF2PAT(dataVersion, postfix=""):
    muonSelectionCounters = [
        "muonSelectionAllEvents"+postfix,
        "muonSelectionPrimaryVertex"+postfix,
        "muonSelectionMuons"+postfix,
        "muonSelectionJets"+postfix,
    ]
    if dataVersion.isMC():
        muonSelectionCounters.extend([
            "muonSelectionJetsSmeared"+postfix, 
            "muonSelectionJetsResDown"+postfix,
            "muonSelectionJetsResUp"+postfix,
            "muonSelectionJetsEnDown"+postfix,
            "muonSelectionJetsEnUp"+postfix
        ])
    return muonSelectionCounters
