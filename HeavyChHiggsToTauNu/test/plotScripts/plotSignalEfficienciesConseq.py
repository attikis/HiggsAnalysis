#!/usr/bin/env python

######################################################################
#
# This plot script is for comparing the embedded data to embedding MC
# within the signal analysis. The corresponding python job
# configuration is signalAnalysis_cfg.py with "doPat=1
# tauEmbeddingInput=1" command line arguments.
#
# Authors: Ritva Kinnunen, Matti Kortelainen
#
######################################################################

import ROOT
ROOT.gROOT.SetBatch(True)
import math
import array

import HiggsAnalysis.HeavyChHiggsToTauNu.tools.dataset as dataset
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.histograms as histograms
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.plots as plots
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.counter as counter
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.tdrstyle as tdrstyle
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.styles as styles
import HiggsAnalysis.HeavyChHiggsToTauNu.tools.crosssection as xsect

# Configuration
analysis = "signalAnalysis"
#analysis = "signalOptimisation"
#analysis = "signalAnalysisJESMinus03eta02METMinus10"
#analysis = "EWKFakeTauAnalysisJESMinus03eta02METMinus10"
#analysis = "signalOptimisation/QCDAnalysisVariation_tauPt40_rtau0_btag2_METcut60_FakeMETCut0"
#analysis = "signalAnalysisTauSelectionHPSTightTauBased2"
#analysis = "signalAnalysisBtaggingTest2"
counters = analysis+"Counters/weighted"

# main function
def main():
    # Read the datasets
    datasets = dataset.getDatasetsFromMulticrabCfg(counters=counters)
    datasets.loadLuminosities()

    plots.mergeRenameReorderForDataMC(datasets)

    # Remove signals other than M120
###    datasets.remove(filter(lambda name: "TTToHplus" in name and not "M120" in name, datasets.getAllDatasetNames()))
###    datasets.remove(filter(lambda name: "HplusTB" in name, datasets.getAllDatasetNames()))

    # Set the signal cross sections to a given BR(t->H), BR(h->taunu)
##    xsect.setHplusCrossSectionsToBR(datasets, br_tH=0.05, br_Htaunu=1)

    # Print counters
    doCounters(datasets)

def doCounters(datasets):
    eventCounter = counter.EventCounter(datasets)

    eventCounter.normalizeMCByLuminosity()
#    eventCounter.normalizeMCToLuminosity(73)
    print "============================================================"
    print "Main counter (MC normalized by collision data luminosity)"
    print eventCounter.getMainCounterTable().format()



    # Set the signal cross sections to a value from MSSM
#    xsect.setHplusCrossSectionsToMSSM(datasets, tanbeta=20, mu=200)

###    plots.mergeWHandHH(datasets) # merging of WH and HH signals must be done after setting the cross section

    style = tdrstyle.TDRStyle()

    eventCounter = counter.EventCounter(datasets, counters=counters)
    eventCounter.normalizeMCByCrossSection()
    mainTable = eventCounter.getMainCounterTable()

    signalDatasets = [
        "TTToHplusBWB_M80",
        "TTToHplusBWB_M90",
        "TTToHplusBWB_M100",
        "TTToHplusBWB_M120",
        "TTToHplusBWB_M140",
        "TTToHplusBWB_M150",
        "TTToHplusBWB_M155",
        "TTToHplusBWB_M160",
        ]
    allName = "All events"

    cuts = [
        "Trigger and HLT_MET cut",
        "primary vertex",
        "taus == 1",
        "trigger scale factor",
        "electron veto",
        "muon veto",
        "njets",
        "MET",
        "btagging",
        "btagging scale factor"
        ]

    xvalues = [80, 90, 100, 120, 140, 150, 155, 160]
    xerrs = [0]*len(xvalues)
    yvalues = {}
    yerrs = {}
    for cut in cuts:
        yvalues[cut] = []
        yerrs[cut] = []
    for name in signalDatasets:
        column = mainTable.getColumn(name=name)

        # Get the counts (returned objects are of type dataset.Count,
        # and have both value and uncertainty
