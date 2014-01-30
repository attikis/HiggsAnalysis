# Description: Calculates QCD Inverted shapes with the appropriate normalization
# Makes also the shape histograms in phase space bins and the final shape
# Note: Systematic uncertainties need to be treated separately (since they should be taken from variation modules)
#
# Authors: LAW

from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
from HiggsAnalysis.HeavyChHiggsToTauNu.qcdCommon.dataDrivenQCDCount import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.extendedCount import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.errorPropagation import *
from HiggsAnalysis.HeavyChHiggsToTauNu.qcdCommon.systematicsForMetShapeDifference import *
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux as aux
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.systematics as systematics
import math

## Class for calculating the QCD factorised results
# Shape has to be a dataDrivenQCDCount object
class QCDInvertedShape:
    def __init__(self, shape, moduleInfoString, normFactors, optionPrintPurityByBins=False, optionDoNQCDByBinHistograms=False):
        self._resultCountObject = None # ExtendedCount object which contains the result
        self._resultShape = None # TH1F which contains the final shape histogram for NQCD
        self._resultShapeEWK = None # TH1F which contains the final shape histogram for EWK MC
        self._resultShapePurity = None # TH1F which contains the final shape histogram for QCD purity
        self._histogramsList = [] # List of TH1F histograms
        self._doCalculate(shape, moduleInfoString, normFactors, optionPrintPurityByBins, optionDoNQCDByBinHistograms)

    def delete(self):
        ROOT.gDirectory.Delete(self._resultShape.GetName())
        for h in self._histogramsList:
            ROOT.gDirectory.Delete(h.GetName())
        self._histogramsList = None

    ## Returns the ExtendedCountObject with the result
    def getResultCountObject(self):
        return self._resultCountObject

    ## Returns the final shape histogram
    def getResultShape(self):
        return self._resultShape

    ## Returns the MC EWK contribution to final shape histogram
    def getResultMCEWK(self):
        return self._resultShapeEWK

    ## Returns the final shape purity histogram
    def getResultPurity(self):
        return self._resultShapePurity

    ## Returns the list of shape histograms (one for each split phase space bin)
    def getNQCDHistograms(self):
        return self._histogramsList

    ## Calculates the result
    def _doCalculate(self, shape, moduleInfoString, normFactors, optionPrintPurityByBins, optionDoNQCDByBinHistograms):
        # Calculate final shape in signal region (shape * w_QCD)
        nSplitBins = shape.getNumberOfPhaseSpaceSplitBins()
        # Initialize result containers
        self._resultShape = aux.Clone(shape.getDataDrivenQCDHistoForSplittedBin(0))
        self._resultShape.Reset()
        self._resultShape.SetTitle("NQCDFinal_Total_%s"%moduleInfoString)
        self._resultShape.SetName("NQCDFinal_Total_%s"%moduleInfoString)
        self._resultShapeEWK = aux.Clone(shape.getDataDrivenQCDHistoForSplittedBin(0))
        self._resultShapeEWK.Reset()
        self._resultShapeEWK.SetTitle("NQCDFinal_EWK_%s"%moduleInfoString)
        self._resultShapeEWK.SetName("NQCDFinal_EWK_%s"%moduleInfoString)
        self._resultShapePurity = aux.Clone(shape.getDataDrivenQCDHistoForSplittedBin(0))
        self._resultShapePurity.Reset()
        self._resultShapePurity.SetTitle("NQCDFinal_Purity_%s"%moduleInfoString)
        self._resultShapePurity.SetName("NQCDFinal_Purity_%s"%moduleInfoString)
        self._histogramsList = []
        myUncertaintyLabels = ["statData", "statEWK"]
        self._resultCountObject = ExtendedCount(0.0, [0.0, 0.0], myUncertaintyLabels)
        if optionDoNQCDByBinHistograms:
            for i in range(0, nSplitBins):
                hBin = aux.Clone(self._resultShape)
                hBin.SetTitle("NQCDFinal_%s_%s"%(shape.getPhaseSpaceBinFileFriendlyTitle(i).replace(" ",""), moduleInfoString))
                hBin.SetName("NQCDFinal_%s_%s"%(shape.getPhaseSpaceBinFileFriendlyTitle(i).replace(" ",""), moduleInfoString))
                self._histogramsList.append(hBin)
        # Intialize counters for purity calculation in final shape binning
        myShapeDataSum = []
        myShapeDataSumUncert = []
        myShapeEwkSum = []
        myShapeEwkSumUncert = []
        for j in range(1,self._resultShape.GetNbinsX()+1):
            myShapeDataSum.append(0.0)
            myShapeDataSumUncert.append(0.0)
            myShapeEwkSum.append(0.0)
            myShapeEwkSumUncert.append(0.0)
        # Calculate results separately for each phase space bin and then combine
        for i in range(0, nSplitBins):
            # Get data-driven QCD, data, and MC EWK shape histogram for the phase space bin
            h = shape.getDataDrivenQCDHistoForSplittedBin(i)
            hData = shape.getDataHistoForSplittedBin(i)
            hEwk = shape.getEwkHistoForSplittedBin(i)
            # Get normalization factor
            if not shape.getPhaseSpaceBinFileFriendlyTitle(i) in normFactors.keys():
                raise Exception(ErrorLabel()+"No normalization factors available for bin '%s' when accessing histogram %s!"%(shape.getPhaseSpaceBinFileFriendlyTitle(i),shape.getHistoName()))
            wQCD = normFactors[shape.getPhaseSpaceBinFileFriendlyTitle(i)]
            # Loop over bins in the shape histogram
            for j in range(1,h.GetNbinsX()+1):
                myResult = 0.0
                myStatDataUncert = 0.0
                myStatEwkUncert = 0.0
                if abs(h.GetBinContent(j)) > 0.00001: # Ignore zero bins
                    # Calculate result
                    myResult = h.GetBinContent(j) * wQCD
                    # Calculate abs. stat. uncert. for data and for MC EWK
                    myStatDataUncert = hData.GetBinError(j) * wQCD
                    myStatEwkUncert = hEwk.GetBinError(j) * wQCD
                    #errorPropagationForProduct(hLeg1.GetBinContent(j), hLeg1Data.GetBinError(j), myEffObject.value(), myEffObject.uncertainty("statData"))
                    # Do not calculate here MC EWK syst.
                myCountObject = ExtendedCount(myResult, [myStatDataUncert, myStatEwkUncert], myUncertaintyLabels)
                self._resultCountObject.add(myCountObject)
                if optionDoNQCDByBinHistograms:
                    self._histogramsList[i].SetBinContent(j, myCountObject.value())
                    self._histogramsList[i].SetBinError(j, myCountObject.statUncertainty())
                self._resultShape.SetBinContent(j, self._resultShape.GetBinContent(j) + myCountObject.value())
                self._resultShape.SetBinError(j, self._resultShape.GetBinError(j) + myCountObject.statUncertainty()**2) # Sum squared
                # Sum items for purity calculation
                myShapeDataSum[j-1] += hData.GetBinContent(j)*wQCD
                myShapeDataSumUncert[j-1] += (hData.GetBinError(j)*wQCD)**2
                myShapeEwkSum[j-1] += hEwk.GetBinContent(j)*wQCD
                myShapeEwkSumUncert[j-1] += (hEwk.GetBinError(j)*wQCD)**2
            ROOT.gDirectory.Delete(h.GetName())
            ROOT.gDirectory.Delete(hData.GetName())
            ROOT.gDirectory.Delete(hEwk.GetName())
        # Take square root of uncertainties
        for j in range(1,self._resultShape.GetNbinsX()+1):
            self._resultShape.SetBinError(j, math.sqrt(self._resultShape.GetBinError(j)))
        # Print result
        print "NQCD Integral(%s) = %s "%(shape.getHistoName(), self._resultCountObject.getResultStringFull("%.1f"))
        # Print purity as function of final shape bins
        if optionPrintPurityByBins:
            print "Purity of shape %s"%shape.getHistoName()
            print "shapeBin purity purityUncert"
        for j in range (1,h.GetNbinsX()+1):
            myPurity = 0.0
            myPurityUncert = 0.0
            if abs(myShapeDataSum[j-1]) > 0.000001:
                myPurity = 1.0 - myShapeEwkSum[j-1] / myShapeDataSum[j-1]
                myPurityUncert = errorPropagationForDivision(myShapeEwkSum[j-1], math.sqrt(myShapeEwkSumUncert[j-1]), myShapeDataSum[j-1], math.sqrt(myShapeDataSumUncert[j-1]))
            # Store MC EWK content
            self._resultShapeEWK.SetBinContent(j, myShapeEwkSum[j-1])
            self._resultShapeEWK.SetBinError(j, math.sqrt(myShapeEwkSumUncert[j-1]))
            self._resultShapePurity.SetBinContent(j, myPurity)
            self._resultShapePurity.SetBinError(j, myPurityUncert)
            # Print purity info of final shape
            if optionPrintPurityByBins:
                myString = ""
                if j < h.GetNbinsX():
                    myString = "%d..%d"%(h.GetXaxis().GetBinLowEdge(j),h.GetXaxis().GetBinUpEdge(j))
                else:
                    myString = ">%d"%(h.GetXaxis().GetBinLowEdge(j))
                myString += " %.3f %.3f"%(myPurity, myPurityUncert)
                print myString

