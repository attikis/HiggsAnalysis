#import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
#import HiggsAnalysis.HeavyChHiggsToTauNu.tools.CommonLimitTools as limitTools
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux as aux
#import HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles as ShellStyles

import os
import ROOT
ROOT.gROOT.SetBatch(True)

_fineBinningSuffix = "_fineBinning"
_originalDatacardDirectory = "originalDatacards"

### Get list of mass points
#def getMassPoints(directory="."):
    ## Find out the mass points
    #mySettings = limitTools.GeneralSettings(directory,[])
    #massPoints = mySettings.getMassPoints(limitTools.LimitProcessType.TAUJETS)
    #return massPoints

### Get luminosity
#def getLuminosity(directory=".", mass=None):
    #m = mass
    #if mass == None:
        #masslist = getMassPoints(directory)
        #m = masslist[0]
    #myLuminosity = float(limitTools.readLuminosityFromDatacard(directory, mySettings.getDatacardPattern(limitTools.LimitProcessType.TAUJETS)%m))
    #return myLuminosity

#mySettings = limitTools.GeneralSettings(directory,[])
#rootFilePattern = mySettings.getRootfilePattern(limitTools.LimitProcessType.TAUJETS)

class DataCardDirectoryManager:
    def __init__(self, directory, datacardFilePattern, rootFilePattern):
        self._datacards = {} # Dictionary, where key is mass and value is DataCardReader object for that mass point
        # Find datacard files
        myList = os.listdir(directory)
        mySplit = datacardFilePattern.split("%s")
        self._massPoints = []
        for item in myList:
            myStatus = True
            myStub = item
            for part in mySplit:
                myStub = myStub.replace(part,"")
                if not part in item:
                    myStatus = False
            if myStatus:
                self._massPoints.append(myStub)
        # initialize datacard objects
        for m in self._massPoints:
            self._datacards[m] = DataCardReader(directory, m, datacardFilePattern, rootFilePattern)

    def close(self):
        for key in self._datacards.keys():
            self._datacards[key].close()

    def replaceColumnNames(self, replaceDictionary):
        for m in self._datacards.keys():
            dcard = self._datacards[m]
            # Do replace in txt file
            for item in replaceDictionary.keys():
                for i in range(0,len(dcard.getDatasetNames())):
                    if dcard._datacardColumnNames[i] == item:
                        dcard._datacardColumnNames[i] = dcard._datacardColumnNames[i].replace(item, replaceDictionary[item])
                for i in range(0,len(dcard._datasetNuisances)):
                    if item in dcard._datasetNuisances[i].keys():
                        dcard._datasetNuisances[i][replaceDictionary[item]] = dcard._datasetNuisances[i][item]
                        del dcard._datasetNuisances[i][item]
                    if dcard._datasetNuisances[i]["name"].startswith(item+"_"):
                        dcard._datasetNuisances[i]["name"] = dcard._datasetNuisances[i]["name"].replace(item, replaceDictionary[item])
            # Do Replace in root file
            for item in replaceDictionary.keys():
                myList = dcard.getRootFileObjectsWithPattern(item)
                # Loop over root objects
                for objectName in myList:
                    o = dcard.getRootFileObject(objectName)
                    o.SetName(o.GetName().replace(item, replaceDictionary[item]))
    
    def replaceNuisanceNames(self, replaceDictionary):
        for m in self._datacards.keys():
            dcard = self._datacards[m]
            # Do replace in txt file
            for item in replaceDictionary.keys():
                for i in range(0,len(dcard._datasetNuisances)):
                    if dcard._datasetNuisances[i]["name"] == item:
                        dcard._datasetNuisances[i]["name"] = dcard._datasetNuisances[i]["name"].replace(item, replaceDictionary[item])
            # Do Replace in root file
            for item in replaceDictionary.keys():
                myList = dcard.getRootFileObjectsWithPattern(item)
                # Loop over root objects
                for objectName in myList:
                    o = self._datacards[m].getRootFileObject(objectName)
                    o.SetName(o.GetName().replace(item, replaceDictionary[item]))

    def recreateShapeStatUncert(self):
        for m in self._datacards.keys():
            dcard = self._datacards[m]
            # Remove previous entries from datacard
            i = 0
            while i < len(dcard._datasetNuisances):
                nuisanceName = dcard._datasetNuisances[i]["name"]
                if "stat" in nuisanceName or "Stat" in nuisanceName:
                    dcard._datasetNuisances.remove(dcard._datasetNuisances[i])
                else:
                    i += 1
            # Remove previous histograms from datacard
            i = 0
            while i < len(dcard._hCache):
                histoName = dcard._hCache[i].GetName()
                if "stat" in histoName or "Stat" in histoName:
                    dcard._hCache[i].Delete()
                    dcard._hCache.remove(dcard._hCache[i])
                else:
                    i += 1
            # Loop over columns and 
            for c in dcard.getDatasetNames():
                hRate = dcard.getRateHisto(c)
                # Loop over bins in rate
                for nbin in range(1, hRate.GetNbinsX()+1):
                    # Check for overlapping bin-by-bin stat. uncertainties
                    myList = dcard.getRootFileObjectsWithPattern(c)
                    if not ("bin%s"%nbin in myList or "Bin%s"%nbin in myList):
                        # Add entries to datacard
                        myDict = {}
                        myDict["name"] = "%s_statBin%d"%(c, nbin)
                        myDict["distribution"] = "shape"
                        for cc in dcard.getDatasetNames():
                            if cc == c:
                                myDict[cc] = "1"
                            else:
                                myDict[cc] = "-"
                        dcard._datasetNuisances.append(myDict)
                        # Add histograms
                        hUp = aux.Clone(hRate)
                        hDown = aux.Clone(hRate)
                        hUp.SetName("%s_%s_statBin%dUp"%(c, c, nbin))
                        hDown.SetName("%s_%s_statBin%dDown"%(c, c, nbin))
                        hUp.SetBinContent(nbin, hUp.GetBinContent(nbin)+hUp.GetBinError(nbin))
                        hDown.SetBinContent(nbin, hDown.GetBinContent(nbin)-hDown.GetBinError(nbin))
                        for k in range(1, hRate.GetNbinsX()+1):
                            hUp.SetBinError(k, 0.0)
                            hDown.SetBinError(k, 0.0)
                        dcard.addHistogram(hUp)
                        dcard.addHistogram(hDown)

