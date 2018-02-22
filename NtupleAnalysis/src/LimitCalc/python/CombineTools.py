'''

\package CombineTools



DESCRIPTION:

Python interface for running Combine with multicrab



The interface for casual user is provided by the functions

generateMultiCrab() (for LEP-CLs and LHC-CLs) and

produceLHCAsymptotic (for LHC-CLs asymptotic).



The multicrab configuration generation saves various parameters to

taskdir/configuration.json, to be used in by combineMergeHistograms.py

script. The script uses tools from this module, which write the

limit results to taskdir/limits.json. I preferred simple text format

over ROOT files due to the ability to read/modify the result files

easily. Since the amount of information in the result file is

relatively small, the performance penalty should be negligible.





INSTRUCTIONS:





EXAMPLE:





LAST USED:



'''

#================================================================================================ 

# Imports

#================================================================================================ 

import HiggsAnalysis.LimitCalc.CommonLimitTools as commonLimitTools



import os

import re

import sys

import glob

import json

import time

import random

import shutil

import tarfile

import subprocess



import HiggsAnalysis.NtupleAnalysis.tools.multicrab as multicrab

import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles

#import HiggsAnalysis.NtupleAnalysis.tools.multicrabWorkflows

import HiggsAnalysis.NtupleAnalysis.tools.git as git

import HiggsAnalysis.NtupleAnalysis.tools.aux as aux

import array



import ROOT



#================================================================================================

# Temporary Global variables

#================================================================================================ 

VERBOSE = False



#================================================================================================ 

# Function Definition

#================================================================================================ 

def Verbose(msg, printHeader=False):

    #if not opts.verbose:

    if not VERBOSE:

        return

    

    if printHeader:

        print "=== CombineTools.py:"

        

    if msg !="":

        print "\t", msg

    return



def Print(msg, printHeader=True):

    if printHeader:

        print "=== CombineTools.py:"

        

    if msg !="":

        print "\t", msg

    return



def atoi(text):

    return int(text) if text.isdigit() else text



def natural_keys(text):

    '''

    alist.sort(key=natural_keys) sorts in human order

    http://nedbatchelder.com/blog/200712/human_sorting.html

    (See Toothy's implementation in the comments)

    '''

    return [ atoi(c) for c in re.split('(\d+)', text) ]





#================================================================================================ 

# Options

#================================================================================================ 

# The Combine git tag to be used (see https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideHiggsAnalysisCombinedLimit)

Combine_tag = "v7.0.1" # 31.8.2017

validCMSSWversions = ["/CMSSW_8_0_26_patch1"]



# Command line options for creating Combine workspace

workspacePattern = "combineWorkspaceM%s.root"

workspaceOptionsBrLimitTemplate = "text2workspace.py %s -P HiggsAnalysis.CombinedLimit.ChargedHiggs:brChargedHiggs -o %s"%("%s",workspacePattern)

workspaceOptionsSigmaBrLimit    = "text2workspace.py %s -o %s"%("%s",workspacePattern%"%s")

taskDirprefix = "CombineResults"



# Command line options for running Combine

if 0:

    asymptoticLimit = "combine -M Asymptotic --picky"

    asymptoticLimitOptionExpectedOnly = " --run expected"



#hybridLimit = "combine -M HybridNew --freq --hintMethod Asymptotic" # --testStat LHC



# Default number of crab jobs

defaultNumberOfJobs = 20



## Default command line options for LHC-CLs (asymptotic, observed limit) 

## NB! # For final limits, one should consider using --cminDefaultMinimizerStrategy 1: it is slower and more error-prone but more accurate 

Verbose("Edit #1", True)

### COMBINE SETTINGS ###
# For tau nu analysis:
#lhcAsymptoticOptionsObserved = '-M AsymptoticLimits -v 3 --cminDefaultMinimizerStrategy 0 --rAbsAcc 0.0001 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --X-rtd MINIMIZER_analytic --cminDefaultMinimizerTolerance=0.1 --cminFallbackAlgo "Minuit,0:0.001"' #default
#For tau nu analysis with lumi scaling (set to 1.0, for lumi scaling set lumiscale=<current_lumi>/<new_lumi>, see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/SWGuideHiggsProjections
l#hcAsymptoticOptionsObserved = '-M AsymptoticLimits -v 3 --cminDefaultMinimizerStrategy 0 --rAbsAcc 0.0001 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --X-rtd MINIMIZER_analytic --cminDefaultMinimizerTolerance=0.1 --cminFallbackAlgo "Minuit,0:0.001" --setParameters lumiscale=1.0'#default
# For tb analysis, default_v1:
#lhcAsymptoticOptionsObserved = '-M AsymptoticLimits -v 3 --cminDefaultMinimizerStrategy 0 --rAbsAcc 0.1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=1.0' 
# For tb analysis, default_v2:
lhcAsymptoticOptionsObserved = '-M AsymptoticLimits -v 3 --cminDefaultMinimizerStrategy 0 --rAbsAcc 0.001 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=1.0' 
########################


# If you use Barlow-Beeston-lite approach for statistical uncertainties, uncomment the next line:

lhcAsymptoticOptionsBlinded = lhcAsymptoticOptionsObserved + " --run blind"

# lhcAsymptoticOptionsObserved += " --X-rtd MINIMIZER_analytic"



## Default "Rmin" parameter for LHC-CLs (asymptotic)

lhcAsymptoticRminSigmaBr = "0.0" # pb

lhcAsymptoticRminBrLimit = "0.0" # plain number



## Default "Rmax" parameter for LHC-CLs (asymptotic)

lhcAsymptoticRmaxSigmaBr = "1.0" # pb

lhcAsymptoticRmaxBrLimit = "0.03" # plain number (updated to 0.05 from 0.03 in 2014 paper due to higher limits)



## Default command line options for observed significance

lhcFreqSignificanceObserved = "-M ProfileLikelihood --significance --scanPoints 1000"

lhcFreqSignificanceExpected = lhcFreqSignificanceObserved + " -t -1 --toysFreq"

lhcFreqSignificanceExpectedSignalSigmaBr = "0.1" # pb

lhcFreqSignificanceExpectedSignalBrLimit = "0.01" # %

