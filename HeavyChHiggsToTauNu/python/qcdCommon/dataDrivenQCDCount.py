from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.splittedHistoReader import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShapeHistoModifier import *
#from HiggsAnalysis.HeavyChHiggsToTauNu.tools.extendedCount import *
from math import sqrt
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset import Count
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histogramsExtras as histogramsExtras
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.errorPropagation import *
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.extendedCount import ExtendedCount
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux as aux
import array

import ROOT
ROOT.gROOT.SetBatch(True) # no flashing canvases

## Container class for information of data and MC EWK at certain point of selection
class DataDrivenQCDShape:
    def __init__(self, dsetMgr, dsetLabelData, dsetLabelEwk, histoName, luminosity, rebinList=None):
        self._uniqueN = 0
        self._splittedHistoReader = SplittedHistoReader(dsetMgr, dsetLabelData)
        self._histoName = histoName
        self._dataList = list(self._splittedHistoReader.getSplittedBinHistograms(dsetMgr, dsetLabelData, histoName, luminosity))
        self._ewkList = list(self._splittedHistoReader.getSplittedBinHistograms(dsetMgr, dsetLabelEwk, histoName, luminosity))
        self._rebinDoneStatus = True
        if rebinList != None:
            # Rebin
            myArray = array.array("d",rebinList)
            for i in range(0,len(self._dataList)):
                if self._dataList[i].GetXaxis().GetXmax() - rebinList[len(rebinList)-1] < -0.00001:
                    raise Exception(ErrorLabel()+"You tried to set as maximum x value %f in rebinning, but maximum of histogram is %f!%s"%(rebinList[len(rebinList)-1],self._dataList[i].GetXaxis().GetXmax(),NormalStyle()))
                self._dataList[i] = self._dataList[i].Rebin(len(myArray)-1,"",myArray)
                self._dataList[i].SetName(self._dataList[i].GetName()+histoName.replace("/",""))
                histogramsExtras.makeFlowBinsVisible(self._dataList[i])
                self._ewkList[i] = self._ewkList[i].Rebin(len(myArray)-1,"",myArray)
                self._ewkList[i].SetName(self._ewkList[i].GetName()+histoName.replace("/",""))
                histogramsExtras.makeFlowBinsVisible(self._ewkList[i])
            self._rebinDoneStatus = True

    ## Delete the histograms
    def delete(self):
        for h in self._dataList:
            if h == None:
                raise Exception("asdf")
            ROOT.gDirectory.Delete(h.GetName())
        for h in self._ewkList:
            if h == None:
                raise Exception()
            ROOT.gDirectory.Delete(h.GetName())
        self._dataList = []
        self._ewkList = []

    def getFileFriendlyHistoName(self):
        return self._histoName.replace("/","_")

    def getHistoName(self):
        return self._histoName

    ## Return the sum of data-ewk in a given phase space split bin
    def getDataDrivenQCDHistoForSplittedBin(self, binIndex, histoSpecs=None):
        if binIndex >= len(self._dataList):
            raise Exception(ErrorLabel()+"DataDrivenQCDShape::getDataDrivenQCDForSplittedBin: requested bin index %d out of range (0-%d)!"%(binIndex,len(self._dataList)))
        if self._rebinDoneStatus:
            h = aux.Clone(self._dataList[binIndex])
            h.SetName(h.GetName()+"dataDriven")
            h.Add(self._ewkList[binIndex], -1.0)
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._dataList[binIndex])
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._dataList[binIndex].GetName(), self._uniqueN), self._dataList[binIndex].GetTitle())
        self._uniqueN += 1
        myModifier.addShape(source=self._dataList[binIndex], dest=h)
        myModifier.subtractShape(source=self._ewkList[binIndex], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the data in a given phase space split bin
    def getDataHistoForSplittedBin(self, binIndex, histoSpecs=None):
        if binIndex >= len(self._dataList):
            raise Exception(ErrorLabel()+"DataDrivenQCDShape::getDataHistoForSplittedBin: requested bin index %d out of range (0-%d)!"%(binIndex,len(self._dataList)))
        if self._rebinDoneStatus:
            h = aux.Clone(self._dataList[binIndex])
            h.SetName(h.GetName()+"_")
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._dataList[binIndex])
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._dataList[binIndex].GetName(), self._uniqueN), self._dataList[binIndex].GetTitle())
        self._uniqueN += 1
        myModifier.addShape(source=self._dataList[binIndex], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the EWK MC in a given phase space split bin
    def getEwkHistoForSplittedBin(self, binIndex, histoSpecs=None):
        if binIndex >= len(self._dataList):
            raise Exception(ErrorLabel()+"DataDrivenQCDShape::getEwkHistoForSplittedBin: requested bin index %d out of range (0-%d)!"%(binIndex,len(self._ewkList)))
        if self._rebinDoneStatus:
            h = aux.Clone(self._ewkList[binIndex])
            h.SetName(h.GetName()+"_")
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._ewkList[binIndex])
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._ewkList[binIndex].GetName(), self._uniqueN), self._ewkList[binIndex].GetTitle())
        self._uniqueN += 1
        myModifier.addShape(source=self._ewkList[binIndex], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the sum of data-ewk integrated over the phase space splitted bins
    def getIntegratedDataDrivenQCDHisto(self, histoSpecs=None):
        if self._rebinDoneStatus:
            h = aux.Clone(self._dataList[0])
            h.SetName(h.GetName()+"Integrated")
            h.Add(self._ewkList[0],-1.0)
            for i in range(1, len(self._dataList)):
                h.Add(self._dataList[i])
                h.Add(self._ewkList[i],-1.0)
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._dataList[0])
        myNameList = self._dataList[0].GetName().split("_")
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._dataList[0].GetName(), self._uniqueN), myNameList[0][:len(myNameList[0])-1])
        self._uniqueN += 1
        for i in range(0, len(self._dataList)):
            myModifier.addShape(source=self._dataList[i], dest=h)
            myModifier.subtractShape(source=self._ewkList[i], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the sum of data integrated over the phase space splitted bins
    def getIntegratedDataHisto(self, histoSpecs=None):
        if self._rebinDoneStatus:
            h = aux.Clone(self._dataList[0])
            h.SetName(h.GetName()+"Integrated")
            for i in range(1, len(self._dataList)):
                h.Add(self._dataList[i])
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._dataList[0])
        myNameList = self._dataList[0].GetName().split("_")
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._dataList[0].GetName(), self._uniqueN), myNameList[0][:len(myNameList[0])-1])
        self._uniqueN += 1
        for i in range(0, len(self._dataList)):
            myModifier.addShape(source=self._dataList[i], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the sum of ewk integrated over the phase space splitted bins
    def getIntegratedEwkHisto(self, histoSpecs=None):
        if self._rebinDoneStatus:
            h = aux.Clone(self._ewkList[0])
            h.SetName(h.GetName()+"Integrated")
            for i in range(1, len(self._dataList)):
                h.Add(self._ewkList[i])
            return h

        # Do summing within shape histo modifier
        myModifier = ShapeHistoModifier(histoSpecs, histoObjectForSpecs=self._ewkList[0])
        myNameList = self._ewkList[0].GetName().split("_")
        h = myModifier.createEmptyShapeHistogram("%s_%d"%(self._ewkList[0].GetName(), self._uniqueN), myNameList[0][:len(myNameList[0])-1])
        self._uniqueN += 1
        for i in range(0, len(self._ewkList)):
            myModifier.addShape(source=self._ewkList[i], dest=h)
        myModifier.finaliseShape(dest=h) # Convert errors from variances to std.devs.
        return h

    ## Return the QCD purity as a histogram with splitted bins on x-axis
    def getPurityHisto(self):
        # Create histogram
        myNameList = self._ewkList[0].GetName().split("_")
        h = ROOT.TH1F("%s_purity_%d"%(self._ewkList[0].GetName(), self._uniqueN), "PurityBySplittedBin_%s"%myNameList[0][:len(myNameList[0])-1], len(self._ewkList),0,len(self._ewkList))
        h.Sumw2()
        h.SetYTitle("Purity, %")
        ROOT.SetOwnership(h, True)
        self._uniqueN += 1
        for i in range(0, len(self._dataList)):
            h.GetXaxis().SetBinLabel(i+1, self._dataList[i].GetTitle())
            nData = 0.0
            nEwk = 0.0
            for j in range(0, self._dataList[i].GetNbinsX()+2):
                nData += self._dataList[i].GetBinContent(j)
                nEwk += self._ewkList[i].GetBinContent(j)
            myPurity = 0.0
            myUncert = 0.0
            if (nData > 0.0):
                myPurity = (nData - nEwk) / nData
                myUncert = sqrt(myPurity * (1.0-myPurity) / nData) # Assume binomial error
            h.SetBinContent(i+1, myPurity * 100.0)
            h.SetBinError(i+1, myUncert * 100.0)
        return h

    ## Return the QCD purity as a Count object
    def getIntegratedPurity(self):
        nData = 0.0
        nEwk = 0.0
        for i in range(0, len(self._dataList)):
            for j in range(0, self._dataList[i].GetNbinsX()+2):
                nData += self._dataList[i].GetBinContent(j)
                nEwk += self._ewkList[i].GetBinContent(j)
        myPurity = 0.0
        myUncert = 0.0
        if (nData > 0.0):
            myPurity = (nData - nEwk) / nData
            myUncert = sqrt(myPurity * (1.0-myPurity) / nData) # Assume binomial error
        return Count(myPurity, myUncert)

    ## Return the minimum QCD purity as a Count object
    def getMinimumPurity(self):
        myMinPurity = 0.0
        myMinPurityUncert = 0.0
        for i in range(0, len(self._dataList)):
            for j in range(0, self._dataList[i].GetNbinsX()+2):
                nData += self._dataList[i].GetBinContent(j)
                nEwk += self._ewkList[i].GetBinContent(j)
        myPurity = 0.0
        myUncert = 0.0
        if (nData > 0.0):
            myPurity = (nData - nEwk) / nData
            myUncert = sqrt(myPurity * (1.0-myPurity) / nData) # Assume binomial error
            if myPurity < myMinPurity:
                myMinPurity = myPurity
                myMinPurityUncert = myUncert
        return Count(myMinPurity, myMinPurityUncert)

    ## Return the QCD purity in bins of the final shape
    def getIntegratedPurityForShapeHisto(self, histoSpecs=None):
        hData = self.getIntegratedDataHisto(histoSpecs=histoSpecs)
        hEwk = self.getIntegratedEwkHisto(histoSpecs=histoSpecs)
        h = aux.Clone(hData, "%s_purity_%d"%(hData,self._uniqueN))
        myNameList = self._dataList[0].GetName().split("_")
        h.SetTitle("PurityByFinalShapeBin_%s"%myNameList[0][:len(myNameList[0])-1])
        self._uniqueN += 1
        for i in range(1, h.GetNbinsX()+1):
            myPurity = 0.0
            myUncert = 0.0
            if (hData.GetBinContent(i) > 0.0):
                myPurity = (hData.GetBinContent(i) - hEwk.GetBinContent(i)) / hData.GetBinContent(i)
                if myPurity < 0.0:
                    myPurity = 0.0
                    myUncert = 0.0
                else:
                    myUncert = sqrt(myPurity * (1.0-myPurity) / hData.GetBinContent(i)) # Assume binomial error
            h.SetBinContent(i, myPurity)
            h.SetBinError(i, myUncert)
        return h

    ## Returns the labels of the phase space splitting axes
    def getPhaseSpaceSplittingAxisLabels(self):
        return self._splittedHistoReader.getBinLabels()

    ## Returns phase space split title for a bin
    def getPhaseSpaceBinTitle(self, binIndex):
        if binIndex >= len(self._dataList):
            raise Exception(ErrorLabel()+"DataDrivenQCDShape::getPhaseSpaceBinTitle: requested bin index %d out of range (0-%d)!"%(binIndex,len(self._dataList)))
        return self._dataList[binIndex].GetTitle()

    ## Returns phase space split title for a bin
    def getPhaseSpaceBinFileFriendlyTitle(self, binIndex):
        if binIndex >= len(self._dataList):
            raise Exception(ErrorLabel()+"DataDrivenQCDShape::getPhaseSpaceBinTitle: requested bin index %d out of range (0-%d)!"%(binIndex,len(self._dataList)))
        return self._dataList[binIndex].GetTitle().replace(">","gt").replace("<","lt").replace("=","eq").replace("{","").replace("}","").replace(" ","").replace("#","").replace("..","to").replace("(","").replace(")","").replace(",","").replace("/","_")

    ## Returns number of phase space bins
    def getNumberOfPhaseSpaceSplitBins(self):
        return self._splittedHistoReader.getMaxBinNumber()

    ## Returns name of histogram combined with the split bin title
    def getOutputHistoName(self, suffix=""):
        s = "%s"%(self._dataList[0].GetName().replace("/","_"))
        if len(suffix) > 0:
            s += "_%s"%suffix
        return s

## Efficiency from two shape objects
class DataDrivenQCDEfficiency:
    ## numerator and denominator are DataDrivenQCDShape objects
    def __init__(self, numerator, denominator, histoSpecs):
        self._efficiencies = [] # List of ExtendedCount objects, one for each phase space split bin

        self._calculate(numerator, denominator, histoSpecs)

    def delete(self):
        for e in self._efficiencies:
            del e
        self._efficiencies = None

    def getEfficiencyForSplitBin(self, binIndex):
        return self._efficiencies[binIndex]

    def _calculate(self, numerator, denominator, histoSpecs):
        self._efficiencies = []
        myUncertaintyLabels = ["statData", "statEWK"]
        nSplitBins = numerator.getNumberOfPhaseSpaceSplitBins()
        for i in range(0, nSplitBins):
            hNum = numerator.getDataDrivenQCDHistoForSplittedBin(i, histoSpecs)
            hNum.SetName("hNum")
            hNumData = numerator.getDataHistoForSplittedBin(i, histoSpecs)
            hNumData.SetName("hNumData")
            hNumEwk = numerator.getEwkHistoForSplittedBin(i, histoSpecs)
            hNumEwk.SetName("hNumEwk")
            hDenom = denominator.getDataDrivenQCDHistoForSplittedBin(i, histoSpecs)
            hDenom.SetName("hDenom")
            hDenomData = denominator.getDataHistoForSplittedBin(i, histoSpecs)
            hDenomData.SetName("hDenomData")
            hDenomEwk = denominator.getEwkHistoForSplittedBin(i, histoSpecs)
            hDenomEwk.SetName("hDenomEwk")
            # Sum over basic shape and leg2 shape to obtain normalisation factor
            mySumNum = hNum.Integral(1, hNum.GetNbinsX()+2)
            mySumNumDataUncert = integratedUncertaintyForHistogram(1, hNumData.GetNbinsX()+2, hNumData)
            mySumNumEwkUncert = integratedUncertaintyForHistogram(1, hNumEwk.GetNbinsX()+2, hNumEwk)
            mySumDenom = hDenom.Integral(1, hDenom.GetNbinsX()+2)
            mySumDenomDataUncert = integratedUncertaintyForHistogram(1, hDenomData.GetNbinsX()+2, hDenomData)
            mySumDenomEwkUncert = integratedUncertaintyForHistogram(1, hDenomEwk.GetNbinsX()+2, hDenomEwk)
            # Calculate efficiency
            myEfficiency = 0.0
            myEfficiencyUncertData = errorPropagationForDivision(mySumNum, mySumNumDataUncert, mySumDenom, mySumDenomDataUncert)
            myEfficiencyUncertEwk = errorPropagationForDivision(mySumNum, mySumNumEwkUncert, mySumDenom, mySumDenomEwkUncert)
            if abs(mySumNum) > 0.000001 and abs(mySumDenom) > 0.000001:
                myEfficiency = mySumNum / mySumDenom
            self._efficiencies.append(ExtendedCount(myEfficiency, [myEfficiencyUncertData, myEfficiencyUncertEwk], myUncertaintyLabels))
            ROOT.gDirectory.Delete("hNum")
            ROOT.gDirectory.Delete("hNumData")
            ROOT.gDirectory.Delete("hNumEwk")
            ROOT.gDirectory.Delete("hDenom")
            ROOT.gDirectory.Delete("hDenomData")
            ROOT.gDirectory.Delete("hDenomEwk")
        #FIXME: add histogram for efficiency

