#!/usr/bin/env python

###########################################################################
#
# This script is only intended as an example, please do NOT modify it.
# For example, start from scratch and look here for help, or make a
# copy of it and modify the copy (including removing all unnecessary
# code).
#
###########################################################################

import ROOT
#ROOT.gROOT.SetBatch(True)
from ROOT import *
import math
import sys
import copy
import re

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset as dataset
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms as histograms
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.counter as counter
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.crosssection as xsect

analysis = "signalAnalysis"
counters = analysis+"Counters/weighted"

def Linear(x,par):
    return par[0]*x[0] + par[1]

def ErrorFunction(x,par):
    return 0.5*(1 + TMath.Erf(par[0]*(x[0] - par[1])))

def ExpFunction(x,par):
    if (x[0] > 280 and x[0] < 300) or x[0] > 360:
        TF1.RejectPoint()
        return 0
    return par[0]*TMath.Exp(-x[0]*par[1])
def Gaussian(x,par):
    return par[0]*TMath.Gaus(x[0],par[1],par[2],1)
def DoubleGaussian(x,par):
    return par[0]*TMath.Gaus(x[0],par[1],par[2],1) + par[3]*TMath.Gaus(x[0],par[4],par[5],1)
def SumFunction(x,par):
    return par[0]*TMath.Gaus(x[0],par[1],par[2],1) + par[3]*TMath.Exp(-x[0]*par[4])

def EWKFunction(x,par,norm = 1,rejectPoints = 0):
#    if not rejectPoints == 0:
#        if (x[0] > 280 and x[0] < 300) or x[0] > 360:
#	if x[0] > 40 and x[0] < 60 :
#	if x[0] > 240 and x[0] < 260:
#	if  (x[0] > 180 and x[0] < 200) or (x[0] > 260 and x[0] < 320):
#	if  (x[0] > 100 and x[0] < 120) or (x[0] > 180 and x[0] < 200):
#	if  (x[0] > 60 and x[0] < 80) or (x[0] > 140 and x[0] < 160) or (x[0] > 180 and x[0] < 220) or (x[0] > 240 and x[0] < 360):
#	if  (x[0] > 40 and x[0] < 60) or (x[0] > 80 and x[0] < 100) or (x[0] > 120 and x[0] < 140) or (x[0] > 160 and x[0] < 180):
#            TF1.RejectPoint()
#            return 0
    value = 130
    if x[0] < value:
	return norm*par[0]*TMath.Gaus(x[0],par[1],par[2],1)
    C = norm*par[0]*TMath.Gaus(value,par[1],par[2],1)*TMath.Exp(value*par[3])
    return C*TMath.Exp(-x[0]*par[3])

def QCDFunction(x,par,norm):
    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Gaus(x[0],par[4],par[5],1)+par[6]*TMath.Exp(-par[7]*x[0]))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Gaus(x[0],par[4],par[5],1))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Exp(-par[4]*x[0]))

def QCDFunctionFixed(x,par):
    return par[0]*(TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Gaus(x[0],par[4],par[5],1)+par[6]*TMath.Exp(-par[7]*x[0]))


#def EWKFunction(x,par,norm):
#    if (x[0] > 280 and x[0] < 300) or x[0] > 360:
#	TF1.RejectPoint()
#	return 0
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Gaus(x[0],par[4],par[5],1))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1))
#    return norm*(par[0]*TMath.Exp(-x[0]*par[1]))
#    return norm*(par[0]*TMath.Landau(x[0],par[1],par[2]))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)+par[3]*TMath.Landau(x[0],par[4],par[5]))
#     return norm*(par[0]*TMath.Poisson(x[0],par[1]))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)*TMath.Exp(-x[0]*par[3]))
#    return norm*(par[0]*TMath.Gaus(x[0],par[1],par[2],1)*TMath.Sqrt(x[0]))

