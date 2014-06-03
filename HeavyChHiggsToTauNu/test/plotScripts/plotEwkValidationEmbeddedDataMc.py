#!/usr/bin/env python

######################################################################
#
# This plot script is for comparing the embedded data to embedded MC
# within the signal analysis. The corresponding python job
# configurations are
# * signalAnalysis_cfg.py with "doPat=1 tauEmbeddingInput=1"
# * signalAnalysis_cfg.py
# for embedding+signal analysis and signal analysis, respectively
#
# Authors: Matti Kortelainen
#
######################################################################

import os
import array
import math

import ROOT
ROOT.gROOT.SetBatch(True)

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset as dataset
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms as histograms
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.counter as counter
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.cutstring import * # And, Not, Or
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.crosssection as xsect
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tauEmbedding as tauEmbedding

dataEra = "Run2012ABCD"
optMode = None

def main():
    # Create the dataset objects
    datasetsEmb = dataset.getDatasetsFromMulticrabCfg(dataEra=dataEra, optimizationMode=optMode)

    # Remove signal and W+3jets datasets
    datasetsEmb.remove(filter(lambda name: "HplusTB" in name, datasetsEmb.getAllDatasetNames()))
    datasetsEmb.remove(filter(lambda name: "TTToHplus" in name, datasetsEmb.getAllDatasetNames()))

    datasetsEmb.updateNAllEventsToPUWeighted()
    plots.mergeRenameReorderForDataMC(datasetsEmb)

    # Apply TDR style
    style = tdrstyle.TDRStyle()
#    histograms.cmsTextMode = histograms.CMSMode.NONE
    histograms.uncertaintyMode.set(histograms.Uncertainty.StatOnly)

    doCounters(datasetsEmb)

    # Remove QCD for plots
    datasetsEmb.remove(["QCD_Pt20_MuEnriched"])
    histograms.createLegend.moveDefaults(dx=-0.04, dh=-0.05)
    doPlots(datasetsEmb)

drawPlotCommon = plots.PlotDrawer(ylabel="Events / %.0f", stackMCHistograms=True, log=True, addMCUncertainty=True,
                                  ratio=True, ratioType="errorScale", ratioCreateLegend=True,
                                  addLuminosityText=True)

def doPlots(datasetsEmb):
    lumi = datasetsEmb.getDataset("Data").getLuminosity()

    def createPlot(name):
        p = plots.DataMCPlot(datasetsEmb, name, normalizeToLumi=lumi)
        # by default pseudo-datasets lead to MC histograms, for these
        # plots we want to treat Data as data
        p.histoMgr.getHisto("Data").setIsDataMC(True, False)
        p.setDefaultStyles()
        return p

    plotter = tauEmbedding.CommonPlotter(optMode, "embdatamc", drawPlotCommon)
    plotter.plot(None, createPlot, {
#        "NBjets": {"moveLegend": {"dx": -0.4, "dy": -0.45}}
    })
    return


def addMcSum(t):
    allDatasets = ["QCD_Pt20_MuEnriched", "WJets", "TTJets", "DYJetsToLL", "SingleTop", "Diboson"]
    t.insertColumn(1, counter.sumColumn("MCSum", [t.getColumn(name=name) for name in allDatasets]))

def doCounters(datasetsEmb):
    eventCounter = counter.EventCounter(datasetsEmb)
    eventCounter.normalizeMCToLuminosity(datasetsEmb.getDataset("Data").getLuminosity())
    table = eventCounter.getMainCounterTable()
    table.keepOnlyRows(["Selected events"])
    addMcSum(table)

    cellFormat = counter.TableFormatText(counter.CellFormatTeX(valueFormat='%.4f', withPrecision=2))
    print table.format(cellFormat)
    


##    # All embedded events
##    eventCounterAll = counter.EventCounter(datasetsEmb.getFirstDatasetManager(), counters=analysisEmbAll+counters)
##    eventCounterAll.normalizeMCByLuminosity()
##    tableAll = eventCounterAll.getMainCounterTable()
##    tableAll.keepOnlyRows([
##            "All events",
##            ])
##    tableAll.renameRows({"All events": "All embedded events"})
##
##    # Mu eff + Wtau mu
##    eventCounterMuEff = counter.EventCounter(datasetsEmb.getFirstDatasetManager(), counters=analysisEmbNoTauEff+counters)
##    eventCounterMuEff.normalizeMCByLuminosity()
##    tauEmbedding.scaleNormalization(eventCounterMuEff)
##    tableMuEff = eventCounterMuEff.getMainCounterTable()
##    tableMuEff.keepOnlyRows([
##            "All events"
##            ])
##    tableMuEff.renameRows({"All events": "mu eff + Wtaumu"})
##
##    # Event counts after embedding normalization, before tau trigger eff,
##    # switch to calculate uncertainties of the mean of 10 trials
##    eventCounterNoTauEff = tauEmbedding.EventCounterMany(datasetsEmb, counters=analysisEmbNoTauEff+counters)
##    tableNoTauEff = eventCounterNoTauEff.getMainCounterTable()
##    tableNoTauEff.keepOnlyRows([
##            "Trigger and HLT_MET cut",
##            "njets",
##            ])
##    tableNoTauEff.renameRows({"Trigger and HLT_MET cut": "caloMET > 60",
##                              "njets": "tau ID"
##                              })
##
##    # Event counts after tau trigger eff
##    eventCounter = tauEmbedding.EventCounterMany(datasetsEmb, counters=analysisEmb+counters)
##    table = eventCounter.getMainCounterTable()
##    table.keepOnlyRows([
##            "njets",
##            "MET",
##            "btagging scale factor",
##            "DeltaPhi(Tau,MET) upper limit",
##            ])
##    table.renameRows({"njets": "Tau trigger efficiency",
##                      "btagging scale factor": "b tagging"
##                      })
##
##    # Combine the rows to one table
##    result = counter.CounterTable()
##    for tbl in [
##        tableAll,
##        tableMuEff,
##        tableNoTauEff,
##        table
##        ]:
##        for iRow in xrange(tbl.getNrows()):
##            result.appendRow(tbl.getRow(index=iRow))
##
##    addMcSum(result)
##    cellFormat = counter.TableFormatText(counter.CellFormatTeX(valueFormat='%.4f', withPrecision=2))
##
##    print result.format(cellFormat)

if __name__ == "__main__":
    main()
