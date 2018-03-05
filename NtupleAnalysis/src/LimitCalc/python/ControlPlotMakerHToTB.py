'''
## \package ControlPlotMaker

Classes for making control plots
'''
#================================================================================================ 
# Imports
#================================================================================================ 
from HiggsAnalysis.LimitCalc.DatacardColumn import DatacardColumn
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
from HiggsAnalysis.NtupleAnalysis.tools.dataset import Count,RootHistoWithUncertainties
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux

import HiggsAnalysis.NtupleAnalysis.tools.histograms as histograms
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.counter as counter
import HiggsAnalysis.NtupleAnalysis.tools.tdrstyle as tdrstyle
import HiggsAnalysis.NtupleAnalysis.tools.styles as styles

from math import pow,sqrt,log10
import os
import sys
import ROOT

#================================================================================================ 
# Definitions
#================================================================================================ 
_legendLabelQCDMC    = "QCD (MC)" 
_legendLabelEWKMC    = "QCD (MC)" 
_legendLabelFakeB    = "Fake-b (data)" 

drawPlot = plots.PlotDrawer(ratio=True, ratioYlabel="Data/Bkg. ", ratioCreateLegend=True,
                            ratioType="errorScale", ratioErrorOptions={"numeratorStatSyst": False},
                            stackMCHistograms=True, addMCUncertainty=True, addLuminosityText=True,
                            cmsTextPosition="outframe")

drawPlot2D = plots.PlotDrawer(opts2={"ymin": 0.5, "ymax": 1.5},
                            ratio=False, #ratioYlabel="Data/Bkg.", ratioCreateLegend=True,
                            #ratioType="errorScale", ratioErrorOptions={"numeratorStatSyst": False},
                            #stackMCHistograms=True, addMCUncertainty=True, 
                            addLuminosityText=True,
                            cmsTextPosition="outframe")


