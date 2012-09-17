#!/usr/bin/env python

import re
from optparse import OptionParser

from HiggsAnalysis.HeavyChHiggsToTauNu.tools.multicrab import *

# Default processing step
#defaultStep = "skim"
#defaultStep = "embedding"
#defaultStep = "analysis"
#defaultStep = "analysisTau"
defaultStep = "signalAnalysis"
#defaultStep = "signalAnalysisGenTau"
#defaultStep = "muonAnalysis"
#defaultStep = "caloMetEfficiency"

# Default era of data to use (meaningful only for signalAnalysis and muonAnalysis)
#defaultEra = "EPS"
#defaultEra = "Run2011A-EPS"
defaultEra = "Run2011A+B"

# Default embedding version(s) to use
defaultVersions = [
# "v13"
# "v13_1"
# "v13_2"
# "v13_2_seedTest1"
# "v13_2_seedTest2"
# "v13_2_seedTest3"
#    "v13_3",
#    "v13_3_seedTest1",
#    "v13_3_seedTest2",
#    "v13_3_seedTest3",
#    "v13_3_seedTest4",
#    "v13_3_seedTest5",
#    "v13_3_seedTest6",
#    "v13_3_seedTest7",
#    "v13_3_seedTest8",
#    "v13_3_seedTest9",
#    "v13_3_seedTest10",
#    "v14"
#    "v44_3_seed0",
    "v44_3_seed1",
#    "v44_3_seed2",
    #"v44_2fix", # for hybrid event production only
    #"v44_2fix_seed1", # for hybrid event production only
    #"v44_2fix_seed2", # for hybrid event production only
]

# Define the processing steps: input dataset, configuration file, output file
config = {"skim":           {"input": "AOD",                           "config": "muonSkim_cfg.py", "output": "skim.root"},
#          "skim_copy":      {"input": "tauembedding_skim_v13",         "config": "copy_cfg.py"}, 
          "embedding":      {"input": "tauembedding_skim_v44_2fix", "config": "embed.py",   "output": "embedded.root"},
          "analysis":       {"input": "tauembedding_embedding_%s",  "config": "embeddingAnalysis_cfg.py"},
          "analysisTau":    {"input": "AOD",                        "config": "tauAnalysis_cfg.py"},
          "signalAnalysis": {"input": "tauembedding_embedding_%s",  "config": "../signalAnalysis_cfg.py"},
          "signalAnalysisGenTau": {"input": "pattuple_v25b",        "config": "../signalAnalysis_cfg.py"},
          "EWKMatching":    {"input": "tauembedding_embedding_%s",  "config": "../EWKMatching_cfg.py"},
          "muonAnalysis":   {"input": "tauembedding_skim_v44_1",          "config": "muonAnalysisFromSkim_cfg.py"},
          "caloMetEfficiency": {"input": "tauembedding_skim_v44_1",         "config": "caloMetEfficiency_cfg.py"},
          }


# "Midfix" for multicrab directory name
dirPrefix = ""
#dirPrefix += "_Met50"
#dirPrefix += "_systematics"

#dirPrefix += "_test"
#dirPrefix += "_debug"

