## \package Extractor
# Classes for extracting observation/rate/nuisance from datasets
#
#

from HiggsAnalysis.HeavyChHiggsToTauNu.tools.counter import EventCounter
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset import _histoToCounter
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShapeHistoModifier import *
from math import pow,sqrt
import sys
import ROOT

# Enumerator class for data mining mode
class ExtractorMode:
    UNKNOWN = 0
    OBSERVATION = 1
    RATE = 2
    NUISANCE = 3
    ASYMMETRICNUISANCE = 4
    SHAPENUISANCE = 5
    CONTROLPLOT = 6

## ExtractorBase class
class ExtractorBase:
    ## Constructor
    def __init__(self, mode, exid, distribution, description):
        self._mode = mode
        self._isPrintable = True
        self._exid = exid
        self._distribution = distribution
        self._description = description
        self._extractablesToBeMerged = []
        self._masterExID = exid

    ## Returns true if extractable mode is observation
    def isObservation(self):
        return self._mode == ExtractorMode.OBSERVATION

    ## Returns true if extractable mode is rate
    def isRate(self):
        return self._mode == ExtractorMode.RATE

    ## Returns true if extractable mode is any type of nuisance
    def isAnyNuisance(self):
        return self._mode == ExtractorMode.NUISANCE or \
               self._mode == ExtractorMode.ASYMMETRICNUISANCE or \
               self._mode == ExtractorMode.SHAPENUISANCE

    ## Returns true if extractable mode is nuisance
    def isNuisance(self):
        return self._mode == ExtractorMode.NUISANCE

    ## Returns true if extractable mode is nuisance with asymmetric limits
    def isAsymmetricNuisance(self):
        return self._mode == ExtractorMode.ASYMMETRICNUISANCE

    ## Returns true if extractable mode is shape nuisance
    def isShapeNuisance(self):
        return self._mode == ExtractorMode.SHAPENUISANCE

    ## True if nuisance will generate a new line in output (i.e. is not merged)
    def isPrintable(self):
        return self._isPrintable

    ## True if the id of the current extractable or it's master is the same as the asked one
    def isId(self, exid):
        return self._exid == exid or self._masterExID == exid

    ## Returns id of master
    def getMasterId(self):
        return self._masterExID

    ## Returns id
    def getId(self):
        return self._exid

    ## Returns distribution string
    def getDistribution(self):
        return self._distribution

    ## Returns description string
    def getDescription(self):
        return self._description

    ## Adds extractable to list of extractables to be merged
    def addExtractorToBeMerged(self, extractable):
        self._extractablesToBeMerged.append(extractable)
        extractable.setAsSlave(self._exid)

    ## Disables printing of extractable and sets id of master 
    def setAsSlave(self, masterId):
        self._isPrintable = False
        self._masterExID = masterId

    ## Returns the counter histogram
    def getCounterHistogram(self, rootFile, counterHisto):
        histo = rootFile.Get(counterHisto)
        if not histo:
            raise Exception(ErrorStyle()+"Error:"+NormalStyle()+" Cannot find counter histogram '"+counterHisto+"'!")
        return histo

    ## Returns index to bin corresponding to first matching label in a counter histogram
    def getCounterItemIndex(self, histo, counterItem):
        for i in range(1, histo.GetNbinsX()+1):
            if histo.GetXaxis().GetBinLabel(i) == myBinLabel:
                return i
        raise Exception(ErrorStyle()+"Error:"+NormalStyle()+" Cannot find counter by name "+counterItem+"!")

    ## Virtual method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        return -1.0

    ## Virtual method for extracting histograms
    def extractHistograms(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        return None

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "- mode = ", self._mode
        print "- extractable ID = ", self._exid
        if self.isAnyNuisance():
            print "- distribution = ", self._distribution
            print "- description = ", self._description
            if not self.isPrintable():
                print "- is slave of extractable with ID = ", self._masterExID

    # obsolete methods ?
    # double getMergedValue(std::vector< Dataset* > datasets, NormalisationInfo* info, double hostValue); // Returns first non zero value

    ## \var _mode
    # Enumerator for data mining mode
    ## \var _distribution
    # string keyword of distribution (usually lnN, see LandS manual for more options)
    ## \var _exid
    # Unique ID (string) of the extractable
    ## \var _description
    # string for describing a nuisance parameter
    ## \var _extractablesToBeMerged
    # list of extractables whose results are to be merged to this one (practically an or function or extractables)
    ## \var _isPrintable
    # if true the extractable will generate a new line in output
    ## \var _masterExID
    # the ID of the master extractable (i.e. specifies line on which this extractable output is printed)

## ConstantExtractor class
# Returns a fixed constant number
class ConstantExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, constantValue, mode, exid = "", distribution = "lnN", description = "", constantUpperValue = 0.0):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._constantValue = constantValue
        self._constantUpperValue = constantUpperValue

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myResult = None
        if self.isAsymmetricNuisance():
            myResult = [-(self._constantValue), self._constantUpperValue]
        else:
            myResult = self._constantValue
        return myResult

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "ConstantExtractor"
        if self.isAsymmetricNuisance():
            print "- value = ", self._constantValue, "/", self._constantUpperValue
        else:
            print "- value = ", self._constantValue
        ExtractorBase.printDebugInfo(self)

    ## \var _constantValue
    # Constant value (either rate or nuisance in percent)
    ## \var _constantUpperValue
    # Constant value for upper bound (either rate or nuisance in percent)