#================================================================================================ 
# Definitions
#================================================================================================ 
class ControlPlotMakerHToTB:
    def __init__(self, opts, config, dirname, luminosity, observation, datasetGroups, verbose=False):
        plots._legendLabels["MCStatError"] = "Bkg. stat."
        plots._legendLabels["MCStatSystError"] = "Bkg. stat.#oplussyst."
        plots._legendLabels["BackgroundStatError"] = "Bkg. stat. unc"
        plots._legendLabels["BackgroundStatSystError"] = "Bkg. stat.#oplussyst. unc."
        if config.ControlPlots == None:
            return
        myStyle = tdrstyle.TDRStyle()
        myStyle.setOptStat(False)
        self._verbose = verbose
        self._opts    = opts
        self._config  = config
        if config.OptionSqrtS == None:
            raise Exception(ShellStyles.ErrorLabel()+"Please set the parameter OptionSqrtS = <integer_value_in_TeV> in the config file!"+ShellStyles.NormalStyle())
        self._dirname = dirname
        self._luminosity = luminosity
        self._observation = observation
        self._datasetGroups = datasetGroups

        # Make control plots
        self.Verbose(ShellStyles.HighlightStyle() + "Generating control plots" + ShellStyles.NormalStyle(), True)
        # Loop over mass points
        massPoints = []
        massPoints.extend(self._config.MassPoints)
        massPoints.append(-1) # for plotting with no signal

        # Definitions
        nMasses = len(massPoints)
        nPlots  = len(self._config.ControlPlots)
        counter = 0

        # For-loop: All mass points
        for m in massPoints:

            # Initialize flow plot
            selectionFlow   = SelectionFlowPlotMaker(self._opts, self._config, m) #fixme
            myBlindedStatus = False

            # For-loop: All control plots
            for i in range(0, nPlots):
                counter += 1
                msg = "Control Plot %d/%d (m=%s GeV)"  % (counter, nMasses*nPlots, str(m))
                self.Print(ShellStyles.AltStyle() + msg + ShellStyles.NormalStyle(), counter==1)
                
                # Skip if control plot does not exist
                if observation.getControlPlotByIndex(i) == None:
                    continue
                
                # Get the control plot
                myCtrlPlot = self._config.ControlPlots[i]
                self.Verbose("Creating control plot \"%s\"" % (myCtrlPlot.title), False)
                myMassSuffix = "_M%d" % (m)

                # Initialize histograms
                hData     = None
                hSignal   = None
                hFakeB    = None
                hQCDMC    = None
                
                # Create a list to save all the histograms to be plotted
                myStackList = []
                # For-loop: All dataset columns (to find histograms)
                for c in self._datasetGroups:                       
                        self.Verbose("Dataset is %s for plot %s" % (myCtrlPlot.title, c.getLabel()), False)
                        # print "Label, Integral:",c.getLabel(), h.getRootHisto().Integral(0,h.GetNbinsX()+2)

                        bDoPlot  = (m < 0 or c.isActiveForMass(m, self._config)) and not c.typeIsEmptyColumn() and not c.getControlPlotByIndex(i) == None
                        if not bDoPlot:
                            continue

                        # Clone histo
                        h = c.getControlPlotByIndex(i)["shape"].Clone()

                        if c.typeIsSignal():
                            if hSignal == None:
                                hSignal = h.Clone()
                            else:
                                hSignal.Add(h)
                        elif c.typeIsFakeB():
                            if hFakeB == None:
                                hFakeB = h.Clone()
                            else:
                                hFakeB.Add(h)
                        elif c.typeIsQCDMC():
                            if hQCD == None:
                                hQCDMC = h.Clone()
                            else:
                                hQCDMC.Add(h)
                        elif c.typeIsEWKMC() or c.typeIsGenuineB():
                            myHisto = histograms.Histo(h, c._datasetMgrColumn)
                            myHisto.setIsDataMC(isData=False, isMC=True)
                            myStackList.append(myHisto)
                            
                # FIXME: what's this exactly?
                if len(myStackList) < 1 or self._config.OptionFakeBMeasurementSource != "DataDriven":
                    continue

                # Stack all the histograms
                if hFakeB != None:
                    myHisto = histograms.Histo(hFakeB, "FakeB", legendLabel=_legendLabelFakeB)
                    myHisto.setIsDataMC(isData=False, isMC=True)
                    myStackList.insert(0, myHisto)
                elif hQCDMC != None:
                    myHisto = histograms.Histo(hQCDMC,"QCDMC",legendLabel=_legendLabelQCDMC)
                    myHisto.setIsDataMC(isData=False, isMC=True)
                    myStackList.insert(0, myHisto)
                    
                hData = observation.getControlPlotByIndex(i)["shape"].Clone()
                hDataUnblinded = hData.Clone()

                # Apply blinding
                myBlindingString = None
                if self._config.BlindAnalysis:
                    if len(myCtrlPlot.blindedRange) > 0:
                        myBlindingString = self._applyBlinding(hData,myCtrlPlot.blindedRange)
                    if self._config.OptionBlindThreshold != None:
                        for k in xrange(1, hData.GetNbinsX()+1):
                            myExpValue = 0.0
                            for item in myStackList:
                                myExpValue += item.getRootHisto().GetBinContent(k)
                            if hSignal.getRootHisto().GetBinContent(k) >= myExpValue * self._config.OptionBlindThreshold:
                                hData.getRootHisto().SetBinContent(k, -1.0)
                                hData.getRootHisto().SetBinError(k, 0.0)
                # Data
                myDataHisto = histograms.Histo(hData,"Data")
                myDataHisto.setIsDataMC(isData=True, isMC=False)
                myStackList.insert(0, myDataHisto)
                    
                # Add signal
                if m > 0:
                    mySignalLabel = "HplusTB_M%d"%m
                    myHisto = histograms.Histo(hSignal,mySignalLabel)
                    myHisto.setIsDataMC(isData=False, isMC=True)
                    myStackList.insert(1, myHisto)
                        
                # Add data to selection flow plot
                selectionFlow.addColumn(myCtrlPlot.flowPlotCaption,hDataUnblinded,myStackList[1:])
                if len(myCtrlPlot.blindedRange) > 0:
                    myBlindedStatus = True
                else:
                    myBlindedStatus = False

                # Make plot
                myStackPlot = None
                myParams = myCtrlPlot.details.copy()
                myStackPlot = plots.DataMCPlot2(myStackList)
                myStackPlot.setLuminosity(self._luminosity)
                myStackPlot.setEnergy("%d"%self._config.OptionSqrtS)
                myStackPlot.setDefaultStyles()
                
                # Tweak paramaters
                if not "unit" in myParams.keys():
                    myParams["unit"] = ""

                if myParams["unit"] != "":
                    myParams["xlabel"] = "%s (%s)"%(myParams["xlabel"],myParams["unit"])

                # ALEX-IRO-START
                self._setYlabelWidthSuffix(hData, myParams)
