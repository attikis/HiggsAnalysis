'''

Instructions:
- Import this module
- Call produceCustomisations just before cms.Path
- Add process.CustomisationsSequence to the cms.Path

'''
#================================================================================================ 
# Import modules
#================================================================================================ 
import FWCore.ParameterSet.Config as cms

#================================================================================================ 
# Function definition
#================================================================================================ 
def produceCustomisations(process, isData):
    process.CustomisationsSequence = cms.Sequence()
#    produceJets(process, isData)
#    reproduceJEC(process)
    reproduceElectronID(process)      # Marina (To produce MVA)
    reproduceMETNoiseFilters(process)
    reproduceMET(process, isData)
#    reproduceJEC(process)
    produceJets(process, isData)
    print "=== Customisations done"

# AK8 Customisations
def produceAK8Customisations(process, isData):
    process.AK8CustomisationsSequence = cms.Sequence()
    produceAK8JEC(process, isData)
    print "=== AK8 Customisations done"

def produceAK8JEC(process, isData):
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    
    JEC = ['L1FastJet','L2Relative','L3Absolute']
    if isData:
        JEC += ['L2L3Residual']
        
    updateJetCollection(
        process,
        labelName = 'AK8PFCHS',
        jetSource = cms.InputTag("slimmedJetsAK8"),
        rParam = 0.8,
        jetCorrections = ('AK8PFchs', cms.vstring(JEC), 'None') 
    )
    
    process.AK8CustomisationsSequence += process.patJetCorrFactorsAK8PFCHS
    process.AK8CustomisationsSequence += process.updatedPatJetsAK8PFCHS
    return

def produceJets(process, isData):
    '''
    JetToolbox twiki:
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
    
    Using the QGTagger with Jet Toolbox: 
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox#QGTagger
    
    QuarkGluonLikelihood twiki: 
    https://twiki.cern.ch/twiki/bin/view/CMS/QuarkGluonLikelihood
    
    More info:
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/QGDataBaseVersion
    '''
    process.load("Configuration.EventContent.EventContent_cff")
    process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
    process.load('Configuration.StandardSequences.MagneticField_38T_cff')
    process.load('Configuration.StandardSequences.Services_cff')
    
    JEC = ['L1FastJet','L2Relative','L3Absolute']
    if isData:
        JEC += ['L2L3Residual']

    from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox
    jetToolbox( process, 'ak4', 'ak4JetSubs', 'out', 
                addQGTagger=True, addPUJetID=True, JETCorrLevels = JEC,
                bTagDiscriminators = ['pfCombinedInclusiveSecondaryVertexV2BJetTags', 'pfCombinedMVAV2BJetTags','pfCombinedCvsBJetTags','pfCombinedCvsLJetTags'],
                updateCollection='cleanedPatJets', JETCorrPayload="AK4PFchs",
                postFix='')

    # Small fix required to add the variables ptD, axis2, mult. See:
    # https://hypernews.cern.ch/HyperNews/CMS/get/jet-algorithms/418/1.html
    getattr( process, 'updatedPatJetsAK4PFCHS').userData.userFloats.src += ['QGTagger'+'AK4PFCHS'+':ptD']
    getattr( process, 'updatedPatJetsAK4PFCHS').userData.userFloats.src += ['QGTagger'+'AK4PFCHS'+':axis2']
    getattr( process, 'updatedPatJetsAK4PFCHS').userData.userInts.src   += ['QGTagger'+'AK4PFCHS'+':mult']

    return


# ===== Reproduce jet collections with the latest JEC =====
def reproduceJEC(process):
    '''
    For instructions and more details see:
    https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#CorrPatJets
    https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#Jets
    https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetAnalysis
    '''
    print "=== Customisation: reproducing jet collections with latest JEC"
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    updateJetCollection(
        process,
        # jetSource = cms.InputTag('slimmedJets'),
        jetSource = cms.InputTag('cleanedPatJets'),
        labelName = 'UpdatedJEC',
        jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None')  # Do not forget 'L2L3Residual' on data!
    )
    # PUPPI jets
    updateJetCollection(
        process,
        jetSource = cms.InputTag('slimmedJetsPuppi'),
        labelName = 'UpdatedJECPuppi',
        jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None')  # Do not
    )
    
    # Add to customisations sequence
    process.CustomisationsSequence += process.patJetCorrFactorsUpdatedJEC
    process.CustomisationsSequence += process.updatedPatJetsUpdatedJEC
    process.CustomisationsSequence += process.patJetCorrFactorsUpdatedJECPuppi
    process.CustomisationsSequence += process.updatedPatJetsUpdatedJECPuppi