## CounterExtractor class
# Extracts a value from a given counter in the list of main counters
class CounterExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, counterItem, mode, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._counterItem = counterItem

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myCount = mainCounterTable.getCount(rowName=self._counterItem, colName=datasetColumn.getDatasetMgrColumn())
        # Return result
        myResult = None
        if self.isRate() or self.isObservation():
            myResult = myCount.value() * additionalNormalisation
            if additionalNormalisation != 1.0 and self.isRate():
                print "      (normalisation applied) rate = %f, rate*normalisation = %f"%(myCount.value(),myResult)
        elif self.isNuisance():
            # protection against zero
            if myCount.value() == 0:
                print WarningStyle()+"Warning:"+NormalStyle()+" In Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"' counter ('"+self._counterItem+"') value is zero!"
                myResult = 0.0
            else:
                myResult = myCount.uncertainty() / myCount.value()
        return myResult

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "CounterExtractor"
        print "- counter item = ", self._counterItem
        ExtractorBase.printDebugInfo(self)

    ## \var _counterItem
    # Name of item (label) in counter histogram

## MaxCounterExtractor class
# Extracts a value from a given counter item in the list of main counters and compares it to the reference value
# Largest deviation from the reference (nominal) value is taken
class MaxCounterExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, counterDirs, counterItem, mode, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._counterItem = counterItem
        self._counterDirs = counterDirs
        if len(self._counterDirs) < 2:
            raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"':"+NormalStyle()+" need to specify at least two directories for counters!")

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myResult = []
        for d in self._counterDirs:
            myHistoPath = d+"/weighted/counter"
            try:
                datasetRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoPath)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting max counter value:"+NormalStyle()+" cannot find histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
            datasetRootHisto.normalizeToLuminosity(luminosity)
            myHisto = datasetRootHisto.getHistogram()
            counterList = _histoToCounter(myHisto)
            myHisto.IsA().Destructor(myHisto)
            myFoundStatus = False # to ensure that the first counter of given name is taken
            for name, count in counterList:
                if name == self._counterItem and not myFoundStatus:
                    myResult.append(count)
                    myFoundStatus = True
            if not myFoundStatus:
                raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" Cannot find counter name '"+self._counterItem+"' in histogram '"+myHistoPath+"'!")
        # Loop over results
        myMaxValue = 0.0
        # Protect for div by zero
        if myResult[0].value() == 0:
            print WarningStyle()+"Warning:"+NormalStyle()+" In Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"' nominal counter ('"+self._counterItem+"')value is zero!"
        else:
            for i in range(1,len(myResult)):
                myValue = abs(myResult[i].value() / myResult[0].value() - 1.0)
                if (myValue > myMaxValue):
                    myMaxValue = myValue
        return myMaxValue

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "MaxCounterExtractor"
        print "- counter item = ", self._counterItem
        ExtractorBase.printDebugInfo(self)

    ## \var _counterDirs
    # List of directories (without /weighted/counter suffix ) for counter histograms; first needs to be the nominal counter
    ## \var _counterItem
    # Name of item (label) in counter histogram