#                ylabelBinInfo = True
#                if "ylabelBinInfo" in myParams:
#                    ylabelBinInfo = myParams["ylabelBinInfo"]
#                    del myParams["ylabelBinInfo"]
#
#                if ylabelBinInfo:
#                    self._setYlabelWidthSuffix(hData, myParams)
#                    minBinWidth, maxBinWidth = self._getMinMaxBinWidth(hData)
#
#                    widthSuffix = ""
#                    minBinWidthString = "%d" % minBinWidth
#                    maxBinWidthString = "%d" % maxBinWidth
#
#                    if minBinWidth < 1.0:
#                        myFormat = "%%.%df" % (abs(int(log10(minBinWidth)))+1)
#                        minBinWidthString = myFormat % minBinWidth
#                    if maxBinWidth < 1.0:
#                        myFormat = "%%.%df" % (abs(int(log10(maxBinWidth)))+1)
#                        maxBinWidthString = myFormat % maxBinWidth
#
#                    widthSuffix = "%s-%s" % (minBinWidthString, maxBinWidthString)
#                    if abs(minBinWidth-maxBinWidth) < 0.001:
#                        widthSuffix = "%s" % (minBinWidthString)
#
#                    if (myParams["unit"] == "" and widthSuffix == "1"):
#                        pass
#                    else:
#                        myParams["ylabel"] = "%s / %s %s" % (myParams["ylabel"], widthSuffix, myParams["unit"])
                # ALEX-IRO-END
                        
                if myBlindingString != None:
                    if myParams["unit"] != "" and myParams["unit"][0] == "^":
                        myParams["blindingRangeString"] = "%s%s"%(myBlindingString, myParams["unit"])
                    else:
                        myParams["blindingRangeString"] = "%s %s"%(myBlindingString, myParams["unit"])
                                
                self._setLegendPosition(myParams)
                self._setRatioLegendPosition(myParams)

                # Remove non-dientified keywords
                del myParams["unit"]
                # Ratio axis
                if not "opts2" in myParams.keys():
                    myParams["opts2"] = {"ymin": 0.3, "ymax": 1.7}

                # Do plotting
                if m > 0:
                    drawPlot(myStackPlot, "%s/DataDrivenCtrlPlot_M%d_%02d_%s"%(self._dirname,m,i,myCtrlPlot.title), **myParams)
                else:
                    drawPlot(myStackPlot, "%s/DataDrivenCtrlPlot_%02d_%s"%(self._dirname,i,myCtrlPlot.title), **myParams)
                
            # Do selection flow plot
            selectionFlow.makePlot(self._dirname,m,len(self._config.ControlPlots),self._luminosity)
        #myEvaluator.save(dirname)
        sys.exit()
        return

    def _setYlabelWidthSuffix(self, histo, myParams):
        ylabelBinInfo = True
        if "ylabelBinInfo" in myParams:
            ylabelBinInfo = myParams["ylabelBinInfo"]
            del myParams["ylabelBinInfo"]

        if ylabelBinInfo:
            minBinWidth, maxBinWidth = self._getMinMaxBinWidth(histo)

            widthSuffix = ""
            minBinWidthString = "%d" % minBinWidth
            maxBinWidthString = "%d" % maxBinWidth
            
            if minBinWidth < 1.0:
                myFormat = "%%.%df" % (abs(int(log10(minBinWidth)))+1)
                minBinWidthString = myFormat % minBinWidth
            if maxBinWidth < 1.0:
                myFormat = "%%.%df" % (abs(int(log10(maxBinWidth)))+1)
                maxBinWidthString = myFormat % maxBinWidth

            widthSuffix = "%s-%s" % (minBinWidthString, maxBinWidthString)
            if abs(minBinWidth-maxBinWidth) < 0.001:
                widthSuffix = "%s" % (minBinWidthString)

            if (myParams["unit"] == "" and widthSuffix == "1"):
                return
            else:
                myParams["ylabel"] = "%s / %s %s" % (myParams["ylabel"], widthSuffix, myParams["unit"])
            return

    def _getMinMaxBinWidth(self, histo):

        minWidth = 10000.0
        maxWidth = 0.0
        
        # For-loop: All bins
        for j in range(1, histo.getRootHisto().GetNbinsX()+1):
            w = histo.getRootHisto().GetBinWidth(j)
            if w < minWidth:
                minWidth = w
            if w > maxWidth:
                maxWidth = w
        return minWidth, maxWidth

    def _setRatioLegendPosition(self, myParams):
        if "ratioLegendPosition" in myParams.keys():
            self.Verbose("Setting the legend (ratio) position to \"%s\"" % ( myParams["ratioLegendPosition"] ) )
            if myParams["ratioLegendPosition"] == "left":
                myParams["ratioMoveLegend"] = {"dx": -0.51, "dy": 0.03}
            elif myParams["ratioLegendPosition"] == "right":
                myParams["ratioMoveLegend"] = {"dx": -0.08, "dy": 0.03}
            elif myParams["ratioLegendPosition"] == "SE":
                myParams["ratioMoveLegend"] = {"dx": -0.08, "dy": -0.33}
            else:
                raise Exception("Unknown value for option ratioLegendPosition: %s!", myParams["ratioLegendPosition"])
            del myParams["ratioLegendPosition"]
        else:
            if not "ratioMoveLegend" in myParams:
                myParams["ratioMoveLegend"] = {"dx": -0.51, "dy": 0.03} # default: left
        return

    def _setLegendPosition(self, myParams):
        if "legendPosition" in myParams.keys():
            self.Verbose("Setting the legend position to \"%s\"" % ( myParams["legendPosition"] ) )
            if myParams["legendPosition"] == "NE":
                myParams["moveLegend"] = {"dx": -0.10, "dy": -0.02, "dh": 0.1}
            elif myParams["legendPosition"] == "SE":
                myParams["moveLegend"] = {"dx": -0.10, "dy": -0.56, "dh": 0.1}
            elif myParams["legendPosition"] == "SW":
                myParams["moveLegend"] = {"dx": -0.53, "dy": -0.56, "dh": 0.1}
            elif myParams["legendPosition"] == "NW":
                myParams["moveLegend"] = {"dx": -0.53, "dy": -0.02, "dh": 0.1}
            else:
                raise Exception("Unknown value for option legendPosition: %s!", myParams["legendPosition"])
            del myParams["legendPosition"]
        elif not "moveLegend" in myParams:
            myParams["moveLegend"] = {"dx": -0.10, "dy": -0.02} # default: NE
        return

    def Verbose(self, msg, printHeader=True):
        '''
        Calls Print() only if verbose options is set to true
        '''                                                                                                                                                                         
        if not self._verbose:
            return
        Print(msg, printHeader)
        return

    def Print(self, msg, printHeader=True):
        '''
        Simple print function. If verbose option is enabled prints, otherwise does nothing
        '''
        fName = __file__.split("/")[-1]
        fName = fName.replace(".pyc", ".py")
        if printHeader:
            print "=== ", fName
        print "\t", msg
        return


    def _applyBlinding(self,myObject,blindedRange = []):
        myMin = None
        myMax = None
        myHisto = myObject.getRootHisto()
        for i in range (1, myHisto.GetNbinsX()+1):
            myUpEdge = myHisto.GetXaxis().GetBinUpEdge(i)
            myLowEdge = myHisto.GetXaxis().GetBinLowEdge(i)
            # Blind if any edge of the current bin is inside the blinded range or if bin spans over the blinded range
            if ((myLowEdge >= blindedRange[0] and myLowEdge <= blindedRange[1]) or
                (myUpEdge >= blindedRange[0] and myUpEdge <= blindedRange[1]) or 
                (myLowEdge <= blindedRange[0] and myUpEdge >= blindedRange[1])):
                if myMin == None or myLowEdge < myMin:
                    myMin = myLowEdge
                if myMax == None or myUpEdge > myMax:
                    myMax = myUpEdge
                myHisto.SetBinContent(i, -1.0)
                myHisto.SetBinError(i, 0.0)
        if myMin == None:
            return None
        myMinFormat = "%"+"d"
        myMaxFormat = "%"+"d"
        if abs(myMin) < 1.0 and abs(myMin) > 0.00000001:
            myMinFormat = "%%.%df"%(abs(int(log10(myMin)))+1)
        if abs(myMax) < 1.0  and abs(myMax) > 0.00000001:
            myMaxFormat = "%%.%df"%(abs(int(log10(myMax)))+1)
        s = myMinFormat%myMin+"-"+myMaxFormat%myMax
        return s