# Define dataset collections
#datasetsData2010 = [
#    "Mu_136035-144114_Apr21", # HLT_Mu9
#    "Mu_146428-147116_Apr21", # HLT_Mu9
#    "Mu_147196-149294_Apr21", # HLT_Mu15_v1
#]
datasetsData2011A = [
    "SingleMu_Mu_160431-163261_2011A_Nov08",  # HLT_Mu20_v1
    "SingleMu_Mu_163270-163869_2011A_Nov08",  # HLT_Mu24_v2
    "SingleMu_Mu_165088-166150_2011A_Nov08", # HLT_Mu30_v3
    "SingleMu_Mu_166161-166164_2011A_Nov08", # HLT_Mu40_v1
    "SingleMu_Mu_166346-166346_2011A_Nov08", # HLT_Mu40_v2
    "SingleMu_Mu_166374-167043_2011A_Nov08", # HLT_Mu40_v1
    "SingleMu_Mu_167078-167913_2011A_Nov08", # HLT_Mu40_v3
    "SingleMu_Mu_170722-172619_2011A_Nov08",  # HLT_Mu40_v5
    "SingleMu_Mu_172620-173198_2011A_Nov08", # HLT_Mu40_v5
    "SingleMu_Mu_173236-173692_2011A_Nov08", # HLT_Mu40_eta2p1_v1
]
datasetsData2011B = [
    "SingleMu_Mu_173693-177452_2011B_Nov19", # HLT_Mu40_eta2p1_v1
    "SingleMu_Mu_177453-178380_2011B_Nov19", # HLT_Mu40_eta2p1_v1
    "SingleMu_Mu_178411-179889_2011B_Nov19", # HLT_Mu40_eta2p1_v4
    "SingleMu_Mu_179942-180371_2011B_Nov19", # HLT_Mu40_eta2p1_v5
]
datasetsData2011 = datasetsData2011A + datasetsData2011B
datasetsMCnoQCD = [
    "TTJets_TuneZ2_Fall11",
    "WJets_TuneZ2_Fall11",
    "DYJetsToLL_M50_TuneZ2_Fall11",
    #"W2Jets_TuneZ2_Fall11",
    #"W3Jets_TuneZ2_Fall11",
    #"W4Jets_TuneZ2_Fall11",
    "T_t-channel_TuneZ2_Fall11",
    "Tbar_t-channel_TuneZ2_Fall11",
    "T_tW-channel_TuneZ2_Fall11",
    "Tbar_tW-channel_TuneZ2_Fall11",
    "T_s-channel_TuneZ2_Fall11",
    "Tbar_s-channel_TuneZ2_Fall11",
    "WW_TuneZ2_Fall11",
    "WZ_TuneZ2_Fall11",
    "ZZ_TuneZ2_Fall11",
]
datasetsMCQCD = [
    "QCD_Pt20_MuEnriched_TuneZ2_Fall11",
]
datasetsSignal = [
    "TTToHplusBWB_M80_Fall11",
    "TTToHplusBWB_M90_Fall11",
    "TTToHplusBWB_M100_Fall11",
    "TTToHplusBWB_M120_Fall11",
    "TTToHplusBWB_M140_Fall11",
    "TTToHplusBWB_M150_Fall11",
    "TTToHplusBWB_M155_Fall11",
    "TTToHplusBWB_M160_Fall11",
    "TTToHplusBHminusB_M80_Fall11",
    "TTToHplusBHminusB_M90_Fall11",
    "TTToHplusBHminusB_M100_Fall11",
    "TTToHplusBHminusB_M120_Fall11",
    "TTToHplusBHminusB_M140_Fall11",
    "TTToHplusBHminusB_M150_Fall11",
    "TTToHplusBHminusB_M155_Fall11",
    "TTToHplusBHminusB_M160_Fall11",
]

datasetsData2011 = []
#datasetsMCnoQCD = []
#datasetsMCQCD = []
datasetsSignal = []
#datasetsData2011 = datasetsData2011B


# Override the default number of jobs
# Goal: ~5 hour jobs
skimNjobs = {
    "WJets_TuneZ2_Fall11": 990, # ~10 hours
    "W2Jets_TuneZ2_Fall11": 490,
    "W3Jets_TuneZ2_Fall11": 490,            
    "W4Jets_TuneZ2_Fall11": 490, 
    "TTJets_TuneZ2_Fall11": 2490,
    "QCD_Pt20_MuEnriched_TuneZ2_Fall11": 490,
    "DYJetsToLL_M50_TuneZ2_Fall11": 990,
    "T_t-channel_TuneZ2_Fall11": 490,
    "Tbar_t-channel_TuneZ2_Fall11": 160,
    "T_tW-channel_TuneZ2_Fall11": 90,
    "Tbar_tW-channel_TuneZ2_Fall11": 90,
    "T_s-channel_TuneZ2_Fall11": 50,
    "Tbar_s-channel_TuneZ2_Fall11": 10,
    "WW_TuneZ2_Fall11": 200,
    "WZ_TuneZ2_Fall11": 200,
    "ZZ_TuneZ2_Fall11": 350,
    }
