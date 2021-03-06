'''
DESCRIPTION:
This is a datacard template for 2016 results. 
It can be used to generate datacards for H+ -> tau nu analysis, 
in the fully hadronic final state. 


USAGE:
./dcardGenerator_v2.py -x dcardDefault2016Datacard.py -d <path-to-directory>
where <path-to-directory> contains SignalAnalysis_* and pseudoMulticrab_QCDMeasurement dirs
'''

#================================================================================================  
# Imports
#================================================================================================  

import HiggsAnalysis.NtupleAnalysis.tools.systematics as systematics
import HiggsAnalysis.NtupleAnalysis.tools.ShellStyles as ShellStyles
import sys
import re

#================================================================================================  
# Define mass points
#================================================================================================  

LightAnalysis = False 
IntermediateAnalysis = False
HeavyAnalysis = True

# Set mass points according to the chosen ranges
LightMassPoints=[80,90,100,120,140,150,155,160]
IntermediateMassPoints=[165,170,175]
IntermediateMassPointsAll=[145,150,155,160,165,170,175,180,190,200]
HeavyMassPoints=[180,200,220,250,300,400,500,750,800,1000,2000,2500,3000] #, 5000, 7000, 10000]

# Set mass points
MassPoints = []
if LightAnalysis:
    MassPoints+=LightMassPoints[:]
else:
    LightMassPoints = []
if IntermediateAnalysis:
    MassPoints+=IntermediateMassPoints[:]    
else:
    IntermediateMassPoints = []
if HeavyAnalysis:
    MassPoints+=HeavyMassPoints[:]
else:
    HeavyMassPoints = []

# For intermediate-only generation, use all intermediate samples (also overlapping)
IntermediateAnalysisOnly = not LightAnalysis and not HeavyAnalysis and IntermediateAnalysis
if IntermediateAnalysisOnly:
    MassPoints=IntermediateMassPointsAll[:]
else:
    IntermediateMassPointsAll=[]

# Set mass points for control plots (overriding the previous settings):
#MassPoints = [200]

#================================================================================================  
# Options
#================================================================================================  

# General options
BlindAnalysis=True
DataCardName ='HplusToTauNu_13TeV'
OptionMassShape="TransverseMass" # Use "FullMass" in order to use invariant mass instead of mT
ToleranceForLuminosityDifference=0.05 # Tolerance for throwing error on luminosity difference (0.01=1 percent agreement is required)

# Control plots and blinding policy
OptionDoControlPlots= False #FIXME: If you want control plots, switch this to true!
OptionCtrlPlotsAfterAllSelections=True # Produce control plots after all selections (all selections for transverse mass)
OptionBlindThreshold=None # If signal exceeds this fraction of expected events, data is blinded; set to None to disable

# Systematic uncertainties
OptionIncludeSystematics=True # Include shape systematics (multicrabs must beproduced with doSystematics=True)
OptionCombineSingleColumnUncertainties = False # (approxmation that makes limit running faster)
# Datasets
OptionUseWJetsHT = True # Use HT binned WJets samples instead of inclusive for WJets background
OptionUseDYHT = True # Use HT binned DY samples instead of inclusive for DY background
OptionGenuineTauBackgroundSource="MC_FakeAndGenuineTauNotSeparated" # Use "DataDriven" to get EWK+tt genuine taus from embedded samples
IntSFuncertainty = 0.297037 # for SF 0.41 (light region)
#IntSFuncertainty = 0.201565 # for SF 0.65 (heavy region)

# Summary tables
OptionDisplayEventYieldSummary=False
OptionNumberOfDecimalsInSummaries=1

# Limit calculation
OptionLimitOnSigmaBr=False # Automatically set to true for heavy H+, set to true if you want to force heavy signal model for all mass points
OptionLimitOnBrBr=False # Automatically set to true for light H+, set to true if you want to force light signal model for all mass points

# Handling of small event yields and stat. uncertainties
MinimumStatUncertainty=0.5 # Minimum stat. uncertainty to set to bins with zero events
UseAutomaticMinimumStatUncertainty = True # Do NOT use the MinimumStatUncertainty value above for ~empty bins, but determine the value from the lowest non-zero rate for each dataset
ToleranceForMinimumRate=0.0 # Tolerance for almost zero rate (columns with smaller rate are suppressed)
#OptionBinByBinLabel="_RtauGt0p75_" # Label to be attached to stat. uncert. shape nuisances, needed to decorrelate stat. uncertainty variations in case of categorization
#OptionBinByBinLabel="_RtauLt0p75_" # Label to be attached to stat. uncert. shape nuisances, needed to decorrelate stat. uncertainty variations in case of categorization

# Nuisances
OptionConvertFromShapeToConstantList=[] # Convert the following nuisances from shape to constant
OptionSeparateShapeAndNormalizationFromSystVariationList=[] # Separate in the following shape nuisances the shape and normalization components
                                                        
# Options for reports and articles
OptionBr=0.01  # Br(t->bH+)
OptionSqrtS=13 # sqrt(s)

#================================================================================================  
# Counter and histogram path definitions
#================================================================================================  

# Rate counter definitions
SignalRateCounter="Selected events"
FakeRateCounter="EWKfaketaus:SelectedEvents"

# Shape histogram definitions
histoPathInclusive="ForDataDrivenCtrlPlots"
histoPathGenuineTaus="ForDataDrivenCtrlPlots" # genuine tau requirement already as part of event selection
histoPathFakeTaus="ForDataDrivenCtrlPlotsEWKFakeTaus"
shapeHistoName=None
if OptionMassShape =="TransverseMass":
    shapeHistoName="shapeTransverseMass"
elif OptionMassShape =="FullMass":
    raise Exception("Does not work")
    shapeHistoName="shapeInvariantMass"
ShapeHistogramsDimensions=systematics.getBinningForPlot(shapeHistoName)
DataCardName +="_"+OptionMassShape.replace("TransverseMass","mT").replace("FullMass","invMass")

#================================================================================================  
# Observation definition (how to retrieve number of observed events)
#================================================================================================  

from HiggsAnalysis.LimitCalc.InputClasses import ObservationInput
Observation=ObservationInput(datasetDefinition="Data", shapeHistoName=shapeHistoName, histoPath=histoPathInclusive)

#================================================================================================
# Function definitions
#================================================================================================
def Print(msg, printHeader=False):
    fName = __file__.split("/")[-1]
    if printHeader==True:
        print "=== ", fName
        print "\t", msg
    else:
        print "\t", msg
    return

def PrintNuisancesTable(Nuisances, DataGroups):
    align   = "{:<3} {:<30} {:<10} {:<20} {:<15} {:<10} {:<40} {:<10}"
    hLine   = "="*150
    header  = align.format("#", "ID", "Distrib.", "Function", "Value (4f)", "Scaling", "Label", "# Datasets")
    table   = []
    table.append(hLine)
    table.append(header)
    table.append(hLine)

    # For-loop: All nuisances
    for i, n in enumerate(Nuisances, 1):
        
        datasetList = []
        for j, dg in enumerate(DataGroups, 1):
            if n.getId() in dg.getNuisances():
                datasetList.append(dg.getLabel())
        if isinstance(n.getArg("value"), float):
            value = "%.4f" % n.getArg("value")
        elif n.getId() == "lumi_13TeV":
            value = n.getArg("value").getUncertaintyMax()
        else:
            value = "N/A"

        # Create the row
        #row = align.format(i, n.getId(), n.getDistribution(), n.getFunction(), value, n.getArg("scaling"), n.getLabel(), ", ".join(datasetList) )
        row = align.format(i, n.getId(), n.getDistribution(), n.getFunction(), value, n.getArg("scaling"), n.getLabel(), len(datasetList) )
        table.append(row)
    table.append(hLine)
    table.append("")
    
    # For-loop: All table rows
    for i,row in enumerate(table, 1):
        Print(row, i==1)
    return

#================================================================================================  
# Groups of nuisances (each nuisance to be defined later)
#================================================================================================  

myTrgSystematics=["CMS_eff_t_trg_data","CMS_eff_t_trg_MC", # Trigger tau part
                  "CMS_eff_met_trg_data","CMS_eff_met_trg_MC"] # Trigger MET part
myTauIDSystematics=["CMS_eff_t"] #tau ID
if not LightAnalysis and OptionIncludeSystematics:
    myTauIDSystematics.extend(["CMS_eff_t_highpt"])

