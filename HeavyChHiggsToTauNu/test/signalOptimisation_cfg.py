import FWCore.ParameterSet.Config as cms
from HiggsAnalysis.HeavyChHiggsToTauNu.HChOptions import getOptionsDataVersion

################################################################################
# Configuration

# Select the version of the data (needed only for interactice running,
# overridden automatically from multicrab
#dataVersion = "39Xredigi" # Winter10 MC
#dataVersion = "39Xdata"   # Run2010 Dec22 ReReco
dataVersion="42Xmc"     # Summer11 MC
#dataVersion = "311Xredigi" # Spring11 MC
#dataVersion = "41Xdata"   # Run2011 PromptReco


##########
# Flags for additional signal analysis modules
# Perform the signal analysis with all tau ID algorithms in addition
# to the "golden" analysis
doAllTauIds = False

# Perform b tagging scanning
doBTagScan = False

# Perform the signal analysis with the JES variations in addition to
# the "golden" analysis
doJESVariation = False
JESVariation = 0.03
JESEtaVariation = 0.02
JESUnclusteredMETVariation = 0.10

# With tau embedding input, tighten the muon selection
tauEmbeddingTightenMuonSelection = True
# With tau embedding input, do the muon selection scan
doTauEmbeddingMuonSelectionScan = False
# Do tau id scan for tau embedding normalisation (no tau embedding input required)
doTauEmbeddingTauSelectionScan = False

# Do trigger parametrisation for MC and tau embedding
doTriggerParametrisation = False
applyTriggerScaleFactor = True

filterGenTaus = False
filterGenTausInaccessible = False

# Re-run trigger matching
doRerunTriggerMatching = False

################################################################################

# Command line arguments (options) and DataVersion object
options, dataVersion = getOptionsDataVersion(dataVersion)

# These are needed for running against tau embedding samples, can be
# given also from command line
#options.doPat=1
#options.tauEmbeddingInput=1

################################################################################
# Define the process
process = cms.Process("HChSignalOptimisation")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(
    #"file:/afs/cern.ch/user/a/attikis/scratch0/CMSSW_4_1_4/src/HiggsAnalysis/HeavyChHiggsToTauNu/test/pattuple_5_1_g68.root"
    #"file:/media/disk/attikis/PATTuples/3683D553-4C4E-E011-9504-E0CB4E19F9A6.root"
    #"rfio:/castor/cern.ch/user/w/wendland/test_pattuplev9_signalM120.root"
    #"file:/media/disk/attikis/PATTuples/v9_1/test_pattuple_v9_JetMet2010A_86.root"
    #"rfio:/castor/cern.ch/user/w/wendland/test_pattuple_v9_qcd120170.root"
    #"rfio:/castor/cern.ch/user/w/wendland/test_JetData_pattuplev9.root"
    # For testing in lxplus
    #       "file:/tmp/kinnunen/pattuple_9_1_KJi.root"
    # dataVersion.getAnalysisDefaultFileCastor()
    # For testing in jade
           dataVersion.getAnalysisDefaultFileMadhatter()
    #dataVersion.getAnalysisDefaultFileMadhatterDcap()
    #      "file:/tmp/kinnunen/pattuple_9_1_KJi.root"
#    "file:/home/wendland/data/pattuple_176_1_ikP.root"
    )
)
if options.tauEmbeddingInput != 0:
    process.source.fileNames = ["/store/group/local/HiggsChToTauNuFullyHadronic/tauembedding/CMSSW_3_9_X/TTJets_TuneZ2_Winter10/TTJets_TuneZ2_7TeV-madgraph-tauola/Winter10_E7TeV_ProbDist_2010Data_BX156_START39_V8_v1_AODSIM_tauembedding_embedding_v6_1/105b277d7ebabf8cba6c221de6c7ed8a/embedded_RECO_29_1_C97.root"]

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string(dataVersion.getGlobalTag())
print "GlobalTag="+dataVersion.getGlobalTag()

process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HChCommon_cfi")