lhcFreqRmaxSigmaBr = "1.0" # pb

lhcFreqRmaxBrLimit = "0.1" # %



def createOptionParser(lepDefault=None, lhcDefault=None, lhcasyDefault=None):

    '''

    Create OptionParser, and add common LandS options to OptionParser object

    

    \param lepDefault     Boolean for the default value of --lep switch (if None, switch is not added)

    \param lhcDefault     Boolean for the default value of --lhc switch (if None, switch is not added)

    \param lhcasyDefault  Boolean for the default value of --lhcasy switch (if None, switch is not added)

    

    \return optparse.OptionParser object

    '''

    return commonLimitTools.createOptionParser(lepDefault, lhcDefault, lhcasyDefault)



def parseOptionParser(parser):

    '''

    Parse OptionParser object

    

    \param parser   optparse.OptionParser object

    

    \return Options object

    '''

    commonLimitTools.parseOptionParser(parser)

    return



def produceLHCAsymptotic(opts, directory,

                         massPoints,

                         datacardPatterns,

                         rootfilePatterns,

                         clsType = None,

                         postfix="",

                         quietStatus=False

                         ):

    '''

    Run Combine for the LHC-CLs asymptotic limit

    \param opts               optparse.OptionParser object, constructed with createOptionParser()

    \param massPoints         List of mass points to calculate the limit for (list of strings)



    \param datacardPatterns   List of datacard patterns to include in the limit calculation (list 

    of strings, each string should have '%s' to denote the  position of the mass)



    \param rootfilePatterns   List of shape ROOT file patterns to include in the limit calculation

                              (list of strings, each string should have '%s' to denote the position of the mass)



    \param clsType            Object defining the CLs flavour (should be LHCTypeAsymptotic). 

                              If None, the default (LHCTypeAsymptotic) is used

    

    \param postfix            String to be added to the multicrab task directory  name



    The options of LHCTypeAsymptotic are controlled by the constructor.

    '''

    cls = clsType

    if clsType == None:

        cls = LHCTypeAsymptotic(opts.brlimit, opts.sigmabrlimit)



    # Multicrab object to generate (LEP-CLs, LHC-CLs) multicrab configuration, or run (LHC-CLs asymptotic) LandS

    massPoints.sort(key=natural_keys)

    Verbose("Computing limits with %s CLs flavour" % cls.nameHuman(), True)

    mcc = MultiCrabCombine(opts, directory, massPoints, datacardPatterns, rootfilePatterns, cls)

    mcc.createMultiCrabDir(postfix)

        

    myStatus = True

    if hasattr(opts, "creategridjobs") and opts.creategridjobs:

        myStatus = False



    if myStatus:

        mcc.copyInputFiles()



    myScripts = mcc.writeScripts()

    if opts.injectSignal:

        mcc.writeCrabCfg("arc", [], ["dummy"])

        mcc.writeMultiCrabCfg(aux.ValuePerMass(opts.injectNumberJobs))

        if opts.multicrabCreate:

            mcc.createMultiCrab()

    elif hasattr(opts, "creategridjobs") and opts.creategridjobs:

        # Works only on CRAB2 and intented for tan beta scans

        # Produce running script for each mass point

        myWorkspaces = []

        for m in massPoints:

            # Create list of input files

            myInputFiles = []

            for item in datacardPatterns:

                if item != None:

                    if "%s" in item:

                        name = item%m

                        if not name in myInputFiles:

                            myInputFiles.append(name)

                    else:

                        if not item in myInputFiles:

                            myInputFiles.append(item)

            # Create input workspace for combine

            print "Merging datacards for m=%s"%m

            combinedCardName = "combinedCardsM%s.txt"%m

            if os.path.exists(combinedCardName):

                os.system("rm %s"%combinedCardName)

            combineCardsCommand = "combineCards.py %s > %s"%(" ".join(map(str, myInputFiles)), combinedCardName)

            print combineCardsCommand

            os.system(combineCardsCommand)

            print "Creating combine workspace for m=%s"%m

            workspaceCommand = workspaceOptionsSigmaBrLimit%(combinedCardName,m)

            print workspaceCommand

            os.system(workspaceCommand)

            os.system("mv %s %s/."%(workspacePattern%m, mcc.dirname))

            #for i in range(len(myInputFiles)):

                #myInputFiles[i] = "%s/%s"%(mcc.dirname, myInputFiles[i])

            #os.system("rm %s %s"%(" ".join(map(str, myInputFiles)),os.path.join(mcc.dirname, combinedCardName)))

            myWorkspaces.append(workspacePattern%m)

            # Copy combine binary here

            os.system("cp %s/bin/%s/combine %s/."%(os.environ["CMSSW_BASE"], os.environ["SCRAM_ARCH"], mcc.dirname))

        if opts.gridRunAllMassesInOneJob:

            # Create crab task config

            mcc.writeCrabCfg("remoteglidein", {"GRID": ["SE_white_list = T2_FI_HIP", "maxtarballsize = 50", "virtual_organization = cms"],

                                                "USER": ["script_exe = runGridJob", "additional_input_files = %s, combine"%(", ".join(map(str, myWorkspaces)))]},

                            ["output.tgz"])

            os.system("mv %s %s/."%(" ".join(map(str,myWorkspaces)), mcc.dirname))

            # Create script for running the grid job

            command = ["#!/bin/sh", "", "# Run combine"]

            for m in massPoints:

                f = open(os.path.join(mcc.dirname, myScripts[m]))

                myLines = f.readlines()

                f.close()

                for line in myLines:

                    if line.startswith("combine "):

                        command.append("./%s"%line.replace("\n","").replace("combinedCardsM%s.txt"%m,workspacePattern%m))

            command.append("")

            command.append("# Collect output")

            command.append("ls -la")

            command.append("tar cfz output.tgz higgsCombine*.root")

            command.append("")

            command.append("# Do job report does not work")

            command.append("#cmsRun -j $RUNTIME_AREA/crab_fjr_$NJob.xml -p pset.py")



            filePath = os.path.join(mcc.dirname, "runGridJob")

            Print("Creating script \"%s\" for mass points %s" % (filePath, massPoints), True)

            aux.writeScript(filePath, "\n".join(command)+"\n")

        else:

            for m in massPoints:

                # Create crab task config

                mcc.writeCrabCfg("remoteglidein", {"GRID": ["SE_white_list = T2_FI_HIP", "maxtarballsize = 50", "virtual_organization = cms"],

                                                    "USER": ["script_exe = runGridJobM%s"%m, "additional_input_files = %s, combine"%(workspacePattern%m)]},

                                ["output.tgz"])

                os.system("mv %s %s/."%(workspacePattern%m, mcc.dirname))

                # Create script for running the grid job

                command = ["#!/bin/sh", "", "# Run combine"]

                f = open(os.path.join(mcc.dirname, myScripts[m]))

                myLines = f.readlines()

                f.close()

                for line in myLines:

                    if line.startswith("combine "):

                        command.append("./%s"%line.replace("\n","").replace("combinedCardsM%s.txt"%m,workspacePattern%m))

                command.append("")

                command.append("# Collect output")

                command.append("tar cfz output.tgz higgsCombine*.root")

                command.append("ls -la")

                command.append("")

                command.append("# Do job report does not work")

                command.append("#cmsRun -j $RUNTIME_AREA/crab_fjr_$NJob.xml -p pset.py")

                filePath = os.path.join(mcc.dirname, "runGridJobM%s" % m)

                Print("Creating script \"%s\" for mass point %s" % (filePath, m), True)

                aux.writeScript(filePath, "\n".join(command)+"\n")

    else:

        Verbose("Run Combine locally for the asymptotic limit", True)

        mcc.runCombineForAsymptotic(quietStatus=quietStatus)

        return mcc.getResults()