## Calculates maximum width of each table cell
def calculateCellWidths(widths,table):
    myResult = widths
    # Initialise widths if necessary
    if len(table) == 0:
      return myResult

    for i in range(len(widths),len(table[0])):
        myResult.append(0)
    # Loop over table cells
    for row in table:
        for i in range(0,len(row)):
            if len(row[i]) > myResult[i]:
                myResult[i] = len(row[i])
    return myResult

## Returns a separator line of correct total width
def getSeparatorLine(widths):
    myTotalSize = 0
    for cell in widths:
        myTotalSize += cell+1
    myTotalSize -= 1
    myResult = ""
    for i in range(0,myTotalSize):
        myResult += "-"
    myResult += "\n"
    return myResult

## Converts a list into a string
def getTableOutput(widths,table,latexMode=False):
    myResult = ""
    for row in table:
        for i in range(0,len(row)):
            if i != 0:
                myResult += " "
                if latexMode:
                    myResult += "& "
            myResult += row[i].ljust(widths[i])
        if latexMode:
            myResult += " \\\\ "
        myResult += "\n"
    return myResult

## Class for containing all information related to a single datacard
class DataCardReader:
    def __init__(self, directory, mass, datacardFilePattern, rootFilePattern):
        # Initialize
        self._directory = directory
        self._mass = mass
        self._datacardFilePattern = datacardFilePattern
        self._rootFilePattern = rootFilePattern
        self._rootFilename = None
        self._datacardFilename = None
        self._hCache = [] # Cache for persistent histograms
        # DatacardInfo
        self._datacardColumnNames = [] # List of columns in datacard
        self._datacardBinName = None
        self._datacardColumnStartIndex = None # Index of first column
        self._datacardHeaderLines = []
        self._observationValue = None
        self._rateValues = {} # Dictionary, where key is dataset name and value is a string of the rate value
        self._datasetNuisances = [] # List of dictionaries, where key is nuisance name

        # Read contents
        self._readDatacardContents(directory, mass)
        self._readRootFileContents(directory, mass)
        
    def close(self):
        print "Writing datacard:",self._datacardFilename
        self._writeDatacardContents()
        
        print "Closing file:",self._rootFilename
        self._writeRootFileContents()

    def getDatasetNames(self):
        return self._datacardColumnNames

    def getNuisanceNamesByDatasetName(self, datasetName):
        self.hasDatasetByName(datasetName, exceptionOnFail=True)
        return self._datasetNuisances[datasetName]

    def hasDatasetByName(self, datasetName, exceptionOnFail=False):
        if not datasetName in self._datacardColumnNames:
            if exceptionOnFail:
                raise Exception("Dataset '%s' not found!"%datasetName)
            return False
        return True

    def datasetHasNuisance(self, datasetName, nuisanceName, exceptionOnFail=False):
        self.hasDatasetByName(datasetName)
        if not nuisanceName in self._datasetNuisances[datasetName]:
            if exceptionOnFail:
                raise Exception("Dataset '%s' does not have nuisance '%s'!"%(datasetName,nuisanceName))
            return False
        return True
      
    def getRateHisto(self, datasetName, fineBinned=False, exceptionOnFail=True):
        self.hasDatasetByName(datasetName, exceptionOnFail=True)
        name = datasetName
        if fineBinned:
            name += _fineBinningSuffix
        for item in self._hCache:
            if item.GetName() == name:
                return item # no clone should be returned
        if exceptionOnFail:
            raise Exception("Could not find histogram '%s'!"%name)
        return None
    
    def getNuisanceHistos(self, datasetName, nuisanceName, exceptionOnFail=True, fineBinned=False):
        self.datasetHasNuisance(datasetName, nuisanceName, exceptionOnFail=True)
        name = "%s_%s"%(datasetName, nuisanceName)
        if "Bin" in name:
            name = "%s_%s"%(datasetName, name) # bin-by-bin uncert. replicate the dataset name
        if fineBinned:
            name += _fineBinningSuffix
        up = None
        down = None
        for item in self._hCache:
            if item.GetName == name+"Up":
                up = item
            elif item.GetName == name+"Down":
                down = item
        if up == None:
            if exceptionOnFail:
                raise Exception("Could not find histogram '%s'!"%name+"Up")
            return (None, None)
        if down == None:
            if exceptionOnFail:
              raise Exception("Could not find histogram '%s'!"%name+"Down")
            return (None, None)
        return (up, down) # no clone should be returned

    def debug(self):
        print "DEBUG info of DataCardReader:"
        names = self.getDatasetNames()
        #for n in names:
            #print "..  dset=%s has shape nuisances:"%n
            #print ".... %s"%", ".join(map(str,self.getNuisanceNamesByDatasetName(n)))
    
    def addHistogram(self, h):
        self._hCache.append(aux.Clone(h))
    
    def _readRootFileContents(self, directory, mass):
        self._rootFilename = os.path.join(directory, self._rootFilePattern%mass)
        # Make backup of original cards
        if not os.path.exists(_originalDatacardDirectory):
            os.mkdir(_originalDatacardDirectory)
        if not os.path.exists(os.path.join(_originalDatacardDirectory,self._rootFilename)):
            os.system("cp %s %s/."%(os.path.join(_originalDatacardDirectory,self._rootFilename), _originalDatacardDirectory))
        else:
            os.system("cp %s ."%(os.path.join(_originalDatacardDirectory,self._rootFilename)))
        # Open file
        print "Opening file:",self._rootFilename
        f = ROOT.TFile.Open(self._rootFilename)
        if f == None:
            raise Exception("Error opening file '%s'!"%self._rootFilename)
        # Read histograms to cache
        myHistoNames = ["data_obs"]
        for c in self._datacardColumnNames:
            myHistoNames.append(c)
            for n in self._datasetNuisances:
                if n["distribution"] == "shape" and n[c] == "1":
                    myHistoNames.append("%s_%sUp"%(c,n["name"]))
                    myHistoNames.append("%s_%sDown"%(c,n["name"]))
        for name in myHistoNames:
            o = f.Get(name)
            if o == None:
                raise Exception("Error: cannot find histo '%s' in root file '%s'!"%(name, self._rootFilename))
            self._hCache.append(aux.Clone(o))
        f.Close()

    def _writeRootFileContents(self):
        f = ROOT.TFile.Open(self._rootFilename, "RECREATE")
        if f == None:
            raise Exception("Error opening file '%s'!"%self._rootFilename)
        for h in self._hCache:
            h.SetDirectory(f)
            print h.GetName()
        f.Write()
        f.Close()
        self._hCache = []

    def getRootFileObjectsWithPattern(self, pattern):
        myOutList = []
        for item in self._hCache:
            if pattern in item.GetName():
                myOutList.append(item.GetName())
        return myOutList

    def getRootFileObject(self, objectName):
        for item in self._hCache:
            if item.GetName() == objectName:
                return item
        raise Exception("Error: Cannot find root object '%s' in root file '%s'!"%(objectName, self._rootFilename))

    def _readDatacardContents(self, directory, mass):
        self._datacardFilename = os.path.join(directory, self._datacardFilePattern%mass)
            # Make backup of original cards
        if not os.path.exists(_originalDatacardDirectory):
            os.mkdir(_originalDatacardDirectory)
        if not os.path.exists(os.path.join(_originalDatacardDirectory,self._datacardFilename)):
            os.system("cp %s %s/."%(os.path.join(_originalDatacardDirectory,self._datacardFilename), _originalDatacardDirectory))
        else:
            os.system("cp %s ."%(os.path.join(_originalDatacardDirectory,self._datacardFilename)))
        # Obtain datacard
        myOriginalCardFile = open(self._datacardFilename)
        myOriginalCardLines = myOriginalCardFile.readlines()
        myOriginalCardFile.close()
        # Parse datacard contents
        self._parseDatacardHeader(myOriginalCardLines)
        self._parseDatacardColumnNames(myOriginalCardLines)
        self._parseDatacardNuisanceNames(myOriginalCardLines)
        #print self._datacardHeaderLines
        #print self._observationValue
        #print self._rateValues
        #print self._datasetNuisances
    
    def _writeDatacardContents(self):
        myOutput = ""
        myObservedLine = ""
        # Create header
        for l in self._datacardHeaderLines:
            mySplit = l.split()
            if mySplit[0] == "observation":
                myOutput += "observation    %s\n"%self._observationValue
            else:
                myOutput += l
        # Create process lines
        myProcessTable = []
        myLine = ["bin",""]
        for c in self._datacardColumnNames:
            myLine.append(self._datacardBinName)
        myProcessTable.append(myLine)
        myProcessTable.append(["process",""]+self._datacardColumnNames[:])
        myLine = ["process",""]
        for i in range(0, len(self._datacardColumnNames)):
            myLine.append("%d"%(self._datacardColumnStartIndex+i))
        myProcessTable.append(myLine)
        # Create rate table
        myRateTable = []
        myRateTable.append(["rate",""]+self._rateValues[:])
        # Create nuisance table
        myNuisanceTable = []
        myStatTable = []
        for n in self._datasetNuisances:
            myRow = []
            # add first two entries
            myRow.append(n["name"])
            myRow.append(n["distribution"])
            # add data from columns
            for c in self._datacardColumnNames:
                myRow.append(n[c])
            # store
            if "stat" in n["name"] or "Stat" in n["name"]:
                myStatTable.append(myRow)
            else:
                myNuisanceTable.append(myRow)
        # Create stat.uncert. table
        
        # Do formatting
        myWidths = []
        for c in self._datacardColumnNames:
            myWidths.append(0)
        calculateCellWidths(myWidths, myProcessTable)
        calculateCellWidths(myWidths, myRateTable)
        calculateCellWidths(myWidths, myNuisanceTable)
        calculateCellWidths(myWidths, myStatTable)
        for i in range(0,len(myWidths)):
            if myWidths[i] < 9:
                myWidths[i] = 9
        mySeparatorLine = getSeparatorLine(myWidths)
        # Add tables to output
        myOutput += getTableOutput(myWidths, myProcessTable)
        myOutput += mySeparatorLine
        myOutput += getTableOutput(myWidths, myRateTable)
        myOutput += mySeparatorLine
        myOutput += getTableOutput(myWidths, myNuisanceTable)
        myOutput += mySeparatorLine
        myOutput += getTableOutput(myWidths, myStatTable)
        myOutput += mySeparatorLine
        # Save
        myOriginalCardFile = open(self._datacardFilename, "w")
        myOriginalCardFile.write(myOutput)
        myOriginalCardFile.close()


    ## Parse header from datacard file
    def _parseDatacardHeader(self, lines):
        self._datacardHeaderLines = []
        for l in lines:
            mySplit = l.split()
            if mySplit[0] == "bin":
                self._datacardBinName = mySplit[1]
            if mySplit[0] == "process":
                del self._datacardHeaderLines[len(self._datacardHeaderLines)-1]
                return
            self._datacardHeaderLines.append(l)
        raise Exception("This line should never be reached")
    
    ## Parse column names from datacard file
    def _parseDatacardColumnNames(self, lines):
        for i in range(0, len(lines)):
            mySplit = lines[i].split()
            if mySplit[0] == "process":
                self._datacardColumnNames = mySplit[1:]
                mySplitNext = lines[i+1].split()
                if mySplitNext[0] != "process":
                    raise Exception("Failed to find two consecutive rows starting with 'process'!")
                self._datacardColumnStartIndex = int(mySplitNext[1])
                #print self._datacardColumnStartIndex
                return
        raise Exception("This line should never be reached")

    ## Parse info of nuisances from datacard file
    def _parseDatacardNuisanceNames(self, lines):
        if len(self._datacardColumnNames) == 0:
            raise Exception("No column names found in datacard!")
        myNames = []
        myRateLinePassedStatus = False
        for l in lines:
            mySplit = l.split()
            if myRateLinePassedStatus and len(mySplit) > 1:# and not "statBin" in mySplit[0]:
                # store nuisance
                myDict = {}
                myDict["name"] = mySplit[0]
                myDict["distribution"] = mySplit[1]
                for i in range(2,len(mySplit)):
                    myDict[self._datacardColumnNames[i-2]] = mySplit[i]
                self._datasetNuisances.append(myDict)
            if mySplit[0] == "observation":
                # store observation
                self._observationValue = mySplit[1]
            if mySplit[0] == "rate":
                # store rate
                self._rateValues = mySplit[1:]
                myRateLinePassedStatus = True
        if len(self._datasetNuisances) == 0:
            raise Exception("No nuisances found!")