class QCDInvertedControlPlot: # OBSOLETE
    def __init__(self, shape, moduleInfoString, normFactors, title=""):
        self._resultShape = None # TH1F which contains the final shape histogram
        self._normFactors = normFactors
        self._title = title
        if title == "":
            title = "NQCDCtrl_Total_%s"%moduleInfoString
        self._doCalculate(shape, moduleInfoString)

    def delete(self):
        ROOT.gDirectory.Delete(self._resultShape.GetName())
        self._normFactors = None

    ## Returns the final shape histogram
    def getResultShape(self):
        return self._resultShape

    ## Calculates the result
    def _doCalculate(self, shape, moduleInfoString):
        # Calculate final shape in signal region (shape * w_QCD)
        nSplitBins = shape.getNumberOfPhaseSpaceSplitBins()
        # Initialize result containers
        self._resultShape = aux.Clone(shape.getDataDrivenQCDHistoForSplittedBin(0))
        self._resultShape.Reset()
        self._resultShape.SetTitle(self._title+"tmp")
        self._resultShape.SetName(self._title+"tmp")
        ROOT.SetOwnership(self._resultShape, True)
        myUncertaintyLabels = ["statData", "statEWK"]
        self._resultCountObject = ExtendedCount(0.0, [0.0, 0.0], myUncertaintyLabels)
        # Calculate results separately for each phase space bin and then combine
        for i in range(0, nSplitBins):
            # Get data-driven QCD, data, and MC EWK shape histogram for the phase space bin
            h = shape.getDataDrivenQCDHistoForSplittedBin(i)
            # Get normalization factor
            if not shape.getPhaseSpaceBinFileFriendlyTitle(i) in self._normFactors.keys():
                raise Exception(ErrorLabel()+"No normalization factors available for bin '%s' when accessing histogram %s!"%(shape.getPhaseSpaceBinFileFriendlyTitle(i),shape.getHistoName()))
            wQCD = self._normFactors[shape.getPhaseSpaceBinFileFriendlyTitle(i)]
            # Loop over bins in the shape histogram
            for j in range(1,h.GetNbinsX()+1):
                myResult = 0.0
                myResultStatUncert = 0.0
                if abs(h.GetBinContent(j)) > 0.00001: # Ignore zero bins
                    # Calculate result
                    myResult = h.GetBinContent(j) * wQCD
                    myResultStatUncert = h.GetBinError(j) * wQCD
                    # Do not calculate here MC EWK syst.
                self._resultShape.SetBinContent(j, self._resultShape.GetBinContent(j) + myResult)
                self._resultShape.SetBinError(j, self._resultShape.GetBinError(j) + myResultStatUncert**2) # Sum squared
            ROOT.gDirectory.Delete(h.GetName())
        # Take square root of uncertainties
        for j in range(1,self._resultShape.GetNbinsX()+1):
            self._resultShape.SetBinError(j, math.sqrt(self._resultShape.GetBinError(j)))
        # Print result
        print "Control plot integral(%s) = %s "%(self._title, self._resultShape.Integral())