class SignalAreaEvaluator:
    def __init__(self):
        self._output = ""

    def addEntry(self,mass,title,evaluationRange,hSignal,hQCD,hEmbedded,hEWKfake):
        # Obtain event counts
        mySignal = self._evaluate(evaluationRange,hSignal)
        myQCD = self._evaluate(evaluationRange,hQCD)
        myEmbedded = self._evaluate(evaluationRange,hEmbedded)
        myEWKfake = self._evaluate(evaluationRange,hEWKfake)
        # Produce output
        myOutput = "%s, mass=%d, range=%d-%d\n"%(title,mass,evaluationRange[0],evaluationRange[1])
        myOutput += "  signal: %f +- %f\n"%(mySignal.value(),mySignal.uncertainty())
        myOutput += "  QCD: %f +- %f\n"%(myQCD.value(),myQCD.uncertainty())
        myOutput += "  EWKtau: %f +- %f\n"%(myEmbedded.value(),myEmbedded.uncertainty())
        myOutput += "  EWKfake: %f +- %f\n"%(myEWKfake.value(),myEWKfake.uncertainty())
        myExpected = Count(0.0, 0.0)
        myExpected.add(myQCD)
        myExpected.add(myEmbedded)
        myExpected.add(myEWKfake)
        myOutput += "  Total expected: %f +- %f\n"%(myExpected.value(),myExpected.uncertainty())
        mySignal.divide(myExpected)
        myOutput += "  signal/expected: %f +- %f\n"%(mySignal.value(),mySignal.uncertainty())
        myOutput += "\n"
        self._output += myOutput

    def save(self,dirname):
        myFilename = dirname+"/signalAreaEvaluation.txt"
        myFile = open(myFilename, "w")
        myFile.write(self._output)
        myFile.close()
        print ShellStyles.HighlightStyle()+"Signal area evaluation written to: "+ShellStyles.NormalStyle()+myFilename
        self._output = ""

    def _evaluate(self,evaluationRange,h):
        myResult = 0.0
        myError = 0.0
        for i in range(1,h.GetNbinsX()+1):
            if (h.GetXaxis().GetBinLowEdge(i) >= evaluationRange[0] and
                h.GetXaxis().GetBinUpEdge(i) <= evaluationRange[1]):
                myResult += h.GetBinContent(i)
                myError += pow(h.GetBinError(i),2)
        return Count(myResult,sqrt(myError))

