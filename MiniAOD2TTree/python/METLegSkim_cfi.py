import FWCore.ParameterSet.Config as cms

skim = cms.EDFilter("METLegSkim",
    TriggerResults = cms.InputTag("TriggerResults::HLT"),
    HLTPaths       = cms.vstring("HLT_MediumChargedIsoPFTau50_Trk30_eta2p1_1pr_v"),
    JetCollection  = cms.InputTag("slimmedJets"),
    JetUserFloats  = cms.vstring(
	"pileupJetId:fullDiscriminant",
    ),
    JetEtCut       = cms.double(20),
    JetEtaCut      = cms.double(2.4),
    NJets          = cms.int32(0),
    GenWeights     = cms.VPSet()
)