class MultiCrabCombine(commonLimitTools.LimitMultiCrabBase):

    '''

    Class to generate (LEP-CLs, LHC-CLs) multicrab configuration, or run (LHC-CLs asymptotic) LandS

    

    The class is not intended to be used directly by casual user, but

    from generateMultiCrab() and produceLHCAsymptotic()

    '''

    def __init__(self, opts, directory, massPoints, datacardPatterns, rootfilePatterns, clsType):

        '''

        Constructor

        

        \param directory          Datacard directory

        \param massPoints         List of mass points to calculate the limit for

        \param datacardPatterns   List of datacard patterns to include in the limit calculation

        \param rootfilePatterns   List of shape ROOT file patterns to include in the limit calculation

        \param clsType            Object defining the CLs flavour (should be either LEPType, or LHCType).

        '''

        commonLimitTools.LimitMultiCrabBase.__init__(self, opts, directory, massPoints, datacardPatterns, rootfilePatterns, clsType)

        self.exe = "combine"

        self.configuration["Combine_tag"] = Combine_tag

        self._results = None

        self.jsonFile = None

        return





    def createMultiCrabDir(self, postfix):

        '''

        Create the multicrab task directory

        

        \param postfix   Additional string to be included in the directory name

        '''

        prefix = taskDirprefix

        self._createMultiCrabDir(prefix, postfix)

        return





    def runCombineForAsymptotic(self, quietStatus=False):

        '''

        Run Combine for the asymptotic limit

        

        This is so fast at the moment that using crab jobs for that

        would be waste of resources and everybodys time.

        '''

        #if not quietStatus:

        #    print "Running Combine for asymptotic limits, saving results to %s" % self.dirname



        fileMode = "wb"

        jsonFile = "configuration.json"

        jsonPath = os.path.join(self.dirname, jsonFile)



        Verbose("Opening file \"%s\" in file mode \"%s\" to write configurations used" % (jsonFile, fileMode), True)

        f = open(jsonPath, fileMode)

        json.dump(self.configuration, f, sort_keys=True, indent=2)

        f.close()

 

        self._results = commonLimitTools.ResultContainer(self.opts.unblinded, self.dirname)

        

        # For-loop: All mass points to run combine on

        for counter, mass in enumerate(self.massPoints, 1):

            msg = "{:<9} {:>3} {:<1} {:<3} {:<50}".format("Mass Point", "%i" % counter, "/", "%i:" % len(self.massPoints), "m = %s GeV" % mass)

            Print(ShellStyles.HighlightAltStyle() + msg + ShellStyles.NormalStyle(), counter==1)



            myResult = self.clsType.runCombine(mass)

            if myResult.failed:

                if not quietStatus:

                    msg = "Fit failed for mass point %s, skipping ..." % mass

                    Print(ShellStyles.WarningLabel()  + msg, True)

            else:

                self._results.append(myResult)

                #msg = "Processed successfully mass point %s, the result is %s" % (mass,self._results.getResultString(mass)) 

                msg = "The result is %s" % (self._results.getResultString(mass))

                if not quietStatus:

                    Print(ShellStyles.SuccessStyle() + msg + ShellStyles.NormalStyle(), False)



        if not quietStatus:

            msg = "Summary of the results:"

            Print(ShellStyles.SuccessStyle() + msg + ShellStyles.NormalStyle(), True)

            self._results.print2()



        fname = self._results.saveJson()

        self.jsonFile = fname

        Print("Wrote results to %s" % fname, True)

        return





    def getResults(self):

        '''

        Return result container (ResultContainer object)

        '''

        return self._results





def _addCombinePreparationCommands(brlimit,datacardFiles,mass,commands):

    '''

    Adds to the commands list the necessary commands and returns the input datacard name

    

    \brlimit               Boolean, set to true to calculate Br limit on light charged Higgs



    \param mass            String for the mass point



    \param datacardFiles   List of strings for datacard file names of the mass point



    \param commands        List of strings of the commands to run Combine

    '''



    # Join datacards if necessary

    myInputName = datacardFiles[0]

    if len(datacardFiles) > 1:

        myInputName = "combinedCardsM%s.txt"%mass

        commands.append("combineCards.py %s > %s"%(" ".join(map(str,datacardFiles)),myInputName))

    # Create workspace with light H+ physics model, if necessary

    if brlimit:

        myNewInputName = "workspaceM%s.root"%mass

        commands.append("text2workspace.py %s -P HiggsAnalysis.CombinedLimit.ChargedHiggs:brChargedHiggs -o %s"%(myInputName,myNewInputName))

        myInputName = myNewInputName

    return myInputName