## PileupUncertaintyExtractor class
# Extracts counter values after selection for nominal case and up/down variations and returns the max. deviation from the nominal, i.e. max(up/nominal, down/nominal)
class PileupUncertaintyExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, counterDirs, counterItem, mode, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._counterItem = counterItem
        self._counterDirs = counterDirs
        if len(self._counterDirs) < 2:
            raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"':"+NormalStyle()+" need to specify at least two directories for counters!")

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myResult = []

        # Normalise with up/down to get up/down histograms
        # mgr.updateNAllEventsToPUWeighted(weightType=PileupWeightType.UP) #FIXME
        # mgr.updateNAllEventsToPUWeighted(weightType=PileupWeightType.DOWN) #FIXME
        for d in self._counterDirs:
            myHistoName = d+"/counters/weighted/counter"
            try:
                datasetRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoName)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting PU uncertainty:"+NormalStyle()+" cannot find histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
            datasetRootHisto.normalizeToLuminosity(luminosity)
            myHisto = datasetRootHisto.getHistogram()
            counterList = _histoToCounter(myHisto)
            myHisto.IsA().Destructor(myHisto)
            myFoundStatus = False # to ensure that the first counter of given name is taken
            for name, count in counterList:
                if name == self._counterItem and not myFoundStatus:
                    myResult.append(count)
                    myFoundStatus = True
            if not myFoundStatus:
                raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" Cannot find counter name '"+self._counterItem+"' in histogram '"+myHistoName+"'!")
        # Revert back to nominal normalisation
        # mgr.updateNAllEventsToPUWeighted(weightType=PileupWeightType.NOMINAL) #FIXME
        # Loop over results
        myMaxValue = 0.0
        # Protect for div by zero
        if myResult[0].value() == 0:
            print WarningStyle()+"Warning:"+NormalStyle()+" In Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"' nominal counter ('"+self._counterItem+"')value is zero!"
        else:
            for i in range(1,len(myResult)):
                myValue = abs(myResult[i].value() / myResult[0].value() - 1.0)
                if (myValue > myMaxValue):
                    myMaxValue = myValue
        return myMaxValue

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "MaxCounterExtractor"
        print "- counter item = ", self._counterItem
        ExtractorBase.printDebugInfo(self)

    ## \var _counterDirs
    # List of directories (without /weighted/counter suffix ) for counter histograms; first needs to be the nominal counter
    ## \var _counterItem
    # Name of item (label) in counter histogram


