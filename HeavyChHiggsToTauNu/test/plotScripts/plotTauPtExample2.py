#!/usr/bin/env python

###########################################################################
#
# This script is only intended as an example, please do NOT modify it.
# For example, start from scratch and look here for help, or make a
# copy of it and modify the copy (including removing all unnecessary
# code).
#
###########################################################################

drawToScreen = True
drawToScreen = False

import ROOT
if not drawToScreen:
    ROOT.gROOT.SetBatch(True)

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset as dataset
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms as histograms
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.counter as counter
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.crosssection as xsect

analysis = "signalAnalysis"
counters = analysis+"Counters/weighted"

def main():
    # Create all datasets from a multicrab task
    datasets = dataset.getDatasetsFromMulticrabCfg(counters=counters)

    # Read integrated luminosities of data datasets from lumi.json
    datasets.loadLuminosities()

    # Include only 120 mass bin of HW and HH datasets
    datasets.remove(filter(lambda name: "TTToHplus" in name and not "M120" in name, datasets.getAllDatasetNames()))

    # Default merging nad ordering of data and MC datasets
    # All data datasets to "Data"
    # All QCD datasets to "QCD"
    # All single top datasets to "SingleTop"
    # WW, WZ, ZZ to "Diboson"
    plots.mergeRenameReorderForDataMC(datasets)

    # Set BR(t->H) to 0.2, keep BR(H->tau) in 1
    xsect.setHplusCrossSectionsToBR(datasets, br_tH=0.05, br_Htaunu=1)

    # Merge WH and HH datasets to one (for each mass bin)
    # TTToHplusBWB_MXXX and TTToHplusBHminusB_MXXX to "TTToHplus_MXXX"
    plots.mergeWHandHH(datasets)

    # Apply TDR style
    style = tdrstyle.TDRStyle()

    dataMCExample(datasets)
    distComparison(datasets)

    # Script execution can be paused like this, it will continue after
    # user has given some input (which must include enter)
    if drawToScreen:
        raw_input("Hit enter to continue")


def dataMCExample(datasets):
    # Create data-MC comparison plot, with the default
    # - legend labels (defined in plots._legendLabels)
    # - plot styles (defined in plots._plotStyles, and in styles)
    # - drawing styles ('HIST' for MC, 'EP' for data)
    # - legend styles ('L' for MC, 'P' for data)
    plot = plots.DataMCPlot(datasets, analysis+"/SelectedTau_pT_AfterTauID")

    # Example of how to rebin all histograms in a histogram manager of a plot
    plot.histoMgr.forEachHisto(lambda h: h.getRootHisto().Rebin(10))

    # Stack all MC histograms, except signal
    # The stacked histograms become filled
    plot.stackMCHistograms()

    # Add MC statistical uncertainty band, calculated as a total of
    # the stacked histograms
    plot.addMCUncertainty()

    # Create the cancas and the frame, with a file name of taupt
    #plot.createFrame("taupt")
    # give explicitly some of the boundaries, leave the rest to be the default
    plot.createFrame("taupt", opts={"ymin": 1e-1, "ymaxfactor": 10})
    # give explicitly the x and y axis boundaries
    #plot.createFrame("taupt", opts={"xmin":40, "xmax":100, "ymin":1e-4, "ymaxfactor": 10})

    # Set Y axis to logarithmic
    plot.getPad().SetLogy(True)

    # Create legend to the default position
    plot.setLegend(histograms.createLegend())
    # to a fixed position
    #plot.setLegend(histograms.createLegend(0.7, 0.6, 0.9, 0.9))
    # to the default position, move the legend after that, and change the width and height
    #plot.setLegend(histograms.moveLegend(histograms.createLegend(), dx=0.1, dy=-0.1, dw=0.1, dh=-0.1)

    # Set X/Y axis labels via TAxis
    plot.frame.GetXaxis().SetTitle("Tau p_{T} (GeV/c)")
    plot.frame.GetYaxis().SetTitle("Number of events")

    # Draw the plot
    plot.draw()

    # Add the various texts to 
    histograms.addCmsPreliminaryText()
    histograms.addEnergyText()
    plot.addLuminosityText()

    # Save the plot to files
    plot.save()

def setName(drh, name):
    drh.setName(name)
    return drh

def distComparison(datasets):
    # Create a comparison plot of two distributions (must have the same binning)
    # Set the names of DatasetRootHisto objects in order to be able easily reference them later
    drh1 = datasets.getDataset("Data").getDatasetRootHisto(analysis+"/SelectedTau_pT_AfterTauID")
    drh1.setName("afterTauID")
    drh2 = datasets.getDataset("Data").getDatasetRootHisto(analysis+"/SelectedTau_pT_AfterMetCut")
    drh2.setName("afterMet")
    plot = plots.ComparisonPlot(drh1, drh2)

    # Set the styles
    st1 = styles.getDataStyle().clone()
    st2 = st1.clone()
    st2.append(styles.StyleLine(lineColor=ROOT.kRed))
    plot.histoMgr.forHisto("afterTauID", st1)
    plot.histoMgr.forHisto("afterMet", st2)

    # Set the legend labels
    plot.histoMgr.setHistoLegendLabelMany({"afterTauID": "After tau ID",
                                           "afterMet": "After MET cut"})
    # Set the legend styles
    plot.histoMgr.setHistoLegendStyleAll("L")
    #plot.histoMgr.setHistoLegendStyle("afterTauID", "P") # exception to the general rule

    # Set the drawing styles
    plot.histoMgr.setHistoDrawStyleAll("HIST")
    #plot.histoMgr.setHistoDrawStyleAll("afterTauID", "EP") # exception to the general rule

    # Rebin, if necessary
    plot.histoMgr.forEachHisto(lambda h: h.getRootHisto().Rebin(10))

    # Create frame with a ratio pad
    plot.createFrame("tauPtComparison", opts={"ymin":1e-1, "ymaxfactor": 10},
                     createRatio=True, opts2={"ymin": 0, "ymax": 150}, # bounds of the ratio plot
                     )

    # Set Y axis of the upper pad to logarithmic
    plot.getPad1().SetLogy(True)

    # Create legend to the default position
    plot.setLegend(histograms.createLegend())

    # Set the X/Y axis labels
    plot.frame.GetXaxis().SetTitle("Tau p_{T} (GeV/c)")
    plot.frame.GetYaxis().SetTitle("Number of events")

    # Draw the plot
    plot.draw()

    # Add the various texts to 
    histograms.addCmsPreliminaryText()
    histograms.addEnergyText()
    histograms.addLuminosityText(x=None, y=None, lumi=datasets.getDataset("Data").getLuminosity())

    # Save the plot to files
    plot.save()


if __name__ == "__main__":
    main()