myTauMisIDSystematics=["CMS_fake_e_to_t","CMS_fake_m_to_t"] # tau mis-ID, "CMS_fake_jetToTau" not included, as jet->tau comes from fake tau BG measurement
myESSystematics=["CMS_scale_t","CMS_scale_j","CMS_res_j","CMS_scale_met"] # TES, JES, CMS_res_j, UES
myBtagSystematics=["CMS_eff_b","CMS_fake_b"] # b tag and mistag
myTopSystematics=["CMS_topPtReweight"] # top pt reweighting
myTopAcceptanceSystematics=["CMS_Hptn_mu_RF_top","CMS_Hptn_pdf_top"]
myTopAcceptanceSystematicsForQCD=["CMS_Hptn_mu_RF_top_forQCD","CMS_Hptn_pdf_top_forQCD"]
myEWKAcceptanceSystematics=["CMS_Hptn_mu_RF_ewk","CMS_Hptn_pdf_ewk"]
myPileupSystematics=["CMS_pileup"] # CMS_pileup
myLeptonVetoSystematics=["CMS_eff_e_veto","CMS_eff_m_veto"] # CMS_pileup

myShapeSystematics=[]
myShapeSystematics.extend(myTrgSystematics)
if not LightAnalysis:
    myShapeSystematics.extend(["CMS_eff_t_highpt"])
myShapeSystematics.extend(myTauMisIDSystematics)
myShapeSystematics.extend(myESSystematics)
myShapeSystematics.extend(myBtagSystematics)
myShapeSystematics.extend(myTopSystematics)
myShapeSystematics.extend(myPileupSystematics)

if not OptionIncludeSystematics:
    myShapeSystematics=[]

myEmbeddingShapeSystematics=["CMS_eff_t_trg_data","CMS_trg_taumet_L1ETM_dataeff","CMS_trg_muon_dataeff","CMS_scale_t","CMS_Hptntj_taubkg_ID_mu","CMS_Hptntj_taubkg_WtauToMu"]

#================================================================================================  
# DataGroups (datacard columns, each corresponding to one process with similar systematics) 
#================================================================================================ 

from HiggsAnalysis.LimitCalc.InputClasses import DataGroup
DataGroups=[]
EmbeddingIdList=[]
EWKFakeIdList=[]

signalTemplate=DataGroup(datasetType="Signal", histoPath=histoPathInclusive, shapeHistoName=shapeHistoName)
mergeColumnsByLabel=[]

if not IntermediateAnalysisOnly:
    for mass in LightMassPoints:
        myMassList=[mass]
        hwx=signalTemplate.clone()
        hwx.setLabel("HW_M"+str(mass)+"_CMS_Hptntj")
        hwx.setLandSProcess(0)
        hwx.setValidMassPoints(myMassList)
        hwx.setNuisances(myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                         +myESSystematics[:]+myBtagSystematics[:]+myPileupSystematics[:]+myLeptonVetoSystematics[:]
#                         +["xsect_ttbar","lumi_13TeV"])
                         +["QCDscale_ttbar","pdf_ttbar","mass_top","lumi_13TeV"])
        hwx.setDatasetDefinition("TTToHplusBWB_M"+str(mass))
        DataGroups.append(hwx)
for mass in HeavyMassPoints+IntermediateMassPoints+IntermediateMassPointsAll:
    myMassList=[mass]
    hx=signalTemplate.clone()
    hx.setLabel("CMS_Hptntj_Hp"+str(mass))
    hx.setLandSProcess(0)
    hx.setValidMassPoints(myMassList)
    # Add nuisances
    hxNuisanceList = myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]+myESSystematics[:]+myBtagSystematics[:]+myPileupSystematics[:]+myLeptonVetoSystematics[:]+["lumi_13TeV"]
    # Add QCDscale acceptance nuisance
    if mass < 760:
        hxNuisanceList += ["CMS_Hptn_mu_RF_Hptn"]
    else:
        hxNuisanceList += ["CMS_Hptn_mu_RF_Hptn_heavy"]
    # Add PDF acceptance nuisance
    hxNuisanceList += ["CMS_Hptn_pdf_Hptn"]
    # Add intermediate region nuisances
    intString=""
    if IntermediateAnalysisOnly:
        if mass in IntermediateMassPointsAll:
            hxNuisanceList += ["CMS_Hptn_int_SF_stat"] #,"CMS_Hptn_int_neutral"]
            intString="intermediate"
    else:
        if mass in IntermediateMassPoints:
            hxNuisanceList += ["CMS_Hptn_int_SF_stat"] #,"CMS_Hptn_int_neutral"]
            intString="intermediate"
    hx.setNuisances(hxNuisanceList)
    hx.setDatasetDefinition("HplusTB"+intString+"_M"+str(mass))
    DataGroups.append(hx)

myQCDSystematics = myTrgSystematics[:]+myESSystematics[:]+myBtagSystematics[:]+myTopSystematics[:]+myTopAcceptanceSystematicsForQCD+myPileupSystematics[:]
#approximation 1: only ttbar xsect uncertinty applied to QCD, as ttbar dominates the EWK BG (but uncertainty is scaled according to 1-purity, i.e. #all_ttbar+EWK_events_in_QCDandFakeTau/#all_events_in_QCDandFakeTau)
myQCDSystematics+=["QCDscale_ttbar_forQCD","pdf_ttbar_forQCD","mass_top_forQCD","lumi_13TeV_forQCD","CMS_eff_t_forQCD"]
#approximation 2: myLeptonVetoSystematics neglected for QCD

if OptionIncludeSystematics: 
    if not LightAnalysis:
        myQCDSystematics += ["CMS_eff_t_highpt"]
    myQCDSystematics += ["CMS_Hptntj_fake_t_transfer_factors","CMS_Hptntj_fake_t_shape"] #these can be used only if QCDMeasurement has been run with systematics

# Set label prefix (or use postfix when signal model requires the name to start in a specifi way)
labelPrefix="CMS_Hptntj_"
labelPostfix="_CMS_Hptntj"

myQCD=DataGroup(label=labelPrefix+"QCDandFakeTau", landsProcess=1, validMassPoints=MassPoints,
                #datasetType="QCD MC", datasetDefinition="QCD",
                #nuisances=myShapeSystematics[:]+["xsect_QCD","lumi_13TeV"],
                datasetType="QCD inverted", datasetDefinition="QCDMeasurementMT",
                nuisances=myQCDSystematics,
                shapeHistoName=shapeHistoName, histoPath=histoPathInclusive)
DataGroups.append(myQCD)

# Choose between WJets and WJetsHT dataset
WJetsDataset = "WJets"
DYDataset = "DYJetsToLL"
if OptionUseWJetsHT:
    WJetsDataset = "WJetsHT"
if OptionUseDYHT:
   DYDataset = "DYJetsToLLHT"

if OptionGenuineTauBackgroundSource =="DataDriven":
    # EWK genuine taus from embedding
    myEmbDataDrivenNuisances=["CMS_EmbSingleMu_QCDcontam","CMS_EmbSingleMu_hybridCaloMET","CMS_Hptntj_taubkg_reweighting"] # EWK + ttbar with genuine taus
    EmbeddingIdList=[3]
    DataGroups.append(DataGroup(label="CMS_Hptntj_EWK_Tau", landsProcess=1, 
                                shapeHistoName=shapeHistoName, histoPath=histoPathInclusive,
                                datasetType="Embedding", 
                                #datasetDefinition=["SingleMu"], 
                                datasetDefinition="Data", 
                                validMassPoints=MassPoints, 
                                #additionalNormalisation=0.25, # not needed anymore
                                nuisances=myEmbeddingShapeSystematics[:]+myEmbDataDrivenNuisances[:]
                                ))
