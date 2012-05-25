## \package LandSTools
# Python interface for running LandS with multicrab
#
# The interface for casual user is provided by the functions
# generateMultiCrab() (for LEP-CLs and LHC-CLs) and
# produceLHCAsymptotic (for LHC-CLs asymptotic).
#
# The multicrab configuration generation saves various parameters to
# taskdir/configuration.json, to be used in by landsMergeHistograms.py
# script. The script uses tools from this module, which write the
# limit results to taskdir/limits.json. I preferred simple text format
# over ROOT files due to the ability to read/modify the result files
# easily. Since the amount of information in the result file is
# relatively small, the performance penalty should be negligible.

import os
import re
import sys
import glob
import stat
import json
import random
import shutil
import subprocess

import multicrab
import git

## The LandS CVS tag to be used
LandS_tag	    = "HEAD" # Recommended by Mingshui 10.5.2012 at 23:23:22 EEST
#LandS_tag           = "V3-04-01_eps" # this one is in the Tapio's scripts
#LandS_tag           = "t3-04-13"

## Common command-line options to LandS
#
# These options are common for all CLs flavours, channels, and mass
# points. At the moment the only such option is the physics model.
commonOptions  = "--PhysicsModel ChargedHiggs"

## Default command-line options for LEP-CLs
lepHybridOptions = "-M Hybrid --bQuickEstimateInitialLimit 0"
## Default number of toys for expected limits for LEP-CLs
lepHybridToys = 50
## Default "Rmin" parameter for LEP-CLs
lepHybridRmin = "0"
## Default "Rmax" parameter for LEP-CLs
lepHybridRmax = "0.09"


## Command-line options with Minos minimizer LHC-CLs (hybrid) (needed for some mass points of combination)
lhcHybridOptionsMinos = "-M Hybrid --freq --scanRs 1 --maximumFunctionCallsInAFit 500000 --minuitSTRATEGY 1"
## Default command-line options for LHC-CLs (hybrid)
lhcHybridOptions = lhcHybridOptionsMinos + "  --PLalgorithm Migrad"
## Default number of toys for CLsb for LHC-CLs (hybrid)
lhcHybridToysCLsb = 300
## Default number of toys for CLb for LHC-CLs (hybrid)
lhcHybridToysCLb = 150
## Default "Rmin" parameter for LHC-CLs (hybrid)
lhcHybridRmin = "0"
## Default "Rmax" parameter for LHC-CLs (hybrid)
lhcHybridRmax = "1"

## Default command line options for LHC-CLs (asymptotic, observed limit)
lhcAsymptoticOptionsObserved = "-M Asymptotic --maximumFunctionCallsInAFit 500000"
## Default command line options for LHC-CLs (asymptotic, expected limit)
lhcAsymptoticOptionsExpected = lhcAsymptoticOptionsObserved + " --PLalgorithm Migrad"
## Default "Rmin" parameter for LHC-CLs (asymptotic)
lhcAsymptoticRmin = "0"
## Default "Rmax" parameter for LHC-CLs (asymptotic)
lhcAsymptoticRmax = "1"

## Default options are LEP-CLs
defaultOptions = lepHybridOptions
## Default number of crab jobs
defaultNumberOfJobs = 20

## Default number of first random number seed in the jobs
defaultFirstSeed = 1000

## List of all mass points
allMassPoints = ["80", "100", "120", "140", "150", "155", "160"]
## Default mass points
defaultMassPoints = ["120"]

## Pattern for tau+jets datacard files (%s denotes the place of the mass)
taujetsDatacardPattern = "lands_datacard_hplushadronic_m%s.txt"
## Pattern for mu+tau datacard files (%s denotes the place of the mass)
mutauDatacardPattern = "datacard_m%s_mutau_miso_20mar12.txt"
## Pattern for e+tau datacard files (%s denotes the place of the mass)
etauDatacardPattern = "datacard_m%s_etau_miso_20mar12.txt"
## Pattern for e+mu datacard files (%s denotes the place of the mass)
emuDatacardPattern = "datacard_m%s_emu_nobtag_20mar12.txt"

## Pattern for tau+jets shape root files (%s denotes the place of the mass)
taujetsRootfilePattern = "lands_histograms_hplushadronic_m%s.root"

## Default list of datacard patterns
defaultDatacardPatterns = [
    taujetsDatacardPattern,
    emuDatacardPattern,
    etauDatacardPattern,
    mutauDatacardPattern
    ]
#defaultDatacardPatterns = [defaultDatacardPatterns[i] for i in [3, 1, 0, 2]] # order in my first crab tests

## Default list of shape root files
defaultRootfilePatterns = [
    taujetsRootfilePattern
]

## Generate multicrab configuration for LEP-CLs or LHC-CLs (hybrid)
#
# \param massPoints         List of mass points to calculate the limit for
#                           (list of strings)
# \param datacardPatterns   List of datacard patterns to include in the
#                           limit calculation (list of strings, each
#                           string should have '%s' to denote the
#                           position of the mass)
# \param rootfilePatterns   List of shape ROOT file patterns to include
#                           in the limit calculation (list of strings,
#                           each string should have '%s' to denote the
#                           position of the mass)
# \param clsType            Object defining the CLs flavour (should be either
#                           LEPType, or LHCType). If None, the default
#                           (LEPType) is used
# \param numberOfJobs       Number of crab jobs. Can be a number, which is
#                           then used for all mass points, or a
#                           dictionary to have mass-specific numbers
#                           of jobs. See ValuePerMass for more
#                           information of the dictionary. If None,
#                           the default value (defaultNumberOfJobs) is
#                           used.
# \param crabScheduler      CRAB scheduler to use (default is arc, if you
#                           want to submit from lxplus, use "glite").
#                           In principle it should be possible to
#                           submit to LSF with a proper scheduler.
# \param crabOptions        Dictionary for specifying additional CRAB
#                           options. The keys correspond to the
#                           sections in crab.cfg. The values are lists
#                           containing lines to be appended to the
#                           section.
# \param postfix            String to be added to the multicrab task directory
#                           name
#
# The CLs-flavour specific options are controlled by the constructors
# of LEPType and LHCType classes.
def generateMultiCrab(massPoints=defaultMassPoints,
                      datacardPatterns=defaultDatacardPatterns,
                      rootfilePatterns=defaultRootfilePatterns,
                      clsType=None,
                      numberOfJobs=None,
                      crabScheduler="arc",
                      crabOptions={},
                      postfix=""
                      ):
    cls = clsType
    if clsType == None:
        cls = LEPType()

    njobs = ValuePerMass(_ifNotNoneElse(numberOfJobs, defaultNumberOfJobs))

    lands = MultiCrabLandS(massPoints, datacardPatterns, rootfilePatterns, cls)
    lands.createMultiCrabDir(postfix)
    lands.copyLandsInputFiles()
    lands.writeLandsScripts()
    lands.writeCrabCfg(crabScheduler, crabOptions)
    lands.writeMultiCrabCfg(njobs)
    lands.printInstruction()