## RatioExtractor class
# Extracts two values from two counter items in the list of main counters and returns th ratio of these scaled by some factor
class RatioExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, scale, numeratorCounterItem, denominatorCounterItem, mode, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._numeratorCounterItem = numeratorCounterItem
        self._denominatorCounterItem = denominatorCounterItem
        self._scale = scale

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myNumeratorCount = mainCounterTable.getCount(rowName=self._numeratorCounterItem, colName=datasetColumn.getDatasetMgrColumn())
        myDenominatorCount = mainCounterTable.getCount(rowName=self._denominatorCounterItem, colName=datasetColumn.getDatasetMgrColumn())
        # Protection against div by zero
        if myDenominatorCount.value() == 0.0:
            print WarningStyle()+"Warning:"+NormalStyle()+" In Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"' denominator counter ('"+self._counterItem+"') value is zero!"
            myResult = 0.0
        else:
            myResult = (myDenominatorCount.value() / myNumeratorCount.value() - 1.0) * self._scale
        # Return result
        return myResult

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "RatioExtractor"
        print "- numeratorCounterItem = ", self._numeratorCounterItem
        print "- denominatorCounterItem = ", self._denominatorCounterItem
        ExtractorBase.printDebugInfo(self)

    ## \var _numeratorCounterItem
    # Name of item (label) in counter histogram for numerator count
    ## \var _denominatorCounterItem
    # Name of item (label) in counter histogram for denominator count
    ## \var _scale
    # Scaling factor for result (float)

## ScaleFactorExtractor class
# Extracts an uncertainty for a scale factor
class ScaleFactorExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, histoDirs, histograms, normalisation, addSystInQuadrature = 0.0, mode = ExtractorMode.NUISANCE, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._histoDirs = histoDirs
        self._histograms = histograms
        self._normalisation = normalisation
        self._addSystInQuadrature = addSystInQuadrature
        if len(self._histoDirs) != len(self._normalisation) or len(self._histoDirs) != len(self._histograms):
            raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" need to specify equal amount of histoDirs, histograms and normalisation histograms!")

    ## Method for extracking information
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        myResult = []
        for i in range (0, len(self._histoDirs)):
            myTotal = 0.0
            mySum = 0.0
            myHistoName = self._histoDirs[i]+"/"+self._histograms[i]
            if self._histoDirs[i] == "":
                myHistoName = self._histograms[i]
            try:
                myValueRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoName)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting scale factor uncertainty:"+NormalStyle()+" cannot find value histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
            myValueRootHisto.normalizeToLuminosity(luminosity)
            hValues = myValueRootHisto.getHistogram()
            if hValues == None:
                raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" Cannot open histogram '"+myHistoName+"'!")
            myHistoName = self._histoDirs[i]+"/"+self._normalisation[i]
            try:
                myNormalisationRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoName)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting scale factor uncertainty:"+NormalStyle()+" cannot find normalisation histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
            myNormalisationRootHisto.normalizeToLuminosity(luminosity)
            hNormalisation = myNormalisationRootHisto.getHistogram()
            if hNormalisation == None:
                raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" Cannot open histogram '"+myHistoName+"'!")
            for j in range (1, hValues.GetNbinsX()+1):
                mySum += pow(hValues.GetBinContent(j) * hValues.GetBinCenter(j),2)
            myTotal = hNormalisation.GetBinContent(1)
            hValues.IsA().Destructor(hValues)
            hNormalisation.IsA().Destructor(hNormalisation)
            # Calculate result, protection against div by zero
            if myTotal == 0.0:
                print WarningStyle()+"Warning:"+NormalStyle()+" In Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"' total count from normalisation histograms is zero!"
                myResult.append(0.0)
            else:
                myResult.append(sqrt(mySum) / myTotal)
        # Combine result
        myCombinedResult = 0.0
        for i in range (0, len(self._histoDirs)):
            myCombinedResult += pow(myResult[i], 2)
        myCombinedResult += pow(self._addSystInQuadrature, 2)
        # Return result
        return sqrt(myCombinedResult)


    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "MaxCounterExtractor"
        print "- counter item = ", self._counterItem
        ExtractorBase.printDebugInfo(self)

    ## \var _counterDirs
    # List of directories (without /weighted/counter suffix ) for counter histograms; first needs to be the nominal counter
    ## \var _counterItem
    # Name of item (label) in counter histogram