else:
    # EWK genuine taus from MC
    DataGroups.append(DataGroup(label="ttbar"+labelPostfix, landsProcess=3,
                                shapeHistoName=shapeHistoName, histoPath=histoPathGenuineTaus,
                                datasetType="Embedding",
                                datasetDefinition="TT_Mtt",
                                validMassPoints=MassPoints,
                                nuisances=myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                                  +myESSystematics[:]+myBtagSystematics[:]+myPileupSystematics[:]+myLeptonVetoSystematics[:]
                                  +myTopSystematics+myTopAcceptanceSystematics+["QCDscale_ttbar","pdf_ttbar","mass_top","lumi_13TeV"]))
    DataGroups.append(DataGroup(label=labelPrefix+"W", landsProcess=4,
                                shapeHistoName=shapeHistoName, histoPath=histoPathGenuineTaus,
                                datasetType="Embedding", 
                                datasetDefinition=WJetsDataset, # can be WJets or WJetsHT
                                validMassPoints=MassPoints,
                                nuisances=myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                                  +myESSystematics[:]+myBtagSystematics[:]+myEWKAcceptanceSystematics+myPileupSystematics[:]+myLeptonVetoSystematics[:]
                                  +["QCDscale_Wjets","pdf_Wjets","lumi_13TeV"]))
    DataGroups.append(DataGroup(label=labelPrefix+"singleTop", landsProcess=5,
                                shapeHistoName=shapeHistoName, histoPath=histoPathGenuineTaus,
                                datasetType="Embedding",
                                datasetDefinition="SingleTop",
                                validMassPoints=MassPoints,
                                nuisances=myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                                  +myESSystematics[:]+myBtagSystematics[:]+["mass_top_forSingleTop"]+myTopAcceptanceSystematics+myPileupSystematics[:]+myLeptonVetoSystematics[:]
                                  +["QCDscale_singleTop","pdf_singleTop","lumi_13TeV"]))
    DataGroups.append(DataGroup(label=labelPrefix+"DY", landsProcess=6,
                                shapeHistoName=shapeHistoName, histoPath=histoPathGenuineTaus,
                                datasetType="Embedding",
                                #datasetDefinition="DYJetsToLLHT",
                                datasetDefinition=DYDataset,
                                validMassPoints=MassPoints,
                                nuisances=myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                                  +myESSystematics[:]+myBtagSystematics[:]+myEWKAcceptanceSystematics+myPileupSystematics[:]+myLeptonVetoSystematics[:]
                                  +["QCDscale_DY","pdf_DY","lumi_13TeV"]))
    DataGroups.append(DataGroup(label=labelPrefix+"VV", landsProcess=7,
                                shapeHistoName=shapeHistoName, histoPath=histoPathGenuineTaus, 
                                datasetType="Embedding", 
                                datasetDefinition="Diboson",
                                validMassPoints=MassPoints,
                                nuisances=myTrgSystematics[:]+myTauIDSystematics[:]+myTauMisIDSystematics[:]
                                  +myESSystematics[:]+myBtagSystematics[:]+myEWKAcceptanceSystematics+myPileupSystematics[:]+myLeptonVetoSystematics[:]
                                  +["QCDscale_VV","pdf_VV","lumi_13TeV"]))

    # Example of how to merge columns
    # mergeColumnsByLabel.append({"label": labelPrefix+"EWK", "mergeList": [labelPrefix+"W",labelPrefix+"DY"]}) #,labelPrefix+"VV"]})

# Reserve column 2 (this was necessary for LandS; code could be updated to combine for this piece)
DataGroups.append(DataGroup(label="res.", landsProcess=2,datasetType="None", validMassPoints=MassPoints))

#================================================================================================  
# Nuisance Parameters (aka systematic uncertainties, repredented by rows in the final datacard) 
#================================================================================================ 

# Note: Remember to include 'stat.' into the label of nuistances of statistical nature

from HiggsAnalysis.LimitCalc.InputClasses import Nuisance
ReservedNuisances=[]
Nuisances=[]

#====signal acceptance
Nuisances.append(Nuisance(id="CMS_Hptn_int_SF_stat", label="uncertainty for NLO vs. LO SF in intermediate region",
    distr="lnN", function="Constant", value=IntSFuncertainty))
#Nuisances.append(Nuisance(id="CMS_Hptn_int_neutral", label="effect of WithNeutral samples in intermediate region",
#    distr="lnN", function="Constant", value=0.1, upperValue=0.0))

#=====tau ID and mis-ID
# tau ID
Nuisances.append(Nuisance(id="CMS_eff_t", label="tau-jet ID (no Rtau) uncertainty for genuine taus",
    distr="lnN", function="Constant", value=0.04))
Nuisances.append(Nuisance(id="CMS_eff_t_forQCD", label="tau-jet ID uncertainty for genuine taus",
    distr="lnN", function="ConstantForQCD", value=0.04))
# tau ID high-pT
if "CMS_eff_t_highpt" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_t_highpt", label="tau-jet ID high-pt uncertainty for genuine taus",
        distr="shapeQ", function="ShapeVariation", systVariation="TauIDSyst"))       
#=====tau and MET trg
if "CMS_eff_t_trg_data" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_t_trg_data", label="tau+MET trg tau part data eff.",
        distr="shapeQ", function="ShapeVariation", systVariation="TauTrgEffData"))
else:
    Nuisances.append(Nuisance(id="CMS_eff_t_trg_data", label="APPROXIMATION for tau+MET trg tau part data eff.",
        distr="lnN", function="Constant", value=0.03))
if "CMS_eff_t_trg_MC" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_t_trg_MC", label="tau+MET trg tau part MC eff.",
        distr="shapeQ", function="ShapeVariation", systVariation="TauTrgEffMC"))
else:
    Nuisances.append(Nuisance(id="CMS_eff_t_trg_MC", label="APPROXIMATION for tau+MET trg tau part MC eff.",
        distr="lnN", function="Constant", value=0.04))
if "CMS_eff_met_trg_data" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_met_trg_data", label="tau+MET trg MET data eff.",
        distr="shapeQ", function="ShapeVariation", systVariation="METTrgEffData"))
else:
    Nuisances.append(Nuisance(id="CMS_eff_met_trg_data", label="APPROXIMATION for tau+MET trg MET data eff.",
        distr="lnN", function="Constant", value=0.2))
if "CMS_eff_met_trg_MC" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_met_trg_MC", label="tau+MET trg MET MC eff.",
        distr="shapeQ", function="ShapeVariation", systVariation="METTrgEffMC"))
else:
    Nuisances.append(Nuisance(id="CMS_eff_met_trg_MC", label="APPROXIMATION for tau+MET trg MET MC eff.",
        distr="lnN", function="Constant", value=0.01))
#=====lepton veto
Nuisances.append(Nuisance(id="CMS_eff_e_veto", label="e veto",
    distr="lnN", function="Ratio",
    numerator="passed e selection (Veto)", # main counter name after electron veto
    denominator="Met trigger SF", # main counter name before electron and muon veto
    scaling=0.02
))
Nuisances.append(Nuisance(id="CMS_eff_m_veto", label="mu veto",
    distr="lnN", function="Ratio",
    numerator="passed mu selection (Veto)", # main counter name after electron and muon veto
    denominator="passed e selection (Veto)", # main counter name before muon veto
    scaling =0.01
))

#===== b tag and mistag SF
if "CMS_eff_b" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_eff_b", label="b tagging",
        distr="shapeQ", function="ShapeVariation", systVariation="BTagSF"))
else:
    Nuisances.append(Nuisance(id="CMS_eff_b", label="APPROXIMATION for b tagging",
        distr="lnN", function="Constant",value=0.05))
if "CMS_fake_b" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_fake_b", label="b mistagging",
        distr="shapeQ", function="ShapeVariation", systVariation="BMistagSF"))
else:
    Nuisances.append(Nuisance(id="CMS_fake_b", label="APPROXIMATION for b mistagging",
        distr="lnN", function="Constant",value=0.02))

#=====  e->tau mis-ID
if "CMS_fake_e_to_t" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_fake_e_to_t", label="tau-jet ID (no Rtau) e->tau",
        distr="shapeQ", function="ShapeVariation", systVariation="FakeTauElectron"))
else:
    Nuisances.append(Nuisance(id="CMS_fake_e_to_t", label="APPROXIMATION for tau-jet ID (no Rtau) e->tau",
        distr="lnN", function="Constant", value=0.001))

# mu->tau mis-ID
if "CMS_fake_m_to_t" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_fake_m_to_t", label="tau-jet ID (no Rtau) mu->tau",
        distr="shapeQ", function="ShapeVariation", systVariation="FakeTauMuon"))
else:
    Nuisances.append(Nuisance(id="CMS_fake_m_to_t", label="APPROXIMATION for tau-jet ID (no Rtau) mu->tau",
        distr="lnN", function="Constant", value=0.001))