muonAnalysisNjobs = { # goal: 30k events/job # FIXME these need to be updated
    "SingleMu_Mu_160431-163261_2011A_Nov08": 2, # HLT_Mu20_v1
    "SingleMu_Mu_163270-163869_2011A_Nov08": 3, # HLT_Mu24_v2
    "SingleMu_Mu_165088-166150_2011A_Nov08": 4, # HLT_Mu30_v3
    "SingleMu_Mu_166161-166164_2011A_Nov08": 1, # HLT_Mu40_v1
    "SingleMu_Mu_166346-166346_2011A_Nov08": 1, # HLT_Mu40_v2
    "SingleMu_Mu_166374-167043_2011A_Nov08": 6, # HLT_Mu40_v1
    "SingleMu_Mu_167078-167913_2011A_Nov08": 3, # HLT_Mu40_v3
    "SingleMu_Mu_170722-172619_2011A_Nov08": 6, # HLT_Mu40_v5
    "SingleMu_Mu_172620-173198_2011A_Nov08": 6, # HLT_Mu40_v5
    "SingleMu_Mu_173236-173692_2011A_Nov08": 4, # HLT_Mu40_eta2p1_v1
    "SingleMu_Mu_173693-177452_2011B_Nov19": 16, # HLT_Mu40_eta2p1_v1
    "SingleMu_Mu_177453-178380_2011B_Nov19": 11, # HLT_Mu40_eta2p1_v1
    "SingleMu_Mu_178411-179889_2011B_Nov19": 11, # HLT_Mu40_eta2p1_v4
    "SingleMu_Mu_179942-180371_2011B_Nov19": 2, # HLT_Mu40_eta2p1_v5
    "WJets_TuneZ2_Fall11": 15,
    "TTJets_TuneZ2_Fall11": 50,
    "QCD_Pt20_MuEnriched_TuneZ2_Fall11": 3,
    "DYJetsToLL_M50_TuneZ2_Fall11": 10,
    "T_t-channel_TuneZ2_Fall11": 2,
    "Tbar_t-channel_TuneZ2_Fall11": 2,
    "T_tW-channel_TuneZ2_Fall11": 2,
    "Tbar_tW-channel_TuneZ2_Fall11": 1,
    "T_s-channel_TuneZ2_Fall11": 1,
    "Tbar_s-channel_TuneZ2_Fall11": 1,
    "WW_TuneZ2_Fall11": 4,
    "WZ_TuneZ2_Fall11": 4,
    "ZZ_TuneZ2_Fall11": 4,
    }


def main():
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("--step", dest="step", default=defaultStep,
                      help="Processing step, one of %s (default: %s)" % (", ".join(config.keys()), defaultStep))
    parser.add_option("--version", dest="version", action="append", default=[],
                      help="Data version(s) to use as an input for 'analysis', 'signalAnalysis', or output for 'skim', 'embedding' (default: %s)" % ", ".join(defaultVersions))
    parser.add_option("--era", dest="era", default=defaultEra,
                      help="Data era to use for analysis, signalAnalysis, and muonAnalysis steps (default: %s)" % defaultEra)
    parser.add_option("--midfix", dest="midfix", default=dirPrefix,
                      help="String to add in the middle of the multicrab directory name (default: %s)" % dirPrefix)
    parser.add_option("--configOnly", dest="configOnly", action="store_true", default=False,
                      help="Generate multicrab configurations only, do not create crab jobs (default is to create crab jobs)")

    (opts, args) = parser.parse_args()
    step = opts.step
    versions = opts.version
    if len(versions) == 0:
        versions = defaultVersions

    tmp = "Processing step %s" % step
    if step in ["skim", "embedding", "analysis", "signalAnalysis","EWKMatching"]:
        inputOutput = "input"
        if step in ["skim", "embedding"]:
            inputOutput = "output"
        if step == "skim" and len(versions) > 1:
            raise Exception("There should be no need to run skim with multiple output versions, you specified %d versions" % len(versions))

        tmp += ", embedded versions '%s' as %s" % (", ".join(versions), inputOutput)
        print tmp

        for v in versions:
            print "########################################"
            print
            print " Creating tasks for embedding %s %s" % (inputOutput, v)
            print
            print "########################################"

            createTasks(opts, step, v)
    else:
        print tmp
        createTasks(opts, step)