class SelectionFlowPlotMaker:
    def __init__(self, opts, config, mass):
        self._opts = opts
        self._config = config
        self._mass = mass
        # Calculate number of bins
        myBinList = []
        for c in self._config.ControlPlots:
            if c.flowPlotCaption != "" and c.flowPlotCaption != "final":
                myBinList.append(c.flowPlotCaption)
        myBinCount = len(myBinList)
        # Make an empty frame
        myPlotName = "SelectionFlow_%d"%mass
        self._hFrame = ROOT.TH1F(myPlotName,myPlotName,myBinCount,0,myBinCount)
        for i in range(0,myBinCount):
            self._hFrame.GetXaxis().SetBinLabel(i+1, myBinList[i])
        # Make empty histograms for HH, HW, QCD, EWKtau, EWKfake, datacard
        self._expectedList = []
        self._expectedLabelList = []
        self._expectedListSystUp = []
        self._expectedListSystDown = []
        self._data = None
        # Initialise column pointer
        self._myCurrentColumn = 1
        self._pickStatus = False
        self._pickLabel = ""

    def delete(self):
        for h in self._expectedList:
            h.Delete()
        self._expectedList = None
        for h in self._expectedListSystUp:
            h.Delete()
        self._expectedListSystUp = None
        for h in self._expectedListSystDown:
            h.Delete()
        self._expectedListSystDown = None
        self._expectedLabelList = None
        self._data.Delete()

    def addColumn(self,label,data,expectedList):
        # System to pick the correct input for correct label
        if label == "":
            return
        # Create histograms if necessary
        if self._data == None:
            self._createHistograms(data,expectedList)
            return
        # Add expected
        for i in range(0,len(expectedList)):
            myRate = expectedList[i].getRootHistoWithUncertainties().getRate()
            self._expectedList[i].SetBinContent(self._myCurrentColumn, myRate)
            self._expectedList[i].SetBinError(self._myCurrentColumn, expectedList[i].getRootHistoWithUncertainties().getRateStatUncertainty())
            uncertUp = 0.0
            uncertDown = 0.0
            if myRate > 0.0:
                (uncertUp,uncertDown) = expectedList[i].getRootHistoWithUncertainties().getRateSystUncertainty()
                self._expectedListSystUp[i].SetBinContent(self._myCurrentColumn, uncertUp/myRate)
                self._expectedListSystDown[i].SetBinContent(self._myCurrentColumn, -uncertDown/myRate)
            if self._opts.debugControlPlots:
                s = "debugControlPlots:,"
                s += "After "+self._pickLabel
                s += ","+expectedList[i].getName()
                s += ",%f"%myRate
                s += ",+-,%f,(stat.)"%self._expectedList[i].GetBinError(self._myCurrentColumn)
                s += ",+,%f"%uncertUp
                s += ",-,%f,(syst.)"%uncertDown
                print s
        # Add data
        if data != None:
            self._data.SetBinContent(self._myCurrentColumn, data.getRate())
            self._data.SetBinError(self._myCurrentColumn, data.getRateStatUncertainty())
        else:
            self._data.SetBinContent(self._myCurrentColumn, -1)
        self._myCurrentColumn += 1
        # Refresh pick status
        self._pickLabel = label

    def _createHistograms(self,data,expectedList):
        for e in expectedList:
            self._expectedList.append(aux.Clone(self._hFrame))
            self._expectedList[len(self._expectedList)-1].Reset()
            self._expectedListSystUp.append(aux.Clone(self._hFrame))
            self._expectedListSystUp[len(self._expectedListSystUp)-1].Reset()
            self._expectedListSystDown.append(aux.Clone(self._hFrame))
            self._expectedListSystDown[len(self._expectedListSystDown)-1].Reset()
            self._expectedLabelList.append(e.name)
        self._data = aux.Clone(self._hFrame)
        self._data.Reset()

    def makePlot(self, dirname, m, index, luminosity):
        if self._data == None:
            return
        myStackList = []
        # expected
        for i in range(0,len(self._expectedList)):
            myRHWU = RootHistoWithUncertainties(self._expectedList[i])
            myRHWU.addShapeUncertaintyRelative("syst", th1Plus=self._expectedListSystUp[i], th1Minus=self._expectedListSystDown[i])
            myRHWU.makeFlowBinsVisible()
            if self._expectedLabelList[i] == "QCD":
                myHisto = histograms.Histo(myRHWU, self._expectedLabelList[i], legendLabel=_legendLabelQCD)
            elif self._expectedLabelList[i] == "FakeB":
                myHisto = histograms.Histo(myRHWU, self._expectedLabelList[i], legendLabel=_legendLabelFakeB)
            elif self._expectedLabelList[i] == "EWKfakes":
                myHisto = histograms.Histo(myRHWU, self._expectedLabelList[i], legendLabel=_legendLabelEWKFakes)
            else:
                myHisto = histograms.Histo(myRHWU, self._expectedLabelList[i])
            myHisto.setIsDataMC(isData=False, isMC=True)
            myStackList.append(myHisto)
        # data
        myRHWU = RootHistoWithUncertainties(self._data)
        myRHWU.makeFlowBinsVisible()
        myHisto = histograms.Histo(myRHWU, "Data")
        myHisto.setIsDataMC(isData=True, isMC=False)
        myStackList.insert(0, myHisto)
        # Make plot
        myStackPlot = plots.DataMCPlot2(myStackList)
        myStackPlot.setLuminosity(luminosity)
        myStackPlot.setEnergy("%d"%self._config.OptionSqrtS)
        myStackPlot.setDefaultStyles()
        myParams = {}
        myParams["ylabel"] = "Events"
        myParams["log"] = True
        myParams["cmsTextPosition"] = "right"
        myParams["opts"] = {"ymin": 0.9}
        myParams["opts2"] = {"ymin": 0.3, "ymax":1.7}
        #myParams["moveLegend"] = {"dx": -0.08, "dy": -0.12, "dh": 0.1} # for MC EWK+tt
        #myParams["moveLegend"] = {"dx": -0.15, "dy": -0.12, "dh":0.05} # for data-driven
        myParams["moveLegend"] = {"dx": -0.53, "dy": -0.52, "dh":0.05} # for data-driven
        myParams["ratioMoveLegend"] = {"dx": -0.51, "dy": 0.03}
        drawPlot(myStackPlot, "%s/DataDrivenCtrlPlot_M%d_%02d_SelectionFlow"%(dirname,m,index), **myParams)