## Run LandS for the LHC-CLs asymptotic limit
#
# \param massPoints         List of mass points to calculate the limit for
#                           (list of strings)
# \param datacardPatterns   List of datacard patterns to include in the
#                           limit calculation (list of strings, each
#                           string should have '%s' to denote the
#                           position of the mass)
# \param rootfilePatterns   List of shape ROOT file patterns to include
#                           in the limit calculation (list of strings,
#                           each string should have '%s' to denote the
#                           position of the mass)
# \param clsType            Object defining the CLs flavour (should be
#                           LHCTypeAsymptotic). If None, the default
#                           (LHCTypeAsymptotic) is used
# \param postfix            String to be added to the multicrab task directory
#                           name
#
# The options of LHCTypeAsymptotic are controlled by the constructor.
def produceLHCAsymptotic(massPoints=defaultMassPoints,
                         datacardPatterns=defaultDatacardPatterns,
                         rootfilePatterns=defaultRootfilePatterns,
                         clsType = None,
                         postfix=""
                         ):

    cls = clsType
    if clsType == None:
        cls = LHCTypeAsymptotic()

    lands = MultiCrabLandS(massPoints, datacardPatterns, rootfilePatterns, cls)
    lands.createMultiCrabDir(postfix)
    lands.copyLandsInputFiles()
    lands.writeLandsScripts()
    lands.runLandSForAsymptotic()


## Class to generate (LEP-CLs, LHC-CLs) multicrab configuration, or run (LHC-CLs asymptotic) LandS
#
# The class is not intended to be used directly by casual user, but
# from generateMultiCrab() and produceLHCAsymptotic()
class MultiCrabLandS:
    ## Constructor
    #
    # \param massPoints         List of mass points to calculate the limit for
    # \param datacardPatterns   List of datacard patterns to include in the
    #                           limit calculation
    # \param rootfilePatterns   List of shape ROOT file patterns to include
    #                           in the limit calculation
    # \param clsType            Object defining the CLs flavour (should be either
    #                           LEPType, or LHCType).
    def __init__(self, massPoints, datacardPatterns, rootfilePatterns, clsType):
        self.exe = findOrInstallLandS()
        self.clsType = clsType.clone()

        self.massPoints = massPoints
        self.datacards = {}
        self.rootfiles = {}
        self.scripts   = []

        # this is a dictionary dumped to configuration.json
        self.configuration = {
            "masspoints": massPoints,
            "datacards": datacardPatterns,
            "rootfiles": rootfilePatterns,
            "landsVersion": LandS_tag,
            "codeVersion": git.getCommitId(),
            "clsType": self.clsType.name(),
        }
        clsConfig = self.clsType.getConfiguration()
        if clsConfig != None:
            self.configuration["clsConfig"] = clsConfig

        for mass in self.massPoints:
            for dc in datacardPatterns:
                fname = dc % mass
                if not os.path.isfile(fname):
                    raise Exception("Datacard file '%s' does not exist!" % fname)

                multicrab._addToDictList(self.datacards, mass, fname)

            for rf in rootfilePatterns:
                fname = rf % mass
                if not os.path.isfile(fname):
                    raise Exception("ROOT file (for shapes) '%s' does not exist!" % fname)

                multicrab._addToDictList(self.rootfiles, mass, fname)

        if len(self.datacards) == 0:
	    print "No LandS datacards found in this directory!"
            print "Mass points:", ", ".join(self.massPoints)
            print "Datacard patterns:", ", ".join(datacardPatterns)
            print "Rootfile patterns:", ", ".join(rootfilePatterns)
	    sys.exit(1)

    ## Create the multicrab task directory
    #
    # \param postfix   Additional string to be included in the directory name
    def createMultiCrabDir(self, postfix):
        prefix = "LandSMultiCrab"
        if len(postfix) > 0:
            prefix += "_"+postfix
	self.dirname = multicrab.createTaskDir(prefix=prefix)
        self.clsType.setDirectory(self.dirname)

    ## Copy input files for LandS (datacards, rootfiles) to the multicrab directory
    def copyLandsInputFiles(self):
        for d in [self.datacards, self.rootfiles]:
            for mass, files in d.iteritems():
                for f in files:
                    shutil.copy(f, self.dirname)
        shutil.copy(self.exe, self.dirname)        

    ## Write LandS shell scripts to the multicrab directory
    def writeLandsScripts(self):
        for mass, datacardFiles in self.datacards.iteritems():
            self.clsType.createScripts(mass, datacardFiles)

    ## Write crab.cfg to the multicrab directory
    # \param crabScheduler      CRAB scheduler to use
    # \param crabOptions        Dictionary for specifying additional CRAB
    #                           options. The keys correspond to the
    #                           sections in crab.cfg. The values are lists
    #                           containing lines to be appended to the
    #                           section.
    def writeCrabCfg(self, crabScheduler, crabOptions):
	filename = os.path.join(self.dirname, "crab.cfg")
	fOUT = open(filename,'w')
	fOUT.write("[CRAB]\n")
        fOUT.write("jobtype                 = cmssw\n")
        fOUT.write("scheduler               = %s\n" % crabScheduler)
        fOUT.write("use_server              = 0\n")
        if "CRAB" in crabOptions:
            for line in crabOptions["CRAB"]:
                fOUT.write(line+"\n")
        fOUT.write("\n")

        fOUT.write("[CMSSW]\n")
        fOUT.write("datasetpath             = none\n")
        fOUT.write("pset                    = none\n")
        fOUT.write("number_of_jobs          = 1\n")
        fOUT.write("output_file             = lands.out\n")
        if "CMSSW" in crabOptions:
            for line in crabOptions["CMSSW"]:
                fOUT.write(line+"\n")
        fOUT.write("\n")

        fOUT.write("[USER]\n")
        fOUT.write("return_data             = 1\n")
        fOUT.write("copy_data               = 0\n")
        if "USER" in crabOptions:
            for line in crabOptions["USER"]:
                fOUT.write(line+"\n")
        fOUT.write("\n")

        if "GRID" in crabOptions:
            fOUT.write("[GRID]\n")
            for line in crabOptions["GRID"]:
                fOUT.write(line+"\n")
            fOUT.write("\n")

	fOUT.close()

    ## Write multicrab.cfg to the multicrab directory
    #
    # \param numberOfJobs   ValuePerMass object holding the information
    #                       of number of crab jobs (per mass point)
    def writeMultiCrabCfg(self, numberOfJobs):
	filename = os.path.join(self.dirname, "multicrab.cfg")
        fOUT = open(filename,'w')
        fOUT.write("[COMMON]\n")
        fOUT.write("CRAB.use_server              = 0\n")
	fOUT.write("CMSSW.datasetpath            = none\n")
	fOUT.write("CMSSW.pset                   = none\n")
        fOUT.write("\n")

        exe = self.exe.split("/")[-1]
        for mass in self.massPoints:
            inputFiles = [exe]+self.datacards[mass]
            if len(self.rootfiles) > 0:
                inputFiles += self.rootfiles[mass]
            self.clsType.writeMultiCrabConfig(fOUT, mass, inputFiles, numberOfJobs.getValue(mass))
            fOUT.write("\n\n")

        f = open(os.path.join(self.dirname, "configuration.json"), "wb")
        json.dump(self.configuration, f, sort_keys=True, indent=2)
        f.close()

    def printInstruction(self):
	print "Multicrab cfg created. Type"
        print "cd",self.dirname,"&& multicrab -create"


    ## Run LandS for the asymptotic limit
    #
    # This is so fast at the moment that using crab jobs for that
    # would be waste of resources and everybodys time.
    def runLandSForAsymptotic(self):
        print "Running LandS for asymptotic limits, saving results to %s" % self.dirname
        f = open(os.path.join(self.dirname, "configuration.json"), "wb")
        json.dump(self.configuration, f, sort_keys=True, indent=2)
        f.close()

        results = ResultContainer(self.dirname)
        for mass in self.massPoints:
            results.append(self.clsType.runLandS(mass))
            print "Processed mass point %s" % mass
        print

        results.print2()
        fname = results.saveJson()
        print "Wrote results to %s" % fname