# Uncomment the following in order to print the counters at the end of
# the job (note that if many other modules are being run in the same
# job, their INFO messages are printed too)
#process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")

# Fragment to run PAT on the fly if requested from command line
from HiggsAnalysis.HeavyChHiggsToTauNu.HChPatTuple import addPatOnTheFly
process.commonSequence, additionalCounters = addPatOnTheFly(process, options, dataVersion)


# Re-run trigger matching
if doRerunTriggerMatching:
        import HiggsAnalysis.HeavyChHiggsToTauNu.HChTriggerMatching as TriggerMatching
        process.triggerMatching = TriggerMatching.addTauTriggerMatching(process, options.trigger, "Tau",
             #pathFilterMap={} # by default, use filter name in trigger matching re-running
                                                                        )
        process.commonSequence *= process.triggerMatching
                


# Add configuration information to histograms.root
from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import addConfigInfo
process.infoPath = addConfigInfo(process, options, dataVersion)

# MC Filter
import HiggsAnalysis.HeavyChHiggsToTauNu.tauEmbedding.customisations as tauEmbeddingCustomisations
if filterGenTaus:
        additionalCounters.extend(tauEmbeddingCustomisations.addGeneratorTauFilter(process, process.commonSequence, filterInaccessible=filterGenTausInaccessible))
        
################################################################################
# The "golden" version of the signal analysis

# Primary vertex selection
from HiggsAnalysis.HeavyChHiggsToTauNu.HChPrimaryVertex import addPrimaryVertexSelection
addPrimaryVertexSelection(process, process.commonSequence)

# Import Standard SignalAnalysis Parameters and change accordingly
import HiggsAnalysis.HeavyChHiggsToTauNu.HChSignalAnalysisParameters_cff as param
param.overrideTriggerFromOptions(options)
param.trigger.triggerSrc.setProcessName(dataVersion.getTriggerProcess())

# Set tau selection mode to 'standard'
param.setAllTauSelectionOperatingMode('standard')

# Set tau sources to non-trigger matched tau collections
param.setAllTauSelectionSrcSelectedPatTausTriggerMatched()
#param.setAllTauSelectionSrcSelectedPatTaus()

if options.tauEmbeddingInput != 0:
        tauEmbeddingCustomisations.addMuonIsolationEmbeddingForSignalAnalysis(process, process.commonSequence)
        tauEmbeddingCustomisations.setCaloMetSum(process, process.commonSequence, param, dataVersion)
        tauEmbeddingCustomisations.customiseParamForTauEmbedding(param, dataVersion)
        if tauEmbeddingFinalizeMuonSelection:
            applyIsolation = not doTauEmbeddingMuonSelectionScan
            additionalCounters.extend(tauEmbeddingCustomisations.addFinalMuonSelection(process, process.commonSequence, param,
                                                                                       enableIsolation=applyIsolation))
                                    

# Set the triggers for trigger efficiency parametrisation
#param.trigger.triggerTauSelection = param.tauSelectionHPSVeryLooseTauBased.clone( # VeryLoose
param.trigger.triggerTauSelection = param.tauSelectionHPSTightTauBased.clone( # Tight
  rtauCut = cms.untracked.double(0.0) # No rtau cut for trigger tau
)
param.trigger.triggerMETSelection = param.MET.clone(
  METCut = cms.untracked.double(0.0) # No MET cut for trigger MET
)
if (doTriggerParametrisation and not dataVersion.isData())  or options.tauEmbeddingInput != 0:
    # 2010 and 2011 scenarios
    #param.setEfficiencyTriggersFor2010()
    param.setEfficiencyTriggersFor2011()
    # Settings for the configuration
#    param.trigger.selectionType = cms.untracked.string("byParametrization")                                                                                 

