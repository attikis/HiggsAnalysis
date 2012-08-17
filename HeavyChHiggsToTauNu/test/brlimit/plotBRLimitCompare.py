#!/usr/bin/env python

import sys
import glob
import json
import array

import ROOT
ROOT.gROOT.SetBatch(True)

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms as histograms
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.limit as limit

def main():
    # Apply TDR style
    style = tdrstyle.TDRStyle()
    histograms.cmsTextMode = histograms.CMSMode.NONE

#    compareTauJets()
#    compareLeptonic()
#    compareCombination()
#    compareCombinationSanitychecksLHC()

    compareTauJetsDeltaPhi()

def compareTauJets():
    doCompare("taujets", [
            # (name, dir)
            ("LHC-CLs", "LandS*taujets_lhc_*"),
            ("LHC-CLs (asymp)", "LandS*taujets_lhcasy_*"),
            ("LEP-CLs", "LandS*taujets_lep_*"),
            ])

def compareLeptonic():
    doCompare("emu", [
            # (name, dir)
            ("LHC-CLs", "LandS*emu_lhc_*"),
            ("LHC-CLs (asymp)", "LandS*emu_lhcasy_*"),
            ("LEP-CLs", "LandS*emu_lep_*"),
            ])

    doCompare("mutau", [
            # (name, dir)
            ("LHC-CLs", "LandS*mutau_lhc_*"),
            ("LHC-CLs (asymp)", "LandS*mutau_lhcasy_*"),
            ("LEP-CLs", "LandS*mutau_lep_*"),
            ])

    doCompare("etau", [
            # (name, dir)
#            ("LHC-CLs", "LandS*etau_lhc_*"),
            ("LHC-CLs", "LandSMultiCrab_etau_lhc_jobs10_sb_600_b300_120514_151345/"),
            ("LHC-CLs (asymp)", "LandS*etau_lhcasy_*"),
            ("LEP-CLs", "LandS*etau_lep_*"),
            ])

def compareCombination():
    doCompare("combination", [
            # (name, dir)
#            ("LHC-CLs", "LandS*combination_lhc_jobs*"),
            ("LHC-CLs", "LandSMultiCrab_combination_lhc_jobs10_sb300_b150_120514_173610"),
            ("LHC-CLs (asymp)", "LandS*combination_lhcasy_*"),
            ("LEP-CLs", "LandS*combination_lep_*"),
            ])

def compareCombinationSanitychecksLHC():
    doCompare("combination_migrad_vs_minos", [
            # (name, dir)
            ("Migrad", "LandS*combination_lhc_sanitycheck_migrad_*"),
            ("Minos", "LandS*combination_lhc_sanitycheck_minos_*"),
            ])


def compareTauJetsDeltaPhi():
    doCompare("taujets_deltaphi", [
              # (name, dir)
              ("Without #Delta#phi selection", "datacards_220312_123012_fully_hadronic_2011A_MET50_withRtau_NoDeltaPhi_withShapes_shapeStat/LandSMultiCrab_taujets_lhc_*"),
              ("#Delta#phi < 160^{o}", "combination_new/LandS*taujets_lhc_*"),
              ("#Delta#phi < 130^{o}", "datacards_220312_122901_fully_hadronic_2011A_MET50_withRtau_DeltaPhi130_withShapes_shapeStat/LandSMultiCrab_taujets_lhc_*")
              ],
              expectedMedianOpts={"ymax": 0.07},
              expectedSigma1Opts={"ymax": 0.1},
              expectedSigma1RelativeOpts={"ymax": 2.2, "ymin": 0.4},
              expectedSigma2RelativeOpts={"ymax": 3.6, "ymin": 0.3},
              moveLegend={"dh": -0.04}
              )
            


styleList = [styles.Style(24, ROOT.kBlack)] + styles.getStyles()