## ShapeExtractor class
# Extracts histogram shapes
class ShapeExtractor(ExtractorBase):
    ## Constructor
    def __init__(self, histoSpecs, histoDirs, histograms, mode = ExtractorMode.NUISANCE, exid = "", distribution = "lnN", description = ""):
        ExtractorBase.__init__(self, mode, exid, distribution, description)
        self._histoSpecs = histoSpecs
        self._histoDirs = histoDirs
        self._histograms = histograms
        if len(self._histoDirs) != len(self._histograms):
            raise Exception(ErrorStyle()+"Error in Rate/Nuisance with id='"+str(self._exid)+"':"+NormalStyle()+" need to specify equal amount of histoDirs and histograms!")
        if len(self._histoDirs) == 0 and self._description != "empty":
            raise Exception(ErrorStyle()+"Error in Rate/Nuisance with id='"+str(self._exid)+"':"+NormalStyle()+" need to specify histoDirs and histograms!")
        if (self.isRate() or self.isObservation()):
            # Rate or observation needs to have exactly one entry (unless empty)
            if len(self._histoDirs) > 1:
                raise Exception(ErrorStyle()+"Error in Observation/Rate:"+NormalStyle()+"need to specify exactly one entry in both histoDirs and histograms!")
        else:
            # Shape nuisance
            if self._distribution == "shapeQ":
                # Shape variation nuisance needs to have exactly two entries (down, up)
                if len(self._histoDirs) != 2:
                    raise Exception(ErrorStyle()+"Error in Nuisance with id='"+str(self._exid)+"' (shapeQ):"+NormalStyle()+" need to specify exactly two entries (down and up) in both histoDirs and histograms!")
            elif self._distribution == "shapeStat": # bin-by-bin
                # Shape variation nuisance needs to have exactly one entry
                if len(self._histoDirs) != 1:
                    raise Exception(ErrorStyle()+"Error in Nuisance with id='"+str(self._exid)+"' (shapeStat):"+NormalStyle()+" need to specify exactly one entry in both histoDirs and histograms!")
            else:
                raise Exception(ErrorStyle()+"Error in Nuisance with id='"+str(self._exid)+"':"+NormalStyle()+" unknown option '"+self._distribution+"' for distribution! Options are 'shapeStat' and 'shapeQ'.")
        #if len(self._histoSpecs) != 3:
        #    raise Exception(ErrorStyle()+"Error in config:"+NormalStyle()+" need to specify to ShapeHistogramsDimensions as list, example = [20,0.0,400.0] (i.e. nbins, min, max)!")

    ## Method for extracking result
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        # Calculate up and down variation numerical values vs. nominal
        myResult = []
        if self._distribution == "shapeQ":
            myNominalRateCount = mainCounterTable.getCount(rowName=self._counterItem, colName=datasetColumn.getDatasetMgrColumn()).value()
            for i in range (0, len(self._histoDirs)):
                myHistoName = self._histoDirs[i]+"/counters/weighted/counter" #FIXME !!!! replace by using main counter table
                try:
                    datasetRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoName)
                except Exception, e:
                    raise Exception (ErrorStyle()+"Error in extracting shape uncertainty:"+NormalStyle()+" cannot find histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
                if datasetRootHisto.isMC():
                    datasetRootHisto.normalizeToLuminosity(luminosity)
                myHisto = datasetRootHisto.getHistogram()
                counterList = _histoToCounter(myHisto)
                myHisto.IsA().Destructor(myHisto)
                myFoundStatus = False # to ensure that the first counter of given name is taken
                for name, count in counterList:
                    if name == self._counterItem and not myFoundStatus:
                        if myNominalRateCount > 0:
                            myResult.append(abs(count.value()/myNominalRateCount-1.0))
                        else:
                            myResult.append(0.0)
                        myFoundStatus = True
                if not myFoundStatus:
                    raise Exception(ErrorStyle()+"Error in Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" Cannot find counter name '"+self._counterItem+"' in histogram '"+myHistoPath+"'!")
        return myResult

    ## Virtual method for extracting histograms
    def extractHistograms(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        # Construct labels for histograms
        myPrefix = datasetColumn.getLabel()
        myLabels = []
        if self.isRate() or self.isObservation():
            myLabels = [myPrefix]
        else:
            myLabels = [myPrefix+"_"+self._masterExID+"Down",
                        myPrefix+"_"+self._masterExID+"Up"]
        myHistograms = []
        myShapeModifier = ShapeHistoModifier(self._histoSpecs)
        for i in range (0, len(self._histoDirs)):
            # Create empty shape histogram
            h = myShapeModifier.createEmptyShapeHistogram(myLabels[i])
            # Obtain source histogram
            myHistoName = self._histoDirs[i]+"/"+self._histograms[i]
            if self._histoDirs[i] == "":
                myHistoName = self._histograms[i]
            #print "group",datasetColumn.getLabel(),"id",self._exid,"histo",myHistoName
            try:
                myDatasetRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoName)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting shape histogram:"+NormalStyle()+" cannot find histogram!\n  Column = %s\n  NuisanceId = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._exid, str(e)))
            if myDatasetRootHisto.isMC():
                myDatasetRootHisto.normalizeToLuminosity(luminosity)
            hSource = myDatasetRootHisto.getHistogram()
            myShapeModifier.addShape(dest=h,source=hSource)
            myShapeModifier.finaliseShape(dest=h)
            hSource.IsA().Destructor(hSource)
            # Add here substraction of negative bins, if necessary
            for k in range(1, h.GetNbinsX()+1):
                if h.GetBinContent(k) < 0.0:
                    if self.isRate() or self.isObservation():
                        print WarningStyle()+"Warning: Column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" rate histo bin %d is negative (%f), it is set to zero but total normalisation is maintained"%(k,h.GetBinContent(k))
                        myIntegral = h.Integral()
                        h.SetBinContent(k, 0.0)
                        if h.Integral() > 0:
                            h.Scale(myIntegral / h.Integral())
                    else:
                        print WarningStyle()+"Warning: Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" shape histo bin %d is negative (%f), it is forced to zero"%(k,h.GetBinContent(k))
                        h.SetBinContent(k, 0.0)
            # Scale by additional normalisation
            h.Scale(additionalNormalisation)
            # Append histogram to output list
            myHistograms.append(h)
        # Make histograms for shape stat
        if self._distribution == "shapeStat":
            # Make second histogram by cloning
            myHistograms.append(myHistograms[0].Clone(myLabels[1]))
            myHistograms[1].SetTitle(myLabels[1])
            # Substract/Add one sigma to get Down/Up variation
            for k in range(1, myHistograms[0].GetNbinsX()+1):
                myHistograms[0].SetBinContent(k, myHistograms[0].GetBinContent(k) - myHistograms[0].GetBinError(k))
                myHistograms[1].SetBinContent(k, myHistograms[1].GetBinContent(k) + myHistograms[1].GetBinError(k))
                if myHistograms[0].GetBinContent(k) < 0:
                    print WarningStyle()+"Warning: shapeStat Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" shapeDown histo bin %d is negative (%f), it is forced to zero"%(k,myHistograms[0].GetBinContent(k))
                    myHistograms[0].SetBinContent(k, 0.0)
                if myHistograms[1].GetBinContent(k) < 0:
                    print WarningStyle()+"Warning: shapeStat Nuisance with id='"+self._exid+"' for column '"+datasetColumn.getLabel()+"':"+NormalStyle()+" shapeUp histo bin %d is negative (%f), it is forced to zero"%(k,myHistograms[0].GetBinContent(k))
                    myHistograms[1].SetBinContent(k, 0.0)
        # No source for histograms for empty column; create an empty histogram with correct dimensions
        if (self.isRate() or self.isObservation()) and datasetColumn.typeIsEmptyColumn():
            h = myShapeModifier.createEmptyShapeHistogram(myLabels[0])
            myHistograms.append(h)
        # Return result
        return myHistograms

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "ShapeExtractor"
        print "- specs:",self._histoSpecs
        print "- histoDirs:",self._histoDirs
        print "- histograms:",self._histograms
        print "- counter item = ", self._counterItem
        ExtractorBase.printDebugInfo(self)