## Helper class to manage mass-specific configuration values
class ValuePerMass:
    ## Constructor
    #
    # \param dictionary   Input dictionary/ValuePerMass object/value
    #
    # If dictionary is dictionary, it must have a "default" key, and
    # it may have more than or equal to zero keys for the mass points.
    # The value of the "default" key is used as the default value for
    # those mass points for which the specific value is not given.
    #
    # If the dictionary is ValuePerMass object, the default and
    # per-mass values are copied from it.
    #
    # If the dictionary is something else, it is used as the default
    # value for all masses
    def __init__(self, dictionary):
        self.values = {}
        if isinstance(dictionary, dict):
            self.values.update(dictionary)
            self.default = self.values["default"]
            del self.values["default"]
        elif isinstance(dictionary, ValuePerMass):
            self.values.update(dictionary.values)
            self.default = dictionary.default
        else:
            self.default = dictionary

    ## Apply a function for all values
    #
    # \param function   Function taking one parameter (the value), the
    #                   return value is not used
    #
    # This allows sanity checks to be performed on the values.
    def forEachValue(self, function):
        function(self.default)
        for value in self.values.values():
            function(value)

    ## Get the value for a given mass point
    def getValue(self, mass):
        return self.values.get(mass, self.default)

    ## Serialize the object to a dictionary
    #
    # Another ValuePerMass can be constructed from the dictionary. The
    # dictionary can be written to a JSON file, allowing the
    # ValuePerMass to be constructed from other scripts.
    def serialize(self):
        ret = {"default": self.default}
        ret.update(self.values)
        return ret

## Definition of the LEP-type CLs (with hybrid treatment of nuisance parameters)
#
# The method itself is described in the CMS-NOTE-2011-005 appendix A.1.2
#
# Calculating limits involves one job for observed limit and N jobs
# for the expected limits for one mass point. A crab task is created
# for both (separately). For the expected limits, the output root
# files are merged, and then LandS is ran one time for the merged root
# file. This is taken care of with the \a landsMergeHistograms.py
# script.
class LEPType:
    ## Constructor
    #
    # \param options     Command line options for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lepHybridOptions)
    # \param toysPerJob  Number of toys per job for expected limits
    #                    (\a -t parameter). Number, dictionary (see
    #                    ValuePerMass), or None for default
    #                    (lepHybridToys)
    # \param firstSeed   First random number seed for the jobs (actually
    #                    first seed is firstSeed+1).
    # \param rMin        The \a --initialRmin parameter for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lepHybridRmin)
    # \param rMax        The \a --initialRmax parameter for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lepHybridRmax)
    #
    # Note: if you add any parameters to the constructor, add the
    # parameters to the clone() method correspondingly.
    def __init__(self, options=None, toysPerJob=None, firstSeed=defaultFirstSeed, rMin=None, rMax=None):
        self.options = ValuePerMass(_ifNotNoneElse(options, lepHybridOptions))
        self.firstSeed = firstSeed
        self.toysPerJob = ValuePerMass(_ifNotNoneElse(toysPerJob, lepHybridToys))
        self.rMin = ValuePerMass(_ifNotNoneElse(rMin, lepHybridRmin))
        self.rMax = ValuePerMass(_ifNotNoneElse(rMax, lepHybridRmax))

        self.expScripts = {}
        self.obsScripts = {}

    ## Return the name of the CLs flavour (for serialization to configuration.json)
    def name(self):
        return "LEP"

    ## Get the configuration dictionary for serialization.
    #
    # LEP-type CLs does not need any specific information to be stored
    def getConfiguration(self):
        return None

    ## Clone the object, possibly overriding some options
    #
    # \param kwargs   Keyword arguments, can be any of the arguments of
    #                 __init__(), with the same meaning.
    def clone(self, **kwargs):
        args = _updateArgs(kwargs, self, ["options", "toysPerJob", "firstSeed", "rMin", "rMax"])
        return LEPType(**args)

    ## Set the multicrab directory path
    #
    # \param dirname   Path to the multicrab directory
    def setDirectory(self, dirname):
        self.dirname = dirname

    ## Create the job scripts for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def createScripts(self, mass, datacardFiles):
        self._createObs(mass, datacardFiles)
        self._createExp(mass, datacardFiles)

    ## Create the observed job script for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def _createObs(self, mass, datacardFiles):
        fileName = "runLandS_Observed_m" + mass
        opts = commonOptions + " " + self.options.getValue(mass) + " --initialRmin %s --initialRmax %s" % (self.rMin.getValue(mass), self.rMax.getValue(mass))
        command = [
            "#!/bin/sh",
            "",
            "SEED=$(expr %d + $1)" % self.firstSeed,
            'echo "LandSSeed=$SEED"',
            "",
            "./lands.exe %s --seed $SEED -d %s | tail -5 > lands.out" % (opts, " ".join(datacardFiles)),
            ""
            "cat lands.out"
            ]
        _writeScript(os.path.join(self.dirname, fileName), "\n".join(command)+"\n")
        self.obsScripts[mass] = fileName

    ## Create the expected job script for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def _createExp(self, mass, datacardFiles):
        fileName = "runLandS_Expected_m" + mass
        opts = commonOptions + " " + self.options.getValue(mass) + " --initialRmin %s --initialRmax %s" % (self.rMin.getValue(mass), self.rMax.getValue(mass))
        command = [
            "#!/bin/sh",
            "",
            "SEED=$(expr %d + $1)" % self.firstSeed,
            'echo "LandSSeed=$SEED"',
            "",
            "./lands.exe %s -n split_m%s --doExpectation 1 -t %s --seed $SEED -d %s | tail -5 > lands.out" % (opts, mass, self.toysPerJob, " ".join(datacardFiles)),
            "",
            "cat lands.out",
            ]
        _writeScript(os.path.join(self.dirname, fileName), "\n".join(command)+"\n")
        self.expScripts[mass] = fileName

    ## Write the multicrab configuration snippet of a single mass point
    #
    # \param output      Output stream to write the contents
    # \param mass        String for the mass point
    # \param inputFiles  List of strings for the (additional) input files to pack in the crab job
    # \param numJobs     Number of jobs for the expected task
    def writeMultiCrabConfig(self, output, mass, inputFiles, numJobs):
        output.write("[Observed_m%s]\n" % mass)
        output.write("USER.script_exe = %s\n" % self.obsScripts[mass])
        output.write("USER.additional_input_files = %s\n" % ",".join(inputFiles))
        output.write("CMSSW.number_of_jobs = 1\n")
        output.write("CMSSW.output_file = lands.out\n")
        output.write("\n")

        output.write("[Expected_m%s]\n" % mass)
        output.write("USER.script_exe = %s\n" % self.expScripts[mass])
        output.write("USER.additional_input_files = %s\n" % ",".join(inputFiles))
        output.write("CMSSW.number_of_jobs = %d\n" % numJobs)
        output.write("CMSSW.output_file = lands.out,split_m%sHybrid_limitbands.root,split_m%sHybrid_limits_tree.root\n" % (mass, mass))

    ## Construct the Result object for a single mass point
    #
    # \param path       Path to the multicrab directory
    # \param mass       String for the mass point
    # \param clsConfig  Dictionary of the CLs-flavour-specific
    #                   configuration (stored in configuration.json).
    #                   Not used by LEPType, but needed for consistent
    #                   interface
    #
    # \return Result object containing the limits for the mass point
    def getResult(self, path, mass, clsConfig):
        result = Result(mass)
        self._parseObserved(result, path, mass)
        self._parseExpected(result, path, mass)
        return result

    ## Read the observed limit and insert to the Result
    #
    # \param result  Result object to modify
    # \param path    Path to the multicrab directory
    # \param mass    String for the mass point
    #
    # Reads the result from the lands.out file (which is fine since
    # there is only one job for observed limit)
    def _parseObserved(self, result, path, mass):
        landsOutFiles = glob.glob(os.path.join(path, "Observed_m%s"%mass, "res", "lands_*.out"))
        if len(landsOutFiles) == 0:
            return
        if len(landsOutFiles) != 1:
            raise Exception("Expected exactly 1 LandS output file, got %d" % len(landsOutFiles))

        result_re = re.compile("= (?P<value>\d+\.\d+)\s+\+/-\s+(?P<error>\d+\.\S+)")
        f = open(landsOutFiles[0])
        for line in f:
            match = result_re.search(line)
            if match:
                result.observed = match.group("value")
                result.observedError =match.group("error")
                f.close()
                return
        raise Exception("Unable to parse observed result from '%s'" % landsOutFiles[0])

    ## Read the expected limits and insert to the Result
    #
    # \param result  Result object to modify
    # \param path    Path to the multicrab directory
    # \param mass    String for the mass point
    #
    # Runds LandS for the merged root file, and reads the expected
    # limits (median, +-1/2sigma) from the output. LandS is run only
    # if the merged output file does not exist
    def _parseExpected(self, result, path, mass):
        mergedFilename = "lands_merged.out"
        crabRes = os.path.join(path, "Expected_m%s"%mass, "res")
        fileExists = self._runLandSForMerge(crabRes, mergedFilename, mass)
        if not fileExists:
            return

        fname = os.path.join(crabRes, mergedFilename)
        f = open(fname)
        result_re = re.compile("BANDS\s+(?P<minus2>\d+\.\d+)\s+(?P<minus1>\d+\.\d+)\s+(?P<mean>\d+\.\d+)\s+(?P<plus1>\d+\.\d+)\s+(?P<plus2>\d+\.\d+)\s+(?P<median>\d+\.\d+)")
        for line in f:
            match = result_re.search(line)
            if match:
		result.expected = match.group("median")
		result.expectedPlus1Sigma  = match.group("plus1")
		result.expectedPlus2Sigma  = match.group("plus2")
		result.expectedMinus1Sigma = match.group("minus1")
		result.expectedMinus2Sigma = match.group("minus2")
                f.close()
                return

        raise Exception("Unable to parse expected result from '%s'" % fname)

    ## Run LandS for the merged root file
    #
    # \param resDir           Path to the \a res directory of the crab task
    # \param mergedfilename   Name of the merged root file in the \a resDir
    # \param mass             String for the mass point
    #
    # \return True, if the result file exists (either before or after
    #         the merge), False, if LandS failed for any reason
    def _runLandSForMerge(self, resDir, mergedFilename, mass):
        targetFile = os.path.join(resDir, mergedFilename)
        if os.path.exists(targetFile):
            return True

        exe = findOrInstallLandS()
        rootFile = os.path.join(resDir, "histograms-Expected_m%s.root" % mass)
        if not os.path.exists(rootFile):
            print "Merged root file '%s' does not exist, did you run landsMergeHistograms.py?" % rootFile
            return False

        cmd = [exe, "--doExpectation", "1", "--readLimitsFromFile", rootFile]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        if p.returncode != 1:
            raise Exception("Call to '%s' failed with exit code %d" % (" ".join(cmd), p.returncode))
        f = open(targetFile, "w")
        f.write(output)
        f.write("\n")
        f.close()
        return True

