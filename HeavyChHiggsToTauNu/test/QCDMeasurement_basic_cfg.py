import FWCore.ParameterSet.Config as cms
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion

################################################################################
# Configuration

# Select the version of the data (needed only for interactice running,
dataVersion="44XmcS6"     # Fall11 MC
#dataVersion="44Xdata"    # Run2011 08Nov and 19Nov ReRecos


##########
# Flags for additional signal analysis modules
# Perform the signal analysis with all tau ID algorithms in addition
# to the "golden" analysis

#for QCD control plots
doAllTauIds = False

# Perform b tagging scanning
doBTagScan = False

doJetThresholdScan = True

# Perform the signal analysis with the JES variations in addition to
# the "golden" analysis
doJESVariation = False
JESVariation = 0.03
JESEtaVariation = 0.02
JESUnclusteredMETVariation = 0.10

# Tree filling
doFillTree = False

# Set level of how many histograms are stored to files
# options are: 'Vital' (least histograms), 'Informative', 'Debug' (all histograms)
myHistogramAmbientLevel = "Debug"

applyTriggerScaleFactor = True

#PF2PATVersion = "PFlow" # For normal PF2PAT
PF2PATVersion = "PFlowChs" # For PF2PAT with CHS

# Temporary switch for disabling prescales (produces tons of unnecessary output
# with Btau data where no prescale is needed at the moment) 
disablePrescales = True



################################################################################

# Command line arguments (options) and DataVersion object
options, dataVersion = getOptionsDataVersion(dataVersion)

################################################################################
# Define the process
#process = cms.Process("HChQCDMeasurementMethod3Part2")
process = cms.Process("HChQCDMeasurementMethodBasic")

#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(500) )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source('PoolSource',
    duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
    fileNames = cms.untracked.vstring(
    #"file:/media/disk/attikis/PATTuples/v18/pattuple_v18_Run2011A_PromptReco_v4_AOD_166374_9_1_jHG.root"
    #"file:/media/disk/attikis/PATTuples/v18/pattuple_v18_TTJets_TuneZ2_Summer11_9_1_bfN.root"
    #
    #"rfio:/castor/cern.ch/user/a/attikis/pattuples/testing/v18/pattuple_v18_Run2011A_PromptReco_v4_AOD_166374_9_1_jHG.root"
    #"rfio:/castor/cern.ch/user/a/attikis/pattuples/testing/v18/pattuple_v18_TTJets_TuneZ2_Summer11_9_1_bfN.root"
    #
    # dataVersion.getAnalysisDefaultFileCastor()
    # For testing in jade
    dataVersion.getAnalysisDefaultFileMadhatter()
    #dataVersion.getAnalysisDefaultFileMadhatterDcap()
    )
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string(dataVersion.getGlobalTag())
print "GlobalTag="+dataVersion.getGlobalTag()

process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChCommon_cfi")

# Uncomment the following in order to print the counters at the end of
# the job (note that if many other modules are being run in the same
# job, their INFO messages are printed too)
process.MessageLogger.cerr.threshold = cms.untracked.string("INFO") #tmp
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

# Fragment to run PAT on the fly if requested from command line
from HiggsAnalysis.HeavyChHiggsToTauNu.HChPatTuple import addPatOnTheFly
process.commonSequence, additionalCounters = addPatOnTheFly(process, options, dataVersion)

# Add configuration information to histograms.root
from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import addConfigInfo
process.infoPath = addConfigInfo(process, options, dataVersion)

################################################################################
# qcdMeasurementMethod3 module

# Primary vertex selection
from HiggsAnalysis.HeavyChHiggsToTauNu.HChPrimaryVertex import addPrimaryVertexSelection
addPrimaryVertexSelection(process, process.commonSequence)

# Import default parameter set and make necessary tweaks
import HiggsAnalysis.HeavyChHiggsToTauNu.HChSignalAnalysisParameters_cff as param
param.overrideTriggerFromOptions(options)
param.trigger.triggerSrc.setProcessName(dataVersion.getTriggerProcess())
# Set tau selection mode (options: 'tauCandidateSelectionOnly', 'tauCandidateSelectionOnlyReversedRtau')
# other options (use not recommended here): 'standard'
param.setAllTauSelectionOperatingMode('tauCandidateSelectionOnly')

# Set tau sources to trigger matched tau collections
param.setAllTauSelectionSrcSelectedPatTausTriggerMatched()

# Trigger with scale factors (at the moment hard coded)
if applyTriggerScaleFactor and dataVersion.isMC():
    param.triggerEfficiencyScaleFactor.mode = "scaleFactor"

# Switch to PF2PAT objects
#param.changeCollectionsToPF2PAT()
param.changeCollectionsToPF2PAT(postfix=PF2PATVersion)