class InvertedTauID:

    def __init__(self):
	self.parInvQCD  = []
	self.parMCEWK   = []
	self.parBaseQCD = []

	self.nInvQCD    = 0
        self.nFitInvQCD = 0
	self.nMCEWK     = 0
	self.nBaseQCD   = 0

	self.normInvQCD  = 1
	self.normEWK     = 1

	self.QCDfraction = 0

	self.label = ""
	self.labels = []
	self.normFactors = []

	self.lumi = 0

	self.errorBars = False

    def setLabel(self, label):
	self.label = label

    def setLumi(self, lumi):
	self.lumi = lumi

    def useErrorBars(self, useHistoErrors):
	self.errorBars = useHistoErrors

    def plotIntegral(self, plot_orig, objectName, canvasName = "Integral"):

#        plot = copy.deepcopy(plot_orig)
        plot = plot_orig
 
        st = styles.getDataStyle().clone()
        st.append(styles.StyleFill(fillColor=ROOT.kYellow))

	plot.histoMgr.forHisto(objectName, st)
	plot.setFrameName(plot.cf.canvas.GetName()+canvasName)
        
	plot.draw()
        plot.save()

        st.append(styles.StyleFill(fillColor=0))
        plot.histoMgr.forHisto(objectName, st)

    def comparison(self,histo1,histo2,norm=1):

	h1 = histo1.Clone("h1")
	h2 = histo2.Clone("h2")
	if norm == 1:
	    h1.Scale(1/h1.GetMaximum())
	    h2.Scale(1/h2.GetMaximum())

	# check that no bin has negative value, negative values possible after subtracting EWK from data  
        iBin = 1
        nBins = h1.GetNbinsX()
        while iBin < nBins:
	    value1 = h1.GetBinContent(iBin)
	    value2 = h2.GetBinContent(iBin)

	    if value1 < 0:
		h1.SetBinContent(iBin,0)

            if value2 < 0:
                h2.SetBinContent(iBin,0)

            iBin = iBin + 1

	if norm > 0:
	    h1.GetYaxis().SetTitle("Arbitrary units")

        plot = plots.ComparisonPlot(
            histograms.Histo(h1, "Inv"),
            histograms.Histo(h2, "Base"),
            )
            # Set the styles
        st1 = styles.getDataStyle().clone()
        st2 = st1.clone()
        st2.append(styles.StyleMarker(markerColor=ROOT.kRed))
	plot.histoMgr.forHisto("Base", st1)
        plot.histoMgr.forHisto("Inv", st2)
        
        # Set the legend labels
        plot.histoMgr.setHistoLegendLabelMany({"Inv": h1.GetTitle(),
                                               "Base": h2.GetTitle()})
        # Set the legend styles
        plot.histoMgr.setHistoLegendStyleAll("P")
        
        # Set the drawing styles
        plot.histoMgr.setHistoDrawStyleAll("EP")
        
        # Create frame with a ratio pad
        plot.createFrame("comparison"+self.label, opts={"ymin":1e-5, "ymaxfactor": 2},
                         createRatio=True, opts2={"ymin": 0, "ymax": 2}, # bounds of the ratio plot
                         )
        
        # Set Y axis of the upper pad to logarithmic
        plot.getPad1().SetLogy(True)

	plot.setLegend(histograms.createLegend(0.4,0.82,0.9,0.93))

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)
 
           
        plot.draw()
        plot.save()



    def cutefficiency(self,histo1,histo2):

        h1 = histo1.Clone("h1")
        h2 = histo2.Clone("h2")

        h1.Scale(1/h1.GetMaximum())
        h2.Scale(1/h2.GetMaximum())

        # check that no bin has negative value, negative values possible after subtracting EWK from data
        iBin = 1
        nBins = h1.GetNbinsX()
        while iBin < nBins:
            value1 = h1.GetBinContent(iBin)
            value2 = h2.GetBinContent(iBin)
        
            if value1 < 0:
                h1.SetBinContent(iBin,0)
        
            if value2 < 0:
                h2.SetBinContent(iBin,0)
        
            iBin = iBin + 1

	h1cut = h1.Clone("h1cut")
	h1cut.Reset()
	h1cut.GetYaxis().SetTitle("Efficiency")
        h1cut.GetXaxis().SetTitle("PF MET cut (GeV)")

        h2cut = h2.Clone("h2cut")
        h2cut.Reset()
	h2cut.SetLineColor(2)

        integralError = ROOT.Double(0.0)
	integralValue = h1.IntegralAndError(1,h1cut.GetNbinsX(),integralError)

        h1_integral = h1.Integral(0,h1.GetNbinsX())
	h2_integral = h2.Integral(0,h2.GetNbinsX())

	iBin = 1
	nBins = h1cut.GetNbinsX()
	while iBin < nBins:
	    error = ROOT.Double(0.0)
	    selected1 = h1.IntegralAndError(iBin,nBins,error)
	    if selected1 > 0:
		error = error/selected1
	    else:
		error = integralError/integralValue
	    efficiency1 = selected1/h1_integral
	    h1cut.SetBinContent(iBin,efficiency1)
	    if self.errorBars:
   	        h1cut.SetBinError(iBin,error)

            error = ROOT.Double(0.0)
            selected2 = h2.IntegralAndError(iBin,nBins,error)
	    if selected2 > 0:
		error = error/selected2
	    else:
		error = integralError/integralValue
            efficiency2 = selected2/h2_integral
            h2cut.SetBinContent(iBin,efficiency2)
	    if self.errorBars:
	        h2cut.SetBinError(iBin,error)

	    iBin = iBin + 1


        plot = plots.ComparisonPlot(
            histograms.Histo(h1cut, "Inv"),
            histograms.Histo(h2cut, "Base"),
            )
            # Set the styles
        st1 = styles.getDataStyle().clone()
        st2 = st1.clone()
        st2.append(styles.StyleLine(lineColor=ROOT.kRed))
	st2.append(styles.StyleMarker(markerColor=ROOT.kRed))
        plot.histoMgr.forHisto("Base", st1)
        plot.histoMgr.forHisto("Inv", st2)

        # Set the legend labels
        plot.histoMgr.setHistoLegendLabelMany({"Inv": h1.GetTitle(),
                                               "Base": h2.GetTitle()})
        # Set the legend styles
        #plot.histoMgr.setHistoLegendStyleAll("L")
	plot.histoMgr.setHistoLegendStyleAll("P")

        # Set the drawing styles
        #plot.histoMgr.setHistoDrawStyleAll("HIST")
        plot.histoMgr.setHistoDrawStyleAll("EP")

        # Create frame with a ratio pad
        plot.createFrame("cuteff"+self.label, opts={"ymin":1e-5, "ymaxfactor": 2},
                         createRatio=True, opts2={"ymin": 0, "ymax": 2}, # bounds of the ratio plot
                         )

        # Set Y axis of the upper pad to logarithmic
        plot.getPad().SetLogy(True)

        plot.setLegend(histograms.createLegend(0.4,0.82,0.9,0.93))
        
        histograms.addCmsPreliminaryText()
        histograms.addEnergyText() 
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)

        plot.draw()
        plot.save()

        ######

        hError = h1cut.Clone("hError")
	hError.Divide(h2cut)

        iBin = 1
        nBins = hError.GetNbinsX()
        while iBin < nBins:
	    hError.SetBinContent(iBin,abs(hError.GetBinContent(iBin) - 1))
	    iBin = iBin + 1

        hError.GetYaxis().SetTitle("abs( (#varepsilon^{Inverted} - #varepsilon^{Baseline})/#varepsilon^{Baseline} )")
        hError.GetXaxis().SetTitle("PF MET cut (GeV)")

        plot2 = plots.PlotBase()
        plot2.histoMgr.appendHisto(histograms.Histo(hError,"ShapeUncertainty"))
        plot2.histoMgr.forHisto("ShapeUncertainty", st1)
        plot2.histoMgr.setHistoDrawStyleAll("EP")