#def validateDatacards(directory="."):
    #def checkItem(testName, booleanTest, failMsg):
        #if booleanTest:
            #print ".. Test: %s: %sPASSED%s"%(testName, ShellStyles.TestPassedStyle(), ShellStyles.NormalStyle())
        #else:
            #print ".. Test: %s: %sFAILED%s"%(testName, ShellStyles.ErrorStyle(), ShellStyles.NormalStyle())
            #print failMsg
            #raise Exception()
        #return 1
  
    #nTests = 0
    #nMassPoints = 0
    #print "\n%sValidating datacards in directory: %s%s"%(ShellStyles.HighlightStyle(),directory,ShellStyles.NormalStyle())
    #massPoints = getMassPoints(directory)
    #if len(massPoints) == 0:
        #raise Exception ("No datacards found in directory '.'!"%directory)
    #for m in massPoints:
        #nMassPoints += 1
        #print "%sConsidering mass: %s%s"%(ShellStyles.HighlightStyle(),m,ShellStyles.NormalStyle())
        #reader = DataCardReader(directory, m)
        #for dset in reader.getDatasetNames():
            #hRate = reader.getRateHisto(dset)
            #myNuisanceNames = reader.getNuisanceNamesByDatasetName(dset)
            ## Check integral of fine binned and non-fine binned histogram
            #hRateFine = reader.getRateHisto(dset, fineBinned=True, exceptionOnFail=False)
            #if hRateFine != None and not "QCD" in dset: # for QCD there can be a difference because negative rate bins are forced to zero in rate histo
                #nTests += checkItem("(%s) Nominal rate vs. fine binned rate "%dset, 
                          #abs(hRate.Integral() / hRateFine.Integral()-1.0) < 0.0000001,
                          #"Nominal rate = %f, fine binned rate = %f"%(hRate.Integral(), hRateFine.Integral()))
            #else:
                #print "   (skipping test for Nominal rate vs. fine binned rate)"
            ## Check if rate is negative
            #for i in range(1,hRate.GetNbinsX()+1):
                #nTests += checkItem("(%s) rate >= 0 for bin %d"%(dset,i), hRate.GetBinContent(i) >= 0.0, "")
            ## Check bin-by-bin nuisances
            #if not "NoFitUncert" in directory and not "noSystUncert" in directory:
                #for i in range(1,hRate.GetNbinsX()+1):
                    #myNames = []
                    #for n in myNuisanceNames:
                        #if n.endswith("Bin%d"%i):
                            #myNames.append(n)
                    ## Check existence of bin-by-bin uncert.
                    #nTests += checkItem("(%s) has at least one bin-by-bin uncert. for bin %d"%(dset,i), len(myNames) > 0, "")
                    #nTests += checkItem("(%s) has exactly one bin-by-bin uncert. for bin %d"%(dset, i), len(myNames) == 1, "found nuisances: %s"%", ".join(map(str,myNames)))
                    #(up,down) = reader.getNuisanceHistos(dset, myNames[0])
                    #rate = hRate.GetBinContent(i)
                    #if (rate < 0.000001):
                        ## Check if zero rate bins are treated properly
                        #nTests += checkItem("(%s) rate=0 and bin-by-bin uncert. (%s) up != 0 for bin %d"%(dset,myNames[0],i), up.GetBinContent(i) > 0.000001, "You need to a non-zero value for the up uncert. in this case!")
                    #else:
                        ## Check that non-zero bins are no have a proper treatment
                        #nTests += checkItem("(%s) rate>0 and bin-by-bin uncert. (%s) up != rate for bin %d"%(dset,myNames[0],i), abs(rate-up.GetBinContent(i)) > 0.000001, "Sounds like a bug")
                        #nTests += checkItem("(%s) rate>0 and bin-by-bin uncert. (%s) down != rate for bin %d"%(dset,myNames[0],i), abs(rate-down.GetBinContent(i)) > 0.000001, "Sounds like a bug")
    #return (nTests, nMassPoints)
