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

def main():
    # Create all datasets from a multicrab task
    datasets = dataset.getDatasetsFromMulticrabCfg(dataEra="Run2012ABCD")

    # As we use weighted counters for MC normalisation, we have to
    # update the all event count to a separately defined value because
    # the analysis job uses skimmed pattuple as an input
    datasets.updateNAllEventsToPUWeighted()

    # Read integrated luminosities of data datasets from lumi.json
    datasets.loadLuminosities()

    # Include only 120 mass bin of HW and HH datasets
    datasets.remove(filter(lambda name: "TTToHplus" in name and not "M120" in name, datasets.getAllDatasetNames()))
    datasets.remove(filter(lambda name: "Hplus_taunu_" in name, datasets.getAllDatasetNames()))
    datasets.remove(filter(lambda name: "HplusTB_M" in name, datasets.getAllDatasetNames()))

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
    plot = plots.DataMCPlot(datasets, "ForDataDrivenCtrlPlots/SelectedTau_pT_AfterStandardSelections")

    # Same as below, but more compact
    #plots.drawPlot(plot, "taupt", xlabel="Tau p_{T} (GeV/c)", ylabel="Number of events",
    #               rebin=10, stackMCHistograms=True, addMCUncertainty=True, addLuminosityText=True,
    #               opts={"ymin": 1e-1, "ymaxfactor": 10}, log=True)
    #return

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
    plot.addStandardTexts()

    # Save the plot to files
    plot.save()

def setName(drh, name):
    drh.setName(name)
    return drh

def distComparison(datasets):
    # Create a comparison plot of two distributions (must have the same binning)
    # Set the names of DatasetRootHisto objects in order to be able easily reference them later
    drh1 = datasets.getDataset("Data").getDatasetRootHisto("ForDataDrivenCtrlPlots/SelectedTau_pT_AfterStandardSelections")
    drh1.setName("AfterStandardSelections")
    drh2 = datasets.getDataset("Data").getDatasetRootHisto("ForDataDrivenCtrlPlots/SelectedTau_pT_AfterMtSelections")
    drh2.setName("AfterMtSelections")
    plot = plots.ComparisonPlot(drh1, drh2)

    # Set the styles
    st1 = styles.getDataStyle().clone()
    st2 = st1.clone()
    st2.append(styles.StyleLine(lineColor=ROOT.kRed))
    plot.histoMgr.forHisto("AfterStandardSelections", st1)
    plot.histoMgr.forHisto("AfterMtSelections", st2)

    # Set the legend labels
    plot.histoMgr.setHistoLegendLabelMany({"AfterStandardSelections": "After standard selections",
                                           "AfterMtSelections": "After all selections"})
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
    histograms.addStandardTexts(lumi=datasets.getDataset("Data").getLuminosity())

    # Save the plot to files
    plot.save()


if __name__ == "__main__":
    main()