#        plot2.createFrame("shapeUncertainty"+self.label, opts={"ymin":-1, "ymax": 1})
	plot2.createFrame("shapeUncertainty"+self.label, opts={"ymin":-0.1, "ymax": 1.1})

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)


	rangeMin = hError.GetXaxis().GetXmin()
        rangeMax = hError.GetXaxis().GetXmax()
#	rangeMax = 80
	rangeMax = 120
#	rangeMax = 380
        
        numberOfParameters = 2

        class FitFunction:
            def __call__( self, x, par ):
#                return Linear(x,par)
		return ErrorFunction(x,par)

        theFit = TF1('theFit',FitFunction(),rangeMin,rangeMax,numberOfParameters)
        theFit.SetParLimits(0,0.01,0.03)
        theFit.SetParLimits(1,50,150)

#	theFit.FixParameter(0,0.02)
#	theFit.FixParameter(1,100)

	hError.Fit(theFit,"LRN")
	print "Error MET > 40",theFit.Eval(40)
	print "Error MET > 50",theFit.Eval(50)
	print "Error MET > 70",theFit.Eval(70)

	plot2.histoMgr.appendHisto(histograms.Histo(theFit,"Fit"))

	plot2.draw()
        plot2.save()

    def plotHisto(self,histo,canvasName):
        plot = plots.PlotBase()
        plot.histoMgr.appendHisto(histograms.Histo(histo,histo.GetName()))
        plot.createFrame(canvasName+self.label, opts={"ymin": 0.1, "ymaxfactor": 2.})

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)

        plot.getPad().SetLogy(True)

        integralValue = int(0.5 + histo.Integral(0,histo.GetNbinsX(),"width"))
        print histo.GetName(),"Integral",histo.Integral(0,histo.GetNbinsX(),"width")
        histograms.addText(0.4,0.7,"Integral = %s ev"% integralValue)

        match = re.search("aseline",histo.GetName())
        if match:
            self.nBaseQCD = integralValue
        match = re.search("nverted",histo.GetName())
        if match:
            self.nInvQCD = integralValue
            
        self.plotIntegral(plot, histo.GetName())
        
    def fitQCD(self,origHisto): 

	histo = origHisto.Clone("histo")

        rangeMin = histo.GetXaxis().GetXmin()
        rangeMax = histo.GetXaxis().GetXmax()

        numberOfParameters = 8

        print "Fit range ",rangeMin, " - ",rangeMax

	class FitFunction:
	    def __call__( self, x, par ):
		return QCDFunction(x,par,1)

        theFit = TF1('theFit',FitFunction(),rangeMin,rangeMax,numberOfParameters)

        theFit.SetParLimits(0,1,20)
        theFit.SetParLimits(1,20,40)
        theFit.SetParLimits(2,10,25)

        theFit.SetParLimits(3,1,10)
        theFit.SetParLimits(4,0,150)
        theFit.SetParLimits(5,10,100)

        theFit.SetParLimits(6,0.0001,1)
        theFit.SetParLimits(7,0.001,0.05)

	if self.label == "Baseline":
	    rangeMax = 240

	if self.label == "7080":
	    theFit.SetParLimits(5,10,100)