# Trigger with scale factors (at the moment hard coded)
if (applyTriggerScaleFactor and not dataVersion.isData()):
        param.trigger.selectionType = cms.untracked.string("byTriggerBitApplyScaleFactor")


        # Set the data scenario for vertex/pileup weighting
        puweight = "Run2011A"
        if len(options.puWeightEra) > 0:
            puweight = options.puWeightEra
        param.setPileupWeightFor2011(dataVersion, era=puweight) # Reweight by true PU distribution
        param.setDataTriggerEfficiency(dataVersion, era=puweight)


        #param.trigger.selectionType = "disabled"

        if options.tauEmbeddingInput != 0:
                param.trigger.selectionType = cms.untracked.string("disabled")
                param.trigger.triggerEfficiency.selectTriggers = cms.VPSet(cms.PSet(trigger = cms.string("SIMPLE"), luminosity = cms.double(0)))
                param.trigger.triggerEfficiency.parameters = cms.PSet(
                    SIMPLE = cms.PSet(
                    tauPtBins = cms.VPSet(
                    cms.PSet(lowEdge = cms.double(0), efficiency = cms.double(0)),
                    cms.PSet(lowEdge = cms.double(40), efficiency = cms.double(0.2790698)),
                    cms.PSet(lowEdge = cms.double(50), efficiency = cms.double(0.5)),
                    cms.PSet(lowEdge = cms.double(60), efficiency = cms.double(0.5454545)),
                    cms.PSet(lowEdge = cms.double(80), efficiency = cms.double(0.8)),
                    # pre-approval
                    #cms.PSet(lowEdge = cms.double(0), efficiency = cms.double(0)),
                    #cms.PSet(lowEdge = cms.double(40), efficiency = cms.double(0.3293233)),
                    #cms.PSet(lowEdge = cms.double(60), efficiency = cms.double(0.3693694)),
                    #cms.PSet(lowEdge = cms.double(80), efficiency = cms.double(0.25)),
                    #cms.PSet(lowEdge = cms.double(100), efficiency = cms.double(0.3529412)),
                    
                    #cms.PSet(lowEdge = cms.double(40), efficiency = cms.double(0.4210526)),
                    #cms.PSet(lowEdge = cms.double(60), efficiency = cms.double(0.4954955)),
                    #cms.PSet(lowEdge = cms.double(80), efficiency = cms.double(0.4166667)),
                    #cms.PSet(lowEdge = cms.double(100), efficiency = cms.double(0.5294118)),
                    
                    #                cms.PSet(lowEdge = cms.double(40), efficiency = cms.double(0.5)),
                    #                cms.PSet(lowEdge = cms.double(50), efficiency = cms.double(1.0)),
                    #                cms.PSet(lowEdge = cms.double(50), efficiency = cms.double(0.7)),
                    #                cms.PSet(lowEdge = cms.double(60), efficiency = cms.double(1.0)),
                    )
                    )
                    )
                




# Signal analysis module for the "golden analysis"
process.signalOptimisation = cms.EDFilter("HPlusSignalOptimisationProducer",
    trigger = param.trigger,
    primaryVertexSelection = param.primaryVertexSelection,
    GlobalElectronVeto = param.GlobalElectronVeto,
    GlobalMuonVeto = param.GlobalMuonVeto,
    # Change default tau algorithm here as needed         
    tauSelection = param.tauSelectionHPSTightTauBased,
    jetSelection = param.jetSelection,
    MET = param.MET,
    bTagging = param.bTagging,
    fakeMETVeto = param.fakeMETVeto,
    jetTauInvMass = param.jetTauInvMass,                                      
    topSelection = param.topSelection,                                      
    forwardJetVeto = param.forwardJetVeto,
    transverseMassCut = param.transverseMassCut,
    EvtTopology = param.EvtTopology,
    vertexWeight = param.vertexWeight,
    tauEmbedding = param.TauEmbeddingAnalysis,
    GenParticleAnalysis = param.GenParticleAnalysis
)
process.signalOptimisation.tauSelection.rtauCut = cms.untracked.double(0.0) #### tmp to be used for Rtau optimisation