## Definition of the LHC-type CLs (with the frequentist treatment of nuisance parameters)
#
# The method itself is described in the CMS-NOTE-2011-005 section 2.
#
# In this case the crab jobs are needed only for the toy MC for the
# sampling distributions of the test statistic. This toy MC is reused
# for the expected limits. Consequence is that a single crab task of N
# jobs gives the information for both the observed and the expected
# limits. Again the root files must be merged, and this time a root
# macro is run (instead of LandS) to produce the limits. This is taken
# care of with the \a landsMergeHistograms.py script.
class LHCType:
    ## Constructor
    #
    # \param options     Command line options for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lhcHybridOptions)
    # \param toysCLsb    Number of toys per job for CLsb (\a
    #                    --nToysForCLsb parameter). Number, dictionary
    #                    (see ValuePerMass), or None for default
    #                    (lhcHybridToysCLsb)
    # \param toysCLb     Number of toys per job for CLb (\a
    #                    --nToysForCLb parameter). Number, dictionary
    #                    (see ValuePerMass), or None for default
    #                    (lhcHybridToysCLb)
    # \param firstSeed   First random number seed for the jobs (actually
    #                    first seed is firstSeed+1).
    # \param vR          The \a -vR parameter for LandS. Pair of strings,
    #                    dictionary (see ValuePerMass), or None for
    #                    not to add \a -vR parameter.
    # \param rMin        The \a --rMin parameter for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lhcHybridRmin)
    # \param rMax        The \a --rMax parameter for LandS. String,
    #                    dictionary (see ValuePerMass), or None for
    #                    default (lhcHybridRmax)
    # \param scanRmin The \a scanRmin parameter for \a fitRvsCLs.C
    #                    macro. String, dictionary (see ValuePerMass),
    #                    or None for not to add the \a scanRmin
    #                    parameter.
    # \param scanRmax    The \a scanRmax parameter for \a fitRvsCLs.C
    #                    macro. String, dictionary (see ValuePerMass),
    #                    or None for not to add the \a scanRmin
    #                    parameter.
    #
    # Note: if you add any parameters to the constructor, add the
    # parameters to the clone() method correspondingly.
    #
    # The \a scanRmin and \a scanRmax parameters are saved to the \a
    # configuration.json file, and can be overridden by editing the
    # file between the multicrab configuration generation and the call
    # to \a landsMergeHistograms.py.
    def __init__(self, options=None, toysCLsb=None, toysCLb=None, firstSeed=defaultFirstSeed, vR=None, rMin=None, rMax=None, scanRmin=None, scanRmax=None):
        self.options = ValuePerMass(_ifNotNoneElse(options, lhcHybridOptions))

        self.firstSeed = firstSeed

        self.toysCLsb = ValuePerMass(_ifNotNoneElse(toysCLsb, lhcHybridToysCLsb))
        self.toysCLb = ValuePerMass(_ifNotNoneElse(toysCLb, lhcHybridToysCLb))

        def assertvR(value):
            if value != None and len(value) != 2:
                raise Exception("vR should be pair (min, max), got length %d: %s" % (len(value), str(value)))
        self.vR = ValuePerMass(vR)
        self.vR.forEachValue(assertvR)

        self.rMin = ValuePerMass(_ifNotNoneElse(rMin, lhcHybridRmin))
        self.rMax = ValuePerMass(_ifNotNoneElse(rMax, lhcHybridRmax))

        self.scanRmin = ValuePerMass(scanRmin)
        self.scanRmax = ValuePerMass(scanRmax)
        self.configuration = {}
        self.configuration["scanRmin"] = self.scanRmin.serialize()
        self.configuration["scanRmax"] = self.scanRmax.serialize()

        self.scripts = {}

    ## Return the name of the CLs flavour (for serialization to configuration.json)
    def name(self):
        return "LHC"

    ## Get the configuration dictionary for serialization.
    #
    # For LHC-type CLs the \ə scanRmin and \a scanRmax are stored
    def getConfiguration(self):
        return self.configuration

    ## Clone the object, possibly overriding some options
    #
    # \param kwargs   Keyword arguments, can be any of the arguments of
    #                 __init__(), with the same meaning.
    def clone(self, **kwargs):
        args = _updateArgs(kwargs, self, ["options", "toysCLsb", "toysCLb", "firstSeed", "vR", "rMin", "rMax", "scanRmin", "scanRmax"])
        return LHCType(**args)

    ## Set the multicrab directory path
    #
    # \param dirname   Path to the multicrab directory
    def setDirectory(self, dirname):
        self.dirname = dirname

    ## Create the job script for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def createScripts(self, mass, datacardFiles):
        filename = "runLandS_m%s" % mass
        opts = commonOptions + " " + self.options.getValue(mass) + " --rMin %s --rMax %s" % (self.rMin.getValue(mass), self.rMax.getValue(mass))
        vR = self.vR.getValue(mass)
        if vR == None:
            opts += " --ExpectationHints Asymptotic"
        else:
            opts += " -vR [%s,%s,x1.05]" % vR
        command = [
            "#!/bin/sh",
            "",
            "SEED=$(expr %d + $1)" % self.firstSeed,
            'echo "LandSSeed=$SEED"',
            "",
            "./lands.exe %s -n split_m%s --nToysForCLsb %d --nToysForCLb %d --seed $SEED -d %s | tee lands.out.tmp" % (opts, mass, self.toysCLsb.getValue(mass), self.toysCLb.getValue(mass), " ".join(datacardFiles)),
            "head -n 50 lands.out.tmp> lands.out",
            "tail -n 5 lands.out.tmp >> lands.out",
            "cat lands.out"
            ]

        _writeScript(os.path.join(self.dirname, filename), "\n".join(command)+"\n")
        self.scripts[mass] = filename

    ## Write the multicrab configuration snippet of a single mass point
    #
    # \param output      Output stream to write the contents
    # \param mass        String for the mass point
    # \param inputFiles  List of strings for the (additional) input files to pack in the crab job
    # \param numJobs     Number of jobs for the expected task
    def writeMultiCrabConfig(self, output, mass, inputFiles, numJobs):
        output.write("[Limit_m%s]\n" % mass)
        output.write("USER.script_exe = %s\n" % self.scripts[mass])
        output.write("USER.additional_input_files = %s\n" % ",".join(inputFiles))
        output.write("CMSSW.number_of_jobs = %d\n" % numJobs)
        output.write("CMSSW.output_file = lands.out,split_m%s_m2lnQ.root\n" % mass)

    ## Construct the Result object for a single mass point
    #
    # \param path       Path to the multicrab directory
    # \param mass       String for the mass point
    # \param clsConfig  Dictionary of the CLs-flavour-specific
    #                   configuration (stored in configuration.json).
    #
    # \return Result object containing the limits for the mass point
    #
    # Runs the \a fitRvsCLs.C macro for the merged root file, and
    # reads the observed and expected limits from the output. The
    # script output is also stored in a text file for later referecence.
    def getResult(self, path, mass, clsConfig):
        result = Result(mass)

        rootFile = os.path.join(path, "Limit_m%s"%mass, "res", "histograms-Limit_m%s.root"%mass)
        if not os.path.exists(rootFile):
            print "Merged root file '%s' does not exist, did you run landsMergeHistograms.py?" % rootFile
            return result

        fitScript = os.path.join(findOrInstallLandS(directory=True), "test", "fitRvsCLs.C")
        if not os.path.exists(fitScript):
            raise Exception("Did not find fit script '%s'" % fitScript)
        rootCommand = ["root", "-l", "-n", "-b", fitScript+"+"]
        p = subprocess.Popen(rootCommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        commands = []

        if clsConfig != None and "scanRmin" in clsConfig:
            scanRmin = ValuePerMass(clsConfig["scanRmin"])
            val = scanRmin.getValue(mass)
            if val != None:
                commands.append("scanRmin = %s" % val)
        if clsConfig != None and "scanRmax" in clsConfig:
            scanRmax = ValuePerMass(clsConfig["scanRmax"])
            val = scanRmax.getValue(mass)
            if val != None:
                commands.append("scanRmax = %s" % val)
        commands.extend([
            'run("%s", "plot_m%s")' % (rootFile, mass),
#            'run("%s", "plot_m%s", "bands", -1, 1)' % (rootFile, mass), # for debug output of the script
            ".q"
            ])
        output = p.communicate("\n".join(commands)+"\n")[0]
#        print output
        f = open(os.path.join(path, "fitRvsCLs_m%s_output.txt"%mass), "w")
        f.write(" ".join(rootCommand)+"\n\n")
        f.write("\n".join(commands)+"\n\n")
        f.write(output)
        f.write("\n")
        f.close()

        lines = output.split("\n")
        lines.reverse()
        def res(s):
            return "(?P<%s>[^+]+)\+/-(?P<%se>[^,]+)" % (s, s)
        result_re = re.compile("EXPECTED LIMIT BANDS.+mass=[^:]+:\s*" + res("obs") + ",\s+" +
                               res("m2s") + ",\s+" + res("m1s") + ",\s+" + res("med") + ",\s+" + res("p1s") + ",\s+" + res("p2s"))
        for line in lines:
            match = result_re.search(line)
            if match:
                result.observed = match.group("obs")
                result.observedError = match.group("obse")
                result.expected = match.group("med")
                result.expectedError = match.group("mede")
                result.expectedPlus1Sigma = match.group("p1s")
                result.expectedPlus1SigmaError = match.group("p1se")
                result.expectedPlus2Sigma = match.group("p2s")
                result.expectedPlus2SigmaError = match.group("p2se")
                result.expectedMinus1Sigma = match.group("m1s")
                result.expectedMinus1SigmaError = match.group("m1se")
                result.expectedMinus2Sigma = match.group("m2s")
                result.expectedMinus2SigmaError = match.group("m2se")

        return result

## Definition of the LHC-type CLs (with the asymptotic treatment of nuisance parameters)
#
# The method itself is described in the CMS-NOTE-2011-005 appendix A.1.3.
#
# At the moment running the asymptotic limit is so fast that running
# it via crab would be waste of time and resources from everybodys
# point of view. Instead, the LandS is run at the "multicrab
# configuration generation" stage. To have similar usage to the other
# CLs flavours, the results are stored in a multicrab task directory.
#
# Because no crab is involved, the user interface is different. This
# is achieved with the produceLHCAsymptotic() function instead of the
# generateMultiCrab().
class LHCTypeAsymptotic:
    ## Constructor
    #
    # \param optionsObserved  Command line options for LandS for the
    #                         observed limit. String, dictionary (see
    #                         ValuePerMass), or None for default
    #                         (lhcAsymptoticOptionsObserved)
    # \param optionsExpected  Command line options for LandS for the
    #                         expected limit. String, dictionary (see
    #                         ValuePerMass), or None for default
    #                         (lhcAsymptoticOptionsExpected)
    # \param rMin             The \a --rMin parameter for LandS. String,
    #                         dictionary (see ValuePerMass), or None for
    #                         default (lhcAsymptoticRmin)
    # \param rMax             The \a --rMax parameter for LandS. String,
    #                         dictionary (see ValuePerMass), or None for
    #                         default (lhcAsymptoticRmax)
    # \param vR               The \a -vR parameter for LandS. Pair of strings,
    #                         dictionary (see ValuePerMass), or None for
    #                         not to add \a -vR parameter.
    #
    # Note: if you add any parameters to the constructor, add the
    # parameters to the clone() method correspondingly.
    def __init__(self, optionsObserved=None, optionsExpected=None, rMin=None, rMax=None, vR=None):
        self.optionsObserved = ValuePerMass(_ifNotNoneElse(optionsObserved, lhcAsymptoticOptionsObserved))
        self.optionsExpected = ValuePerMass(_ifNotNoneElse(optionsExpected, lhcAsymptoticOptionsExpected))
        self.rMin = ValuePerMass(_ifNotNoneElse(rMin, lhcAsymptoticRmin))
        self.rMax = ValuePerMass(_ifNotNoneElse(rMax, lhcAsymptoticRmax))

        def assertvR(value):
            if value != None and len(value) != 2:
                raise Exception("vR should be pair (min, max), got length %d: %s" % (len(value), str(value)))
        self.vR = ValuePerMass(vR)
        self.vR.forEachValue(assertvR)

        self.obsScripts = {}
        self.expScripts = {}

    ## Return the name of the CLs flavour (for serialization to configuration.json)
    def name(self):
        return "LHCAsymptotic"

    ## Get the configuration dictionary for serialization.
    #
    # LHC-type asymptotic CLs does not need any specific information to be stored
    def getConfiguration(self):
        return None

    ## Clone the object, possibly overriding some options
    #
    # \param kwargs   Keyword arguments, can be any of the arguments of
    #                 __init__(), with the same meaning.
    def clone(self, **kwargs):
        args = _updateArgs(kwargs, self, ["optionsObserved", "optionsExpected", "rMin", "rMax", "vR"])
        return LHCTypeAsymptotic(**args)

    ## Set the multicrab directory path
    #
    # \param dirname   Path to the multicrab directory
    def setDirectory(self, dirname):
        self.dirname = dirname

    ## Create the job scripts for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def createScripts(self, mass, datacardFiles):
        self._createObs(mass, datacardFiles)
        self._createExp(mass, datacardFiles)

    ## Create the observed job script for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def _createObs(self, mass, datacardFiles):
        fileName = "runLandS_Observed_m" + mass
        opts = commonOptions + " " + self.optionsObserved.getValue(mass) + " --rMin %s --rMax %s" % (self.rMin.getValue(mass), self.rMax.getValue(mass))
        vR = self.vR.getValue(mass)
        if vR != None:
            opts += " -vR [%s,%s,x1.05]" % vR

        command = [
            "#!/bin/sh",
            "",
            "./lands.exe %s --minuitSTRATEGY 1 -n obs_m%s -d %s" % (opts, mass, " ".join(datacardFiles)),
            ]
        _writeScript(os.path.join(self.dirname, fileName), "\n".join(command)+"\n")
        self.obsScripts[mass] = fileName

    ## Create the expected job script for a single mass point
    #
    # \param mass            String for the mass point
    # \param datacardFiles   List of strings for datacard file names of the mass point
    def _createExp(self, mass, datacardFiles):
        fileName = "runLandS_Expected_m" + mass
        opts = commonOptions + " " + self.optionsExpected.getValue(mass) + " --rMin %s --rMax %s" % (self.rMin.getValue(mass), self.rMax.getValue(mass))
        vR = self.vR.getValue(mass)
        if vR != None:
            opts += " -vR [%s,%s,x1.05]" % vR

        command = [
            "#!/bin/sh",
            "",
            "./lands.exe %s --minuitSTRATEGY 2 -n exp_m%s -D asimov_b -d %s" % (opts, mass, " ".join(datacardFiles)),
            ]
        _writeScript(os.path.join(self.dirname, fileName), "\n".join(command)+"\n")
        self.expScripts[mass] = fileName

    ## Run LandS for the observed and expected limits for a single mass point
    #
    # \param mass   String for the mass point
    #
    # \return Result object containing the limits for the mass point
    def runLandS(self, mass):
        result = Result(mass)
        self._runObserved(result, mass)
        self._runExpected(result, mass)
        return result

    ## Helper method to run a script
    #
    # \param script      Path to the script to run
    # \param outputfile  Path to a file to store the script output
    #
    # \ŗeturn The output of the script as a string
    def _run(self, script, outputfile):
        exe = findOrInstallLandS()
        pwd = os.getcwd()
        os.chdir(self.dirname)

        p = subprocess.Popen(["./"+script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()[0]
        if p.returncode != 0:
            print output
            raise Exception("LandS failed with exit code %d\nCommand: %s" % (p.returncode, script))
        os.chdir(pwd)

        f = open(os.path.join(self.dirname, outputfile), "w")
        f.write(output)
        f.write("\n")
        f.close()

        return output

    ## Run LandS for the observed limit
    #
    # \param result  Result object to modify
    # \param mass    String for the mass point
    def _runObserved(self, result, mass):
        script = self.obsScripts[mass]
        output = self._run(script, "obs_m%s_output.txt"%mass)

        result_re = re.compile("Observed Upper Limit .* =\s*(?P<value>\d+\.\d+)")
        lines = output.split("\n")
        lines.reverse()
        for line in lines:
            match = result_re.search(line)
            if match:
                result.observed = match.group("value")
                return result

        print output
        raise Exception("Unable to parse the output of command '%s'" % script)

    ## Run LandS for the expected limit
    #
    # \param result  Result object to modify
    # \param mass    String for the mass point
    def _runExpected(self, result, mass):
        script = self.expScripts[mass]
        output = self._run(script, "exp_m%s_output.txt"%mass)

        result_re = re.compile("BANDS\s+(?P<minus2>\d+\.\d+)\s+(?P<minus1>\d+\.\d+)\s+(?P<mean>\d+\.\d+)\s+(?P<plus1>\d+\.\d+)\s+(?P<plus2>\d+\.\d+)\s+(?P<median>\d+\.\d+)")
        lines = output.split("\n")
        lines.reverse()
        for line in lines:
            match = result_re.search(line)
            if match:
		result.expected = match.group("median")
		result.expectedPlus1Sigma  = match.group("plus1")
		result.expectedPlus2Sigma  = match.group("plus2")
		result.expectedMinus1Sigma = match.group("minus1")
		result.expectedMinus2Sigma = match.group("minus2")
                return result

        print output
        raise Exception("Unable to parse the output of command '%s'" % script)

## Class to hold the limit results
#
# \todo This class could be simplified if we can get rid of \a
# mkBrLimits.py script.
class Result:
    ## Constructor
    def __init__(self, mass = None, observed = None, expected = None, expectedPlus1Sigma = None, expectedPlus2Sigma = None, expectedMinus1Sigma = None, expectedMinus2Sigma = None):
        self.mass                = mass
        self.observed            = observed
        self.expected            = expected
        self.expectedPlus1Sigma  = expectedPlus1Sigma
        self.expectedPlus2Sigma  = expectedPlus2Sigma
        self.expectedMinus1Sigma = expectedMinus1Sigma
        self.expectedMinus2Sigma = expectedMinus2Sigma

    ## Convert the string values to floating point
    #
    # \todo Could be removed
    def toFloat(self):
        for attr in ["mass", "observed", "expected", "expectedPlus1Sigma", "expectedPlus2Sigma", "expectedMinus1Sigma", "expectedMinus2Sigma"]:
            setattr(self, attr, float(getattr(self, attr)))

    ## Check if the result is empty, i.e. no limits has been assigned
    def empty(self):
        return self.observed == None and self.expected == None

    ## Check if result already exists
    #
    # \todo Could be removed
    def Exists(self, result):
        if self.mass == result.mass:
            return True
        return False
        
    ## Add another result to this
    #
    # \todo Could be removed
    def Add(self, result):
        if self.mass == result.mass:
            if self.observed == None:
                self.observed = result.observed
            if self.expected == None:
                self.expected            = result.expected
                self.expectedPlus1Sigma  = result.expectedPlus1Sigma
                self.expectedPlus2Sigma  = result.expectedPlus2Sigma
                self.expectedMinus1Sigma = result.expectedMinus1Sigma
                self.expectedMinus2Sigma = result.expectedMinus2Sigma
  
    ## Print the result
    #
    # \todo Could be removed
    def Print(self):
        print "Mass = ",self.mass
        print "    Observed = ",self.observed
        print "    Expected = ",self.expected
        print "     -1sigma = ",self.expectedMinus1Sigma," +1sigma = ",self.expectedPlus1Sigma
        print "     -2sigma = ",self.expectedMinus2Sigma," +2sigma = ",self.expectedPlus2Sigma
#        print "     +1sigma = ",self.expectedPlus1Sigma," -1sigma = ",self.expectedMinus1Sigma
#        print "     +2sigma = ",self.expectedPlus2Sigma," -2sigma = ",self.expectedMinus2Sigma


## Collection of Result objects
class ResultContainer:
    ## Constructor
    #
    # \param path  Path to the multicrab directory (where configuration.json exists)
    def __init__(self, path):
        self.path = path

        # Read task configuration json file
        configFile = os.path.join(path, "configuration.json")
        f = open(configFile)
        self.config = json.load(f)
        f.close()

        # Read the luminosity, use tau+jets one if that's available, if not, use the first one
        datacards = self.config["datacards"]
        taujetsDc = None
        for dc in datacards:
            if "hplushadronic" in dc:
                taujetsDc = dc
                break
        if taujetsDc != None:
            self._readLuminosityTaujets(taujetsDc % self.config["masspoints"][0])
        else:
            self._readLuminosityLeptonic(self.config["datacards"][0] % self.config["masspoints"][0])

        self.results = []

    ## Append a result object to the list
    #
    # \param obj   Result object
    def append(self, obj):
        self.results.append(obj)

    ## Read luminosity from a datacard assuming it follows the tau+jets convention
    #
    # \param filename  Name of the datacard file inside the multicrab directory
    def _readLuminosityTaujets(self, filename):
        lumi_re = re.compile("luminosity=[\S| ]*(?P<lumi>\d+\.\d+)")
        fname = os.path.join(self.path, filename)
        f = open(fname)
        for line in f:
            match = lumi_re.search(line)
            if match:
                self.lumi = str(1000*float(match.group("lumi"))) # 1/fb -> 1/pb
                f.close()
                return
        raise Exception("Did not find luminosity information from '%s'" % fname)

    ## Read luminosity from a datacard assuming it follows the leptonic convention
    #
    # \param filename  Name of the datacard file inside the multicrab directory
    #
    # \todo This needs to be updated, it get's the scale wrong
    def _readLuminosityLeptonic(self, filename):
        scale_re = re.compile("lumi scale (?P<scale>\S+)")
        lumi_re = re.compile("lumi=(?P<lumi>\S+)")
        scale = None
        lumi = None

        fname = os.path.join(self.path, filename)
        f = open(fname)
        for line in f:
            match = scale_re.search(line)
            if match:
                scale = float(match.group("scale"))
                continue
            match = lumi_re.search(line)
            if match:
                lumi = float(match.group("lumi"))
                break
        f.close()
        if lumi == None:
            raise Exception("Did not find luminosity information from '%s'" % fname)
        if scale != None:
            lumi *= scale
        self.lumi = str(lumi)

    ## Get the integrated luminosity as a string in 1/pb
    def getLuminosity(self):
        return self.lumi

    ## Print the limits
    def print2(self):
        print
        print "                  Expected"
        print "Mass  Observed    Median       -2sigma     -1sigma     +1sigma     +2sigma"
        format = "%3s:  %-9s   %-10s   %-10s  %-10s  %-10s  %-10s"
        massIndex = [(int(self.results[i].mass), i) for i in range(len(self.results))]
        massIndex.sort()
        for mass, index in massIndex:
            result = self.results[index]
            if result.empty():
                continue
            print format % (result.mass, result.observed, result.expected, result.expectedMinus2Sigma, result.expectedMinus1Sigma, result.expectedPlus1Sigma, result.expectedPlus2Sigma)
        print
    
    ## Store the results in a limits.json file
    #
    # \param data   Dictionary of additional data to be stored
    def saveJson(self, data={}):
        output = {}
        output.update(data)
        output.update({
                "luminosity": self.getLuminosity(),
                "masspoints": {}
                })

        massIndex = [(int(self.results[i].mass), i) for i in range(len(self.results))]
        massIndex.sort()
        for mass, index in massIndex:
            result = self.results[index]
            if result.empty():
                continue

            output["masspoints"][result.mass] = {
                "mass": result.mass,
                "observed": result.observed,
                "expected": {
                    "-2sigma": result.expectedMinus2Sigma,
                    "-1sigma": result.expectedMinus1Sigma,
                    "median": result.expected,
                    "+1sigma": result.expectedPlus1Sigma,
                    "+2sigma": result.expectedPlus2Sigma,
                    }
                }
            if hasattr(result, "observedError"):
                output["masspoints"][result.mass]["observed_error"] = result.observedError
            if hasattr(result, "expectedError"):
                output["masspoints"][result.mass]["expected"].update({
                        "-2sigma_error": result.expectedMinus2SigmaError,
                        "-1sigma_error": result.expectedMinus1SigmaError,
                        "median_error": result.expectedError,
                        "+1sigma_error": result.expectedPlus1SigmaError,
                        "+2sigma_error": result.expectedPlus2SigmaError,
                        })


        fname = os.path.join(self.path, "limits.json")
        f = open(fname, "wb")
        json.dump(output, f, sort_keys=True, indent=2)
        f.close()
        return fname

## Convert the error bands in Result object from absolute to relative
#
# \todo Could be removed
def ConvertToErrorBands(result):
    return Result(float(result.mass),
                  float(result.observed),
                  float(result.expected),
                  float(result.expectedPlus1Sigma) - float(result.expected),
                  float(result.expectedPlus2Sigma) - float(result.expected), 
                  float(result.expected) - float(result.expectedMinus1Sigma),
                  float(result.expected) - float(result.expectedMinus2Sigma))

## Class to parse the limits from LandS output
#
# This is used from \a landsMergeHistograms.py to read the LandS
# output. The limits are stored in \a limits.json file for easier
# subsequent access.
class ParseLandsOutput:
    ## Constructor
    #
    # \param path   Path to the multicrab directory
    def __init__(self, path):
	self.path = path
	self.lumi = 0

        # Read task configuration json file
        configFile = os.path.join(path, "configuration.json")
        f = open(configFile)
        self.config = json.load(f)
        f.close()

        if self.config["clsType"] == "LEP":
            self.clsType = LEPType()
        elif self.config["clsType"] == "LHC":
            self.clsType = LHCType()
        else:
            raise Exception("Unsupported CLs type '%s' in %s" % (self.config["clsType"], configFile))

        # Read in the results
        self.results = ResultContainer(self.path)
        try:
            clsConfig = self.config["clsConfig"]
        except KeyError:
            clsConfig = None
        for mass in self.config["masspoints"]:
            self.results.append(self.clsType.getResult(self.path, mass, clsConfig))
            print "Processed mass point %s" % mass


    ## Get the integrated luminosity as a string in 1/pb
    def getLuminosity(self):
	return self.results.getLuminosity()

    ## Print the results
    #
    # \todo Could be removed in favour of print2()
    def Print(self):
	for result in self.results.results:
	    result.Print()

    ## Save the results to a text file
    #
    # \todo Could be removed in favour of saveJson()
    def Save(self, dOUT):
	outputFileNaming = "output_lands_datacard_hplushadronic_m"

	if not os.isdir(dOUT):
            os.mkdir(dOUT)

	print "Saving in",dOUT
	for result in self.results.results:
	    fileName = outputFileNaming + result.mass
	    print "    ",fileName
	    fileName = dOUT + "/" + fileName
	    fOUT = open(fileName, 'w')
	    fOUT.write(str(result.observed) + "\n")
	    fOUT.write(str(result.expectedMinus2Sigma) + " " + \
                       str(result.expectedMinus1Sigma) + " " + \
                       str(result.expected) + " " + \
                       str(result.expectedPlus1Sigma) + " " + \
                       str(result.expectedPlus2Sigma))
	    fOUT.close()

    ## Print the results
    def print2(self):
        self.results.print2()

    ## Save the results to \a limits.json file
    def saveJson(self):
        fname = self.results.saveJson()
        print "Wrote results to %s" % fname

    ## Get the limit data
    #
    # \todo Could be removed
    def Data(self):
	return self.results.results


## Find or install the LandS
#
# \param directory   Return the path to the LandS directory (True), or to lands.exe (False)
#
# \return Absolute path to lands.exe (if \a directory was False), or
#         to LandS directory (if \a directory was True)
#
# Looks for LandS in
# $CMSSW_BASE/src/HiggsAnalysis/HeavyChHiggsToTauNu/test/brlimit. If
# found, return the path. If not found, install LandS and return the
# path. Installation consists of cvs checkout and compilation with make.
def findOrInstallLandS(directory=False):
    try:
        cmsswBase = os.environ["CMSSW_BASE"]
    except KeyError:
        raise Exception("Did you 'cmsenv'? I can't find $CMSSW_BASE environment variable")

    brlimitBase = os.path.join(cmsswBase, "src", "HiggsAnalysis", "HeavyChHiggsToTauNu", "test", "brlimit")
    landsDir = "LandS_"+LandS_tag
    landsDirAbs = os.path.join(brlimitBase, landsDir)
    landsExe = os.path.join(landsDirAbs, "test", "lands.exe")
    if os.path.exists(landsDirAbs):
        if not os.path.isfile(landsExe):
            raise Exception("Found LandS directory in '%s', but not lands.exe in '%s'" % (landsDirAbs, landsExe))

        if directory:
            return landsDirAbs
        else:
            return landsExe
    else:
        pwd = os.getcwd()
        os.chdir(brlimitBase)

        command = ["cvs", "checkout", "-r", LandS_tag, "-d", landsDir, "UserCode/mschen/LandS"]
        ret = subprocess.call(command)
        if ret != 0:
            raise Exception("cvs checkout failed (exit code %d), command '%s'" % (ret, " ".join(command)))
        if not os.path.exists(landsDir):
            raise Exception("cvs checkout failed to create directory '%s' under '%s'" % (brlimitBase, landsDir))

        os.chdir(landsDir)
        ret = subprocess.call(["make", "clean"])
        if ret != 0:
            raise Exception("Compiling LandS failed (exit code %d), command 'make clean'" % ret)
        ret = subprocess.call(["make"])
        if ret != 0:
            raise Exception("Compiling LandS failed (exit code %d), command 'make'" % ret)

        if not os.path.isfile(landsExe):
            raise Exception("After LandS checkout and compilation, the lands.exe is not found in '%s'" % landsExe)

        os.chdir(pwd)

        if directory:
            return landsDirAbs
        else:
            return landsExe

## Helper function to update keyword argument dictionary
#
# \param kwargs    Dictionary for keyword arguments
# \param obj       Object
# \param names     List of attribute names
#
# Constructs a new dictionary, where key,value pairs are taken from
# kwargs for all attribute names, or if some name does not exist in
# the kwargs, the value is taken from the object.
#
# The kwargs may not contain any other keys than the ones in names
# (typo protection)
def _updateArgs(kwargs, obj, names):
    for k in kwargs.keys():
        if not k in names:
            raise Exception("Unknown keyword argument '%s', known arguments are %s" % ", ".join(names))

    args = {}
    for n in names:
        args[n] = kwargs.get(n, getattr(obj, n))
    return args

## Write content to file, and make the file executable
#
# \param filename   Path to file
# \param content    String to write to the file
def _writeScript(filename, content):
    fOUT = open(filename, 'w')
    fOUT.write(content)
    fOUT.close()

    # make the script executable
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IXUSR)

## Pick default value if value is None
def _ifNotNoneElse(value, default):
    if value == None:
        return default
    return value