#	if self.label == "100120":
#	    theFit.SetParLimits(0,1,20)
#	    theFit.SetParLimits(2,1,25)
#	    theFit.SetParLimits(3,0.1,20)

	if self.label == "120150":
            theFit.SetParLimits(0,1,20)
            theFit.SetParLimits(3,0.1,5)


	gStyle.SetOptFit(0)

	plot = plots.PlotBase()
	plot.histoMgr.appendHisto(histograms.Histo(histo,histo.GetName()))
	plot.createFrame("qcdfit"+self.label, opts={"ymin": 1e-5, "ymaxfactor": 2.})

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)

	self.normInvQCD = histo.Integral(0,histo.GetNbinsX())

	histo.Scale(1/self.normInvQCD)
        histo.Fit(theFit,"LR")         
                                      
        theFit.SetRange(histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
        theFit.SetLineStyle(2)                                                
        theFit.Draw("same")


        histograms.addText(0.4,0.8,"Inverted TauID")

	plot.histoMgr.appendHisto(histograms.Histo(theFit,"Fit"))

        plot.getPad().SetLogy(True) 
        
        plot.draw()
        plot.save()

        self.parInvQCD = theFit.GetParameters()                               
                                                                              
        fitPars = "fit parameters "                                           
        i = 0                                                                 
        while i < numberOfParameters:
            fitPars = fitPars + " " + str(self.parInvQCD[i])
            i = i + 1
        print fitPars
	self.nFitInvQCD = theFit.Integral(0,1000,self.parInvQCD)
        print "Integral ",self.normInvQCD*self.nFitInvQCD


    def fitEWK(self,histo,options="R"):

        rangeMin = histo.GetXaxis().GetXmin()
        rangeMax = histo.GetXaxis().GetXmax()
#	rangeMin = 120
#	rangeMax = 120

        numberOfParameters = 4

        print "Fit range ",rangeMin, " - ",rangeMax

        class FitFunction:
            def __call__( self, x, par ):
                return EWKFunction(x,par,1,1)
#		return SumFunction(x,par)
#	        return TestFunction(x,par,1)
	class PlotFunction:
	    def __call__( self, x, par ):
		return EWKFunction(x,par,0)

        theFit = TF1('theFit',FitFunction(),rangeMin,rangeMax,numberOfParameters)
	thePlot = TF1('thePlot',PlotFunction(),rangeMin,rangeMax,numberOfParameters)

        theFit.SetParLimits(0,5,30)
        theFit.SetParLimits(1,90,120)
        theFit.SetParLimits(2,30,50) 
        theFit.SetParLimits(3,0.001,1)


        if self.label == "4050":
            theFit.SetParLimits(0,5,20) 
            theFit.SetParLimits(1,90,120)
            theFit.SetParLimits(2,30,50)
            theFit.SetParLimits(3,0.001,1)

	if self.label == "5060":
            theFit.SetParLimits(0,5,20)     
            theFit.SetParLimits(1,90,120)   
            theFit.SetParLimits(2,30,50)
            theFit.SetParLimits(3,0.001,1)

        if self.label == "6070":
            theFit.SetParLimits(0,5,20)
            theFit.SetParLimits(1,90,150)
            theFit.SetParLimits(2,20,50)
            theFit.SetParLimits(3,0.001,1)

        if self.label == "7080":
            theFit.SetParLimits(0,5,40)
            theFit.SetParLimits(1,90,170)
            theFit.SetParLimits(2,20,60)
            theFit.SetParLimits(3,0.001,1)

        if self.label == "80100":
            theFit.SetParLimits(0,5,50)
            theFit.SetParLimits(1,90,170)
            theFit.SetParLimits(2,20,60)
            theFit.SetParLimits(3,0.001,1)

        if self.label == "100120":
            theFit.SetParLimits(0,5,50)
            theFit.SetParLimits(1,90,170)
            theFit.SetParLimits(2,20,60) 
            theFit.SetParLimits(3,0.001,1)

        if self.label == "120150":
            theFit.SetParLimits(0,5,50)
            theFit.SetParLimits(1,60,170)
            theFit.SetParLimits(2,10,60)
            theFit.SetParLimits(3,0.001,1)

        if self.label == "150":
            theFit.SetParLimits(0,5,50)
            theFit.SetParLimits(1,70,170)
            theFit.SetParLimits(2,20,60)
            theFit.SetParLimits(3,0.001,1)


        plot = plots.PlotBase()
        plot.histoMgr.appendHisto(histograms.Histo(histo,histo.GetName()))
        plot.createFrame("ewkfit"+self.label, opts={"ymin": 1e-5, "ymaxfactor": 2.})

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)
                        
	self.normEWK = histo.Integral(0,histo.GetNbinsX())

	histo.Scale(1/self.normEWK)

	histo.Fit(theFit,options) 
       
        theFit.SetRange(histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
        theFit.SetLineStyle(2)
        theFit.Draw("same")

        self.parMCEWK = theFit.GetParameters()
        
        fitPars = "fit parameters "

	i = 0
	while i < numberOfParameters:
	    fitPars = fitPars + " " + str(self.parMCEWK[i])
	    thePlot.SetParameter(i,theFit.GetParameter(i))
	    i = i + 1
	thePlot.Draw("same")

        histograms.addText(0.2,0.2,"EWK MC, baseline TauID")

        plot.histoMgr.appendHisto(histograms.Histo(theFit,"Fit"))

        plot.getPad().SetLogy(True)

        plot.draw()
        plot.save()
                           
        self.parMCEWK = theFit.GetParameters()
        
        print fitPars
        self.nMCEWK = theFit.Integral(0,1000,self.parMCEWK)
        print "Integral ",self.normEWK*self.nMCEWK

    def fitData(self,histo):

	parInvQCD  = self.parInvQCD
	parMCEWK   = self.parMCEWK
	nInvQCD    = self.nInvQCD
        nFitInvQCD = self.nFitInvQCD
        nMCEWK     = self.nMCEWK

        class FitFunction:
            def __call__( self, x, par ):
                return par[0]*(par[1] * QCDFunction(x,parInvQCD,1/nFitInvQCD) + ( 1 - par[1] ) * EWKFunction(x,parMCEWK,1/nMCEWK))

	class QCDOnly:
	    def __call__( self, x, par ):
		return par[0]*par[1] * QCDFunction(x,parInvQCD,1/nFitInvQCD)

        rangeMin = histo.GetXaxis().GetXmin()
        rangeMax = histo.GetXaxis().GetXmax()
        numberOfParameters = 2
        
        print "Fit range ",rangeMin, " - ",rangeMax
        
        theFit = TF1("theFit",FitFunction(),rangeMin,rangeMax,numberOfParameters)
        
        plot = plots.PlotBase()
        plot.histoMgr.appendHisto(histograms.Histo(histo,histo.GetName()))
        plot.createFrame("combinedfit"+self.label, opts={"ymin": 1e-5, "ymaxfactor": 2.})

        histograms.addCmsPreliminaryText()
        histograms.addEnergyText()
        histograms.addLuminosityText(x=None, y=None, lumi=self.lumi)
                                        
	print "data events ",histo.Integral(0,histo.GetNbinsX())

        histo.Fit(theFit,"R")

        theFit.SetRange(histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
        theFit.SetLineStyle(2)
        theFit.Draw("same")

	par = theFit.GetParameters()

	qcdOnly = TF1("qcdOnly",QCDOnly(),rangeMin,rangeMax,numberOfParameters)
	qcdOnly.FixParameter(0,par[0])
	qcdOnly.FixParameter(1,par[1])
	qcdOnly.SetLineStyle(2)
	qcdOnly.Draw("same")

        histograms.addText(0.35,0.8,"Data, Baseline TauID")
        histograms.addText(0.4,0.3,"QCD",15)


        plot.histoMgr.appendHisto(histograms.Histo(qcdOnly,"qcdOnly"))
        
        plot.getPad().SetLogy(True)

        plot.draw()
        plot.save()
                                        
        fitPars = "fit parameters "
        i = 0
        while i < numberOfParameters:
            fitPars = fitPars + " " + str(par[i])
            i = i + 1
        print fitPars
	nBaseQCD = par[0]
	self.QCDfraction = par[1]
	if len(self.label) > 0:
	    print "Bin ",self.label
        print "Integral     ", nBaseQCD
	print "QCD fraction ",self.QCDfraction

        return theFit

    def fitBaselineData(self,histoInv,histoBase):

	parInvQCD = self.parInvQCD
        parMCEWK  = self.parMCEWK
        nMCEWK    = self.nMCEWK
	normEWK   = self.normEWK
        print "check",self.nMCEWK,self.normEWK
	i = 0
        while i < 4: 
            print "param",i,parMCEWK[i]
            i = i + 1

        class FitFunction: 
            def __call__( self, x, par ):
#		print "check FitFunction",QCDFunction(x,par,1),normEWK * nMCEWK * EWKFunction(x,parMCEWK,1)
#		par[3] = par[0] * parInvQCD[3] / parInvQCD[0] 
		if x[0] > 200 and x[0] < 220:
        	    TF1.RejectPoint()
                    return 0
		return QCDFunctionFixed(x,par) + normEWK * EWKFunction(x,parMCEWK,1)

        class QCDOnly:
            def __call__( self, x, par ):
		return QCDFunctionFixed(x,par)
#		return QCDFunction(x,par,1)

        class QCDOnly2:
            def __call__( self, x, par ):
                return QCDFunction(x,par,1)

        class EWKOnly:
            def __call__( self, x, par ):
                return normEWK * EWKFunction(x,par,1)

	norm = histoBase.GetMaximum()/histoInv.GetMaximum()
	class InvertedFit:
	    def __call__( self, x, par ):
		return QCDFunction(x,par,norm)
        
        rangeMin = histoInv.GetXaxis().GetXmin()
        rangeMax = histoInv.GetXaxis().GetXmax()
#	rangeMax = 300

        numberOfParameters = 8
        
        print "Fit range ",rangeMin, " - ",rangeMax
                
        theFit = TF1('theFit',FitFunction(),rangeMin,rangeMax,numberOfParameters)

        theFit.SetParLimits(0,10,20000)
        theFit.SetParLimits(1,20,40)
        theFit.SetParLimits(2,1,25)
        
        theFit.SetParLimits(3,1,10000)  
        theFit.SetParLimits(4,50,150)
        theFit.SetParLimits(5,1,100)

	theFit.FixParameter(1,parInvQCD[1])
        theFit.FixParameter(2,parInvQCD[2])
	theFit.FixParameter(3,parInvQCD[3]/parInvQCD[0])
        theFit.FixParameter(4,parInvQCD[4])
        theFit.FixParameter(5,parInvQCD[5])

        
        theFit.SetParLimits(6,0.001,100)
        theFit.SetParLimits(7,0.001,0.05)        
        print "Fit range ",rangeMin, " - ",rangeMax
    
        
        cshape = TCanvas("cshape","",500,500)
        cshape.cd()
        cshape.SetLogy()
#        print "data events ",histo.Integral(0,histo.GetNbinsX())   

        histoInv.Scale(histoBase.GetMaximum()/histoInv.GetMaximum())
        histoInv.SetMarkerColor(4)
        histoInv.Draw("hist ep");

#	histoBase.GetYaxis().SetLimits(0.001,300.)
#	histoBase.SetBinContent(11,0)
	histoBase.Draw("histo epsame")
        histoBase.Fit(theFit,"RN")
	theFit.Draw("same")

#        theFit.SetRange(histoInv.GetXaxis().GetXmin(),histoInv.GetXaxis().GetXmax())
#        theFit.SetLineStyle(2)
#        theFit.DrawClone("same")

        par = theFit.GetParameters()

	ewkOnly = TF1("ewkOnly",EWKOnly(),rangeMin,rangeMax,4)
	ewkOnly.SetLineStyle(2)
	ewkOnly.SetLineColor(3)
	ewkOnly.Draw("same")
	i = 0
	while i < 4:
	    ewkOnly.FixParameter(i,parMCEWK[i])
            i = i + 1



        theFit2 = TF1('theFit2',QCDOnly(),rangeMin,rangeMax,numberOfParameters)
            
        theFit2.SetParLimits(0,10,20000)
        theFit2.SetParLimits(1,20,40)
        theFit2.SetParLimits(2,10,25)
        
        theFit2.SetParLimits(3,1,10000)
        theFit2.SetParLimits(4,0,150)
        theFit2.SetParLimits(5,20,100)
        
        theFit2.SetParLimits(6,0.0001,100)
        theFit2.SetParLimits(7,0.001,0.05)

        theFit2.FixParameter(1,parInvQCD[1])
        theFit2.FixParameter(2,parInvQCD[2])
        theFit2.FixParameter(3,parInvQCD[3]/parInvQCD[0])
        theFit2.FixParameter(4,parInvQCD[4])
        theFit2.FixParameter(5,parInvQCD[5])

	QCDbase = histoBase.Clone("QCDbase")
	i = 1
	while i < QCDbase.GetNbinsX():
	    newBinValue = QCDbase.GetBinContent(i) - ewkOnly.Eval(QCDbase.GetBinCenter(i))
	    print "check newBinValue",QCDbase.GetBinContent(i),ewkOnly.Eval(QCDbase.GetBinCenter(i)),QCDbase.GetBinCenter(i)
	    QCDbase.SetBinContent(i,newBinValue)
	    i = i + 1
	QCDbase.SetMarkerColor(5)
	QCDbase.Draw("same")
	QCDbase.Fit(theFit2,"LRN")
	theFit2.Draw("same")
        
        qcdOnly = TF1("qcdOnly",QCDOnly(),rangeMin,rangeMax,numberOfParameters)
	i = 0
	while i < numberOfParameters:
            qcdOnly.FixParameter(i,par[i])
	    i = i + 1
        qcdOnly.SetLineStyle(2)
        qcdOnly.Draw("same")


#        histoInv.Scale(histoBase.GetMaximum()/histoInv.GetMaximum())
#        histoInv.SetMarkerColor(4)
#        histoInv.Draw("hist epsame");

	inverted = TF1("inverted",InvertedFit(),rangeMin,rangeMax,numberOfParameters)
        i = 0
        while i < numberOfParameters:   
            inverted.FixParameter(i,parInvQCD[i])
            i = i + 1
        inverted.SetLineStyle(3)
	inverted.SetLineColor(4)
        inverted.Draw("same")	

        cshape.Print("shapefit"+self.label+".eps")

    def getNormalization(self):
	nQCDbaseline = self.nBaseQCD
	nQCDinverted = self.nInvQCD
	QCDfractionInBaseLineEvents = self.QCDfraction
	normalizationForInvertedEvents = nQCDbaseline*QCDfractionInBaseLineEvents/nQCDinverted

	self.normFactors.append(normalizationForInvertedEvents)
	self.labels.append(self.label)

	print "\n"
	print "Normalizing to baseline TauID qcd fraction from a fit using inverted QCD MET distribution shape and EWK MC baseline shape"
	print "    Number of baseline QCD events       ",nQCDbaseline
	print "    QCD fraction in baseline QCD events ",QCDfractionInBaseLineEvents
        print "    Number of inverted QCD events       ",nQCDinverted 
	print "\n"
	print "Normalization for inverted QCD events   ",normalizationForInvertedEvents
	print "\n"
	return normalizationForInvertedEvents

    def Summary(self):
	if len(self.normFactors) == 0:
	    return

        print "Normalization factors for each bin"
        i = 0
	while i < len(self.normFactors):
	    label = self.labels[i]
	    while len(label) < 10:
		label = label  + " "
	    print "    Label",label,", normalization",self.normFactors[i]
	    i = i + 1