class LHCTypeAsymptotic:

    '''

    Definition of the LHC-type CLs (with the asymptotic treatment of nuisance parameters)

    

    The method itself is described in the CMS-NOTE-2011-005 appendix A.1.3.

    

    At the moment running the asymptotic limit is so fast that running

    it via crab would be waste of time and resources from everybodys

    point of view. Instead, the LandS is run at the "multicrab

    configuration generation" stage. To have similar usage to the other

    CLs flavours, the results are stored in a multicrab task directory.

    

    Because no crab is involved, the user interface is different. This

    is achieved with the produceLHCAsymptotic() function instead of the

    generateMultiCrab().

    '''

    def __init__(self, opts, optionsObservedAndExpected=None, optionsBlinded=None, rMin=None, rMax=None):

        '''

        Constructor

        

        \param optionsObserved  Command line options for LandS for the observed limit. 

        String, dictionary (see ValuePerMass), or None for default (lhcAsymptoticOptionsObserved)



        \param optionsExpected  Command line options for LandS for the expected limit. 

        String, dictionary (see ValuePerMass), or None for default (lhcAsymptoticOptionsExpected)



        \param rMin             The \a --rMin parameter for LandS. 

        String, dictionary (see ValuePerMass), or None for default (lhcAsymptoticRmin)



        \param rMax             The \a --rMax parameter for LandS. 

        String, dictionary (see ValuePerMass), or None for default (lhcAsymptoticRmax)

                                

        Note: if you add any parameters to the constructor, add the parameters to the clone()

        method correspondingly.

        '''

        self.opts = opts

        self.brlimit = opts.brlimit

        self.sigmabrlimit = opts.sigmabrlimit

        

        # print "*"*100

        # print "opts.htb = ", opts.htb

        # print "*"*100



        self.optionsObservedAndExpected = aux.ValuePerMass(aux.ifNotNoneElse(optionsObservedAndExpected, lhcAsymptoticOptionsObserved))

        self.optionsBlinded = aux.ValuePerMass(aux.ifNotNoneElse(optionsBlinded, lhcAsymptoticOptionsBlinded))

        if self.brlimit:

            self.rMin = aux.ValuePerMass(aux.ifNotNoneElse(rMin, lhcAsymptoticRminBrLimit))

            self.rMax = aux.ValuePerMass(aux.ifNotNoneElse(rMax, lhcAsymptoticRmaxBrLimit))

        elif self.sigmabrlimit:

            self.rMin = aux.ValuePerMass(aux.ifNotNoneElse(rMin, lhcAsymptoticRminSigmaBr))

            self.rMax = aux.ValuePerMass(aux.ifNotNoneElse(rMax, lhcAsymptoticRmaxSigmaBr))

        if opts.rmin != None:

            self.rMin = aux.ValuePerMass(opts.rmin)

        if opts.rmax != None:

            self.rMax = aux.ValuePerMass(opts.rmax)



        self.obsAndExpScripts       = {}

        self.blindedScripts         = {}

        self.mlfitScripts           = {}

        self.significanceScripts    = {}

        self.signalInjectionScripts = {}



        self.configuration = {}

        return





    def name(self):

        '''

        Return the name of the CLs flavour (for serialization to configuration.json)

        '''

        return "LHCAsymptotic"



    def nameHuman(self):

        '''

        Return human-readable name of the CLs flavour

        '''

        return "LHC-type asymptotic"





    def getConfiguration(self, mcconf):

        '''

        Get the configuration dictionary for serialization.

        

         LHC-type asymptotic CLs does not need any specific information to be stored

         '''

        self.multicrabConfiguration = mcconf

        return self.configuration





    def clone(self, **kwargs):

        '''

        Clone the object, possibly overriding some options

        

        \param kwargs   Keyword arguments, can be any of the arguments of

        __init__(), with the same meaning.

        '''

        args = aux.updateArgs(kwargs, self, ["opts", "optionsObservedAndExpected", "optionsBlinded", "rMin", "rMax"])

        return LHCTypeAsymptotic(**args)





    def setDirectory(self, dirname):

        '''

        Set the multicrab directory path

        

         \param dirname   Path to the multicrab directory

        '''

        self.dirname = dirname

        return





    def createScripts(self, mass, datacardFiles):

        '''

        Create the job scripts for a single mass point

        

        \param mass            String for the mass point

        \param datacardFiles   List of strings for datacard file names of the mass point

        '''

        if self.opts.unblinded:

            self._createObsAndExp(mass, datacardFiles)

        else:

            self._createBlinded(mass, datacardFiles)

        if self.opts.significance:

            self._createSignificance(mass, datacardFiles)

        if self.opts.injectSignal:

            self._createInjection(mass, datacardFiles)

        return





    def _createObsAndExp(self, mass, datacardFiles):

        '''

        Create the observed and expected job script for a single mass point

        

        \param mass            String for the mass point

        \param datacardFiles   List of strings for datacard file names of the mass point

        '''

        msg = "Creating the observed and expected job script for mass point %s" % mass

        Print(msg, True)



        fileName = "runCombine_LHCasy_ObsAndExp_m" + mass

        opts = ""

        opts += " " + self.optionsObservedAndExpected.getValue(mass)

        opts += " --rMin %s"%self.rMin.getValue(mass)

        opts += " --rMax %s"%self.rMax.getValue(mass)

        opts += " -m %s"%mass

        opts += " -n obs_m%s"%mass

#        if self.brlimit:

#            opts += " --rAbsAcc 0.00001" # increase accuracy of calculation for br limit

        command = ["#!/bin/sh", ""]

        # Combine cards and prepare workspace for physics model, if necessary

        myInputDatacardName = _addCombinePreparationCommands(self.brlimit, datacardFiles, mass, command)

        # Add command for running combine

        command.append("combine %s -d %s" % (opts, myInputDatacardName))

        

        filePath = os.path.join(self.dirname, fileName)

        Verbose("Creating script \"%s\" for mass point %s" % (filePath, mass), True)

        aux.writeScript(filePath, "\n".join(command) + "\n")



        self.obsAndExpScripts[mass] = fileName

        self._createMLFit(mass, fileName, myInputDatacardName, blindedMode=False)

        return





    def _createBlinded(self, mass, datacardFiles):

        '''

        Create the expected job script for a single mass point

        

        \param mass            String for the mass point

        \param datacardFiles   List of strings for datacard file names of the mass point

        '''

        msg = "Creating the expected job script for mass point %s" % mass

        Verbose(msg, True)



        fileName = "runCombine_LHCasy_Blinded_m" + mass



        # Construct options to be passed to "combine" at runtime

        opts = ""

        opts += " " + self.optionsBlinded.getValue(mass)

        opts += " --rMin %s"%self.rMin.getValue(mass)

        opts += " --rMax %s"%self.rMax.getValue(mass)

        opts += " -m %s"%mass

        opts += " -n blinded_m%s"%mass

        # opts += " -v 4" # FIXME: Add this as a command-line option



        #if self.brlimit:

        #    opts += " --rAbsAcc 0.00001" # increase accuracy of calculation for br limit

        command = ["#!/bin/sh", ""]



        # Combine cards and prepare workspace for physics model, if necessary

        myInputDatacardName = _addCombinePreparationCommands(self.brlimit, datacardFiles, mass, command)



        # Add command for running combine

        command.append("combine %s -d %s" % (opts, myInputDatacardName))



        filePath = os.path.join(self.dirname, fileName)

        Verbose("Creating script \"%s\" for mass point %s" % (filePath, mass), True)

        aux.writeScript(filePath, "\n".join(command)+"\n")



        self.blindedScripts[mass] = fileName

        self._createMLFit(mass, fileName, myInputDatacardName, blindedMode=True)

        return



    def _createMLFit(self, mass, fileName, datacardName, blindedMode):

        if self.opts.nomlfit:

            # print "skipping creation of ML fit scripts, to enable run with --mlfit"

            return

          

        fname = fileName.replace("runCombine", "runCombineMLFit")

        outputdir = "mlfit_m%s" % mass

        opts = "-M MaxLikelihoodFit"

        opts += " -m %s" % mass

        opts += " --out %s" % outputdir

        # From https://github.com/cms-analysis/HiggsAnalysis-HiggsToTauTau/blob/master/scripts/limit.py

        #opts += " --minimizerAlgo minuit"

        opts += " --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.01 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=0 --minimizerTolerance=0.001 --cminFallbackAlgo \"Minuit,0:0.001\" --keepFailures" # following options may not suit for us? --preFitValue=1.

        command = ["#!/bin/sh", ""]

        command.append("mkdir -p %s" % outputdir)

        command.append("combine %s %s" % (opts, datacardName))



        opts = "-a"

        if self.brlimit:

            opts += " -p BR"

        opts2 = opts + " -g mlfit_m%s_pulls.png" % mass

        command.append("python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py %s %s/mlfit.root > %s/diffNuisances.txt" % (os.environ["CMSSW_BASE"], opts2, outputdir, outputdir))

        opts += " -A"

        opts2 = opts + " --vtol 1.0 --stol 0.99 --vtol2 2.0 --stol2 0.99" 

        command.append("python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py %s %s/mlfit.root > %s/diffNuisances_largest_pulls.txt" % (os.environ["CMSSW_BASE"], opts2, outputdir, outputdir))

        opts2 = opts + " --vtol 99. --stol 0.50 --vtol2 99. --stol2 0.90" 

        command.append("python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py %s %s/mlfit.root > %s/diffNuisances_largest_constraints.txt" % (os.environ["CMSSW_BASE"], opts2, outputdir, outputdir))

        command.append("combineReadMLFit.py -f %s/diffNuisances.txt -c configuration.json -m %s -o mlfit.json" % (outputdir, mass))

        opts3 = ""

        if blindedMode:

            opts3 = " --bkgonlyfit"

        else:

            opts3 = " --sbfit"

        command.append("python %s/src/HiggsAnalysis/NtupleAnalysis/test/brlimit/plotMLFits.py -m %s %s" % (os.environ["CMSSW_BASE"], mass, opts3))

          

        filePath = os.path.join(self.dirname, fname)

        Verbose("Creating script \"%s\" for mass point %s" % (filePath, mass), True)

        aux.writeScript(filePath, "\n".join(command)+"\n")



        self.mlfitScripts[mass] = fname

        return





    def _createSignificance(self, mass, datacardFiles):

        ''' 

        Create the observed significance for a single mass point

        

        \param mass            String for the mass point

        

        \param datacardFiles   List of strings for datacard file names of the mass point

         '''

        if self.opts.unblinded:

            fileName = "runCombineSignif_ObsAndExp_m" + mass

        else:

            fileName = "runCombineSignif_Exp_m" + mass



        opts = " -m %s"%mass

        opts += " -n signif_m%s"%mass

        if self.brlimit:

            opts += " --rMin %s --rMax %s" % (lhcAsymptoticRminBrLimit, lhcFreqRmaxBrLimit)

        else:

            opts += " --rMin %s --rMax %s" % (lhcAsymptoticRminSigmaBr, lhcFreqRmaxSigmaBr)

            

        command = ["#!/bin/sh", ""]

        # Combine cards and prepare workspace for physics model, if necessary

        myInputDatacardName = _addCombinePreparationCommands(self.brlimit, datacardFiles, mass, command)

        # Add command for running combine

        tmpfile = "signif_%s_data.txt" % mass



        # First the expected limit

        optsExpected = lhcFreqSignificanceExpected + opts

        if self.brlimit:

            optsExpected += " --expectSignal %s" % lhcFreqSignificanceExpectedSignalBrLimit

        else:

            optsExpected += " --expectSignal %s" % lhcFreqSignificanceExpectedSignalSigmaBr



        command.append("combine %s -d %s" % (optsExpected, myInputDatacardName))

        command.append("echo '#### PVALUE AFTER THIS LINE ###'")

        command.append("combine %s --pvalue -d %s" % (optsExpected, myInputDatacardName))



        # Then the expected limit

        if self.opts.unblinded:

            command.append("echo '#### OBSERVED AFTER THIS LINE ###'")

            optsObserved = lhcFreqSignificanceObserved + opts

            command.append("combine %s -d %s" % (optsObserved, myInputDatacardName))

            command.append("echo '#### PVALUE AFTER THIS LINE ###'")

            command.append("combine %s --pvalue -d %s" % (optsObserved, myInputDatacardName))



        filePath = os.path.join(self.dirname, fileName)    

        Verbose("Creating script \"%s\" for mass point %s" % (filePath, mass), True)

        aux.writeScript(filePath, "\n".join(command)+"\n")

        self.significanceScripts[mass] = fileName

        return



        

    def _createInjection(self, mass, datacardFiles):

        if not self.brlimit:

            raise Exception("Signal injection supported only for brlimit for now")

        if len(datacardFiles) != 1:

            raise Exception("Signal injection supported only for one datacard for now (got %d)" % len(datacardFiles))

        if len(self.multicrabConfiguration["rootfiles"]) != 1:

            raise Exception("Signal injection supported only for one root file for now (got %d)" % len(self.configuration["rootfiles"]))



        fileName = "runCombine_LHCasy_SignalInjected_m" + mass



        shutil.copy(os.path.join(os.environ["CMSSW_BASE"], "bin", os.environ["SCRAM_ARCH"], "combine"), self.dirname)

        shutil.copy(os.path.join(os.environ["CMSSW_BASE"], "bin", os.environ["SCRAM_ARCH"], "text2workspace.py"), self.dirname)

        shutil.copy(os.path.join(os.environ["CMSSW_BASE"], "src", "HiggsAnalysis", "NtupleAnalysis", "scripts", "combineInjectSignalLight.py"), self.dirname)

        tar = tarfile.open(os.path.join(self.dirname, "python.tar.gz"), mode="w:gz", dereference=True)

        tar.add(os.path.join(os.environ["CMSSW_BASE"], "python"), arcname="python")

        tar.close()



        datacard = datacardFiles[0]

        rootfile = self.multicrabConfiguration["rootfiles"][0] % mass

        rootfileSignal = self.multicrabConfiguration["rootfiles"][0] % self.opts.injectSignalMass



        rfs = ""

        if rootfileSignal != rootfile:

            rfs = rootfileSignal



        command = """

#!/bin/bash



SEED_START=1

NUMBER_OF_ITERATIONS={NTOYS}



if [ $# -ge 1 ]; then

    SEED_START=$(($1 * 10000))

fi



tar zxf python.tar.gz

export PYTHONPATH=$PWD/python:$PYTHONPATH



if [ ! -d original ]; then

    mkdir original

    mv {DATACARD} {ROOTFILE} {ROOTFILESIGNAL_OR_EMPTY} original

fi



function runcombine {{

    ./combineInjectSignalLight.py --inputDatacard original/{DATACARD} --inputRoot original/{ROOTFILE} --inputRootSignal original/{ROOTFILESIGNAL} --outputDatacard {DATACARD} --outputRoot {ROOTFILE} --brtop {BRTOP} --brh {BRHPLUS} -s $1

    ./text2workspace.py ./{DATACARD} -P HiggsAnalysis.CombinedLimit.ChargedHiggs:brChargedHiggs -o workspaceM{MASS}.root

#    combine  -M Asymptotic --picky -v 2 --rAbsAcc 0.00001 --rMin 0 --rMax 1.0 -m {MASS} -n obs_m{MASS} -d workspaceM{MASS}.root

    ./combine {OPTS} --rMin {RMIN} --rMax {RMAX} -m {MASS} -n inj_m{MASS} -d workspaceM{MASS}.root

    mv higgsCombineinj_m{MASS}.Asymptotic.mH{MASS}.root higgsCombineinj_m{MASS}.Asymptotic.mH{MASS}.seed$1.root

}}





for ((I=0; I<$NUMBER_OF_ITERATIONS; I++)); do

    runcombine $(($SEED_START+$I))

done



hadd higgsCombineinj_m{MASS}.Asymptotic.mH{MASS}.root higgsCombineinj_m{MASS}.Asymptotic.mH{MASS}.seed*.root



""".format(

    DATACARD=datacard, ROOTFILE=rootfile, ROOTFILESIGNAL=rootfileSignal, ROOTFILESIGNAL_OR_EMPTY=rfs,

    BRTOP=self.opts.injectSignalBRTop, BRHPLUS=self.opts.injectSignalBRHplus,

    NTOYS=self.opts.injectNumberToys, MASS=mass,

    OPTS=self.optionsObservedAndExpected.getValue(mass),

    RMIN=self.rMin.getValue(mass),

    RMAX=self.rMax.getValue(mass),

)



        if "signalInjection" not in self.configuration:

            self.configuration["signalInjection"] = {

                "mass": self.opts.injectSignalMass,

                "brTop": self.opts.injectSignalBRTop,

                "brHplus": self.opts.injectSignalBRHplus

            }

        if not os.path.exists(os.path.join(self.dirname, "limits.json")):

            # Insert luminosity to limits.json already here

            limits = {"luminosity": commonLimitTools.readLuminosityFromDatacard(self.dirname, datacard)}

            f = open(os.path.join(self.dirname, "limits.json"), "w")

            json.dump(limits, f, sort_keys=True, indent=2)

            f.close()



        filePath = os.path.join(self.dirname, fileName)

        Verbose("Creating script \"%s\" for mass point %s" % (filePath, mass), True)

        aux.writeScript(filePath, command)

        self.signalInjectionScripts[mass] = fileName

        return





    def runCombine(self, mass):

        '''

        Run LandS for the observed and expected limits for a single mass point

        

        \param mass   String for the mass point

        

        \return Result object containing the limits for the mass point

        '''

        Verbose("Running combine ...", False)

        result = commonLimitTools.Result(mass)

        if self.opts.limit:

            if self.opts.unblinded:

                msg = "Running unblinded LandS for the observed and expected limits for mass point %s" % mass

                Verbose(msg, True)

                self._runObservedAndExpected(result, mass)

            else:

                msg = "Running blinded LandS for the observed and expected limits for mass point %s" % mass

                Verbose(msg, True)

                self._runBlinded(result, mass)

        else:

            Print(ShellStyles.WarningLabel() + "Skipping limit for mass point %s" % mass, True)



        # xenios-1: What do we do here?

        self._runMLFit(mass)



        # xenios-2: What do we do here?

        self._runSignificance(mass)

        return result





    def _run(self, script, outputFile, errorFile):

        '''

        Helper method to run a script

        

        \param script      Path to the script to run



        \param outputFile  Path to a file to store the script stdout



        \param errorFiel   Path to a file to store the script stderr

        

        \return The output of the script as a string

        '''

        pwd = os.getcwd()

        os.chdir(self.dirname)

        msg = "Changing directory to \"%s\". Current working directory is:\n\t\"%s\"" % (self.dirname, os.getcwd())

        Verbose(msg, True)



        cmdList  = ["./" + script]

        outFile  = os.path.join(os.getcwd(), outputFile)   

        errFile  = os.path.join(os.getcwd(), errorFile)

        fileMode = "wb"



        # Run the script and redirect stdout and stderr to dedicated files

        Verbose("Opening file \"%s\" in mode \"%s\"" % (outFile, fileMode), True)

        with open(outFile, fileMode) as out, open(errFile, fileMode) as err:

            Verbose("Executing command \"%s\"" % (" ".join(cmdList)), True)

            p = subprocess.Popen(cmdList, stdout=out, stderr=err)

            output = p.communicate()[0]

            Verbose("Subprocess returned \"%s\"" % (output), True)



        if p.returncode != 0:

            # print output

            raise Exception("Combine failed with exit code %d\nCommand: %s" % (p.returncode, script))



        os.chdir(pwd)

        msg = "Changed directory to \"%s\". Current working directory is:\n\t\"%s\"" % (pwd, os.getcwd())

        Verbose(msg, True)



        if 0:

            f = open(outFile, fileMode)

            f.write(output)

            f.write("\n")

            f.close()

        return output





    def _parseResultFromCombineOutput(self, result, mass):

        '''

        Extracts the result from combine output

        

        \param result  Result object to modify

        

        \param mass    Mass



        \return number of matches found

        '''

        return parseResultFromCombineOutput(self.dirname, result, mass)





    def _runObservedAndExpected(self, result, mass):

        '''

        Run LandS for the observed limit

        

        \param result  Result object to modify

        \param mass    String for the mass point

        '''

        script = sel.obsAndExpScripts[mass]

        output = self._run(script, "obsAndExp_m%s_output.txt"%mass)



        n = self._parseResultFromCombineOutput(result, mass)

        if n == 6: # 1 obs + 5 exp values

            return result

        if n < 0: # fit failed

            return result

        result.failed = True

        print "Fit failed"

        return result

        #print output

        #raise Exception("Unable to parse the output of command '%s'" % script)

    

    def _runBlinded(self, result, mass):

        '''

        Run LandS for the expected limit

        

        \param result  Result object to modify

        \param mass    String for the mass point

        '''

        # Run combine script with customly-defined settings

        script  = self.blindedScripts[mass]



        # Inform user of log files created and shell script to be run

        logFile = "blinded_m%s_stdout.txt" % mass

        errFile = "blinded_m%s_stderr.txt" % mass

        msg1    = "{:<20} {:<50}".format("Saving output to file:", os.path.join(self.dirname, logFile) )

        msg2    = "{:<20} {:<50}".format("Saving output to file:", os.path.join(self.dirname, errFile) )

        msg3    = "{:<20} {:<50}".format("Running shell script :", os.path.join(self.dirname, script) )

        Verbose(msg1, True)

        Verbose(msg2, False)

        Verbose(msg3, False)



        # Execute the shell script that runs combine

        output = self._run(script, logFile, errFile)



        # Get the number of combine output results. Should be 5 or 6. The results are:

        # expected -2sigma, expected -1sigma, expected, expected + 1sigma, expected + 2sigma, observed

        n = self._parseResultFromCombineOutput(result, mass)



        if n == 5: # 5 exp values

            return result

        if n < 0: # fit failed

            result.failed = True

            Print(ShellStyles.ErrorStyle() + "Fit failed" + ShellStyles.NormalStyle(), True)

            return result





    def _runMLFit(self, mass):

        if mass in self.mlfitScripts.keys() and not self.opts.nomlfit:

            print "Running ML fits..."

            script = self.mlfitScripts[mass]

            self._run(script, "mlfit_m_%s_output.txt" % mass)

        return





    def _runSignificance(self, mass):

        jsonFile = os.path.join(self.dirname, "significance.json")



        if os.path.exists(jsonFile):

            f = open(jsonFile)

            result = json.load(f)

            f.close()

        else:

            result = {

                "expectedSignalBrLimit": lhcFreqSignificanceExpectedSignalBrLimit,

                "expectedSignalSigmaBr": lhcFreqSignificanceExpectedSignalSigmaBr

            }

        if mass in self.significanceScripts:

            script = self.significanceScripts[mass]

            output = self._run(script, "signif_m_%s_output.txt" % mass)

            result[mass] = parseSignificanceOutput(mass, outputString=output)



        f = open(jsonFile, "w")

        json.dump(result, f, sort_keys=True, indent=2)

        f.close()



    def writeMultiCrabConfig(self, opts, output, mass, inputFiles, njobs):

        if self.opts.injectSignal:

            self.writeInjectedMultiCrabConfig(opts, output, mass, inputFiles, njobs)



    def writeInjectedMultiCrabConfig(self, opts, output, mass, inputFiles, njobs):

        inp = inputFiles[:]

        if mass != str(opts.injectSignalMass):

            inp.append(self.multicrabConfiguration["rootfiles"][0] % self.opts.injectSignalMass)

        output.write("[Injected_m%s]\n" % mass)

        output.write("USER.script_exe = %s\n" % self.signalInjectionScripts[mass])

        output.write("USER.additional_input_files = text2workspace.py,combineInjectSignalLight.py,python.tar.gz,%s\n" % ",".join(inp))

        output.write("CMSSW.number_of_jobs = %d\n" % njobs)

        output.write("CMSSW.output_file = higgsCombineinj_m{MASS}.Asymptotic.mH{MASS}.root\n".format(MASS=mass))