# jet->tau mis-ID
#if "CMS_fake_jetToTau" in myShapeSystematics:
#    Nuisances.append(Nuisance(id="CMS_fake_jetToTau", label="tau-jet ID (no Rtau) jet->tau",
#        distr="shapeQ", function="ShapeVariation", systVariation="FakeTauJet"))
#else:
#    Nuisances.append(Nuisance(id="CMS_fake_jetToTau", label="APPROXIMATION for tau-jet ID (no Rtau) jet->tau",
#        distr="lnN", function="Constant", value=0.01))

#===== energy scales
# tau ES
if "CMS_scale_t" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_scale_t", label="Tau energy scale",
        distr="shapeQ", function="ShapeVariation", systVariation="TauES"))
else:
    Nuisances.append(Nuisance(id="CMS_scale_t", label="APPROXIMATION for tau ES",
        distr="lnN", function="Constant", value=0.06))
# jet ES
if "CMS_scale_j" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_scale_j", label="Jet energy scale",
        distr="shapeQ", function="ShapeVariation", systVariation="JES"))
else:
    Nuisances.append(Nuisance(id="CMS_scale_j", label="APPROXIMATION for jet ES",
        distr="lnN", function="Constant", value=0.03))
# unclustered MET ES
if "CMS_scale_met" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_scale_met", label="Unclustered MET energy scale",
        distr="shapeQ", function="ShapeVariation", systVariation="UES"))
else:
    Nuisances.append(Nuisance(id="CMS_scale_met", label="APPROXIMATION for unclustered MET ES",
        distr="lnN", function="Constant",value=0.03))
# CMS_res_j
if "CMS_res_j" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_res_j", label="Jet energy resolution",
        distr="shapeQ", function="ShapeVariation", systVariation="JER"))
else:
    Nuisances.append(Nuisance(id="CMS_res_j", label="APPROXIMATION for CMS_res_j",
        distr="lnN", function="Constant",value=0.04))

#===== Top pt SF
if "CMS_topPtReweight" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_topPtReweight", label="top pT reweighting",
        distr="shapeQ", function="ShapeVariation", systVariation="TopPt"))
else:
    Nuisances.append(Nuisance(id="CMS_topPtReweight", label="APPROXIMATION for top pT reweighting",
        distr="lnN", function="Constant",value=0.25))

#===== Pileup
if "CMS_pileup" in myShapeSystematics:
    Nuisances.append(Nuisance(id="CMS_pileup", label="CMS_pileup",
        distr="shapeQ", function="ShapeVariation", systVariation="PUWeight"))
else:
    Nuisances.append(Nuisance(id="CMS_pileup", label="APPROXIMATION for CMS_pileup",
        distr="lnN", function="Constant",value=0.05))

#==== Acceotance uncertainties / QCDscale

Nuisances.append(Nuisance(id="CMS_Hptn_mu_RF_top", label="QCDscale acceptance uncertainty for top backgrounds",
        distr="lnN", function="Constant",value=0.02))

Nuisances.append(Nuisance(id="CMS_Hptn_mu_RF_ewk", label="QCDscale acceptance uncertainty for EWK backgrounds",
        distr="lnN", function="Constant",value=0.05))

Nuisances.append(Nuisance(id="CMS_Hptn_mu_RF_Hptn", label="QCDscale acceptance uncertainty for signal",
        distr="lnN", function="Constant",value=0.048))

Nuisances.append(Nuisance(id="CMS_Hptn_mu_RF_Hptn_heavy", label="QCDscale acceptance uncertainty for signal",
        distr="lnN", function="Constant",value=0.012))

Nuisances.append(Nuisance(id="CMS_Hptn_mu_RF_top_forQCD", label="QCDscale acceptance uncertainty for fake tau background",
        distr="lnN", function="ConstantForQCD",value=0.02))

#==== Acceptance uncertainties / pdf

Nuisances.append(Nuisance(id="CMS_Hptn_pdf_top", label="PDF acceptance uncertainty for top backgrounds",
        distr="lnN", function="Constant",value=0.02,upperValue=0.0027))

Nuisances.append(Nuisance(id="CMS_Hptn_pdf_ewk", label="PDF acceptance uncertainty for EWK backgrounds",
        distr="lnN", function="Constant",value=0.033,upperValue=0.046))

Nuisances.append(Nuisance(id="CMS_Hptn_pdf_Hptn", label="PDF acceptance uncertainty for signal",
        distr="lnN", function="Constant",value=0.004,upperValue=0.017))

Nuisances.append(Nuisance(id="CMS_Hptn_pdf_top_forQCD", label="PDF acceptance uncertainty for fake tau background",
        distr="lnN", function="ConstantForQCD",value=0.02,upperValue=0.0027))

#===== Cross section uncertainties