# Prescale fetching done automatically for data
if dataVersion.isData()   and options.tauEmbeddingInput == 0:
    process.load("HiggsAnalysis.HeavyChHiggsToTauNu.HPlusPrescaleWeightProducer_cfi")
    process.hplusPrescaleWeightProducer.prescaleWeightTriggerResults.setProcessName(dataVersion.getTriggerProcess())
    process.hplusPrescaleWeightProducer.prescaleWeightHltPaths = param.trigger.triggers.value()
    process.commonSequence *= process.hplusPrescaleWeightProducer
    process.signalOptimisation.prescaleSource = cms.untracked.InputTag("hplusPrescaleWeightProducer")

# Print output
print "\nVertexWeight:", process.signalOptimisation.vertexWeight
print "\nTrigger:", process.signalOptimisation.trigger
print "\nPV Selection:", process.signalOptimisation.primaryVertexSelection
print "\nTauSelection operating mode:", process.signalOptimisation.tauSelection.operatingMode
print "TauSelection src:", process.signalOptimisation.tauSelection.src
print "TauSelection selection:", process.signalOptimisation.tauSelection.selection
print "TauSelection ptCut:", process.signalOptimisation.tauSelection.ptCut
print "TauSelection etacut:", process.signalOptimisation.tauSelection.etaCut
print "TauSelection leadingTrackPtCut:", process.signalOptimisation.tauSelection.leadingTrackPtCut
print "TauSelection rtauCut:", process.signalOptimisation.tauSelection.rtauCut
print "TauSelection antiRtauCut:", process.signalOptimisation.tauSelection.antiRtauCut
print "TauSelection invMassCut:", process.signalOptimisation.tauSelection.invMassCut
print "TauSelection nprongs:", process.signalOptimisation.tauSelection.nprongs
print "\nMET:", process.signalOptimisation.MET
print "\nGlobalElectronVeto:", process.signalOptimisation.GlobalElectronVeto
print "\nGlobalMuonVeto:", process.signalOptimisation.GlobalMuonVeto
print "\nJetSelection:", process.signalOptimisation.jetSelection
print "\nbTagging: ", process.signalOptimisation.bTagging
print "\nFakeMETVeto:", process.signalOptimisation.fakeMETVeto
print "\nEvtTopology:", process.signalOptimisation.EvtTopology
#print "\nMetTables:", process.signalOptimisation.factorization
print "\nTopSelection:", process.signalOptimisation.topSelection
print "****************************************************"
#print "\nInvMassVetoOnJets:", process.signalOptimisation.InvMassVetoOnJets
print "\nEvtTopology:", process.signalOptimisation.EvtTopology
print "\nForwardJetVeto:", process.signalOptimisation.forwardJetVeto

# Counter analyzer (in order to produce compatible root file with the
# python approach)
process.signalOptimisationCounters = cms.EDAnalyzer("HPlusEventCountAnalyzer",
    counterNames = cms.untracked.InputTag("signalOptimisation", "counterNames"),
    counterInstances = cms.untracked.InputTag("signalOptimisation", "counterInstances"),
    printMainCounter = cms.untracked.bool(True),
    printSubCounters = cms.untracked.bool(False), # Default False
    printAvailableCounters = cms.untracked.bool(False),
)
if len(additionalCounters) > 0:
    process.signalOptimisationCounters.counters = cms.untracked.VInputTag([cms.InputTag(c) for c in additionalCounters])

# PickEvent module and the main Path. The picked events are only the
# ones selected by the golden analysis defined above.
process.load("HiggsAnalysis.HeavyChHiggsToTauNu.PickEventsDumper_cfi")
process.signalOptimisationPath = cms.Path(
    process.commonSequence * # supposed to be empty, unless "doPat=1" command line argument is given
    process.signalOptimisation *
    process.signalOptimisationCounters *
    process.PickEvents
)


# b tagging testing
if doBTagScan:
    from HiggsAnalysis.HeavyChHiggsToTauNu.HChTools import addAnalysis
    module = process.signalOptimisation.clone()
    #module.bTagging.discriminator = "trackCountingHighPurBJetTags"
    module.bTagging.discriminatorCut = 3.0
    addAnalysis(process, "signalOptimisationBtaggingTest", module,
                preSequence=process.commonSequence,
                additionalCounters=additionalCounters,
                signalOptimisationCounters=True)