## ControlPlotExtractor class
# Extracts histograms for control plot
class ControlPlotExtractor(ExtractorBase):
    ## Constructor, note that if multiplet directories and names are given, the second, third, etc. are substracted from the first one
    def __init__(self, histoSpecs, histoTitle, histoDirs, histoNames):
        ExtractorBase.__init__(self, mode=ExtractorMode.CONTROLPLOT, exid="-1", distribution="-", description="-")
        self._histoSpecs = histoSpecs
        self._histoTitle = histoTitle
        self._histoDirs = []
        if isinstance(histoDirs, list):
            self._histoDirs.extend(histoDirs)
        else:
            self._histoDirs.append(histoDirs)
        self._histoNames = []
        if isinstance(histoNames, list):
            self._histoNames.extend(histoNames)
        else:
            self._histoNames.append(histoNames)
        if len(self._histoDirs) != len(self._histoNames):
            raise Exception (ErrorStyle()+"Error in ControlPlot "+histoTitle+":"+NormalStyle()+" need to specify equal amount of histoDirs and histoNames!")

    ## Method for extracking result
    def extractResult(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        print WarningStyle()+"Did you actually call extractResult for a ControlPlot by name "+self._histoTitle+"? (you shouldn't)"+NormalStyle()
        return 0.0 # Dummy number, this method

    ## Virtual method for extracting histograms
    def extractHistograms(self, datasetColumn, dsetMgr, mainCounterTable, luminosity, additionalNormalisation = 1.0):
        # Create an empty histogram
        myLabel = datasetColumn.getLabel()+"_"+self._histoTitle
        myShapeModifier = ShapeHistoModifier(self._histoSpecs)
        h = myShapeModifier.createEmptyShapeHistogram(myLabel)
        for i in range (0, len(self._histoDirs)):
            #print "Extractor ",self._histoDirs[i],self._histoNames[i]
            # Obtain histogram from dataset
            myHistoname = self._histoDirs[i]+"/"+self._histoNames[i]
            if self._histoDirs[i] == "":
                myHistoname = self._histoNames[i]
            try:
                myDatasetRootHisto = dsetMgr.getDataset(datasetColumn.getDatasetMgrColumn()).getDatasetRootHisto(myHistoname)
            except Exception, e:
                raise Exception (ErrorStyle()+"Error in extracting ControlPlots:"+NormalStyle()+" cannot find histogram!\n  Column = %s\n  Histogram title = %s\n  Message = %s!"%(datasetColumn.getLabel(),self._histoTitle, str(e)))
            if myDatasetRootHisto.isMC():
                myDatasetRootHisto.normalizeToLuminosity(luminosity)
            hSource = myDatasetRootHisto.getHistogram()
            if i == 0:
                myShapeModifier.addShape(dest=h,source=hSource)
            else:
                myShapeModifier.subtractShape(dest=h,source=hSource)
            hSource.IsA().Destructor(hSource)
        # Finalise histogram
        myShapeModifier.finaliseShape(dest=h)
        # Apply additional normalisation
        h.Scale(additionalNormalisation)
        # Add here substraction of negative bins, if necessary
        # ... no use case currently, therefore no code added
        # Return result
        return h

    ## Virtual method for printing debug information
    def printDebugInfo(self):
        print "ControlPlotExtractor"
        print "- title:",self._histoTitle
        print "- specs:",self._histoSpecs
        print "- histoDirs:",self._histoDirs
        print "- histoNames:",self._histoNames
        ExtractorBase.printDebugInfo(self)