class QCDInvertedResultManager:
    def __init__(self, shapeString, normalizationPoint, dsetMgr, luminosity, moduleInfoString, normFactors, shapeOnly=False, displayPurityBreakdown=False):
        print HighlightStyle()+"...Obtaining final shape"+NormalStyle()
        # Obtain QCD shapes
        myShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", shapeString, luminosity, systematics.getBinningForPlot(shapeString))
        # Calculate final shape in signal region (leg1 * leg2 / basic)
        myResult = QCDInvertedShape(myShape, moduleInfoString, normFactors, optionPrintPurityByBins=displayPurityBreakdown)
        myShape.delete()
        self._hShape = aux.Clone(myResult.getResultShape())
        self._hShape.SetName(self._hShape.GetName()+"finalShapeInManager")
        self._hShapeMCEWK = aux.Clone(myResult.getResultMCEWK())
        self._hShapeMCEWK.SetName(self._hShape.GetName()+"finalShapeInManager")
        self._hShapePurity = aux.Clone(myResult.getResultPurity())
        self._hShapePurity.SetName(self._hShape.GetName()+"finalShapeInManager")
        myResult.delete()
        if not shapeOnly:
            print HighlightStyle()+"...Obtaining region transition systematics"+NormalStyle()
            # Do systematics coming from met shape difference
            histoNamePrefix = "MT"
            if shapeString == "shapeInvariantMass":
                histoNamePrefix = "INVMASS"
            myCtrlRegionName = "Inverted/%sInvertedTauId%s"%(histoNamePrefix, normalizationPoint)
            mySignalRegionName = "baseline/%sBaselineTauId%s"%(histoNamePrefix, normalizationPoint)
            myCtrlRegionShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", myCtrlRegionName, luminosity, systematics.getBinningForPlot(shapeString))
            mySignalRegionShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", mySignalRegionName, luminosity, systematics.getBinningForPlot(shapeString))
            myRegionTransitionSyst = SystematicsForMetShapeDifference(mySignalRegionShape, myCtrlRegionShape, self._hShape, moduleInfoString=moduleInfoString)
            self._hRegionSystUp = aux.Clone(myRegionTransitionSyst.getUpHistogram(), "QCDinvMgrQCDSystUp")
            self._hRegionSystDown = aux.Clone(myRegionTransitionSyst.getDownHistogram(), "QCDinvMgrQCDSystDown")
            myRegionTransitionSyst.delete()
            # Obtain data-driven control plots
            self._hCtrlPlotLabels = []
            self._hCtrlPlots = []
            self._hRegionSystUpCtrlPlots = []
            self._hRegionSystDownCtrlPlots = []
            myObjects = dsetMgr.getDataset("Data").getDirectoryContent("ForDataDrivenCtrlPlots")
            i = 0
            for item in myObjects:
                myStatus = True
                i += 1
                print HighlightStyle()+"...Obtaining ctrl plot %d/%d: %s%s"%(i,len(myObjects),item,NormalStyle())
                myEWKFoundStatus = True
                for d in dsetMgr.getDataset("EWK").datasets:
                    if not d.hasRootHisto("%s/%s"%("ForDataDrivenCtrlPlots",item)):
                        myEWKFoundStatus = False
                if not myEWKFoundStatus:
                    myStatus = False
                    print WarningLabel()+"Skipping '%s', because it does not exist for all EWK datasets (you probably forgot to set histo level to Vital when producing the multicrab)!"%(item)+NormalStyle()
                else:
                    (myRootObject, myRootObjectName) = dsetMgr.getDataset("EWK").getFirstRootHisto("%s/%s"%("ForDataDrivenCtrlPlots",item))
                    if isinstance(myRootObject, ROOT.TH2):
                        print WarningLabel()+"Skipping '%s', because it is not a TH1 object!"%(item)+NormalStyle()
                        myStatus = False
                if myStatus:
                    self._hCtrlPlotLabels.append(item)
                    myRebinList = systematics.getBinningForPlot(item)
                    myCtrlShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", "ForDataDrivenCtrlPlots/%s"%item, luminosity, rebinList=myRebinList)
                    myCtrlPlot = QCDInvertedShape(myCtrlShape, moduleInfoString+"_"+item, normFactors)
                    myCtrlShape.delete()
                    myCtrlPlotHisto = aux.Clone(myCtrlPlot.getResultShape(), "ctrlPlotShapeInManager")
                    myCtrlPlotHisto.SetName(item+"%d"%i)
                    myCtrlPlotHisto.SetTitle(item)
                    self._hCtrlPlots.append(myCtrlPlotHisto)
                    # MC EWK and purity
                    self._hCtrlPlotLabels.append(item+"_MCEWK")
                    myCtrlPlotMCEWKHisto = aux.Clone(myCtrlPlot.getResultMCEWK(), "ctrlPlotMCEWKInManager")
                    myCtrlPlotMCEWKHisto.SetName(item+"%d_MCEWK"%i)
                    myCtrlPlotMCEWKHisto.SetTitle(item+"_MCEWK")
                    self._hCtrlPlots.append(myCtrlPlotMCEWKHisto)
                    self._hCtrlPlotLabels.append(item+"_Purity")
                    myCtrlPlotPurityHisto = aux.Clone(myCtrlPlot.getResultPurity(), "ctrlPlotPurityInManager")
                    myCtrlPlotPurityHisto.SetName(item+"%d_Purity"%i)
                    myCtrlPlotPurityHisto.SetTitle(item+"_Purity")
                    self._hCtrlPlots.append(myCtrlPlotPurityHisto)
                    myCtrlPlot.delete()
                    # Do systematics coming from met shape difference for control plots
                    myCtrlPlotSignalRegionShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", "%s/%s"%("ForDataDrivenCtrlPlotsQCDNormalizationSignal",item), luminosity, rebinList=myRebinList)
                    myCtrlPlotControlRegionShape = DataDrivenQCDShape(dsetMgr, "Data", "EWK", "%s/%s"%("ForDataDrivenCtrlPlotsQCDNormalizationControl",item), luminosity, rebinList=myRebinList)
                    myCtrlPlotRegionTransitionSyst = SystematicsForMetShapeDifference(myCtrlPlotSignalRegionShape, myCtrlPlotControlRegionShape, myCtrlPlotHisto, moduleInfoString=moduleInfoString, quietMode=True)
                    myCtrlPlotSignalRegionShape.delete()
                    myCtrlPlotControlRegionShape.delete()
                    hUp = aux.Clone(myCtrlPlotRegionTransitionSyst.getUpHistogram(), "QCDfactMgrSystQCDSystUp%d"%i)
                    hUp.SetTitle(item)
                    self._hRegionSystUpCtrlPlots.append(hUp)
                    hDown = aux.Clone(myCtrlPlotRegionTransitionSyst.getDownHistogram(), "QCDfactMgrSystQCDSystDown%d"%i)
                    hDown.SetTitle(item)
                    self._hRegionSystDownCtrlPlots.append(hDown)
                    myCtrlPlotRegionTransitionSyst.delete()
                    #print "\n***** memdebug %d\n"%i
                    #if i <= 2:
                    #    ROOT.gDirectory.GetList().ls()
                ROOT.gDirectory.Delete(myRootObject.GetName())
        myCtrlRegionShape.delete()
        mySignalRegionShape.delete()

    ## Delete the histograms
    def delete(self):
        ROOT.gDirectory.Delete(self._hShape.GetName())
        ROOT.gDirectory.Delete(self._hShapeMCEWK.GetName())
        ROOT.gDirectory.Delete(self._hShapePurity.GetName())
        ROOT.gDirectory.Delete(self._hRegionSystDown.GetName())
        ROOT.gDirectory.Delete(self._hRegionSystUp.GetName())
        self._hCtrlPlotLabels = None
        for h in self._hCtrlPlots:
            ROOT.gDirectory.Delete(h.GetName())
        for h in self._hRegionSystUpCtrlPlots:
            ROOT.gDirectory.Delete(h.GetName())
        for h in self._hRegionSystDownCtrlPlots:
            ROOT.gDirectory.Delete(h.GetName())
        self._hCtrlPlots = None
        self._hRegionSystUpCtrlPlots = None
        self._hRegionSystDownCtrlPlots = None

    def getShape(self):
        return self._hShape

    def getShapeMCEWK(self):
        return self._hShapeMCEWK

    def getShapePurity(self):
        return self._hShapePurity

    def getRegionSystUp(self):
        return self._hRegionSystUp

    def getRegionSystDown(self):
        return self._hRegionSystDown

    def getControlPlotLabels(self):
        return self._hCtrlPlotLabels

    def getControlPlots(self):
        return self._hCtrlPlots

    def getRegionSystUpCtrlPlots(self):
        return self._hRegionSystUpCtrlPlots

    def getRegionSystDownCtrlPlots(self):
        return self._hRegionSystDownCtrlPlots