################################################################################
# The signal analysis with different tau ID algorithms
#
# Run the analysis for the different tau ID algorithms at the same job
# as the golden analysis. It is significantly more efficiency to run
# many analyses in a single job compared to many jobs (this avoids
# some of the I/O and grid overhead). The fragment below creates the
# following histogram directories
# signalOptimisationTauSelectionShrinkingConeCutBased
# signalOptimisationTauSelectionShrinkingConeTaNCBased
# signalOptimisationTauSelectionCaloTauCutBased
# signalOptimisationTauSelectionHPSTightTauBased
# signalOptimisationTauSelectionCombinedHPSTaNCBased
#
# The corresponding Counter directories have "Counters" postfix, and
# cms.Paths "Path" postfix. The paths are run independently of each
# other. It is important to give the process.commonSequence for the
# function, so that it will be run before the analysis module in the
# Path. Then, in case PAT is run on the fly, the framework runs the
# analysis module after PAT (and runs PAT only once).
if doAllTauIds:
    param.addTauIdAnalyses(process, "signalOptimisation", process.signalOptimisation, process.commonSequence, additionalCounters)

################################################################################
# The signal analysis with jet energy scale variation
#
# If the flag is true, create two paths for the variation in plus and
# minus, and clone the signal analysis and counter modules to the
# paths. The tau, jet and MET collections to adjust are taken from the
# configuration of the golden analysis. The fragment below creates the
# following histogram directories
# signalOptimisationJESPlus05
# signalOptimisationJESMinus05
from HiggsAnalysis.HeavyChHiggsToTauNu.JetEnergyScaleVariation import addJESVariationAnalysis
if doJESVariation:
    # In principle here could be more than two JES variation analyses
    JESs = "%02d" % int(JESVariation*100)
    JESe = "%02d" % int(JESEtaVariation*100)
    JESm = "%02d" % int(JESUnclusteredMETVariation*100)
    addJESVariationAnalysis(process, "signalOptimisation", "JESPlus"+JESs+"eta"+JESe+"METPlus"+JESm, process.signalOptimisation, additionalCounters, JESVariation, JESEtaVariation, JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, "signalOptimisation", "JESMinus"+JESs+"eta"+JESe+"METPlus"+JESm, process.signalOptimisation, additionalCounters, -JESVariation, JESEtaVariation, JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, "signalOptimisation", "JESPlus"+JESs+"eta"+JESe+"METMinus"+JESm, process.signalOptimisation, additionalCounters, JESVariation, JESEtaVariation, -JESUnclusteredMETVariation)
    addJESVariationAnalysis(process, "signalOptimisation", "JESMinus"+JESs+"eta"+JESe+"METMinus"+JESm, process.signalOptimisation, additionalCounters, -JESVariation, JESEtaVariation, -JESUnclusteredMETVariation)

# Signal analysis with various tightened muon selections for tau embedding
if options.tauEmbeddingInput != 0 and doTauEmbeddingMuonSelectionScan:
    tauEmbeddingCustomisations.addMuonIsolationAnalyses(process, "signalOptimisation", process.signalOptimisation, process.commonSequence, additionalCounters)

if doTauEmbeddingTauSelectionScan:
    tauEmbeddingCustomisations.addTauAnalyses(process, "signalOptimisation", process.signalOptimisation, process.commonSequence, additionalCounters)

# Print tau discriminators from one tau from one event. Note that if
# the path below is commented, the discriminators are not printed.
process.tauDiscriminatorPrint = cms.EDAnalyzer("HPlusTauDiscriminatorPrintAnalyzer",
    src = process.signalOptimisation.tauSelection.src
)
#process.tauDiscriminatorPrintPath = cms.Path(
#    process.commonSequence *
#    process.tauDiscriminatorPrint
#)

################################################################################

# Define the output module. Note that it is not run if it is not in
# any Path! Hence it is enough to (un)comment the process.outpath
# below to enable/disable the EDM output.
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('output.root'),
    outputCommands = cms.untracked.vstring(
        "keep *_*_*_HChSignalOptimisation",
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