def parseDiffNuisancesOutput(outputFileName, configFileName, mass):

    # first read nuisance types from datacards

    f = open(configFileName)

    config = json.load(f)

    f.close()

    datacardFiles = [dc % mass for dc in config["datacards"]]



    nuisanceTypes = {}

    type_re = re.compile("\s*(?P<name>\S+)\s+(?P<type>\S+)\s+[\d-]")

    for dc in datacardFiles:

        f = open(dc)

        # rewind until rate

        for line in f:

            if line[0:4] == "rate":

                break

        for line in f:

            m = type_re.search(line)

            if m:

                aux.addToDictList(nuisanceTypes, m.group("name"), m.group("type"))



    # then read the fit values

    f = open(outputFileName)



    ret_bkg = {}

    ret_sbkg = {}

    ret_rho = {}



    nuisanceNames = []



    num1 = "[+-]\d+.\d+"

    num2 = "\d+.\d+"

    nuis_re = re.compile("(?P<name>\S+)\s+(!|\*)?\s+(?P<bshift>%s),\s+(?P<bunc>%s)\s*(!|\*)?\s+(!|\*)?\s+(?P<sbshift>%s),\s+(?P<sbunc>%s)\s*(!|\*)?\s+(?P<rho>%s)" % (num1, num2, num1, num2, num1))

    for line in f:

        m = nuis_re.search(line)

        if m:

            nuisanceNames.append(m.group("name"))

            nuisanceType = nuisanceTypes.get(m.group("name"), None)

            if nuisanceType is not None and len(nuisanceType) == 1:

                nuisanceType = nuisanceType[0]

            if "statBin" in m.group("name"):

                nuisanceType = "shapeStat"

            if nuisanceType is None:

                nuisanceType = "unknown"

            ret_bkg[m.group("name")] = {"fitted_value": m.group("bshift"),

                                        "fitted_uncertainty": m.group("bunc"),

                                        "type": nuisanceType}

            ret_sbkg[m.group("name")] = {"fitted_value": m.group("sbshift"),

                                         "fitted_uncertainty": m.group("sbunc"),

                                         "type": nuisanceType}

            ret_rho[m.group("name")] = {"value": m.group("rho")}



    f.close()



    ret_bkg["nuisanceParameters"] = nuisanceNames

    ret_sbkg["nuisanceParameters"] = nuisanceNames



    return (ret_bkg, ret_sbkg, ret_rho)