# ===== Set up electron ID (VID framework) =====
from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
def reproduceElectronID(process):
    '''
    For instructions and more details see:
    https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2
    '''
    print "=== Customisation: reproducing electron ID discriminators"
    switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
    # define which IDs we want to produce and add them to the VID producer
    for idmod in ['RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_GeneralPurpose_V1_cff',
                  #'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_PHYS14_PU20bx25_nonTrig_V1_cff', 
                  ]:   # Marina
        setupAllVIDIdsInModule(process, idmod, setupVIDElectronSelection)
    process.CustomisationsSequence += process.egmGsfElectronIDSequence

# ===== Set up HBHE noise filter =====
def reproduceMETNoiseFilters(process):
    '''
    For instructions and more details see:
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2
    '''
    print "=== Customisation: reproducing HBHE noise filter"
    process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
    process.HBHENoiseFilterResultProducer.minZeros = cms.int32(99999)
    process.HBHENoiseFilterResultProducer.IgnoreTS4TS5ifJetInLowBVRegion=cms.bool(False)
    process.HBHENoiseFilterResultProducer.defaultDecision = cms.string("HBHENoiseFilterResultRun2Loose")

    process.load('RecoMET.METFilters.BadPFMuonFilter_cfi')
    process.BadPFMuonFilter.muons = cms.InputTag("slimmedMuons")
    process.BadPFMuonFilter.PFCandidates = cms.InputTag("packedPFCandidates")
    process.BadPFMuonFilter.taggingMode   = cms.bool(True)

    process.load('RecoMET.METFilters.BadChargedCandidateFilter_cfi')
    process.BadChargedCandidateFilter.muons = cms.InputTag("slimmedMuons")
    process.BadChargedCandidateFilter.PFCandidates = cms.InputTag("packedPFCandidates")
    process.BadChargedCandidateFilter.taggingMode   = cms.bool(True)

    # Do not apply EDfilters for HBHE noise, the discriminators for them are saved into the ttree
    process.CustomisationsSequence += process.HBHENoiseFilterResultProducer
    process.CustomisationsSequence += process.BadPFMuonFilter
    process.CustomisationsSequence += process.BadChargedCandidateFilter

# ===== Set up MET uncertainties =====

def reproduceMET(process,isdata):
    '''
    For instructions and more details see:
    https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription#A_tool_to_help_you_calculate_MET
    https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
    https://github.com/cms-jet/JRDatabase/tree/master/SQLiteFiles
    '''
    from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
    import os

    if isdata:
#      era="Spring16_25nsV6_DATA"
       era="Summer16_23Sep2016AllV4_DATA"
    else:
#      era="Spring16_25nsV6_MC"
      era="Summer16_23Sep2016V4_MC"

#    jerera="Spring16_25nsV6"
#    jerera="Spring16_25nsV10"
    jerera="Summer16_25nsV1_80X"
    
##___________________________External JEC file________________________________||
 
    process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
#                               connect = cms.string("sqlite:PhysicsTools/PatUtils/data/"+era+".db"),
                               connect = cms.string("sqlite:"+era+"_JEC.db"),
                               toGet =  cms.VPSet(
            cms.PSet(
                record = cms.string("JetCorrectionsRecord"),
                tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PF"),
                label= cms.untracked.string("AK4PF")
                ),
            cms.PSet(
                record = cms.string("JetCorrectionsRecord"),
                tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFchs"),  
                label= cms.untracked.string("AK4PFchs")
                ),
            cms.PSet(record  = cms.string("JetCorrectionsRecord"),
                tag     = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFPuppi"),
                label   = cms.untracked.string("AK4PFPuppi")
                ),
            cms.PSet(record  = cms.string("JetCorrectionsRecord"),
                tag     = cms.string("JetCorrectorParametersCollection_"+era+"_AK8PFchs"),
                label   = cms.untracked.string("AK8PFchs")
                ),
    
            )
                               )
    process.es_prefer_jec = cms.ESPrefer("PoolDBESSource",'jec')