def doCompare(name, compareList, **kwargs):
    legendLabels = []
    limits = []
    for label, path in compareList:
        legendLabels.append(label)
        dirs = glob.glob(path)
        dirs.sort()
        if len(dirs) == 0:
            raise Exception("No directories for pattern '%s'" % path)
        directory = dirs[-1]
        print "Picked %s" % directory
        limits.append(limit.BRLimits(directory, excludeMassPoints=["155"]))

    doPlot2(limits, legendLabels, name)

    limitOpts = kwargs.get("limitOpts", {"ymax": limits[0].getFinalstateYmaxBR()})
    expectedSigmaRelativeOpts = kwargs.get("expectedSigmaRelativeOpts", {"ymaxfactor": 1.2})
    moveLegend = kwargs.get("moveLegend", {})

    doPlot(limits, legendLabels, [l.observedGraph() for l in limits],
           name+"_observed", limit.BRlimit, opts=kwargs.get("observedOpts", limitOpts), moveLegend=moveLegend,
           plotLabel="Observed")

    doPlot(limits, legendLabels, [l.expectedGraph() for l in limits],
           name+"_expectedMedian", limit.BRlimit, opts=kwargs.get("expectedMedianOpts", limitOpts), moveLegend=moveLegend,
           plotLabel="Expected median")

    legendLabels2 = legendLabels + [None]*len(legendLabels)

    doPlot(limits, legendLabels2,
           [limit.divideGraph(l.expectedGraph(sigma=+1), l.expectedGraph()) for l in limits] +
           [limit.divideGraph(l.expectedGraph(sigma=-1), l.expectedGraph()) for l in limits],
           name+"_expectedSigma1Relative", "Expected #pm1#sigma / median", opts=kwargs.get("expectedSigma1RelativeOpts", expectedSigmaRelativeOpts), moveLegend=moveLegend,
           plotLabel="Expected #pm1#sigma / median")

    doPlot(limits, legendLabels2,
           [limit.divideGraph(l.expectedGraph(sigma=+2), l.expectedGraph()) for l in limits] +
           [limit.divideGraph(l.expectedGraph(sigma=-2), l.expectedGraph()) for l in limits],
           name+"_expectedSigma2Relative", "Expected #pm2#sigma / median", opts=kwargs.get("expectedSigma2RelativeOpts", expectedSigmaRelativeOpts), moveLegend=moveLegend,
           plotLabel="Expected #pm2#sigma / median")

    doPlot(limits, legendLabels2,
           [l.expectedGraph(sigma=+1) for l in limits] +
           [l.expectedGraph(sigma=-1) for l in limits],
           name+"_expectedSigma1", "Expected #pm1#sigma", opts=kwargs.get("expectedSigma1Opts", limitOpts), moveLegend=moveLegend,
           plotLabel="Expexted #pm1sigma")

    doPlot(limits, legendLabels2,
           [l.expectedGraph(sigma=+2) for l in limits] +
           [l.expectedGraph(sigma=-2) for l in limits],
           name+"_expectedSigma2", "Expected #pm2#sigma", opts=kwargs.get("expectedSigma2Opts", limitOpts), moveLegend=moveLegend,
           plotLabel="Expected #pm2sigma")

    # doPlot(limits, legendLabels,
    #        [limit.divideGraph(l.expectedGraph(sigma=+1), l.expectedGraph()) for l in limits]
    #        name+"_expectedSigma1Plus", "Expected +1#sigma / median", opts={"ymaxfactor": 1.2})

    # doPlot(limits, legendLabels,
    #        [limit.divideGraph(l.expectedGraph(sigma=+2), l.expectedGraph()) for l in limits]
    #        name+"_expectedSigma2Plus", "Expected +2#sigma / median", opts={"ymaxfactor": 1.2})

    # doPlot(limits, legendLabels,
    #        [limit.divideGraph(l.expectedGraph(sigma=-1), l.expectedGraph()) for l in limits],
    #        name+"_expectedSigma1Minus", "Expected -1#sigma / median", opts={"ymaxfactor": 1.2})

    # doPlot(limits, legendLabels,
    #        [limit.divideGraph(l.expectedGraph(sigma=-2), l.expectedGraph()) for l in limits],
    #        name+"_expectedSigma2Minus", "Expected -2#sigma / median", opts={"ymaxfactor": 1.2})