def createTasks(opts, step, version=None):
    crabcfg = "crab.cfg"
    if step in ["analysis", "analysisTau", "signalAnalysis", "signalAnalysisGenTau", "muonAnalysis", "caloMetEfficiency","EWKMatching"]:
        crabcfg = "../crab_analysis.cfg"

    dirName = opts.midfix
    if step in ["embedding", "analysis", "signalAnalysis", "EWKMatching"]:
        dirName += "_"+version
    if step in ["analysis", "signalAnalysis", "EWKMatching"]:
        dirName += "_"+opts.era.replace("+","")


    multicrab = Multicrab(crabcfg, config[step]["config"], lumiMaskDir="..")


    # Select the datasets based on the processing step and data era
    datasets = []
    if step in ["analysisTau", "signalAnalysisGenTau"]:
        datasets.extend(datasetsMCnoQCD)
    else:
    #    datasets.extend(datasetsData2010)
        if step in ["analysis", "signalAnalysis","EWKMatching"]:
            if opts.era == "Run2011A":
                datasets.extend(datasetsData2011A)
            if opts.era == "Run2011B":
                datasets.extend(datasetsData2011B)
            if opts.era == "Run2011A+B":
                datasets.extend(datasetsData2011)
            else:
                raise Exception("Unsupported era %s" % opts.era)
        else:
            datasets.extend(datasetsData2011)
        datasets.extend(datasetsMCnoQCD)
        datasets.extend(datasetsMCQCD)
    
    if step in ["skim", "embedding", "signalAnalysis","EWKMatching"]:
        datasets.extend(datasetsSignal)

    dataInput = config[step]["input"]
    if step in ["analysis", "signalAnalysis","EWKMatching"]:
        dataInput = dataInput % version

    # Hack for JSON files
    if step in ["signalAnalysis", "analysisTau", "muonAnalysis", "caloMetEfficiency","EWKMatching"]:
        import HiggsAnalysis.HeavyChHiggsToTauNu.tools.multicrabDatasets as multicrabDatasets
        for dataset in datasets:
            if not "SingleMu" in dataset: # is data
                continue
            multicrabDatasets.datasets[dataset]["data"][dataInput]["lumiMask"] = "Nov08ReReco"

    multicrab.extendDatasets(dataInput, datasets)

    multicrab.appendLineAll("GRID.maxtarballsize = 15")
    if step != "skim":
        multicrab.extendBlackWhiteListAll("ce_white_list", ["jade-cms.hip.fi"])


    # Define the processing version number, meaningful for skim/embedding
    path_re = re.compile("_tauembedding_.*")
    tauname = "_tauembedding_%s_%s" % (step, version)

    reco_re = re.compile("^Run[^_]+_(?P<reco>[^_]+_v\d+_[^_]+_)")

    # Let's do the naming like this until we get some answer from crab people
    multicrab.addCommonLine("USER.publish_data_name = Tauembedding_%s_%s" % (step, version))

    # Modification function for skim/embedding steps
    def modify(dataset):
        # Remove skimming of trigger or jets
        for key in dataset.data.keys():
            if key == "skimConfig":
                del dataset.data[key]
            #elif key == "args":
                #arglist = dataset.data[key]
                #for argkey in arglist.keys():
                    #if argkey == "triggerMC":
                        #del arglist[argkey]
        # Proceed
        name = ""
        if dataset.isData() or step != "skim":
            dataset.appendLine("CMSSW.total_number_of_lumis = -1")
        else:
            # split by events can only be used for MC and in skim step
            # embedding step is impossible, because the counters are saved
            # in the lumi sections, and will get doubly counted in split
            # by events mode
            dataset.appendLine("CMSSW.total_number_of_events = -1")
    
        path = dataset.getDatasetPath().split("/")
        if step == "skim":
            name = path[2].replace("-", "_")
            name += "_"+path[3]
            name += tauname
    
            if dataset.isData():
                frun = dataset.getName().split("_")[1].split("-")[0]
                m = reco_re.search(name)
                name = reco_re.sub(m.group("reco")+frun+"_", name)
    
            dataset.useServer(False)
    
            try:
                njobs = skimNjobs[dataset.getName()]
                dataset.setNumberOfJobs(njobs)
    #            if njobs > 490:
    #                dataset.useServer(True)
            except KeyError:
                pass
    
    
        else:
            name = path_re.sub(tauname, path[2])
            name = name.replace("local-", "")
            if step == "embedding_copy":
                name = name.replace("v13_2", "v13_3")
                import HiggsAnalysis.HeavyChHiggsToTauNu.tools.multicrabDatasetsTauEmbedding as tauEmbeddingDatasets
                njobs = tauEmbeddingDatasets.njobs[dataset.getName()]["skim"]
                dataset.setNumberOfJobs(njobs)
            elif step == "skim_copy":
                import HiggsAnalysis.HeavyChHiggsToTauNu.tools.multicrabDatasetsTauEmbedding as tauEmbeddingDatasets
                njobs = tauEmbeddingDatasets.njobs[dataset.getName()]["skim"]
                dataset.setNumberOfJobs(njobs*2)
              
    
        if dataset.isData() and step in ["generation", "embedding"]:
            dataset.appendArg("overrideBeamSpot=1")
    
        dataset.appendLine("USER.publish_data_name = "+name)
        if step == "embedding_copy":
            dataset.appendArg("outputFile=embedded_copy.root")
            dataset.appendLine("CMSSW.output_file = embedded_copy.root")
        elif step == "skim_copy":
            dataset.appendArg("outputFile=skim_copy.root")
            dataset.appendLine("CMSSW.output_file = skim_copy.root")
        else:
            dataset.appendLine("CMSSW.output_file = "+config[step]["output"])
            dataset.appendLine("USER.additional_input_files = copy_cfg.py")
            dataset.appendCopyFile("../copy_cfg.py")
    
    # Modification step for analysis steps
    def modifyAnalysis(dataset):
        if dataset.isMC():
            dataset.appendArg("puWeightEra="+opts.era)
            dataset.appendArg("runOnCrab=1") # Needed for btag scale factor mechanism
        if step in ["signalAnalysis","EWKMatching"]:
            for key in dataset.data.keys():
                if key == "skimConfig":
                    del dataset.data[key]
            dataset.appendArg("tauEmbeddingInput=1")
            dataset.appendArg("doPat=1")
            if dataset.isData():
                for key in dataset.data.keys():
                    if key == "trigger":
                        del dataset.data[key]
                dataset.appendArg("triggerMC=1")
                dataset.appendArg("runOnCrab=1")