def parseSignificanceOutput(mass, outputFileName=None, outputString=None):

    if outputFileName is None and outputString is None:

        raise Exception("Must give either outputFileName or outputString")

    if outputFileName is not None and outputString is not None:

        raise Exception("Must not give both outputFileName and outputString")



    content = []

    if outputFileName is not None:

        f = open(outputFileName)

        content = f.readlines()

        f.close()

    else:

        content = outputString.split("\n")



    # Read the significance values



    fl = "[+-]?\d+\.?\d*(e[+-]?\d+)?"



    signif_re = re.compile("Significance: (?P<signif>%s)" % fl)

    pvalue_re = re.compile("p-value of background: (?P<pvalue>%s)" % fl)



    signif_exp = None

    pvalue_exp = None

    signif_obs = None

    pvalue_obs = None



    signif = None

    pvalue = None



    def error(message):

        if outputFileName is not None:

            raise Exception("%s from file %s" % (message, outputFileName))

        print "Combine output"

        print outputString

        raise Exception("%s from the combine output (see above)" % message)



    for line in content:

        if "OBSERVED AFTER THIS LINE" in line:

            if signif is None:

                error("Expected significance not found")

            if pvalue is None:

                error("Expected p-value not found")

            signif_exp = signif

            pvalue_exp = pvalue

            signif = None

            pvalue = None



        m = signif_re.search(line)

        if m:

            if signif is not None:

                raise Exception("Significance already found, line %s" % line)

            signif = m.group("signif")

            continue

        m = pvalue_re.search(line)

        if m:

            if pvalue is not None:

                raise Exception("P-value already found, line %s" % line)

            pvalue = m.group("pvalue")



    if signif_exp is None:

        signif_exp = signif

        pvalue_exp = pvalue

    else:

        signif_obs = signif

        pvalue_obs = pvalue



    if signif_exp is None:

        error("Expected significance not found")

    if pvalue_exp is None:

        error("Expected p-value not found")



    ret = {"expected": {"significance": signif_exp,

                        "pvalue": pvalue_exp}}

    if signif_obs is not None:

        if pvalue_obs is None:

            error("Found observed significance but not pvalue")

        ret["observed"] = {"significance": signif_obs,

                           "pvalue": pvalue_obs}



    return ret