# Set the data scenario for vertex/pileup weighting
puweight = "Run2011A"
if len(options.puWeightEra) > 0:
    puweight = options.puWeightEra
param.setPileupWeight(dataVersion, process=process, commonSequence=process.commonSequence, pset=param.vertexWeight, psetReader=param.vertexWeightReader, era=puweight) # Reweight by true PU distribution
param.setDataTriggerEfficiency(dataVersion, era=puweight)

#Reminder(from HChSignalAnalysisParameters_cff.py):
#def setTriggerPileupFor2011(**kwargs):
#    setEfficiencyTriggersFor2011(**kwargs)
#    setPileupWeightFor2011()

# Overwrite necessary values here
#param.trigger.hltMetCut = 45.0 # note: 45 is the minimum possible value for which HLT_MET is saved (see histogram hlt_met) attikis
#param.trigger.hltMetCut = 0.0 
print "\nhltMetCut:", param.trigger.hltMetCut
param.InvMassVetoOnJets.setTrueToUseModule = False

##############################################################################
process.QCDMeasurement = cms.EDFilter("HPlusQCDMeasurementBasicFilter",
    blindAnalysisStatus = param.blindAnalysisStatus,
    histogramAmbientLevel = param.histogramAmbientLevel,
    trigger = param.trigger.clone(),
    triggerEfficiencyScaleFactor = param.triggerEfficiencyScaleFactor.clone(),
    primaryVertexSelection = param.primaryVertexSelection.clone(),
    GlobalElectronVeto = param.GlobalElectronVeto.clone(),
    GlobalMuonVeto = param.GlobalMuonVeto.clone(),
    tauSelection = param.tauSelectionHPSMediumTauBased.clone(),
    vetoTauSelection = param.vetoTauSelection.clone(),
    jetSelection = param.jetSelection.clone(),
    MET = param.MET.clone(),
    bTagging = param.bTagging.clone(),
    fakeMETVeto = param.fakeMETVeto.clone(),
    jetTauInvMass = param.jetTauInvMass.clone(),
    deltaPhiTauMET = param.deltaPhiTauMET,
    topReconstruction = param.topReconstruction,
    topSelection = param.topSelection.clone(),
    bjetSelection = param.bjetSelection.clone(),
    topChiSelection = param.topChiSelection.clone(),
    topWithBSelection = param.topWithBSelection.clone(),
    topWithWSelection = param.topWithWSelection.clone(),
    forwardJetVeto = param.forwardJetVeto.clone(),
    transverseMassCut = param.transverseMassCut,
    EvtTopology = param.EvtTopology.clone(),
    vertexWeight = param.vertexWeight.clone(),
    vertexWeightReader = param.vertexWeightReader.clone(),
    GenParticleAnalysis = param.GenParticleAnalysis.clone(),
    Tree = param.tree.clone(),
    eventCounter = param.eventCounter.clone()
)
# Factorization (quick and dirty version)
import HiggsAnalysis.HeavyChHiggsToTauNu.HChMetTableFactorization_cfi as mettables
import HiggsAnalysis.HeavyChHiggsToTauNu.METTableFactorization_NoFactorization_cfi as mettableCoeff
#process.QCDMeasurement.factorization = cms.untracked.PSet()
#mettableCoeff.METTableFactorizationCoefficients.METTables_Coefficients = cms.untracked.vdouble( *(
#0.0, 0.0, 0.0223602484, 0.0263059, 0.0210332103, 0.016273393, 0.018639329, 0.0176211454, 0.0183615819, 0.0159055926, 0.025789813, 0.0652346858
#) )
mettableCoeff.METTableFactorizationCoefficients.factorizationSourceName = cms.untracked.string('PMET70_afterJetSelection_fromData_v3')

process.QCDMeasurement.factorization = mettables.METTableParameters
process.QCDMeasurement.factorization.factorizationTables = mettableCoeff.METTableFactorizationCoefficients
# Type 1 MET

# Add type 1 MET
import HiggsAnalysis.HeavyChHiggsToTauNu.HChMetCorrection as MetCorrection
sequence = MetCorrection.addCorrectedMet(process, process.QCDMeasurement, postfix=PF2PATVersion)
process.commonSequence *= sequence

# Prescale fetching done automatically for data
if dataVersion.isData() and not disablePrescales:
    process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HPlusPrescaleWeightProducer_cfi")
    process.hplusPrescaleWeightProducer.prescaleWeightTriggerResults.setProcessName(dataVersion.getTriggerProcess())
    process.hplusPrescaleWeightProducer.prescaleWeightHltPaths = param.trigger.triggers.value()
    process.commonSequence *= process.hplusPrescaleWeightProducer
    process.QCDMeasurement.prescaleSource = cms.untracked.InputTag("hplusPrescaleWeightProducer")