def doPlot(limits, legendLabels, graphs, name, ylabel, opts={}, plotLabel=None, moveLegend={}):
    hg = []
    ll = {}
    for i in xrange(len(graphs)):
        hg.append(histograms.HistoGraph(graphs[i], "Graph%d"%i, drawStyle="PL", legendStyle="lp"))
        ll["Graph%d"%i] = legendLabels[i]

    plot = plots.PlotBase(hg)
    plot.histoMgr.forEachHisto(styles.Generator(styleList[0:len(limits)]))
    def sty(h):
        r = h.getRootHisto()
        r.SetLineWidth(3)
        r.SetLineStyle(1)
    plot.histoMgr.forEachHisto(sty)
    plot.histoMgr.setHistoLegendLabelMany(ll)
    legend = histograms.createLegend(0.48, 0.75, 0.85, 0.92)
    if len(limits[0].getFinalstates()) > 1:
        legend = histograms.moveLegend(legend, dy=-0.1)
    if plotLabel:
        legend = histograms.moveLegend(legend, dy=-0.04)
    legend = histograms.moveLegend(legend, **moveLegend)
    plot.setLegend(legend)
    opts_ = {"ymin": 0}
    opts_.update(opts)
    plot.createFrame(name, opts=opts_)

    plot.frame.GetXaxis().SetTitle(limit.mHplus())
    plot.frame.GetYaxis().SetTitle(ylabel)

    plot.draw()

    histograms.addCmsPreliminaryText()
    histograms.addEnergyText()
    histograms.addLuminosityText(x=None, y=None, lumi=limits[0].getLuminosity())

    size = 20
    x = 0.2
    histograms.addText(x, 0.88, limit.process, size=size)
    histograms.addText(x, 0.84, limits[0].getFinalstateText(), size=size)
    histograms.addText(x, 0.79, limit.BRassumption, size=size)
    if plotLabel:
        histograms.addText(legend.GetX1()+0.01, legend.GetY2(), plotLabel, size=size)

    plot.save()

def doPlot2(limits, legendLabels, name):
    graphs = [
        histograms.HistoGraph(limits[0].expectedGraph(), "Expected", drawStyle="L"),
        histograms.HistoGraph(limits[0].expectedBandGraph(sigma=1), "Expected1", drawStyle="F", legendStyle="fl"),
        histograms.HistoGraph(limits[0].expectedBandGraph(sigma=2), "Expected2", drawStyle="F", legendStyle="fl"),
        ]
    graphs[0].getRootHisto().SetLineStyle(1)
    plot = plots.PlotBase(graphs)
    ll = {
        "Expected": None,
        "Expected1": "%s exp. median #pm 1#sigma" % legendLabels[0],
        "Expected2": "%s exp. median #pm 2#sigma" % legendLabels[0],
        }

    stGen = styles.generator()
    for i in xrange(1, len(limits)):
        gr = histograms.HistoGraph(limits[i].expectedGraph(), "Exp%d"%i, drawStyle="L")
        stGen(gr)
        gr.getRootHisto().SetLineWidth(3)
        gr.getRootHisto().SetLineStyle(1)
        plot.histoMgr.insertHisto(len(plot.histoMgr)-2, gr, legendIndex=len(plot.histoMgr))
        ll["Exp%d"%i] = "%s exp. median" % legendLabels[i]

    plot.histoMgr.setHistoLegendLabelMany(ll)

    legend = histograms.moveLegend(histograms.createLegend(0.48, 0.75, 0.85, 0.92), dx=-0.02)
    if len(limits[0].getFinalstates()) > 1:
        legend = histograms.moveLegend(legend, dy=-0.1)
    plot.setLegend(legend)

    plot.createFrame(name+"_limits", opts={"ymin": 0, "ymax": limits[0].getFinalstateYmaxBR()})
    plot.frame.GetXaxis().SetTitle(limit.mHplus())
    plot.frame.GetYaxis().SetTitle(limit.BRlimit)

    plot.draw()

    histograms.addCmsPreliminaryText()
    histograms.addEnergyText()
    histograms.addLuminosityText(x=None, y=None, lumi=limits[0].getLuminosity())

    size = 20
    x = 0.2
    histograms.addText(x, 0.88, limit.process, size=size)
    histograms.addText(x, 0.84, limits[0].getFinalstateText(), size=size)
    histograms.addText(x, 0.79, limit.BRassumption, size=size)

    plot.save()


if __name__ == "__main__":
    main()