# ttbar
#Nuisances.append(Nuisance(id="xsect_ttbar", label="ttbar cross section",
#    distr="lnN", function="Constant",
#    value=systematics.getCrossSectionUncertainty("TTJets").getUncertaintyDown(),
#    upperValue=systematics.getCrossSectionUncertainty("TTJets").getUncertaintyUp()))
Nuisances.append(Nuisance(id="QCDscale_ttbar", label="ttbar cross section scale uncertainty ",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("TTJets_scale").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("TTJets_scale").getUncertaintyUp()))
Nuisances.append(Nuisance(id="pdf_ttbar", label="ttbar pdf uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("TTJets_pdf").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("TTJets_pdf").getUncertaintyUp()))
Nuisances.append(Nuisance(id="mass_top", label="ttbar top mass uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("TTJets_mass").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("TTJets_mass").getUncertaintyUp()))

# ttbar for QCD
#Nuisances.append(Nuisance(id="xsect_ttbar_forQCD", label="ttbar cross section",
#    distr="lnN", function="ConstantForQCD",
#    value=systematics.getCrossSectionUncertainty("TTJets").getUncertaintyDown(),
#    upperValue=systematics.getCrossSectionUncertainty("TTJets").getUncertaintyUp()))
Nuisances.append(Nuisance(id="QCDscale_ttbar_forQCD", label="ttbar cross section scale uncertainty ",
    distr="lnN", function="ConstantForQCD",
    value=systematics.getCrossSectionUncertainty("TTJets_scale").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("TTJets_scale").getUncertaintyUp()))
Nuisances.append(Nuisance(id="pdf_ttbar_forQCD", label="ttbar pdf uncertainty",
    distr="lnN", function="ConstantForQCD",
    value=systematics.getCrossSectionUncertainty("TTJets_pdf").getUncertaintyDown()))
Nuisances.append(Nuisance(id="mass_top_forQCD", label="ttbar top mass uncertainty",
    distr="lnN", function="ConstantForQCD",
    value=systematics.getCrossSectionUncertainty("TTJets_mass").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("TTJets_mass").getUncertaintyUp()))
    
# WJets
#Nuisances.append(Nuisance(id="xsect_Wjets", label="W+jets cross section",
#    distr="lnN", function="Constant",
#    value=systematics.getCrossSectionUncertainty("WJets").getUncertaintyDown()))
Nuisances.append(Nuisance(id="QCDscale_Wjets", label="W+jets cross section scale uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("WJets_scale").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("WJets_scale").getUncertaintyUp()))
Nuisances.append(Nuisance(id="pdf_Wjets", label="W+jets pdf uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("WJets_pdf").getUncertaintyDown()))


# Single top
#Nuisances.append(Nuisance(id="xsect_singleTop", label="single top cross section",
#    distr="lnN", function="Constant",
#    value=systematics.getCrossSectionUncertainty("SingleTop").getUncertaintyDown()))
Nuisances.append(Nuisance(id="QCDscale_singleTop", label="single top cross section sale uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("SingleTop_scale").getUncertaintyDown()))
Nuisances.append(Nuisance(id="pdf_singleTop", label="single top pdf ucnertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("SingleTop_pdf").getUncertaintyDown()))
Nuisances.append(Nuisance(id="mass_top_forSingleTop", label="single top mass uncertainty",
    distr="lnN", function="Constant",
    value=0.022))


# DY
#Nuisances.append(Nuisance(id="xsect_DYtoll", label="Z->ll cross section",
#    distr="lnN", function="Constant",
#    value=systematics.getCrossSectionUncertainty("DYJetsToLL").getUncertaintyDown()))
Nuisances.append(Nuisance(id="QCDscale_DY", label="Z->ll cross section scale uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("DYJetsToLL_scale").getUncertaintyDown(),
    upperValue=systematics.getCrossSectionUncertainty("DYJetsToLL_scale").getUncertaintyUp()))
Nuisances.append(Nuisance(id="pdf_DY", label="Z->ll pdf uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("DYJetsToLL_pdf").getUncertaintyDown()))

# Diboson
#Nuisances.append(Nuisance(id="xsect_VV", label="diboson cross section",
#    distr="lnN", function="Constant",
#    value=systematics.getCrossSectionUncertainty("Diboson").getUncertaintyDown()))
Nuisances.append(Nuisance(id="QCDscale_VV", label="diboson cross section scale uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("Diboson_scale").getUncertaintyDown()))
Nuisances.append(Nuisance(id="pdf_VV", label="diboson pdf uncertainty",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("Diboson_pdf").getUncertaintyDown()))


# QCD MC
Nuisances.append(Nuisance(id="xsect_QCD", label="QCD MC cross section",
    distr="lnN", function="Constant",
    value=systematics.getCrossSectionUncertainty("QCD").getUncertaintyDown()))

#===== Luminosity
Nuisances.append(Nuisance(id="lumi_13TeV", label="lumi_13TeVnosity",
    distr="lnN", function="Constant",
    value=systematics.getLuminosityUncertainty("2016")))
Nuisances.append(Nuisance(id="lumi_13TeV_forQCD", label="lumi_13TeVnosity",
    distr="lnN", function="ConstantForQCD",
    value=systematics.getLuminosityUncertainty("2016")))

#===== QCD measurement
if OptionIncludeSystematics:
    Nuisances.append(Nuisance(id="CMS_Hptntj_fake_t_transfer_factors", label="Jet to tau BG transfer factors",
        distr="lnN", function="Constant", value=0.05)) #0.05032 for RtauMore, 0.03857 for RtauLess
    Nuisances.append(Nuisance(id="CMS_Hptntj_fake_t_shape", label="Jet to tau BG mT shape",
        distr="shapeQ", function="QCDShapeVariation", systVariation="QCDNormSource"))

#===== Embedding
if OptionGenuineTauBackgroundSource == "DataDriven":
    Nuisances.append(Nuisance(id="CMS_EmbSingleMu_QCDcontam", label="EWK with taus QCD contamination",
        distr="lnN", function="Constant", value=0.020 #FIXME
    ))
    Nuisances.append(Nuisance(id="CMS_EmbSingleMu_hybridCaloMET", label="EWK with taus hybrid calo MET and L1ETM",
        distr="lnN", function="Constant", value=0.12 #FIXME
    ))
    if "CMS_Hptntj_taubkg_WtauToMu" in myEmbeddingShapeSystematics:
        Nuisances.append(Nuisance(id="CMS_Hptntj_taubkg_WtauToMu", label="EWK with taus W->tau->mu",
            distr="shapeQ", function="ShapeVariation", systVariation="WTauMu", ))
    else:
        Nuisances.append(Nuisance(id="CMS_Hptntj_taubkg_WtauToMu", label="EWK with taus W->tau->mu",
            distr="lnN", function="Constant", value=0.007 ))
    Nuisances.append(Nuisance(id="CMS_Hptntj_taubkg_reweighting", label="Embedding reweighting",
        distr="shapeQ", function="ShapeVariation", systVariation="EmbMTWeight",
    ))

# Print summary table of all defined nuisances!
PrintNuisancesTable(Nuisances, DataGroups)

#================================================================================================ 
# Merge nuisances to same row (first item specifies the name for the row)
# This is for correlated uncertainties. It forces 2 nuisances to be on SAME datacard row
# For examle, ttbar xs scale and singleTop pdf should be varied togethed (up or down) but alwasy in phase
#================================================================================================ 

MergeNuisances=[]

# Merge trigger nuisances into tau/met efficiency
#MergeNuisances.append(["CMS_eff_t","CMS_eff_t_trg_data","CMS_eff_t_trg_MC"]) #FIXME: CMS_eff_t should be shape for this to work, add also high-pT uncertainty
#MergeNuisances.append(["CMS_eff_t_trg_data","CMS_eff_t_trg_MC"]) #FIXME: mergning should add uncerteinties quadratically
#MergeNuisances.append(["CMS_eff_met","CMS_eff_met_trg_MC"]) #FIXME: mergning should add uncerteinties quadratically

# Correlate b tagging and b mistagging
#MergeNuisances.append(["CMS_eff_b","CMS_fake_b"]) #FIXME: mergning should add uncerteinties quadratically

# Correlate ttbar and single top xsect uncertainties
#MergeNuisances.append(["QCDscale_ttbar","QCDscale_singleTop"])
#MergeNuisances.append(["pdf_ttbar","pdf_singleTop"])

# Merge QCDandFakeTau nuisances to corresponding t_genuine nuisances
MergeNuisances.append(["CMS_eff_t","CMS_eff_t_forQCD"])
#MergeNuisances.append(["xsect_ttbar", "xsect_ttbar_forQCD"])
MergeNuisances.append(["QCDscale_ttbar", "QCDscale_ttbar_forQCD"])
MergeNuisances.append(["pdf_ttbar", "pdf_ttbar_forQCD"])
MergeNuisances.append(["CMS_Hptn_mu_RF_top", "CMS_Hptn_mu_RF_top_forQCD"])
MergeNuisances.append(["CMS_Hptn_pdf_top", "CMS_Hptn_pdf_top_forQCD"])
MergeNuisances.append(["mass_top", "mass_top_forQCD","mass_top_forSingleTop"])
MergeNuisances.append(["lumi_13TeV", "lumi_13TeV_forQCD"])

#================================================================================================ 
# Convert shape systematics to constants if needed
#================================================================================================ 

from HiggsAnalysis.LimitCalc.InputClasses import convertFromSystVariationToConstant
convertFromSystVariationToConstant(Nuisances, OptionConvertFromShapeToConstantList)

from HiggsAnalysis.LimitCalc.InputClasses import separateShapeAndNormalizationFromSystVariation
separateShapeAndNormalizationFromSystVariation(Nuisances, OptionSeparateShapeAndNormalizationFromSystVariationList)

#================================================================================================ 
# Control plots
#================================================================================================ 

from HiggsAnalysis.LimitCalc.InputClasses import ControlPlotInput
ControlPlots=[]
#EWKPath="ForDataDrivenCtrlPlotsEWKFakeTaus"
EWKPath="ForDataDrivenCtrlPlotsEWKGenuineTaus"

#NB! Binnings of these control plots are defined in NtupleAnalysis/python/tools/systematics.py: _dataDrivenCtrlPlotBinning

ControlPlots.append(ControlPlotInput(
    title            = "NVertices_AfterStandardSelections",
    histoName        = "NVertices_AfterStandardSelections",
    details          = { "xlabel": "N_{vertices}",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "NE",
                         "ratioLegendPosition": "right",
                         "opts": {"ymin": 0.0009} }
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_pT_AfterStandardSelections",
    histoName        = "SelectedTau_pT_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "legendPosition": "NE",
                         "opts": {"ymin": 0.0009, "ymaxfactor": 25, "xmax": 500} }
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_ldgTrkPt_AfterStandardSelections",
    histoName        = "SelectedTau_ldgTrkPt_AfterStandardSelections",
    details          = { "xlabel": "#tau leading track ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "ratioLegendPosition": "right",
                         "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} }
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_eta_AfterStandardSelections",
    histoName        = "SelectedTau_eta_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau #eta",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.0009} }
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_phi_AfterStandardSelections",
    histoName        = "SelectedTau_phi_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau #phi",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "{}^{o}",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.0009} }
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_Rtau_FullRange_AfterStandardSelections",
    histoName        = "SelectedTau_Rtau_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau ^{}R_{#tau}",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SE",
                         "ratioLegendPosition": "right",
                         "opts": {"ymin": 0.0009,  "xmax": 0.75} },
))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_Rtau_AfterStandardSelections",
    histoName        = "SelectedTau_Rtau_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau ^{}R_{#tau}",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SE",
                         "ratioLegendPosition": "right",
                         "opts": {"ymin": 0.0009,  "xmin": 0.75} },
))
#ControlPlots.append(ControlPlotInput(
#    title            = "SelectedTau_DecayMode_AfterStandardSelections",
#    histoName        = "SelectedTau_DecayMode_AfterStandardSelections",
#    details          = { "xlabel": "Selected #tau Decay mode",
#                         "ylabel": "Events",
#                         "divideByBinWidth": False,
#                         "unit": "",
#                         "log": True,
#                         "ratioLegendPosition": "right",
#                         "opts": {"ymin": 0.9} },
#))
ControlPlots.append(ControlPlotInput(
    title            = "SelectedTau_Nprongs_AfterStandardSelections",
    histoName        = "SelectedTau_Nprongs_AfterStandardSelections",
    details          = { "xlabel": "Selected #tau N_{prongs}",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "ratioLegendPosition": "right",
                         "opts": {"ymin": 0.9} },
))
#ControlPlots.append(ControlPlotInput(
#    title            = "SelectedTau_source_AfterStandardSelections",
#    histoName        = "SelectedTau_source_AfterStandardSelections",
#    details          = { "xlabel": "",
#                         "ylabel": "Events",
#                         "xlabelsize": 10,
#                         "divideByBinWidth": False,
#                         "unit": "",
#                         "log": True,
#                         "ratioLegendPosition": "right",
#                         "opts": {"ymin": 0.9} },
#))
ControlPlots.append(ControlPlotInput(
    title            = "Njets_AfterStandardSelections",
    histoName        = "Njets_AfterStandardSelections",
    details          = { "xlabel": "Number of selected jets",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "opts": {"ymin": 0.9} },
    flowPlotCaption  = "^{}#tau_{h}+#geq3j", # Leave blank if you don't want to include the item to the selection flow plot
))
ControlPlots.append(ControlPlotInput(
    title            = "JetPt_AfterStandardSelections",
    histoName        = "JetPt_AfterStandardSelections",
    details          = { "xlabel": "jet ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} },
))
ControlPlots.append(ControlPlotInput(
    title            = "JetEta_AfterStandardSelections",
    histoName        = "JetEta_AfterStandardSelections",
    details          = { "xlabel": "jet #eta",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.09} },
))
ControlPlots.append(ControlPlotInput(
    title            = "CollinearAngularCutsMinimum",
    histoName        = "CollinearAngularCutsMinimum",
    details          = { "xlabel": "R_{coll}^{min}",
        #"xlabel": "min(#sqrt{#Delta#phi(#tau,MET)^{2}+(180^{o}-#Delta#phi(jet_{1..3},MET))^{2}})",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "{}^{o}",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.09} },
#    flowPlotCaption  = "R_{coll}^{min}", # Leave blank if you don't want to include the item to the selection flow plot
    flowPlotCaption  = "", # Leave blank if you don't want to include the item to the selection flow plot
))
ControlPlots.append(ControlPlotInput(
    title            = "BJetSelection",
    histoName        = "NBjets",
    details          = { "xlabel": "Number of selected b jets",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "opts": {"ymin": 0.09} },
    flowPlotCaption  = "#geq1 b tag", # Leave blank if you don't want to include the item to the selection flow plot
))
ControlPlots.append(ControlPlotInput(
    title            = "BJetPt",
    histoName        = "BJetPt",
    details          = { "xlabel": "b jet ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} },
))
ControlPlots.append(ControlPlotInput(
    title            = "BJetEta",
    histoName        = "BJetEta",
    details          = { "xlabel": "b jet #eta",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.09} },
))
ControlPlots.append(ControlPlotInput(
    title            = "BtagDiscriminator",
    histoName        = "BtagDiscriminator",
    details          = { "xlabel": "b tag discriminator",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "legendPosition": "SE",
                         "opts": {"ymin": 0.9} },
))
ControlPlots.append(ControlPlotInput(
    title            = "MET",
    histoName        = "MET",
    details          = { "xlabel": "E_{T}^{miss}",
                         "ylabel": "Events/^{}#DeltaE_{T}^{miss}",
                         "divideByBinWidth": True,
                         "unit": "GeV",
                         "log": True,
                         "opts": {"ymin": 0.00009, "ymaxfactor": 10, "xmax": 400} },
    flowPlotCaption  = "^{}E_{T}^{miss}", # Leave blank if you don't want to include the item to the selection flow plot
))
ControlPlots.append(ControlPlotInput(
    title            = "METPhi",
    histoName        = "METPhi",
    details          = { "xlabel": "E_{T}^{miss} #phi",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "{}^{o}",
                         "log": True,
                         "legendPosition": "SW",
                         "opts": {"ymin": 0.09} }))
ControlPlots.append(ControlPlotInput(
    title            = "BackToBackAngularCutsMinimum",
    histoName        = "BackToBackAngularCutsMinimum",
    details          = { "xlabel": "^{}R_{bb}^{min}",
    #"xlabel": "min(#sqrt{(180^{o}-#Delta#phi(#tau,MET))^{2}+#Delta#phi(jet_{1..3},MET)^{2}})",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "{}^{o}",
                         "log": True,
                         "legendPosition": "SE",
                         "opts": {"ymin": 0.09} },
    flowPlotCaption  = "^{}R_{bb}^{min}", # Leave blank if you don't want to include the item to the selection flow plot
))

if OptionMassShape =="TransverseMass":
    ControlPlots.append(ControlPlotInput(title="TransverseMass",
        histoName="shapeTransverseMass",
        details={"cmsTextPosition": "right",
            #"xlabel": "m_{T}(^{}#tau_{h},^{}E_{T}^{miss})",
            #"ylabel": "Events/^{}#Deltam_{T}",
            #"unit": "GeV",
            "xlabel": "m_{T} (GeV)",
            "ylabel": "< Events / bin >", "ylabelBinInfo": False,
#            "moveLegend": {"dx": -0.10, "dy": -0.12, "dh":0.1},
#            "ratioMoveLegend": {"dx": -0.06, "dy": -0.33},
            "divideByBinWidth": True,
            "log": False,
            "opts": {"ymin": 0.0, "ymaxfactor": 1.1, "xmax": 500},
            "opts2": {"ymin": 0.0, "ymax": 2.0}
        }, blindedRange=[81, 6000], # specify range min,max if blinding applies to this control plot
        flowPlotCaption="final", # Leave blank if you don't want to include the item to the selection flow plot
    ))
    ControlPlots.append(ControlPlotInput(title="TransverseMassLog",
        histoName="shapeTransverseMass",
        details={"cmsTextPosition": "right",
            #"xlabel": "m_{T}(^{}#tau_{h},^{}E_{T}^{miss})",
            #"ylabel": "Events/^{}#Deltam_{T}",
            #"unit": "GeV",
            "xlabel": "m_{T} (GeV)",
            "ylabel": "< Events / bin >", "ylabelBinInfo": False,
#            "moveLegend": {"dx": -0.10, "dy": -0.12, "dh":0.1},
#            "ratioMoveLegend": {"dx": -0.06, "dy": -0.33},
            "divideByBinWidth": True,
            "log": True,
            "opts": {"ymin": 1e-4, "ymaxfactor": 15, "xmax": 500},
            "opts2": {"ymin": 0.0, "ymax": 2.0}
        }, blindedRange=[81, 6000], # specify range min,max if blinding applies to this control plot
    ))
    ControlPlots.append(ControlPlotInput(title="TransverseMassLogx",
        histoName="shapeTransverseMass",
        details={"cmsTextPosition": "right",
            #"xlabel": "m_{T}(^{}#tau_{h},^{}E_{T}^{miss})",
            #"ylabel": "Events/^{}#Deltam_{T}",
            #"unit": "GeV",
            "xlabel": "m_{T} (GeV)",
            "ylabel": "< Events / bin >", "ylabelBinInfo": False,
#            "moveLegend": {"dx": -0.10, "dy": -0.12, "dh":0.1},
#            "ratioMoveLegend": {"dx": -0.06, "dy": -0.33},
            "divideByBinWidth": True,
            "logx": True,
            "opts": {"ymin": 1e-4,"ymaxfactor": 1.3,"xmax": 5000},
            "opts2": {"ymin": 0.0, "ymax": 2.0}
        }, blindedRange=[81, 6000], # specify range min,max if blinding applies to this control plot
    ))
    ControlPlots.append(ControlPlotInput(title="TransverseMassLogxLog",
        histoName="shapeTransverseMass",
        details={"cmsTextPosition": "right",
            #"xlabel": "m_{T}(^{}#tau_{h},^{}E_{T}^{miss})",
            #"ylabel": "Events/^{}#Deltam_{T}",
            #"unit": "GeV",
            "xlabel": "m_{T} (GeV)",
            "ylabel": "< Events / bin >", "ylabelBinInfo": False,
            "moveLegend": {"dx": -0.10, "dy": -0.12, "dh":0.1},
            "ratioMoveLegend": {"dx": -0.06, "dy": -0.33},
            "divideByBinWidth": True,
            "log": True,
            "logx": True,
            "opts": {"xmin": 9, "ymin": 1e-4,"ymaxfactor": 10.0},
            "opts2": {"ymin": 0.0, "ymax": 2.0}
        }, blindedRange=[81, 6000], # specify range min,max if blinding applies to this control plot
    ))
elif OptionMassShape =="FullMass":
    ControlPlots.append(ControlPlotInput(title="FullMass",
        histoName="shapeInvariantMass",
        details={ "xlabel": "m(^{}#tau_{h},^{}E_{T}^{miss})",
          "ylabel": "Events/#Deltam",
          "divideByBinWidth": True,
          "unit": "GeV",
          "log": False,
          "opts": {"ymin": 0.0},
          "opts2": {"ymin": 0.0, "ymax": 2.0},
        }, blindedRange=[-1, 6000], # specify range min,max if blinding applies to this control plot
        flowPlotCaption="final", # Leave blank if you don't want to include the item to the selection flow plot
    ))

if OptionCtrlPlotsAfterAllSelections:
    ControlPlots.append(ControlPlotInput(title="NVertices_AfterAllSelections",
        histoName="NVertices_AfterAllSelections",
        details={ "xlabel": "N_{vertices}",
          "ylabel": "Events",
          "divideByBinWidth": False,
          "unit": "",
          "log": True,
          "ratioLegendPosition": "right",
          "opts": {"ymin": 0.0009} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_pT_AfterAllSelections",
        histoName="SelectedTau_pT_AfterAllSelections",
        details={ "xlabel": "Selected #tau ^{}p_{T}",
          "ylabel": "Events/^{}#Deltap_{T}",
          "divideByBinWidth": True,
          "unit": "GeV/c",
          "log": True,
          "opts": {"ymin": 0.0009, "ymaxfactor": 15, "xmax": 500} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_ldgTrkPt_AfterAllSelections",
        histoName="SelectedTau_ldgTrkPt_AfterAllSelections",
        details={ "xlabel": "#tau leading track p{}_{T}",
          "ylabel": "Events/^{}#Deltap_{T}",
          "divideByBinWidth": True,
          "unit": "GeV/c",
          "log": True,
          "ratioLegendPosition": "right",
          "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_eta_AfterAllSelections",
        histoName="SelectedTau_eta_AfterAllSelections",
        details={ "xlabel": "Selected #tau #eta",
          "ylabel": "Events",
          "divideByBinWidth": False,
          "unit": "",
          "log": True,
          "legendPosition": "SW",
          "opts": {"ymin": 0.009} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_phi_AfterAllSelections",
        histoName="SelectedTau_phi_AfterAllSelections",
        details={ "xlabel": "Selected #tau #phi",
          "ylabel": "Events",
          "divideByBinWidth": False,
          "unit": "{}^{o}",
          "log": True,
          "legendPosition": "SW",
          "opts": {"ymin": 0.09} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_Rtau_FullRange_AfterAllSelections",
        histoName="SelectedTau_Rtau_AfterAllSelections",
        details={ "xlabel": "Selected #tau R_{#tau}",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "legendPosition": "SW",
        "opts": {"ymin": 0.009}, 
        "opts2": {"ymin": 0.2, "ymax": 1.8} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_Rtau_AfterAllSelections",
        histoName="SelectedTau_Rtau_AfterAllSelections",
        details={ "xlabel": "Selected #tau R_{#tau}",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "legendPosition": "SE",
        "ratioLegendPosition": "right",
        "opts": {"ymin": 0.009, "xmin" : 0.75} }))
#    ControlPlots.append(ControlPlotInput(title="SelectedTau_DecayMode_AfterAllSelections",
#        histoName="SelectedTau_DecayMode_AfterAllSelections",
#        details={ "xlabel": "Selected #tau Decay mode",
#        "ylabel": "Events",
#        "divideByBinWidth": False,
#        "unit": "",
#        "log": True,
#        "ratioLegendPosition": "right",
#        "opts": {"ymin": 0.9} }))
    ControlPlots.append(ControlPlotInput(title="SelectedTau_Nprongs_AfterAllSelections",
        histoName="SelectedTau_Nprongs_AfterAllSelections",
        details={ "xlabel": "Selected #tau N_{prongs}",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "ratioLegendPosition": "right",
        "opts": {"ymin": 0.9} }))
#    ControlPlots.append(ControlPlotInput(title="SelectedTau_source_AfterAllSelections",
#        histoName="SelectedTau_source_AfterAllSelections",
#        details={ "xlabel": "",
#        "ylabel": "Events",
#        "xlabelsize": 10,
#        "divideByBinWidth": False,
#        "unit": "",
#        "log": True,
#        "ratioLegendPosition": "right",
#        "opts": {"ymin": 0.9} }))
    ControlPlots.append(ControlPlotInput(title="Njets_AfterAllSelections",
        histoName="Njets_AfterAllSelections",
        details={ "xlabel": "Number of selected jets",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "opts": {"ymin": 0.9} }))
    ControlPlots.append(ControlPlotInput(title="JetPt_AfterAllSelections",
    histoName="JetPt_AfterAllSelections",
        details={ "xlabel": "jet ^{}p_{T}",
        "ylabel": "Events/^{}Deltap_{T}",
        "divideByBinWidth": True,
        "unit": "GeV/c",
        "log": True,
        "opts": {"ymin": 0.009, "ymaxfactor": 10, "xmax": 500} }))
    ControlPlots.append(ControlPlotInput(title="JetEta_AfterAllSelections",
    histoName="JetEta_AfterAllSelections",
        details={ "xlabel": "jet #eta",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "legendPosition": "SW",
        "opts": {"ymin": 0.09} }))
    ControlPlots.append(ControlPlotInput(title="CollinearAngularCutsMinimum_AfterAllSelections",
        histoName="CollinearAngularCutsMinimum_AfterAllSelections",
        details={ "xlabel": "R_{coll}^{min}", #"xlabel": "min(#sqrt{#Delta#phi(#tau,MET)^{2}+(180^{o}-#Delta#phi(jet_{1..3},MET))^{2}})",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "{}^{o}",
        "log": True,
        "legendPosition": "NE",
        "opts": {"ymin": 0.09} }))
    ControlPlots.append(ControlPlotInput(title="BJetSelection_AfterAllSelections",
        histoName="NBjets_AfterAllSelections",
        details={ "xlabel": "Number of selected b jets",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "opts": {"ymin": 0.09} }))
    ControlPlots.append(ControlPlotInput(title="BJetPt_AfterAllSelections",
        histoName="BJetPt_AfterAllSelections",
        details={ "xlabel": "b jet ^{}p_{T}",
        "ylabel": "Events/^{}#Deltap_{T}",
        "divideByBinWidth": True,
        "unit": "GeV/c",
        "log": True,
        "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} }))
    ControlPlots.append(ControlPlotInput(title="BJetEta_AfterAllSelections",
        histoName="BJetEta_AfterAllSelections",
        details={ "xlabel": "b jet #eta",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "legendPosition": "SW",
        "opts": {"ymin": 0.09} }))
    ControlPlots.append(ControlPlotInput(title="BtagDiscriminator_AfterAllSelections",
        histoName="BtagDiscriminator_AfterAllSelections",
        details={ "xlabel": "b tag discriminator",
        "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "",
        "log": True,
        "legendPosition": "SE",
        "opts": {"ymin": 0.9} }))
    ControlPlots.append(ControlPlotInput(title="MET_AfterAllSelections",
        histoName="MET_AfterAllSelections",
        details={ "xlabel": "E_{T}^{miss}",
        "ylabel": "Events/^{}#DeltaE_{T}^{miss}",
        "divideByBinWidth": True,
        "unit": "GeV",
        "log": True,
        "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} }))
    ControlPlots.append(ControlPlotInput(title="METPhi_AfterAllSelections",
        histoName="METPhi_AfterAllSelections",
        details={ "xlabel": "E_{T}^{miss} #phi",
        "ylabel": "Events/^{}#DeltaE_{T}^{miss}#phi",
        "divideByBinWidth": True,
        "unit": "{}^{o}",
        "log": True,
        "legendPosition": "SW",
        "opts": {"ymin": 0.009} }))
    #for i in range(1,5):    
        #ControlPlots.append(ControlPlotInput(title="AngularCuts2DJet%d_AfterAllSelections"%i,
            #histoName="ImprovedDeltaPhiCuts2DJet%dBackToBack"%i,
            #details={"xlabel": "#Delta#phi(#tau,E_{T}^{miss})",
                #"ylabel": "#Delta#phi(jet_{%d},E_{T}^{miss})"%i,
                #"divideByBinWidth": False,
                #"unit": "{}^{o}",
                #"log": False,
                #"legendPosition": "NE"))
    #ControlPlots.append(ControlPlotInput(title="AngularCuts2DMinimum_AfterAllSelections",
        #histoName="ImprovedDeltaPhiCuts2DMinimum",
        #details={ "xlabel": "#Delta#phi(#tau,E_{T}^{miss})",
            #"ylabel": "#Delta#phi(jet_{1..3},E_{T}^{miss})",
            #"divideByBinWidth": False,
            #"unit": "{}^{o}",
            #"log": False,
            #"legendPosition": "NE",
            #"opts": {"zmin": 0.0} }))
    ControlPlots.append(ControlPlotInput(title="DeltaPhiTauMet_AfterAllSelections",
        histoName="DeltaPhiTauMet_AfterAllSelections",
        details={ "xlabel": "#Delta#phi(#tau,E_{T}^{miss})",
          "ylabel": "Events",
        "divideByBinWidth": False,
        "unit": "{}^{o}",
        "log": True,
        "legendPosition": "NE",
        "opts": {"ymin": 0.9} }))
    #ControlPlots.append(ControlPlotInput(title="MinDeltaPhiTauJet_AfterAllSelections",
        #histoName="MinDeltaPhiTauJet_AfterAllSelections",
        #details={ "xlabel": "min (#Delta#phi(jet_{1..3},E_{T}^{miss}))",
            #"ylabel": "Events",
            #"divideByBinWidth": False,
            #"unit": "{}^{o}",
            #"log": True,
            #"legendPosition": "NE",
            #"opts": {"ymin": 0.9} }))
    #ControlPlots.append(ControlPlotInput(title="MaxDeltaPhiTauJet_AfterAllSelections",
        #histoName="MaxDeltaPhiTauJet_AfterAllSelections",
        #details={ "xlabel": "max (#Delta#phi(jet_{1..3},E_{T}^{miss}))",
            #"ylabel": "Events",
            #"divideByBinWidth": False,
            #"unit": "{}^{o}",
            #"log": True,
            #"legendPosition": "NE",
            #"opts": {"ymin": 0.9} }))
    #ControlPlots.append(ControlPlotInput(title="DeltaPhi_AfterAllSelections",
        #histoName="deltaPhi_AfterAllSelections",
        #details={ "bins": 11,
            #"rangeMin": 0.0,
            #"rangeMax": 180.0,
            #"variableBinSizeLowEdges": [0., 10., 20., 30., 40., 60., 80., 100., 120., 140., 160.], # if an empty list is given, then uniform bin width is used                         #"binLabels": [], # leave empty to disable bin labels                         #"xlabel": "#Delta#phi(#tau_{h},^{}E_{T}^{miss})",
            #"ylabel": "Events",
            #"unit": "^{o}",
            #"log": True,
            #"DeltaRatio": 0.5,
            #"ymin": 0.9,
            #"ymax": -1},
        #blindedRange=[-1, 300], # specify range min,max if blinding applies to this control plot
        #flowPlotCaption="^{}N_{b jets}", # Leave blank if you don't want to include the item to the selection flow plot
        #))
    #ControlPlots.append(ControlPlotInput(title="MaxDeltaPhi",
        #histoName="maxDeltaPhiJetMet",
        #details={ "bins": 18,
            #"rangeMin": 0.0,
            #"rangeMax": 180.0,
            #"variableBinSizeLowEdges": [], # if an empty list is given, then uniform bin width is used                         #"binLabels": [], # leave empty to disable bin labels                         #"xlabel": "max(#Delta#phi(jet,^{}E_{T}^{miss})",
            #"ylabel": "Events",
            #"unit": "^{o}",
            #"log": True,
            #"DeltaRatio": 0.5,
            #"ymin": 0.9,
            #"ymax": -1},
        #blindedRange=[-1, 300], # specify range min,max if blinding applies to this control plot
        #flowPlotCaption="#Delta#phi(^{}#tau_{h},^{}E_{T}^{miss})", # Leave blank if you don't want to include the item to the selection flow plot
        #))
    #ControlPlots.append(ControlPlotInput(title="WMass",
        #histoName="WMass",
        #details={ "bins": 20,
            #"rangeMin": 0.0,
            #"rangeMax": 200.0,
            #"variableBinSizeLowEdges": [], # if an empty list is given, then uniform bin width is used                         #"binLabels": [], # leave empty to disable bin labels                         #"xlabel": "m_{jj}",
            #"ylabel": "Events",
            #"unit": "GeV/c^{2}",
            #"log": True,
            #"DeltaRatio": 0.5,
            #"ymin": 0.9,
            #"ymax": -1},
        #blindedRange=[-1, 400], # specify range min,max if blinding applies to this control plot
        #flowPlotCaption="", # Leave blank if you don't want to include the item to the selection flow plot
        #))
    #ControlPlots.append(ControlPlotInput(title="TopMass",
        #histoName="TopMass",
        #details={ "bins": 20,
            #"rangeMin": 0.0,
            #"rangeMax": 400.0,
            #"variableBinSizeLowEdges": [], # if an empty list is given, then uniform bin width is used                         #"binLabels": [], # leave empty to disable bin labels                         #"xlabel": "m_{bjj}",
            #"ylabel": "Events",
            #"unit": "GeV/c^{2}",
            #"log": True,
            #"DeltaRatio": 0.5,
            #"ymin": 0.9,
            #"ymax": -1},
        #blindedRange=[-1, 400], # specify range min,max if blinding applies to this control plot
        #flowPlotCaption="", # Leave blank if you don't want to include the item to the selection flow plot
        #))
    ControlPlots.append(ControlPlotInput(title="BackToBackAngularCutsMinimum_AfterAllSelections",
        histoName="BackToBackAngularCutsMinimum_AfterAllSelections",
        details={ #"xlabel": "min(#sqrt{(180^{o}-#Delta#phi(#tau,MET))^{2}+#Delta#phi(jet_{1..3},MET)^{2}})",
          "xlabel": "R_{bb}^{min}",
          "ylabel": "Events",
          "divideByBinWidth": False,
          "unit": "^{o}",
          "log": True,
          "legendPosition": "SE",
          "opts": {"ymin": 0.09} }))

# New control plots

ControlPlots.append(ControlPlotInput(
    title            = "Njets_AfterBtagSF",
    histoName        = "Njets_AfterBtagSF",
    details          = { "xlabel": "Number of selected jets",
                         "ylabel": "Events",
                         "divideByBinWidth": False,
                         "unit": "",
                         "log": True,
                         "opts": {"ymin": 0.9} },
))

ControlPlots.append(ControlPlotInput(
    title            = "JetPt_AfterBtagSF",
    histoName        = "JetPt_AfterBtagSF",
    details          = { "xlabel": "jet ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} },
))

ControlPlots.append(ControlPlotInput(
    title            = "BJetPt_AfterBtagSF",
    histoName        = "BJetPt_AfterBtagSF",
    details          = { "xlabel": "b jet ^{}p_{T}",
                         "ylabel": "Events/^{}#Deltap_{T}",
                         "divideByBinWidth": True,
                         "unit": "GeV/c",
                         "log": True,
                         "opts": {"ymin": 0.0009, "ymaxfactor": 10, "xmax": 500} },
))