def parseResultFromCombineOutput(dirname, result, mass):

    '''

    Extracts the result from combine output

    

    \param result  Result object to modify

    

    \param mass    Mass

    

    \return number of matches found

    '''

    # Find combine output root file

    possibleNames = ["higgsCombineobs_m%s.AsymptoticLimits.mH%s.root"%(mass,mass),

                     "higgsCombineblinded_m%s.AsymptoticLimits.mH%s.root"%(mass,mass),

                     ]

    name = None



    # For-loop: All possible names

    for n in possibleNames:

        if os.path.exists(os.path.join(dirname,n)):

            name = os.path.join(dirname,n)

    if name == None:

        raise Exception("Error: Could not find combine output root file! (checked: %s)"%", ".join(map(str, possibleNames)))



    # Open root file

    f = ROOT.TFile.Open(name)

    myTree = f.Get("limit")

    x = array.array('d', [0])

    myTree.SetBranchAddress("limit",x)

    myResultList = []



    if myTree == None:

        raise Exception("Error: Cannot open TTree in file '%s'!"%name)



    # For-loop: Tree Entries

    for i in range(0, myTree.GetEntries()):

        myTree.GetEvent(i)

        myResultList.append(x[0])

    f.Close()





    # Store results

    nResults = len(myResultList) 

    if nResults < 5:

        msg = "Combine failed to produce all the results (only got %i / 5)L" % (nResults)

        Print(msg, True)



        for i, r in enumerate(myResultList, 1):

            msg = "#%i = %s" % (i, r)

            Print(msg, False)

        result.failed = True

        return -1

    result.expectedMinus2Sigma = myResultList[0]

    result.expectedMinus1Sigma = myResultList[1]

    result.expected = myResultList[2]

    result.expectedPlus1Sigma = myResultList[3]

    result.expectedPlus2Sigma = myResultList[4]

    if len(myResultList) == 6:

        result.observed = myResultList[5]

    return len(myResultList)