#        allCount = column.getCount(column.getRowNames().index("All events"))

        for cut in cuts:
            cutCount = column.getCount(column.getRowNames().index(cut))
            if column.getRowNames().index(cut) == 1: ## trigger
                allCount = column.getCount(column.getRowNames().index("All events"))
                
            if column.getRowNames().index(cut) == 4: ## tau id
                allCount = column.getCount(column.getRowNames().index("Trigger and HLT_MET cut"))
                
            if column.getRowNames().index(cut) == 7: ## electron veto
                allCount = column.getCount(column.getRowNames().index("taus == 1"))
                
            if column.getRowNames().index(cut) == 8:  ## muon veto
                ## muon veto for lepton veto
                allCount = column.getCount(column.getRowNames().index("taus == 1"))
#                allCount = column.getCount(column.getRowNames().index("electron veto"))

            if column.getRowNames().index(cut) == 9: ## njets
                allCount = column.getCount(column.getRowNames().index("muon veto"))
                
            if column.getRowNames().index(cut) == 10: ## MET
                allCount = column.getCount(column.getRowNames().index("njets"))
                
            if column.getRowNames().index(cut) == 11: ## btagging
                allCount = column.getCount(column.getRowNames().index("MET"))
                                 
            eff = cutCount.clone()
            eff.divide(allCount) # N(cut) / N(all)
#            print "cutCount ",cutCount.value(),"allCount  ",allCount.value()
                                           
            yvalues[cut].append(eff.value())
            yerrs[cut].append(eff.uncertainty())

    def createErrors(cutname):
        gr = ROOT.TGraphErrors(len(xvalues), array.array("d", xvalues), array.array("d", yvalues[cutname]),
                               array.array("d", xerrs), array.array("d", yerrs[cutname]))
        gr.SetMarkerStyle(24)
        gr.SetMarkerColor(2)
        gr.SetMarkerSize(0.9)
        gr.SetLineStyle(1)
        gr.SetLineWidth(2)
        return gr

    gtrig = createErrors("Trigger and HLT_MET cut")
    gtrig.SetLineColor(38)
    gtrig.SetMarkerColor(38)
    gtrig.SetLineStyle(2) 
    gtau = createErrors("taus == 1")
    gtau.SetLineColor(2)
    gtau.SetMarkerColor(2)
    gtau.SetLineStyle(3)  
    #gtau = createErrors("trigger scale factor")
    gveto = createErrors("muon veto")
    gveto.SetLineColor(1)
    gveto.SetMarkerColor(1)
    gveto.SetLineStyle(4) 
    gjets = createErrors("njets")
    gjets.SetLineColor(4)
    gjets.SetMarkerColor(4)
    gjets.SetLineStyle(1) 
    gmet = createErrors("MET")
    gmet.SetLineColor(2)
    gmet.SetMarkerColor(2)
    gmet.SetLineStyle(5) 
    gbtag = createErrors("btagging")
    gbtag.SetLineColor(1)
    gbtag.SetMarkerColor(1)
    gbtag.SetLineStyle(6) 
    #gtau = createErrors("trigger scale factor")

                        
    glist = [gtrig, gtau, gveto, gjets, gmet, gbtag]
    
    opts = {"xmin": 75, "xmax": 165, "ymin": 0.03}
    canvasFrame = histograms.CanvasFrame([histograms.HistoGraph(g, "", "") for g in glist], "SignalEfficiencyConseq", **opts)
    canvasFrame.frame.GetYaxis().SetTitle("Selection efficiency")
    canvasFrame.frame.GetXaxis().SetTitle("m_{H^{#pm}} (GeV/c^{2})")
    canvasFrame.canvas.SetLogy(True)
    canvasFrame.frame.Draw()

    for gr in glist:
        gr.Draw("PC same")
    
    histograms.addEnergyText()
    histograms.addCmsPreliminaryText()

    legend = histograms.createLegend(x1=0.5, y1=0.53, x2=0.85, y2=0.75)

    legend.AddEntry(gtrig,"Trigger", "l"); 
    legend.AddEntry(gtau, "#tau identification", "l"); 
    legend.AddEntry(gveto ,"lepton vetoes", "l"); 
    legend.AddEntry(gjets ,"3 jets", "l"); 
    legend.AddEntry(gmet,"MET ", "l")
    legend.AddEntry(gbtag,"b tagging ", "l")
    legend.Draw()
    
    canvasFrame.canvas.SaveAs(".png")
    canvasFrame.canvas.SaveAs(".C")
    canvasFrame.canvas.SaveAs(".eps")
    
# Call the main function if the script is executed (i.e. not imported)
if __name__ == "__main__":
    main()
