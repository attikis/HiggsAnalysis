## \package TableProducer
# Classes for producing output
#
#

from HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.Extractor import ExtractorBase
from HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.DatacardColumn import DatacardColumn
from HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.ControlPlotMaker import ControlPlotMaker
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.systematics import ScalarUncertaintyItem
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux as aux
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.git as git

from math import pow,sqrt
import os
import sys
import time
import ROOT

## TableProducer class
class TableProducer:
    ## Constructor
    def __init__(self, opts, config, outputPrefix, luminosity, observation, datasetGroups, extractors, mcrabInfoOutput):
        self._opts = opts
        self._config = config
        self._outputPrefix = outputPrefix
        self._luminosity = luminosity
        self._observation = observation
        self._datasetGroups = datasetGroups
        self._extractors = extractors
        self._timestamp = time.strftime("%y%m%d_%H%M%S", time.gmtime(time.time()))
        if self._opts.lands:
            self._outputFileStem = "lands_datacard_hplushadronic_m"
            self._outputRootFileStem = "lands_histograms_hplushadronic_m"
        elif self._opts.combine:
            self._outputFileStem = "combine_datacard_hplushadronic_m"
            self._outputRootFileStem = "combine_histograms_hplushadronic_m"
        # Calculate number of nuisance parameters
        # Make directory for output
        myLimitCode = None
        if opts.lands:
            myLimitCode = "lands"
        elif opts.combine:
            myLimitCode = "combine"
        self._dirname = "datacards_%s_%s_%s_%s"%(myLimitCode,self._timestamp,self._config.DataCardName.replace(" ","_"),self._outputPrefix)
        os.mkdir(self._dirname)
        self._infoDirname = self._dirname + "/info"
        os.mkdir(self._infoDirname)
        self._ctrlPlotDirname = self._dirname + "/controlPlots"
        os.mkdir(self._ctrlPlotDirname)
        # Copy datacard to directory
        os.system("cp %s %s/inputDatacardForDatacardGenerator.py"%(opts.datacard, self._dirname))

        # Make control plots
        if self._config.OptionDoControlPlots:
            ControlPlotMaker(self._opts, self._config, self._ctrlPlotDirname, self._luminosity, self._observation, self._datasetGroups)
        else:
            print "\n"+WarningLabel()+"Skipped making of data-driven Control plots. To enable, set OptionDoControlPlots = True in the input datacard."

        # Make datacards
        self.makeDataCards()

        # Make other reports
        print "\n"+HighlightStyle()+"Generating reports"+NormalStyle()
        # Print table of shape variation for shapeQ nuisances
        self.makeShapeVariationTable()
        # Print event yield summary table
        self.makeEventYieldSummary()
        # Print systematics summary table
        self.makeSystematicsSummary()
        # Prints QCD purity information
        self.makeQCDPuritySummary()
        
        # Debugging info
        # Make copy of input datacard
        os.system("cp %s %s/input_datacard.py"%(self._opts.datacard,self._infoDirname))
        # Write input multicrab directory names
        f = open(os.path.join(self._infoDirname, "inputDirectories.txt"), "w")
        f.write("\n".join(map(str, mcrabInfoOutput))+"\n")
        f.close()
        f = open(os.path.join(self._infoDirname, "codeVersion.txt"), "w")
        f.write(git.getCommitId()+"\n")
        f.close()
        f = open(os.path.join(self._infoDirname, "codeStatus.txt"), "w")
        f.write(git.getStatus()+"\n")
        f.close()
        f = open(os.path.join(self._infoDirname, "codeDiff.txt"), "w")
        f.write(git.getDiff()+"\n")
        f.close()

    ## Returns name of results directory
    def getDirectory(self):
        return self._dirname

    ## Generates datacards
    def makeDataCards(self):

        # For combine, do some formatting
        if self._opts.combine:
            mySubtractAfterId = None
            mySmallestColumnId = 9
            # Find and remove empty column
            myRemoveList = []
            for c in self._datasetGroups:
                if c.getLandsProcess() < mySmallestColumnId:
                    mySmallestColumnId = c.getLandsProcess()
                if c.typeIsEmptyColumn():
                    mySubtractAfterId = c.getLandsProcess()
                    myRemoveList.append(c)
            if len(myRemoveList) > 0:
                self._datasetGroups.remove(c)
                print "Removed empty column for combine datacard"
            for c in self._datasetGroups:
                if c.getLandsProcess() > mySubtractAfterId:
                    c._landsProcess = c.getLandsProcess() - 1
            # Move column with ID -1 to zero
            #if mySmallestColumnId < 0:
            #    for c in self._datasetGroups:
            #        c._landsProcess = c.getLandsProcess() + 1

        self._purgeColumnsWithSmallRate()

        # Loop over mass points
        for m in self._config.MassPoints:
            print "\n"+HighlightStyle()+"Generating datacard for mass point %d for "%m +self._outputPrefix+NormalStyle()
            # Open output root file
            myFilename = self._dirname+"/"+self._outputFileStem+"%d.txt"%m
            myRootFilename = self._dirname+"/"+self._outputRootFileStem+"%d.root"%m
            myRootFile = ROOT.TFile.Open(myRootFilename, "RECREATE")
            if myRootFile == None:
                print ErrorStyle()+"Error:"+NormalStyle()+" Cannot open file '"+myRootFilename+"' for output!"
                sys.exit()
            # Invoke extractors
            if self._opts.verbose:
                print "TableProducer/producing observation line"
            myObservationLine = self._generateObservationLine()
            if self._opts.verbose:
                print "TableProducer/producing rate line"
            myRateHeaderTable = self._generateRateHeaderTable(m)
            myRateDataTable = self._generateRateDataTable(m)
            if self._opts.verbose:
                print "TableProducer/producing nuisance lines"
            myNuisanceTable = self._generateNuisanceTable(m)
            # Calculate dimensions of tables
            myWidths = []
            myWidths = self._calculateCellWidths(myWidths, myRateHeaderTable)
            myWidths = self._calculateCellWidths(myWidths, myRateDataTable)
            myWidths = self._calculateCellWidths(myWidths, myNuisanceTable)
            mySeparatorLine = self._getSeparatorLine(myWidths)
            # Construct datacard
            myCard = ""
            myCard += self._generateHeader(m)
            myCard += mySeparatorLine
            myCard += self._generateParameterLines(len(myNuisanceTable))
            myCard += mySeparatorLine
            myCard += self._generateShapeHeader(m)
            myCard += mySeparatorLine
            myCard += myObservationLine
            myCard += mySeparatorLine
            myCard += self._getTableOutput(myWidths,myRateHeaderTable)
            myCard += mySeparatorLine
            myCard += self._getTableOutput(myWidths,myRateDataTable)
            myCard += mySeparatorLine
            myCard += self._getTableOutput(myWidths,myNuisanceTable)
            # Print datacard to screen if requested
            if self._opts.showDatacard:
                if self._config.BlindAnalysis:
                    print WarningStyle()+"You are BLINDED: Refused cowardly to print datacard on screen (you're not supposed to look at it)!"+NormalStyle()
                else:
                    print myCard
            # Save datacard to file
            myFile = open(myFilename, "w")
            myFile.write(myCard)
            myFile.close()
            print "Written datacard to:",myFilename
            # Save histograms to root file
            self._saveHistograms(myRootFile,m),
            # Close root file
            myRootFile.Write()
            myRootFile.Close()
            print "Written shape root file to:",myRootFilename

    ## Purge columns with zero rate
    def _purgeColumnsWithSmallRate(self):
        myLastUntouchableLandsProcessNumber = 0 # For sigma x br
        if not self._config.OptionLimitOnSigmaBr and (self._datasetGroups[0].getLabel()[:2] == "HW" or self._datasetGroups[1].getLabel()[:2] == "HW"):
            if self._opts.lands:
                myLastUntouchableLandsProcessNumber = 2 # For light H+ physics model
            elif self._opts.combine:
                myLastUntouchableLandsProcessNumber = 1 # For light H+ physics model
        myIdsForRemoval = []
        for c in self._datasetGroups:
            if c.getLandsProcess() > myLastUntouchableLandsProcessNumber:
                if abs(c._rateResult.getResult()) < self._config.ToleranceForMinimumRate:
                    # Zero rate, flag column for removal
                    myIdsForRemoval.append(c.getLandsProcess())
        # Remove columns
        for i in myIdsForRemoval:
            for c in self._datasetGroups:
                if c.getLandsProcess() == i:
                    print WarningLabel()+"Rate for column '%s' (%f) is smaller than %f. Removing column from datacard."%(c.getLabel(),c._rateResult.getResult(),self._config.ToleranceForMinimumRate)
                    self._datasetGroups.remove(c)
        # Update process numbers
        for c in self._datasetGroups:
            offset = 0
            for i in myIdsForRemoval:
                if int(c.getLandsProcess()) > int(i):
                    offset += 1
            c._landsProcess -= offset

    ## Generates header of datacard
    def _generateHeader(self, mass=None):
        myString = ""
        myLimitCode = None
        if self._opts.lands:
            myLimitCode = "LandS"
        elif self._opts.combine:
            myLimitCode = "Combine"
        if mass == None:
            myString += "Description: %s datacard (auto generated) luminosity=%f 1/pb, %s/%s\n"%(myLimitCode, self._luminosity,self._config.DataCardName,self._outputPrefix)
        else:
            myString += "Description: %s datacard (auto generated) mass=%d, luminosity=%f 1/pb, %s/%s\n"%(myLimitCode, mass,self._luminosity,self._config.DataCardName,self._outputPrefix)
        myString += "Date: %s\n"%time.ctime()
        return myString

    ## Generates parameter lines
    def _generateParameterLines(self, kmax):
        # Produce result
        myResult =  "imax     1     number of channels\n"
        myResult += "jmax     *     number of backgrounds\n"
        myResult += "kmax    %2d     number of parameters\n"%kmax
        return myResult

    ## Generates shape header
    def _generateShapeHeader(self,mass):
        myResult = "shapes * * %s%d.root $PROCESS $PROCESS_$SYSTEMATIC\n"%(self._outputRootFileStem,mass)
        return myResult

    ## Generates observation lines
    def _generateObservationLine(self):
        # Obtain observed number of events
        if self._observation == None:
            return "Observation    is not specified\n"
        myObsCount = self._observation.getRateResult()
        if self._opts.debugMining:
            print "  Observation is %d"%myObsCount
        if self._opts.lands:
            myResult = "Observation    %d\n"%myObsCount
        elif self._opts.combine:
            myResult =  "bin            taunuhadr\n"
            myResult += "observation    %d\n"%myObsCount
        return myResult

    ## Generates header for rate table as list
    def _generateRateHeaderTable(self,mass):
        myResult = []
        # obtain bin numbers
        myRow = ["bin",""]
        for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
            if c.isActiveForMass(mass,self._config):
                if self._opts.lands:
                    myRow.append("1")
                elif self._opts.combine:
                    myRow.append("taunuhadr")
        myResult.append(myRow)
        # obtain labels
        myRow = ["process",""]
        for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
            if c.isActiveForMass(mass,self._config):
                myRow.append(c.getLabel())
        myResult.append(myRow)
        # obtain process numbers
        myRow = ["process",""]
        myOffset = 0
        for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
            if c.isActiveForMass(mass,self._config):
                myRow.append(str(c.getLandsProcess()+myOffset))
            else:
                if c.getLabel() == "res.": # Take into account that the empty column is no longer needed for sigma x Br limits
                    myOffset -= 1
        myResult.append(myRow)
        return myResult

    ## Generates rate numbers for rate table as list
    def _generateRateDataTable(self,mass):
        myResult = []
        myRow = ["rate",""]
        for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
            if c.isActiveForMass(mass,self._config):
                if self._opts.verbose:
                    print "- obtaining cached rate for column %s"%c.getLabel()
                myRateValue = c.getRateResult()
                if myRateValue == None:
                    myRateValue = 0.0
                if self._opts.debugMining:
                    print "  Rate for '%s' = %.3f"%(c.getLabel(),myRateValue)
                # Need better precision for sigma x br limits
                if (self._config.OptionLimitOnSigmaBr or mass > 179) and c.getLandsProcess() <= 0:
                    myRow.append("%.6f"%myRateValue)
                else:
                    myRow.append("%.3f"%myRateValue)
        myResult.append(myRow)
        return myResult

    ## Generates nuisance table as list
    def _generateNuisanceTable(self,mass):
        myResult = []
        myVetoList = [] # List of nuisance id's to veto
        mySingleList = [] # List of nuisance id's that apply only to single column
        # Suppress nuisance rows that are not affecting anything
        for n in self._extractors:
            myCount = 0
            for c in self._datasetGroups:
                if c.isActiveForMass(mass,self._config) and n.isPrintable() and c.hasNuisanceByMasterId(n.getId()):
                    myCount += 1
            if myCount == 0 and n.isPrintable():
                print WarningLabel()+"Suppressed nuisance %s: '%s' because it does not affect any data column!"%(n.getId(),n.getDescription())
                myVetoList.append(n.getId())
            if myCount == 1:
                mySingleList.append(n.getId())
        # Merge nuisances (quadratic sum) together, if they apply to only one column (is mathematically equal treatrment, but makes datacard running faster)
        # Note that it is not possible to merge physically the nuisances, because it would affect all other parts as well
        # Only solution is to do a virtual merge affecting only this method
        myVirtualMergeInformation = {}
        myVirtuallyInactivatedIds = []
        for c in self._datasetGroups:
            if c.isActiveForMass(mass,self._config):
                myFoundSingles = []
                for n in self._extractors:
                    if c.hasNuisanceByMasterId(n.getId()) and n.getId() in mySingleList and not n.isShapeNuisance():
                        myFoundSingles.append(n.getId())
                if len(myFoundSingles) > 1:
                    # Do virtual merge
                    myDescription = ""
                    myValue = ScalarUncertaintyItem("sum",0.0)
                    for n in self._extractors:
                        if n.getId() in myFoundSingles:
                            if myDescription == "":
                                myDescription = n.getDescription()
                                myValue.add(c.getNuisanceResultByMasterId(n.getId())) # Is added quadratically via ScalarUncertaintyItem
                            else:
                                myDescription += " + "+n.getDescription()
                                myValue.add(c.getNuisanceResultByMasterId(n.getId())) # Is added quadratically via ScalarUncertaintyItem
                                myVetoList.append(n.getId())
                    myVirtualMergeInformation[myFoundSingles[0]] = myValue
                    myVirtualMergeInformation["%sdescription"%myFoundSingles[0]] = myDescription
                    print WarningLabel()+"Combined nuisances '%s' for column %s!"%(myDescription, c.getLabel())
        # Loop over rows
        for n in self._extractors:
            if n.isPrintable() and n.getId() not in myVetoList:
                # Suppress rows that are not affecting anything
                myRow = ["%s"%(n.getId())]
                if self._opts.lands:
                    myRow.append(n.getDistribution())
                elif self._opts.combine:
                    myRow.append(n.getDistribution().replace("shapeQ","shape").replace("shapeStat","shape"))
                # Loop over columns
                for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
                    if c.isActiveForMass(mass,self._config):
                        # Check that column has current nuisance or has nuisance that is slave to current nuisance
                        if c.hasNuisanceByMasterId(n.getId()):
                            if self._opts.verbose:
                                print "- obtaining cached nuisance %s for column %s"%(n.getId(),c.getLabel())
                            myValue = c.getNuisanceResultByMasterId(n.getId())
                            if n.getId() in myVirtualMergeInformation.keys():
                                myValue = myVirtualMergeInformation[n.getId()] # Overwrite virtually merged value
                            myValueString = ""
                            # Check output format
                            if myValue == None or n.isShapeNuisance():
                                myValueString = "1"
                            else:
                                if isinstance(myValue, ScalarUncertaintyItem):
                                    # Check if nuisance is asymmetric
                                    if myValue.isAsymmetric():
                                        myValueString += "%.3f/%.3f"%(1.0-myValue.getUncertaintyDown(),1.0+myValue.getUncertaintyUp())
                                    else:
                                        myValueString += "%.3f"%(myValue.getUncertaintyUp()+1.0)
                                elif isinstance(myValue, list):
                                    myValueString += "%.3f/%.3f"%(1.0+myValue[0],1.0+myValue[1])
                                else:
                                    # Assume that result is a plain number
                                    #print "nid=",n.getId(),"c=",c.getLabel()
                                    myValueString += "%.3f"%(myValue+1.0)
                            if self._opts.debugMining:
                                print "  Nuisance for '%s/%s' in column '%s': %s"%(n.getId(),n.getDescription(),c.getLabel(),myValueString)
                            myRow.append(myValueString)
                        else:
                            if n.isShapeNuisance():
                                if self._opts.lands:
                                    myRow.append("0")
                                elif self._opts.combine:
                                    myRow.append("-")
                            else:
                                myRow.append("1")
                if self._opts.lands:
                    # Add description to end of the row for LandS
                    if n.getId() in myVirtualMergeInformation.keys():
                        myRow.append(myVirtualMergeInformation["%sdescription"%n.getId()])
                    else:
                        myRow.append(n.getDescription())
                myResult.append(myRow)
        return myResult

    ## Generates nuisance table as list
    # Recipe is to integrate first (linear sum for variations), then to evaluate
    def _generateShapeNuisanceVariationTable(self,mass):
        myResult = []
        # Loop over rows
        for n in self._extractors:
            if n.isPrintable() and (n.getDistribution() == "shapeQ"):
                myDownRow = ["%s_ShapeDown"%(n.getId()), ""]
                myScalarDownRow = ["%s_DownDevFromScalar"%(n.getId()), ""]
                myUpRow = ["%s_ShapeUp"%(n.getId()), ""]
                myScalarUpRow = ["%s_UpDevFromScalar"%(n.getId()), ""]
                # Loop over columns
                for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
                    if c.isActiveForMass(mass,self._config):
                        # Check that column has current nuisance or has nuisance that is slave to current nuisance
                        if c.hasNuisanceByMasterId(n.getId()):
                            #print "column=%s extractor id=%s"%(c.getLabel(),n.getId())
                            # Obtain histograms
                            myHistograms = c.getFullNuisanceResultByMasterId(n.getId()).getHistograms()
                            if len(myHistograms) > 0:
                                hUp = myHistograms[0]
                                hDown = myHistograms[1]
                                hNominal = c.getRateHistogram()
                                # Calculate
                                myDownDeltaSquared = 0.0
                                myUpDeltaSquared = 0.0
                                myDownAverage = 0.0
                                myUpAverage = 0.0
                                if hNominal.Integral() > 0.0:
                                    myDownAverage = abs(hDown.Integral()-hNominal.Integral())/hNominal.Integral()
                                    myUpAverage = abs(hUp.Integral()-hNominal.Integral())/hNominal.Integral()
                                for i in range(1,hNominal.GetNbinsX()):
                                    myDownDeltaSquared += (abs(hDown.GetBinContent(i) - hNominal.GetBinContent(i)) - myDownAverage)**2
                                    myUpDeltaSquared += (abs(hUp.GetBinContent(i) - hNominal.GetBinContent(i)) - myUpAverage)**2
                                if hNominal.Integral() > 0.0:
                                    myDownDeltaSquared = sqrt(myDownDeltaSquared)/hNominal.Integral()
                                    myUpDeltaSquared = sqrt(myUpDeltaSquared)/hNominal.Integral()
                                else:
                                    myDownDeltaSquared = 0.0
                                    myUpDeltaSquared = 0.0
                                    myScalarDownRow.append("%.3f"%(myDownDeltaSquared))
                                    myScalarUpRow.append("%.3f"%(myUpDeltaSquared))
                                myDownRow.append("%.3f"%(myDownAverage))
                                myUpRow.append("%.3f"%(myUpAverage))
                            else:
                                myDownRow.append("ignored")
                                myUpRow.append("ignored")
                                myScalarDownRow.append("ignored")
                                myScalarUpRow.append("ignored")
                        else:
                            myDownRow.append("-")
                            myUpRow.append("-")
                            myScalarDownRow.append("-")
                            myScalarUpRow.append("-")
                # Add description to end of the row
                myDownRow.append(n.getDescription())
                myUpRow.append(n.getDescription())
                myScalarDownRow.append(n.getDescription())
                myScalarUpRow.append(n.getDescription())
                myResult.append(myDownRow)
                #myResult.append(myScalarDownRow)
                myResult.append(myUpRow)
                #myResult.append(myScalarUpRow)
            if n.isPrintable() and (n.getDistribution() == "shapeStat"):
                myDownRow = ["%s_ShapeStat"%(n.getId()), ""]
                # Loop over columns
                for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
                    if c.isActiveForMass(mass,self._config):
                        # Check that column has current nuisance or has nuisance that is slave to current nuisance
                        if c.hasNuisanceByMasterId(n.getId()):
                            mySum = 0.0
                            hNominal = c.getRateHistogram()
                            for i in range(1,hNominal.GetNbinsX()+1):
                                mySum += hNominal.GetBinError(i)**2
                            myIntegral = hNominal.Integral()
                            if myIntegral > 0.0:
                                myDownRow.append("%.3f"%(sqrt(mySum)/myIntegral))
                            else:
                                myDownRow.append("0.0")
                        else:
                            myDownRow.append("-")
                myResult.append(myDownRow)
        return myResult

    ## Save histograms to root file
    def _saveHistograms(self,rootFile,mass):
        # Observation
        if self._observation != None:
            self._observation.setResultHistogramsToRootFile(rootFile)
        # Loop over columns
        for c in sorted(self._datasetGroups, key=lambda x: x.getLandsProcess()):
            if c.isActiveForMass(mass,self._config):
                c.setResultHistogramsToRootFile(rootFile)

    ## Calculates maximum width of each table cell
    def _calculateCellWidths(self,widths,table):
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
    def _getSeparatorLine(self,widths):
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
    def _getTableOutput(self,widths,table,latexMode=False):
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

    ## Generates table of shape variation for shapeQ nuisances
    def makeShapeVariationTable(self):
        myOutput = ""
        for m in self._config.MassPoints:
            # Invoke extractors
            myRateHeaderTable = self._generateRateHeaderTable(m)
            myNuisanceTable = self._generateShapeNuisanceVariationTable(m)
            # Calculate dimensions of tables
            myWidths = []
            myWidths = self._calculateCellWidths(myWidths, myRateHeaderTable)
            myWidths = self._calculateCellWidths(myWidths, myNuisanceTable)
            mySeparatorLine = self._getSeparatorLine(myWidths)
            # Construct output
            myOutput += "*** Shape nuisance variation summary ***\n"
            myOutput += self._generateHeader(m)
            myOutput += mySeparatorLine
            myOutput += self._getTableOutput(myWidths,myRateHeaderTable)
            myOutput += mySeparatorLine
            myOutput += self._getTableOutput(myWidths,myNuisanceTable)
            myOutput += "\n"
            myOutput += "Note: Linear sum is used to obtain the values, i.e. cancellations might occur. Bin-by-bin uncertainties could be larger.\n"
        # Save output to file
        myFilename = self._infoDirname+"/shapeVariationResults.txt"
        myFile = open(myFilename, "w")
        myFile.write(myOutput)
        myFile.close()
        print HighlightStyle()+"Shape variation tables written to: "+NormalStyle()+myFilename

    ## Prints event yield summary table
    def makeEventYieldSummary(self):
        formatStr = "%6."
        myPrecision = None
        if self._config.OptionNumberOfDecimalsInSummaries == None:
            print WarningLabel()+"Using default value for number of decimals in summaries. To change, set OptionNumberOfDecimalsInSummaries in your config."+NormalStyle()
            formatStr += "1"
            myPrecision = 1
        else:
            formatStr += "%d"%self._config.OptionNumberOfDecimalsInSummaries
            myPrecision = self._config.OptionNumberOfDecimalsInSummaries
        formatStr += "f"

        def getFormattedUnc(formatStr,myPrecision,uncUp,uncDown):
            if abs(round(uncDown,myPrecision)-round(uncUp,myPrecision)) < pow(0.1,myPrecision)-pow(0.1,myPrecision+2): # last term needed because of float point fluctuations
                # symmetric
                return "+- %s"%(formatStr%uncDown)
            else:
                # asymmetric
                return "+%s -%s"%(formatStr%uncUp,formatStr%uncDown)

        def getResultString(hwu,formatStr,myPrecision):
            return "%s +- %s (stat.) %s (syst.)\n"%(formatStr%hwu.getRate(),formatStr%hwu.getRateStatUncertainty(),
                getFormattedUnc(formatStr,myPrecision,*hwu.getRateSystUncertainty()))

        def getLatexFormattedUnc(formatStr,myPrecision,uncUp,uncDown):
            if abs(round(uncDown,myPrecision)-round(uncUp,myPrecision)) < pow(0.1,myPrecision)-pow(0.1,myPrecision+2): # last term needed because of float point fluctuations
                # symmetric
                return "\\pm %s"%(formatStr%uncDown)
            else:
                # asymmetric
                return "~^{+%s}){-%s}"%(formatStr%uncUp, formatStr%uncDown)

        def getLatexResultString(hwu,formatStr,myPrecision):
            return "$%s \\pm %s %s $"%(formatStr%hwu.getRate(),formatStr%hwu.getRateStatUncertainty(),
                getLatexFormattedUnc(formatStr,myPrecision,*hwu.getRateSystUncertainty()))

        # Loop over mass points
        for m in self._config.MassPoints:
            # Initialize
            HH = None
            HW = None
            QCD = None
            Embedding = None
            EWKFakes = None
            # Loop over columns to obtain RootHistoWithUncertainties objects
            for c in self._datasetGroups:
                if c.isActiveForMass(m,self._config) and not c.typeIsEmptyColumn():
                    # Find out what type the column is
                    if c.getLabel().startswith("HH"):
                        HH = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                    elif c.getLabel().startswith("WH") or c.getLabel().startswith("HW"):
                        HW = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                    elif c.getLabel().startswith("Hp"):
                        HW = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                    elif c.typeIsQCD():
                        if QCD == None:
                            QCD = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                        else:
                            QCD.Add(c.getCachedShapeRootHistogramWithUncertainties())
                    elif c.typeIsEWK() or (c.typeIsEWKfake() and self._config.OptionReplaceEmbeddingByMC and not self._config.OptionRealisticEmbeddingWithMC):
                        if Embedding == None:
                            Embedding = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                        else:
                            Embedding.Add(c.getCachedShapeRootHistogramWithUncertainties())
                    elif c.typeIsEWKfake():
                        if EWKFakes == None:
                            EWKFakes = c.getCachedShapeRootHistogramWithUncertainties().Clone()
                        else:
                            EWKFakes.Add(c.getCachedShapeRootHistogramWithUncertainties())
                    else:
                        raise Exception(ErrorLabel()+"Unknown dataset type for dataset %s!%s"%(c.getLabel(),NormalStyle()))
            # Calculate signal yield
            myBr = self._config.OptionBr
            if not (self._config.OptionLimitOnSigmaBr or m > 179):
                if self._config.OptionBr == None:
                    print WarningStyle()+"Warning: Br(t->bH+) has not been specified in config file, using default 0.01! To specify, add OptionBr=0.05 to the config file."+NormalStyle()
                    myBr = 0.01
                HW.Scale(2.0 * myBr * (1.0 - myBr))
            if HH != None:
                HH.Scale(myBr**2)
                HW.Add(HH)
            # From this line on, HW includes all signal
            # Calculate expected yield
            TotalExpected = QCD.Clone()
            TotalExpected.Add(Embedding)
            if not (self._config.OptionReplaceEmbeddingByMC and not self._config.OptionRealisticEmbeddingWithMC):
                TotalExpected.Add(EWKFakes)
            # Construct table
            myOutput = "*** Event yield summary ***\n"
            myOutput += self._generateHeader(m)
            myOutput += "\n"
            myOutput += "Number of events\n"
            if not (self._config.OptionLimitOnSigmaBr or m > 179):
                myOutput += "Signal, mH+=%3d GeV, Br(t->bH+)=%.2f: %s"%(m,myBr,getResultString(HW,formatStr,myPrecision))
            else:
                myOutput += "Signal, mH+=%3d GeV, sigma x Br=1 pb: %s"%(m,getResultString(HW,formatStr,myPrecision))
            myOutput += "Backgrounds:\n"
            myOutput += "                           Multijets: %s"%getResultString(QCD,formatStr,myPrecision)
            if self._config.OptionReplaceEmbeddingByMC and not self._config.OptionRealisticEmbeddingWithMC:
                myOutput += "                           MC EWK+tt: %s"%getResultString(Embedding,formatStr,myPrecision)
            else:
                myOutput += "                    EWK+tt with taus: %s"%getResultString(Embedding,formatStr,myPrecision)
                myOutput += "               EWK+tt with fake taus: %s"%getResultString(EWKFakes,formatStr,myPrecision)
            myOutput += "                      Total expected: %s"%getResultString(TotalExpected,formatStr,myPrecision)
            if self._config.BlindAnalysis:
                myOutput += "                            Observed: BLINDED\n\n"
            else:
                myOutput += "                            Observed: %5d\n\n"%Data.getRate()
            # Print to screen
            if self._config.OptionDisplayEventYieldSummary:
                print myOutput
            # Save output to file
            myFilename = self._infoDirname+"/EventYieldSummary_m%d.txt"%m
            myFile = open(myFilename, "w")
            myFile.write(myOutput)
            myFile.close()
            print HighlightStyle()+"Event yield summary for mass %d written to: "%m +NormalStyle()+myFilename

            myOutputLatex = "% table auto generated by datacard generator on "+self._timestamp+" for "+self._config.DataCardName+" / "+self._outputPrefix+"\n"
            myOutputLatex += "\\renewcommand{\\arraystretch}{1.2}\n"
            myOutputLatex += "\\begin{table}\n"
            myOutputLatex += "  \\centering\n"
            if not (self._config.OptionLimitOnSigmaBr or m > 179):
                myOutputLatex += "  \\caption{Summary of the number of events from the signal with mass point $\\mHpm=%d\\GeVcc$ with $\\BRtH=%.2f$,\n"%(m,myBr)
            else:
                myOutputLatex += "  \\caption{Summary of the number of events from the signal with mass point $\\mHpm=%d\\GeVcc$,\n"%(m)
            myOutputLatex += "           from the background measurements, and the observed event yield. Luminosity uncertainty is not included in the numbers.}\n"
            myOutputLatex += "  \\label{tab:summary:yields}\n"
            myOutputLatex += "  \\vskip 0.1 in\n"
            myOutputLatex += "  \\hspace*{-.8cm}\n"
            myOutputLatex += "  \\begin{tabular}{ l c }\n"
            myOutputLatex += "  \\hline\n"
            myOutputLatex += "  \\multicolumn{1}{ c }{Source}  & $N_{\\text{events}} \\pm \\text{stat.} \\pm \\text{syst.}$  \\\\ \n"
            myOutputLatex += "  \\hline\n"
            myOutputLatex += "  HH+HW, $\\mHplus = %3d\\GeVcc             & %s \\\\ \n"%(m,getLatexResultString(HW,formatStr,myPrecision))
            myOutputLatex += "  \\hline\n"
            myOutputLatex += "  Multijet background (data-driven)       & %s \\\\ \n"%getLatexResultString(QCD,formatStr,myPrecision)
            if self._config.OptionReplaceEmbeddingByMC and not self._config.OptionRealisticEmbeddingWithMC:
                myOutputLatex += "  MC EWK+\\ttbar                           & %s \\\\ \n"%getLatexResultString(Embedding,formatStr,myPrecision)
            else:
                myOutputLatex += "  EWK+\\ttbar with $\\tau$ (data-driven)    & %s \\\\ \n"%getLatexResultString(Embedding,formatStr,myPrecision)
                myOutputLatex += "  EWK+\\ttbar with e/\\mu/jet\\to$\\tau$ (MC) & %s \\\\ \n"%getLatexResultString(EWKFakes,formatStr,myPrecision)
            myOutputLatex += "  \\hline\n"
            myOutputLatex += "  Total expected from the SM              & %s \\\\ \n"%getLatexResultString(TotalExpected,formatStr,myPrecision)
            if self._config.BlindAnalysis:
                myOutputLatex += "  Observed: & BLINDED \\\\ \n"
            else:
                myOutputLatex += "  Observed: & %5d \\\\ \n"%Data.getRate()
            myOutputLatex += "  \\hline\n"
            myOutputLatex += "  \\end{tabular}\n"
            myOutputLatex += "\\end{table}\n"
            myOutputLatex += "\\renewcommand{\\arraystretch}{1}\n"
            # Save output to file
            myFilename = self._infoDirname+"/EventYieldSummary_m%d_"%(m) +self._timestamp+"_"+self._outputPrefix+"_"+self._config.DataCardName.replace(" ","_")+".tex"
            myFile = open(myFilename, "w")
            myFile.write(myOutputLatex)
            myFile.close()
            print HighlightStyle()+"Latex table of event yield summary for mass %d written to: "%m +NormalStyle()+myFilename

    ## Returns a string with proper numerical formatting
    def _getFormattedSystematicsNumber(self,value):
        if abs(value) > 0.1:
            return "%.0f"%(abs(value)*100)
        elif abs(value) > 0.001:
            return "%.1f"%(abs(value)*100)
        else:
            return "<0.1"

    ## Prints systematics summary table
    def makeSystematicsSummary(self):
        myColumnOrder = ["HH",
                         "HW",
                         "QCD",
                         "EWK_Tau",
                         "EWK_DY",
                         "EWK_VV",
                         "EWK_tt_faketau",
                         "EWK_W_faketau",
                         "EWK_t_faketau"]
        myNuisanceOrder = [["01","$\\tau - p_T^{miss}$ trigger"], # trg
                           ["03", "$\\tau$ jet ID (excl. $R_\\tau$"], # tau ID
                           ["04", "jet, $\\mathcal{l}\\to\\tau$ mis-ID"], # tau mis-ID
                           ["45", "TES"], # energy scale
                           ["46", "JES"], # energy scale
                           ["47", "Unclustered MET ES"], # energy scale
                           ["09", "lepton veto"], # lepton veto
                           ["10", "b-jet tagging"], # b tagging
                           ["11", "jet$\\to$b mis-ID"], # b mis-tagging
                           ["12", "multi-jet stat."], # QCD stat.
                           ["13", "multi-jet syst."], # QCD syst.
                           ["19", "EWK+$t\\bar{t}$ $\\tau$ stat."], # embedding stat.
                           ["14", "multi-jet contam."], # QCD contamination in embedding
                           ["15", "$f_{W\\to\\tau\\to\\mu}"], # tau decays to muons in embedding
                           ["16", "muon selections"], # muon selections in embedding
                           ["34", "pile-up"], # pile-up
                           [["17","18","19","22","24","25","26","27"], "simulation stat."], # MC statistics
                           [["28","29","30","31","32"], "cross section"], # cross section
                           ["33", "luminosity"]] # luminosity
        # Make table
        myTable = []
        for n in myNuisanceOrder:
            myRow = [n[1]]
            for columnName in myColumnOrder:
                myMinValue = 9999.0
                myMaxValue = -9999.0
                mySavedMinResult = None
                mySavedMaxResult = None
                for c in self._datasetGroups:
                    if columnName in c.getLabel():
                        # Correct column found, now check if column has nuisance
                        if isinstance(n[0], list):
                            for nid in n[0]:
                                if c.hasNuisanceByMasterId(nid):
                                    myResult = c.getFullNuisanceResultByMasterId(nid)
                                    myValue = myResult.getResultAverage()
                                    if myValue < myMinValue:
                                        myMinValue = myValue
                                        mySavedMinResult = myResult.getResult()
                                    if myValue > myMaxValue:
                                        myMaxValue = myValue
                                        mySavedMaxResult = myResult.getResult()
                        else:
                            if c.hasNuisanceByMasterId(n[0]):
                                myResult = c.getFullNuisanceResultByMasterId(n[0])
                                myValue = myResult.getResultAverage()
                                if myValue < myMinValue:
                                    myMinValue = myValue
                                    mySavedMinResult = myResult.getResult()
                                if myValue > myMaxValue:
                                    myMaxValue = myValue
                                    mySavedMaxResult = myResult.getResult()
                myStr = ""
                if mySavedMinResult == None:
                    myStr = ""
                elif abs(myMinValue-myMaxValue)<0.001:
                    if isinstance(mySavedMaxResult, list):
                        # Asymmetric
                        if mySavedMaxResult[0]>=0 and mySavedMaxResult[1]>=0:
                            myValue = (mySavedMaxResult[0]+mySavedMaxResult[1])/2.0
                            myStr = "%s"%(self._getFormattedSystematicsNumber(myValue))
                        else:
                            myStr = "_{-%s}^{+%s}"%(self._getFormattedSystematicsNumber(mySavedMaxResult[0]),
                                                    self._getFormattedSystematicsNumber(mySavedMaxResult[1]))
                    else:
                        # Symmetric
                        myStr = self._getFormattedSystematicsNumber(mySavedMaxResult)
                else:
                    # Range
                    if isinstance(mySavedMaxResult, list):
                        # Asymmetric range
                        if mySavedMaxResult[0]>=0 and mySavedMaxResult[1]>=0:
                            myValueUp = (mySavedMaxResult[0]+mySavedMaxResult[1])/2.0
                            myValueDown = (mySavedMinResult[0]+mySavedMinResult[1])/2.0
                            myStr = "%s..%s"%(self._getFormattedSystematicsNumber(myValueDown),
                                              self._getFormattedSystematicsNumber(myValueUp))
                        else:
                            myStr = "_{-%s..%s}^{+%s..%s}"%(self._getFormattedSystematicsNumber(mySavedMinResult[0]),
                                                            self._getFormattedSystematicsNumber(mySavedMaxResult[0]),
                                                            self._getFormattedSystematicsNumber(mySavedMinResult[1]),
                                                            self._getFormattedSystematicsNumber(mySavedMaxResult[1]))
                    else:
                        # Symmetric range
                        myStr = "%s..%s"%(self._getFormattedSystematicsNumber(mySavedMinResult),
                                          self._getFormattedSystematicsNumber(mySavedMaxResult))
                myRow.append(myStr)
            myTable.append(myRow)
        # Make table
        myOutput = "% table auto generated by datacard generator on "+self._timestamp+" for "+self._config.DataCardName+" / "+self._outputPrefix+"\n"
        myOutput += "\\renewcommand{\\arraystretch}{1.2}\n"
        myOutput += "\\begin{table}%%[h]\n"
        myOutput += "\\begin{center}\n"
        myOutput += "\\caption{The systematic uncertainties (in \\%%) for the backgrounds\n"
        myOutput += "and the signal from \\ttTobHpmbHmp (HH) and \\ttTobWpmbHmp (WH)\n"
        myOutput += "processes at $\\mHpm=80$--$160\\GeVcc$.\n"
        myOutput += "\\label{tab:summary:systematics}\n"
        myOutput += "\\vskip 0.1 in\n"
        myOutput += "\\noindent\\makebox[\\textwidth]{\n"
        myOutput += "\\begin{tabular}{l|cc|c|ccc|ccc}\n"
        myOutput += "\\hline\n"
        myOutput += "& HH   &  WH  &  QCD & \\multicolumn{3}{c|}{EWK+$t\\bar{t}$ genuine $\\tau$}\n"
        myOutput += "& \\multicolumn{3}{c}{EWK+$t\\bar{t}$~$\\tau$~fakes}\n"
        # Captions
        myCaptionLine = [["","","","","Emb.data","Res.DY","Res.WW","$t\\bar{t}$","tW","W+jets"]]
        # Calculate dimensions of tables
        myWidths = []
        myWidths = self._calculateCellWidths(myWidths, myTable)
        myWidths = self._calculateCellWidths(myWidths, myCaptionLine)
        mySeparatorLine = self._getSeparatorLine(myWidths)
        # Add caption and table
        myOutput += self._getTableOutput(myWidths,myCaptionLine,True)
        myOutput += "\\hline\n"
        myOutput += self._getTableOutput(myWidths,myTable,True)
        myOutput += "\\hline\n"
        myOutput += "\\end{tabular}\n"
        myOutput += "}\n"
        myOutput += "\\end{center}\n"
        myOutput += "\\end{table}\n"
        myOutput += "\\renewcommand{\\arraystretch}{1}\n"
        # Save output to file
        myFilename = self._infoDirname+"/SystematicsSummary_"+self._timestamp+"_"+self._outputPrefix+"_"+self._config.DataCardName.replace(" ","_")+".tex"
        myFile = open(myFilename, "w")
        myFile.write(myOutput)
        myFile.close()
        print HighlightStyle()+"Latex table of systematics summary written to: "+NormalStyle()+myFilename

    ## Prints QCD purity information
    def makeQCDPuritySummary(self):
        h = aux.Clone(self._observation.getRateHistogram(), "dummy")
        h.Reset()
        hQCD = None
        hQCDPurity = None
        for c in self._datasetGroups:
            if c.typeIsQCD():
                hQCD = c.getRateHistogram()
                hQCDPurity = c.getPurityHistogram()
            elif not c.typeIsSignal():
                h.Add(c.getRateHistogram())
        s = "QCD purity by bins for shape histogram:\n"
        for i in range(1,hQCD.GetNbinsX()+1):
            # bin
            s += "  bin: %03d..%03d"%(hQCDPurity.GetXaxis().GetBinLowEdge(i), hQCDPurity.GetXaxis().GetBinUpEdge(i))
            # QCD purity
            myGoodPurityStatus = hQCDPurity.GetBinContent(i) > 0.5
            s += "  purity: %.3f +- %.3f"%(hQCDPurity.GetBinContent(i), hQCDPurity.GetBinError(i))
            # QCD fraction out of all expected events
            f = 0.0
            if abs(h.GetBinContent(i)+hQCD.GetBinContent(i)) > 0.0:
                f = (hQCD.GetBinContent(i)) / (h.GetBinContent(i)+hQCD.GetBinContent(i))
            s += "  QCD/Exp.: %.3f"%f
            mySignificantFractionStatus = f > 0.2
            if not myGoodPurityStatus and mySignificantFractionStatus:
                s += "  #W# check if bad purity of QCD has impact on results!"
            else:
                s += "  OK"
            s += "\n"
        print "\n%s"%s.replace("#W#",WarningLabel())
        myFilename = self._infoDirname+"/QCDpurity.txt"
        myFile = open(myFilename, "w")
        myFile.write(s.replace("#W#","Warning:"))
        myFile.close()
        h.IsA().Destructor(h)