#            if dataset.getName() in datasetsData2011_Run2011A_noEPS:
#                dataset.appendArg("tauEmbeddingCaloMet=caloMetSum")
        if step == "signalAnalysisGenTau":
            dataset.appendArg("doTauEmbeddingLikePreselection=1")
    #    if step == "analysisTau":
    #        if dataset.getName() == "WJets":
    #            dataset.setNumberOfJobs(100)
    
    def modifyMuonAnalysis(dataset):
        if dataset.isMC():
            dataset.appendArg("puWeightEra="+opts.era)
        try:
            dataset.setNumberOfJobs(muonAnalysisNjobs[dataset.getName()])
        except KeyError:
            pass
        
    # Apply the modifications
    if step in ["analysis", "analysisTau", "signalAnalysisGenTau", "signalAnalysis", "EWKMatching"]:
        if step != "signalAnalysis":
            multicrab.appendLineAll("CMSSW.output_file = histograms.root")
        multicrab.forEachDataset(modifyAnalysis)
    elif step in ["muonAnalysis", "caloMetEfficiency"]:
        multicrab.appendLineAll("CMSSW.output_file = histograms.root")
        multicrab.forEachDataset(modifyMuonAnalysis)
    else: # skim or embedding
        multicrab.forEachDataset(modify)
    
    multicrab.extendBlackWhiteListAll("se_black_list", defaultSeBlacklist)
    
    # Create the multicrab task
    prefix = "multicrab_"+step+dirName
    
    taskDir = multicrab.createTasks(configOnly=opts.configOnly, prefix=prefix)

    # patch CMSSW.sh
    if not opts.configOnly and step in ["skim", "embedding"]:
        import HiggsAnalysis.HeavyChHiggsToTauNu.tools.crabPatchCMSSWsh as patch
        import os
        os.chdir(taskDir)
        patch.main(Wrapper(dirs=datasets, input={"skim": "skim",
                                             "embedding": "embedded"}[step]))
        os.chdir("..")


# patch CMSSW.sh
class Wrapper:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



if __name__ == "__main__":
    main()