# Disable filling of TTree
if not doFillTree:
    process.QCDMeasurement.Tree.fill = cms.untracked.bool(False)

process.QCDMeasurement.histogramAmbientLevel = myHistogramAmbientLevel

# Print output
print "\ntree will be filled:", process.QCDMeasurement.Tree.fill
print "\nVertexWeight:", process.QCDMeasurement.vertexWeight
print "\nTrigger:", process.QCDMeasurement.trigger
print "\nPV Selection:", process.QCDMeasurement.primaryVertexSelection
print "\nTauSelection operating mode:", process.QCDMeasurement.tauSelection.operatingMode
print "TauSelection src:", process.QCDMeasurement.tauSelection.src
print "TauSelection selection:", process.QCDMeasurement.tauSelection.selection
print "TauSelection isolation:", process.QCDMeasurement.tauSelection.isolationDiscriminator
print "TauSelection ptCut:", process.QCDMeasurement.tauSelection.ptCut
print "TauSelection etacut:", process.QCDMeasurement.tauSelection.etaCut
print "TauSelection leadingTrackPtCut:", process.QCDMeasurement.tauSelection.leadingTrackPtCut
print "TauSelection rtauCut:", process.QCDMeasurement.tauSelection.rtauCut
print "TauSelection nprongs:", process.QCDMeasurement.tauSelection.nprongs
print "\nMET:", process.QCDMeasurement.MET
print "\nGlobalElectronVeto:", process.QCDMeasurement.GlobalElectronVeto
print "\nNonIsolatedElectronVeto:", process.QCDMeasurement.NonIsolatedElectronVeto
print "\nGlobalMuonVeto:", process.QCDMeasurement.GlobalMuonVeto
print "\nNonIsolatedMuonVeto:", process.QCDMeasurement.NonIsolatedMuonVeto
print "\nJetSelection:", process.QCDMeasurement.jetSelection
print "\nbTagging: ", process.QCDMeasurement.bTagging
print "\nFakeMETVeto:", process.QCDMeasurement.fakeMETVeto
print "\nEvtTopology:", process.QCDMeasurement.EvtTopology
#print "\nMetTables:", process.QCDMeasurement.factorization
print "\nTopSelection:", process.QCDMeasurement.topSelection
print "****************************************************"
print "\nInvMassVetoOnJets:", process.QCDMeasurement.InvMassVetoOnJets
print "\nEvtTopology:", process.QCDMeasurement.EvtTopology
print "\nForwardJetVeto:", process.QCDMeasurement.forwardJetVeto
# Counter analyzer (in order to produce compatible root file with the
# python approach)
process.QCDMeasurementCounters = cms.EDAnalyzer("HPlusEventCountAnalyzer",
    counterNames = cms.untracked.InputTag("QCDMeasurement", "counterNames"),
    counterInstances = cms.untracked.InputTag("QCDMeasurement", "counterInstances"),
    printMainCounter = cms.untracked.bool(True),
#    printSubCounters = cms.untracked.bool(True),
#    printAvailableCounters = cms.untracked.bool(False),
)
if len(additionalCounters) > 0:
    process.QCDMeasurementCounters.counters = cms.untracked.VInputTag([cms.InputTag(c) for c in additionalCounters])

# PickEvent module and the main Path. The picked events are only the
# ones selected by the golden analysis defined above.
process.load("HiggsAnalysis.HeavyChHiggsToTauNu.PickEventsDumper_cfi")
process.QCDMeasurementPath = cms.Path(
    process.commonSequence * # supposed to be empty, unless "doPat=1" command line argument is given
    process.QCDMeasurement *
    process.QCDMeasurementCounters
    #* process.PickEvents
)

################################################################################
# The signal analysis with different tau ID algorithms
# # FIXME
# Run the analysis for the different tau ID algorithms at the same job
# as the golden analysis. It is significantly more efficiency to run
# many analyses in a single job compared to many jobs (this avoids
# some of the I/O and grid overhead). The fragment below creates the
# following histogram directories
# QCDMeasurementTauSelectionShrinkingConeCutBased
# QCDMeasurementTauSelectionShrinkingConeTaNCBased
# QCDMeasurementTauSelectionCaloTauCutBased
# QCDMeasurementTauSelectionHPSTightTauBased
# QCDMeasurementTauSelectionCombinedHPSTaNCBased
#
# The corresponding Counter directories have "Counters" postfix, and
# cms.Paths "Path" postfix. The paths are run independently of each
# other. It is important to give the process.commonSequence for the
# function, so that it will be run before the analysis module in the
# Path. Then, in case PAT is run on the fly, the framework runs the
# analysis module after PAT (and runs PAT only once).
if doAllTauIds:
    module = process.QCDMeasurement.clone()
    module.Tree.fill = False #attikis (default is False)
    param.addTauIdAnalyses(process, dataVersion, "QCDMeasurement", module, process.commonSequence, additionalCounters)

