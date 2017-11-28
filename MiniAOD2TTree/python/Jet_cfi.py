#================================================================================================
# Import modules
#================================================================================================
import FWCore.ParameterSet.Config as cms


# Workaround: use PSets because this module is loaded
#JECpayloadAK4PFchs = cms.PSet(
#    payload = cms.string("AK4PFchs")
#)
#JECpayloadAK4PFPuppi = cms.PSet(
#    payload = cms.string("AK4PFPuppi")
#)

Jets = cms.VPSet(
    cms.PSet(
        branchname = cms.untracked.string("Jets"),
#        src = cms.InputTag("patJetsReapplyJECAK4CHS"), # made from ak4PFJetsCHS
        src = cms.InputTag("selectedPatJetsAK4PFCHS"),#updatedPatJetsUpdatedJEC"),
#        src = cms.InputTag("selectedPatJetsForMetT1T2SmearCorr"),
#        src = cms.InputTag("cleanedPatJets"),
#        src = cms.InputTag("patJetsReapplyJEC"),
	systVariations = cms.bool(False),
        srcJESup   = cms.InputTag("shiftedPatJetEnUp"),
	srcJESdown = cms.InputTag("shiftedPatJetEnDown"),
        srcJERup   = cms.InputTag("shiftedPatSmearedJetResUp"),
        srcJERdown = cms.InputTag("shiftedPatSmearedJetResDown"),
#        jecPayload = JECpayloadAK4PFchs.payload,

        discriminators = cms.vstring( #https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80X
            "pfJetBProbabilityBJetTags",
            "pfJetProbabilityBJetTags",
            "pfTrackCountingHighEffBJetTags",
            "pfSimpleSecondaryVertexHighEffBJetTags",
            "pfSimpleInclusiveSecondaryVertexHighEffBJetTags",
            "pfCombinedSecondaryVertexV2BJetTags",
            "pfCombinedInclusiveSecondaryVertexV2BJetTags",
            "softPFMuonBJetTags",
            "softPFElectronBJetTags",
            "pfCombinedMVAV2BJetTags",
            "pfCombinedCvsLJetTags",
            "pfCombinedCvsBJetTags",
            "tightpfCombinedSecondaryVertexV2BJetTags",
            "tightpfCombinedInclusiveSecondaryVertexV2BJetTags",
            "tightpfCombinedCvsLJetTags",
            "tightpfCombinedCvsBJetTags"
        ),
        userFloats = cms.vstring(
            "pileupJetId:fullDiscriminant",
            "AK4PFCHSpileupJetIdEvaluator:fullDiscriminant",
            "QGTaggerAK4PFCHS:qgLikelihood",
            "QGTaggerAK4PFCHS:ptD",
            "QGTaggerAK4PFCHS:axis2",
        ),       
        userInts = cms.vstring(
            "QGTaggerAK4PFCHS:mult",
        ),
        checkSubjets = cms.bool(False),
    ),

    # AK8 (aka fat-jets)
    cms.PSet(
        branchname = cms.untracked.string("AK8Jets"),
        src        = cms.InputTag("selectedPatJetsAK8PFCHS"),
        systVariations = cms.bool(False),

        discriminators = cms.vstring(
            "pfCombinedInclusiveSecondaryVertexV2BJetTags",
            "pfCombinedMVAV2BJetTags",
            "pfCombinedCvsLJetTags",
            "pfCombinedCvsBJetTags"
            ),
        userFloats = cms.vstring(
            "NjettinessAK8CHS:tau1",
            "NjettinessAK8CHS:tau2",
            "NjettinessAK8CHS:tau3",
            "NjettinessAK8CHS:tau4",
            ),

        userInts = cms.vstring(
            ),
        
        checkSubjets = cms.bool(False),
        ),
    
    # AK8 - SoftDrop Subjets
    cms.PSet(
        branchname = cms.untracked.string("AK8JetsSoftDrop"),
        src        = cms.InputTag("packedPatJetsAK8PFCHSSoftDrop"),
        systVariations = cms.bool(False),

        discriminators = cms.vstring(
            "pfCombinedInclusiveSecondaryVertexV2BJetTags",
            ),
        userFloats = cms.vstring(
            ),
        userInts = cms.vstring(
            ),
        checkSubjets = cms.bool(True),
        ),

#    cms.PSet(
#        branchname = cms.untracked.string("JetsPuppi"),
##        src = cms.InputTag("patJetsReapplyJECPuppi"), # made from ak4PFJets
#        src        = cms.InputTag("updatedPatJetsUpdatedJECPuppi"),
#        srcJESup   = cms.InputTag("shiftedPatJetEnUp"),
#        srcJESdown = cms.InputTag("shiftedPatJetEnDown"),
#        srcJERup   = cms.InputTag("shiftedPatJetResUp"),
#        srcJERdown = cms.InputTag("shiftedPatJetResDown"),
##        jecPayload = JECpayloadAK4PFPuppi.payload,
#        discriminators = cms.vstring(
#            "pfCombinedInclusiveSecondaryVertexV2BJetTags",
#            "pfCombinedMVAV2BJetTags", 
#            "pfCombinedCvsLJetTags", 
#            "pfCombinedCvsBJetTags"
#         ),
#        userFloats = cms.vstring(
##           "pileupJetId:fullDiscriminant"
#        ),
#    )
)


JetsNoSysVariations = cms.VPSet()
for i in range(len(Jets)):
    pset = Jets[i].clone()
    pset.systVariations = cms.bool(False)
    JetsNoSysVariations.append(pset)

