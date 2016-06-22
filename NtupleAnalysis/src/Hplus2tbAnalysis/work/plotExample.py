#!/usr/bin/env python

import os
import sys
import re

import HiggsAnalysis.NtupleAnalysis.tools.dataset as dataset
import HiggsAnalysis.NtupleAnalysis.tools.tdrstyle as tdrstyle
import HiggsAnalysis.NtupleAnalysis.tools.styles as styles
import HiggsAnalysis.NtupleAnalysis.tools.plots as plots
import HiggsAnalysis.NtupleAnalysis.tools.histograms as histograms
import HiggsAnalysis.NtupleAnalysis.tools.aux as aux

plotDir = "Plots2015"
formats = [".pdf",".png",".C"]

def usage():
    print "\n"
    print "### Usage:   "+sys.argv[0]+" <multicrab dir>\n"
    print "\n"
    sys.exit()


def removeNegatives(histo):
    for bin in range(histo.GetNbinsX()):
        if histo.GetBinContent(bin) < 0:
            histo.SetBinContent(bin,0.)


def main():

    if len(sys.argv) < 2:
        usage()

    plot(hName = "associatedTPt",  title_x = "Associated Top p_{T} (GeV/c)", rebin = 2)
    plot(hName = "associatedTEta", title_x = "Associated Top Eta", rebin = 4)
    plot(hName = "associatedTPhi", title_x = "Associated Top Phi", rebin = 5)

    plot(hName = "associatedBPt",  title_x = "Associated B p_{T} (GeV/c)", rebin = 2)
    plot(hName = "associatedBEta", title_x = "Associated B Eta", rebin = 4)
    plot(hName = "associatedBPhi", title_x = "Associated B Phi", rebin = 5)

    plot(hName = "HplusToTPt",  title_x = "H^{+} Top p_{T} (GeV/c)", rebin = 2)
    plot(hName = "HplusToTEta", title_x = "H^{+} Top Eta", rebin = 4)
    plot(hName = "HplusToTPhi", title_x = "H^{+} Top Phi", rebin = 5)

    plot(hName = "HplusToBPt",  title_x = "H^{+} B p_{T} (GeV/c)", rebin = 2)
    plot(hName = "HplusToBEta", title_x = "H^{+} B Eta", rebin = 4)
    plot(hName = "HplusToBPhi", title_x = "H^{+} B Phi", rebin = 5)

    plot(hName = "genMetEt",  title_x = "Gen MET", rebin = 2)
    plot(hName = "genMetPhi", title_x = "Gen MET phi", rebin = 5)

    plot(hName = "HplusPt",  title_x = "H^{+} p_{T} (GeV/c)", rebin = 2)
    plot(hName = "HplusEta", title_x = "H^{+} Eta", rebin = 4)
    plot(hName = "HplusPhi", title_x = "H^{+} Phi", rebin = 5)

    plot(hName = "genHt", title_x = "Gen HT (GeV/c)", rebin = 10)

    plot(hName = "nGenJets", title_x = "nGenJets", rebin = 5)

    plot(hName = "MetEt",  title_x = "MET", rebin = 4)
    plot(hName = "MetPhi", title_x = "MET phi", rebin = 5)

    plot(hName = "Ht", title_x = "HT (GeV/c)", rebin = 10)

    plot(hName = "nJets", title_x = "nJets", rebin = 4)
    plot(hName = "nBJets", title_x = "nBJets", rebin = 1)

    plot(hName = "LeadingJetPt", title_x = "Leading Jet p_{T} (GeV/c)", rebin = 4)
    plot(hName = "LeadingBJetPt", title_x = "Leading B Jet p_{T} (GeV/c)", rebin = 4)


def plot(hName, title_x, rebin = 0):
    print(hName)
    paths = [sys.argv[1]]
    analysis = "Hplus2tbAnalysis"
    plotname = analysis+"_"+hName

    datasetsHiggs = dataset.getDatasetsFromMulticrabDirs(paths,analysisName=analysis,includeOnlyTasks="ChargedHiggs_HplusTB_HplusToTauB_M_")
    datasetsTT    = dataset.getDatasetsFromMulticrabDirs(paths,analysisName=analysis,includeOnlyTasks="TT")
    datasetsTT.merge("MC", ["TT"], keepSources=True)

    style = tdrstyle.TDRStyle()

    masses = datasetsHiggs.getAllDatasetNames()

    for m in masses:
        m_re = re.compile("\S+_M_(?P<value>(\d+))$")
        match = m_re.search(m)
        m_str = match.group("value")

        dataset1 = datasetsHiggs.getDataset(m).getDatasetRootHisto(hName)
        dataset2 = datasetsTT.getDataset("MC").getDatasetRootHisto(hName)
#        dataset1.normalizeToOne()
        dataset2.normalizeToOne()

        histo1 = dataset1.getHistogram()
        histo1.SetMarkerColor(2)
        histo1.SetMarkerStyle(20)
        removeNegatives(histo1)
	if histo1.Integral() > 0:
            histo1.Scale(1./histo1.Integral())

        histo2 = dataset2.getHistogram()
        histo2.SetMarkerColor(4)
        histo2.SetMarkerStyle(21)

        if rebin:
            histo1.Rebin(rebin)
            histo2.Rebin(rebin)

        p = plots.ComparisonPlot(histograms.Histo(histo1, "m_{H^{#pm}} = " + m_str + " GeV/c^{2}", "p", "P"),
                                 histograms.Histo(histo2, "t#bar{t}", "p", "P"))

        opts = {"ymin": 0, "ymax": 0.2}
        opts2 = {"ymin": 0.5, "ymax": 1.5}
        p.createFrame(os.path.join(plotDir + "/" + m_str, plotname), createRatio=True, opts=opts, opts2=opts2)

        moveLegend = {"dx": -0.2, "dy": -0.1, "dh": -0.1}
        p.setLegend(histograms.moveLegend(histograms.createLegend(), **moveLegend))

        p.getFrame().GetYaxis().SetTitle("Arbitrary units")
        p.getFrame().GetXaxis().SetTitle(title_x)
        p.getFrame2().GetYaxis().SetTitle("Ratio")
        p.getFrame2().GetYaxis().SetTitleOffset(1.6)

        p.draw()
        if not os.path.exists(plotDir):
            os.mkdir(plotDir)
        if not os.path.exists(plotDir + "/" + m_str):
            os.mkdir(plotDir + "/" + m_str)
        p.save(formats)

if __name__ == "__main__":
    main()