from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import addAnalysis
if doJetThresholdScan:
    moduleA = process.QCDMeasurement.clone()
    moduleA.jetSelection.ptCut = 20.0
    addAnalysis(process, "QCDMeasurement3Jets20", moduleA,
                preSequence=process.commonSequence,
                additionalCounters=additionalCounters,
                signalAnalysisCounters=True)
    moduleB = process.QCDMeasurement.clone()
    moduleB.jetSelection.ptCut = 20.0
    moduleB.jetSelection.minNumber = 4
    addAnalysis(process, "QCDMeasurement4Jets20", moduleB,
                preSequence=process.commonSequence,
                additionalCounters=additionalCounters,
                signalAnalysisCounters=True)
    moduleC = process.QCDMeasurement.clone()
    moduleC.jetSelection.ptCut = 20.0
    moduleC.jetSelection.minNumber = 4
    moduleC.bTagging.minNumber = 2
    addAnalysis(process, "QCDMeasurement4Jets20TwoBjets", moduleC,
                preSequence=process.commonSequence,
                additionalCounters=additionalCounters,
                signalAnalysisCounters=True)


################################################################################
# The signal analysis with jet energy scale variation
#
# If the flag is true, create two paths for the variation in plus and
# minus, and clone the signal analysis and counter modules to the
# paths. The tau, jet and MET collections to adjust are taken from the
# configuration of the golden analysis. The fragment below creates the
# following histogram directories
# QCDMeasurementCountersJESPlus05
# QCDMeasurementCountersJESMinus05
from HiggsAnalysis.HeavyChHiggsToTauNu.JetEnergyScaleVariation import addJESVariationAnalysis
if doJESVariation:
    # FIXME: copy new code from signal analysis 
    # In principle here could be more than two JES variation analyses
    JESs = "%02d" % int(JESVariation*100)
    JESe = "%02d" % int(JESEtaVariation*100)
    JESm = "%02d" % int(JESUnclusteredMETVariation*100)
    module = process.QCDMeasurement.clone()
    module.Tree.fill = False
    module.Tree.fillJetEnergyFractions = False # JES variation will make the fractions invalid

    addJESVariationAnalysis(process, dataVersion, "QCDMeasurement", "JESPlus"+JESs+"eta"+JESe+"METPlus"+JESm, module, additionalCounters, JESVariation, JESEtaVariation, JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, dataVersion, "QCDMeasurement", "JESMinus"+JESs+"eta"+JESe+"METPlus"+JESm, module, additionalCounters, -JESVariation, JESEtaVariation, JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, dataVersion, "QCDMeasurement", "JESPlus"+JESs+"eta"+JESe+"METMinus"+JESm, module, additionalCounters, JESVariation, JESEtaVariation, -JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, dataVersion, "QCDMeasurement", "JESMinus"+JESs+"eta"+JESe+"METMinus"+JESm, module, additionalCounters, -JESVariation, JESEtaVariation, -JESUnclusteredMETVariation)

# Print tau discriminators from one tau from one event. Note that if
# the path below is commented, the discriminators are not printed.
process.tauDiscriminatorPrint = cms.EDAnalyzer("HPlusTauDiscriminatorPrintAnalyzer",
    src = process.QCDMeasurement.tauSelection.src
)
#process.tauDiscriminatorPrintPath = cms.Path(
#    process.patSequence *
#    process.tauDiscriminatorPrint
#)


################################################################################
#for QCD control plots
if doAllTauIds:
    process.out = cms.OutputModule("PoolOutputModule",
                                   fileName = cms.untracked.string('output.root'),
                                   outputCommands = cms.untracked.vstring(
        "keep *_*_*_HChQCDMeasurement_*_*_*",
        "drop *_*_counterNames_*",
        "drop *_*_counterInstances_*"
        #	"drop *",
        #	"keep *",
        #        "keep edmMergeableCounter_*_*_*"
        )
                                   )
else:
    process.out = cms.OutputModule("PoolOutputModule",
                                   fileName = cms.untracked.string('output.root'),
                                   outputCommands = cms.untracked.vstring(
        "keep *_*_*_HChQCDMeasurement",
        "drop *_*_counterNames_*",
        "drop *_*_counterInstances_*"
        #	"drop *",
        #	"keep *",
        #        "keep edmMergeableCounter_*_*_*"
        )
                                   )
    

# Uncomment the following line to get also the event output (can be
# useful for debugging purposes)
#process.outpath = cms.EndPath(process.out)

