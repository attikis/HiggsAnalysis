import FWCore.ParameterSet.Config as cms
Taus = cms.VPSet(
    cms.PSet(
            branchname = cms.untracked.string("Taus"),
            src = cms.InputTag("slimmedTaus"),
            discriminators = cms.vstring(
		'againstElectronLooseMVA6',
		'againstElectronMVA6Raw',
		'againstElectronMVA6category',
		'againstElectronMediumMVA6',
		'againstElectronTightMVA6',
		'againstElectronVLooseMVA6',
		'againstElectronVTightMVA6',
		'againstMuonLoose3',
		'againstMuonTight3',
		'byCombinedIsolationDeltaBetaCorrRaw3Hits',
		'byIsolationMVArun2v1DBdR03oldDMwLTraw',
		'byIsolationMVArun2v1DBnewDMwLTraw',
		'byIsolationMVArun2v1DBoldDMwLTraw',
		'byIsolationMVArun2v1PWdR03oldDMwLTraw',
		'byIsolationMVArun2v1PWnewDMwLTraw',
		'byIsolationMVArun2v1PWoldDMwLTraw',
		'byLooseCombinedIsolationDeltaBetaCorr3Hits',
		'byLooseIsolationMVArun2v1DBdR03oldDMwLT',
		'byLooseIsolationMVArun2v1DBnewDMwLT',
		'byLooseIsolationMVArun2v1DBoldDMwLT',
		'byLooseIsolationMVArun2v1PWdR03oldDMwLT',
		'byLooseIsolationMVArun2v1PWnewDMwLT',
		'byLooseIsolationMVArun2v1PWoldDMwLT',
		'byMediumCombinedIsolationDeltaBetaCorr3Hits',
		'byMediumIsolationMVArun2v1DBdR03oldDMwLT',
		'byMediumIsolationMVArun2v1DBnewDMwLT',
		'byMediumIsolationMVArun2v1DBoldDMwLT',
		'byMediumIsolationMVArun2v1PWdR03oldDMwLT',
		'byMediumIsolationMVArun2v1PWnewDMwLT',
		'byMediumIsolationMVArun2v1PWoldDMwLT',
		'byPhotonPtSumOutsideSignalCone',
		'byTightCombinedIsolationDeltaBetaCorr3Hits',
		'byTightIsolationMVArun2v1DBdR03oldDMwLT',
		'byTightIsolationMVArun2v1DBnewDMwLT',
		'byTightIsolationMVArun2v1DBoldDMwLT',
		'byTightIsolationMVArun2v1PWdR03oldDMwLT',
		'byTightIsolationMVArun2v1PWnewDMwLT',
		'byTightIsolationMVArun2v1PWoldDMwLT',
		'byVLooseIsolationMVArun2v1DBdR03oldDMwLT',
		'byVLooseIsolationMVArun2v1DBnewDMwLT',
		'byVLooseIsolationMVArun2v1DBoldDMwLT',
		'byVLooseIsolationMVArun2v1PWdR03oldDMwLT',
		'byVLooseIsolationMVArun2v1PWnewDMwLT',
		'byVLooseIsolationMVArun2v1PWoldDMwLT',
		'byVTightIsolationMVArun2v1DBdR03oldDMwLT',
		'byVTightIsolationMVArun2v1DBnewDMwLT',
		'byVTightIsolationMVArun2v1DBoldDMwLT',
		'byVTightIsolationMVArun2v1PWdR03oldDMwLT',
		'byVTightIsolationMVArun2v1PWnewDMwLT',
		'byVTightIsolationMVArun2v1PWoldDMwLT',
		'byVVTightIsolationMVArun2v1DBdR03oldDMwLT',
		'byVVTightIsolationMVArun2v1DBnewDMwLT',
		'byVVTightIsolationMVArun2v1DBoldDMwLT',
		'byVVTightIsolationMVArun2v1PWdR03oldDMwLT',
		'byVVTightIsolationMVArun2v1PWnewDMwLT',
		'byVVTightIsolationMVArun2v1PWoldDMwLT',
		'chargedIsoPtSum',
		'chargedIsoPtSumdR03',
		'decayModeFinding',
		'decayModeFindingNewDMs',
		'footprintCorrection',
		'footprintCorrectiondR03',
		'neutralIsoPtSum',
		'neutralIsoPtSumWeight',
		'neutralIsoPtSumWeightdR03',
		'neutralIsoPtSumdR03',
		'photonPtSumOutsideSignalCone',
		'photonPtSumOutsideSignalConedR03',
		'puCorrPtSum'
            ),
            filter = cms.untracked.bool(False), 
            jetSrc = cms.InputTag("slimmedJets"), # made from ak4PFJetsCHS
            systVariations = cms.bool(True),
            TEScorrection = cms.bool(True),
            TESvariation = cms.untracked.double(0.012),
            TESvariationExtreme = cms.untracked.double(0.03)
    )
)

# https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV
Taus_TauPOGRecommendation = cms.VPSet()
Taus_TauPOGRecommendation.append(Taus[0].clone())
Taus_TauPOGRecommendation[0].discriminators = cms.vstring(
                'againstElectronLooseMVA6',                                                                                                                                                                                               
                'againstElectronMediumMVA6',                                                                                                                                                                                              
                'againstElectronTightMVA6',                                                                                                                                                                                               
                'againstElectronVLooseMVA6',                                                                                                                                                                                              
                'againstElectronVTightMVA6',                                                                                                                                                                                              
                'againstMuonLoose3',                                                                                                                                                                                                      
                'againstMuonTight3',                                                                                                                                                                                                      
                'byLooseCombinedIsolationDeltaBetaCorr3Hits',                                                                                                                                                                             
                'byMediumCombinedIsolationDeltaBetaCorr3Hits',                                                                                                                                                                            
                'byTightCombinedIsolationDeltaBetaCorr3Hits',                                                                                                                                                                             
                'decayModeFinding',                                                                                                                                                                                                       
                'decayModeFindingNewDMs',
                'byVLooseIsolationMVArun2v1DBoldDMwLT'
)

TausNoSysVariations = cms.VPSet()
TausNoSysVariations.append(Taus_TauPOGRecommendation[0].clone())
for i in range(len(TausNoSysVariations)):
    TausNoSysVariations[i].systVariations = cms.bool(False)