##___________________________External JER file________________________________||
    
    process.jer = cms.ESSource("PoolDBESSource",CondDBSetup,
#                               connect = cms.string("sqlite:PhysicsTools/PatUtils/data/JER/"+jerera+"_MC.db"),
                               connect = cms.string("sqlite:"+jerera+"_MC_JER.db"),
                               toGet =  cms.VPSet(
        #######
        ### read the PFchs  

        cms.PSet(
          record = cms.string('JetResolutionRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_PtResolution_AK4PFchs'),
          label  = cms.untracked.string('AK4PFchs_pt')
          ),
        cms.PSet(
          record = cms.string("JetResolutionRcd"),
          tag    = cms.string('JR_'+jerera+'_MC_PhiResolution_AK4PFchs'),
          label  = cms.untracked.string("AK4PFchs_phi")
          ),
        cms.PSet( 
          record = cms.string('JetResolutionScaleFactorRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_SF_AK4PFchs'),
          label  = cms.untracked.string('AK4PFchs')
          ),
        
        ### read the AK8 JER
        cms.PSet(
          record = cms.string('JetResolutionRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_PtResolution_AK8PFchs'),
          label  = cms.untracked.string('AK8PFchs_pt')
          ),
        cms.PSet(
          record = cms.string("JetResolutionRcd"),
          tag    = cms.string('JR_'+jerera+'_MC_PhiResolution_AK8PFchs'),
          label  = cms.untracked.string("AK8PFchs_phi")
          ),
        cms.PSet( 
          record = cms.string('JetResolutionScaleFactorRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_SF_AK8PFchs'),
          label  = cms.untracked.string('AK8PFchs')
          ),
        
          
        #######
        ### read the Puppi JER

#        cms.PSet( 
#          record = cms.string('JetResolutionRcd'),
#          tag    = cms.string('JR_'+jerera+'_MC_PtResolution_AK4PFPuppi'),
#          label  = cms.untracked.string('AK4PFPuppi_pt')
#          ),
#        cms.PSet(
#          record = cms.string("JetResolutionRcd"),
#          tag = cms.string('JR_'+jerera+'_MC_PhiResolution_AK4PFPuppi'),
#          label= cms.untracked.string("AK4PFPuppi_phi")
#          ),
#        cms.PSet(
#          record = cms.string('JetResolutionScaleFactorRcd'),
#          tag    = cms.string('JR_'+jerera+'_MC_SF_AK4PFPuppi'),
#          label  = cms.untracked.string('AK4PFPuppi')
#          ),
        ) 
    )
          
    process.es_prefer_jer = cms.ESPrefer("PoolDBESSource",'jer')

    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
    
    #default configuration for miniAOD reprocessing, change the isData flag to run on data
    #for a full met computation, remove the pfCandColl input
    runMetCorAndUncFromMiniAOD(process,
                           isData=isdata,
                           )

#    process.selectedPatJetsForMetT1T2Corr.src = cms.InputTag("cleanedPatJets")
#    process.patPFMetT1.src = cms.InputTag("slimmedMETs")
#
#    process.CustomisationsSequence += process.patJetCorrFactorsReapplyJEC 
#    process.CustomisationsSequence += process.patJetsReapplyJEC
#    process.CustomisationsSequence += process.basicJetsForMet
#    process.CustomisationsSequence += process.jetSelectorForMet
#    process.CustomisationsSequence += process.cleanedPatJets
#    process.CustomisationsSequence += process.metrawCalo
#    process.CustomisationsSequence += process.selectedPatJetsForMetT1T2Corr   
#    process.CustomisationsSequence += process.patPFMetT1T2Corr
#    process.CustomisationsSequence += process.patPFMetT1

#    process.CustomisationsSequence += process.patMetCorrectionSequence

    if isdata:
        return

#    process.CustomisationsSequence += process.patMetUncertaintySequence #only for MC
#    process.CustomisationsSequence += process.patShiftedModuleSequence #only for MC


    """    
    # puppi jets and puppi met
    from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
    makePuppiesFromMiniAOD(process);

    runMetCorAndUncFromMiniAOD(process,
                             isData=isdata,
                             pfCandColl=cms.InputTag("puppiForMET"),
                             recoMetFromPFCs=True,
                             reclusterJets=True,
                             jetFlavor="AK4PFPuppi",
                             postfix="Puppi"
                             )
    process.patPFMetPuppi.addGenMET = cms.bool(False)
    process.basicJetsForMetPuppi.src = cms.InputTag("slimmedJetsPuppi")
    process.patPFMetT1Puppi.src = cms.InputTag("slimmedMETsPuppi")

    process.producePatPFMETCorrectionsPuppi.remove(process.patPFMetPuppi)
    process.CustomisationsSequence += process.producePatPFMETCorrectionsPuppi

#    process.CustomisationsSequence += process.pfNoLepPUPPI
#    process.CustomisationsSequence += process.puppiNoLep
#    process.CustomisationsSequence += process.pfLeptonsPUPPET
#    process.CustomisationsSequence += process.puppiMerged
#    process.CustomisationsSequence += process.puppiForMET
##    process.CustomisationsSequence += process.pfMetPuppi
##    process.CustomisationsSequence += process.patPFMetPuppi
#    process.CustomisationsSequence += process.ak4PFJetsPuppi
#    process.CustomisationsSequence += process.basicJetsForMetPuppi
#    process.CustomisationsSequence += process.jetSelectorForMetPuppi
#    process.CustomisationsSequence += process.cleanedPatJetsPuppi
#    process.CustomisationsSequence += process.pfMetPuppi
#    process.CustomisationsSequence += process.metrawCaloPuppi
#    process.CustomisationsSequence += process.patPFMetT1Puppi
#
#    process.CustomisationsSequence += process.patMetUncertaintySequencePuppi
#    process.CustomisationsSequence += process.patShiftedModuleSequencePuppi
#    process.CustomisationsSequence += process.patMetCorrectionSequencePuppi
    """
