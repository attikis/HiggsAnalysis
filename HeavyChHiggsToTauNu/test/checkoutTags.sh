#!/bin/sh

set -e

# Tag list modification history
# 7.7.2010/S.Lehti CMSSW_3_6_3
# 9.8.2010/M.Kortelainen CMSSW_3_7_0_patch_3
# 21.9.2010/S.Lehti CMSSW_3_8_4
# 27.9.2010/M.Kortelainen CMSSW_3_8_4_patch2
# 29.9.2010/S.Lehti CMSSW_3_8_4_patch2 (discriminators moved under RecoTau)
# 15.10.2010/S.Lehti CMSSW_3_8_5 (discriminators moved under RecoTau)
# 19.10.2010/M.Kortelainen CMSSW_3_8_5 (lumi tag update)
# 21.10.2010/M.Kortelainen CMSSW_3_8_5_patch2 (Updated PatAlgos tag, added revision numbers for files)
# 28.10.2010/M.Kortelainen CMSSW_3_8_5_patch3 (Electron ID and additional PAT tags from the release notes)
# 2.11.2010/M.Kortelainen CMSSW_3_8_5_patch3 (tag for filterJSON.py etc. scripts) 
# 11.11.2010/M.Kortelainen CMSSW_3_8_6 Moved the tau embedding tag here since it is needed for compilation
# 12.11.2010/M.Kortelainen CMSSW_3_8_6 Removed the tau embedding tag (added workaround)
# 9.12.2010/M.Kortelainen CMSSW_3_8_7 Updated PAT tags to latest recipe, updated lumi tag
# 27.12.2010/M.Kortelainen CMSSW_3_9_7 Updated tags to latest recipes
# 12.1.2011/M.Kortelainen CMSSW_3_9_7 Added HPS+TaNC tags
# 18.1.2011/M.Kortelainen CMSSW_3_9_7 Update PFRecoTauDiscriminationByInvMass.cc
# 19.1.2011/M.Kortelainen CMSSW_3_9_7 Updated the tau tags
# 16.2.2011/M.Kortelainen CMSSW_3_9_7 Mechanism to not to take HPS+TaNC tags
# 17.2.2011/M.Kortelainen CMSSW_3_9_7 Updated lumi tag 
# 24.2.2011/M.Kortelainen CMSSW_3_11_1_patch2 Taking into account what is included in the release
# 17.3.2011/M.Kortelainen CMSSW_3_9_7 Suffering from HiggsAnalysis/Skimming being checked out without a tag...
# 18.3.2011/M.Kortelainen CMSSW_3_9_9_patch1 Updated PAT tags for trigger
# 21.3.2011/M.Kortelainen CMSSW_4_1_3 Still suffering from HiggsAnalysis/Skimming...
# 21.3.2011/M.Kortelainen CMSSW_3_9_9_patch1 Updated pfTools.py
# 23.3.2011/M.Kortelainen CMSSW_4_1_3 Updated PAT tags for the latest recipe for 41X, removed HPS+TaNC tags as it is in AOD
# 23.3.2011/M.Kortelainen CMSSW_4_1_3 Updated PAT tags
# 24.3.2011/M.Kortelainen CMSSW_4_1_3_patch2 Updated PAT tags
# 1.4.2011/M.Kortelainen CMSSW_4_1_3_patch3 Updated tau and PAT tags to the latest recipe for 41X
# 4.4.2011/M.Kortelainen CMSSW_4_1_4 Updated tags for the new release, 
# 27.4.2011/M.Kortelainen CMSSW_4_1_4 Updated tau tags for the latest recipe for 41X
# 28.4.2011/M.Kortelainen CMSSW_4_1_5 Updated PAT tags for the latest recipe from Michal Bluj
# 3.5.2011/M.Kortelainen CMSSW_4_1_5 Minor tau tag update thanks to Mike Bachtis
# 4.5.2011/M.Kortelainen CMSSW_4_1_5 Checkout JEC sqlite file
# 4.5.2011/M.Kortelainen CMSSW_4_1_5 Updated tau tags
# 9.5.2011/M.Kortelainen CMSSW_4_2_2 Updated tags for the new release
# 23.5.2011/M.Kortelainen CMSSW_4_2_3_patch2 Updated tau and PAT tags
# 25.5.2011/M.Kortelainen CMSSW_4_2_3_patch2 Updated tau and PAT tags
# 27.5.2011/M.Kortelainen CMSSW_4_2_3_patch2 Updated tau and PAT tags
# 31.5.2011/M.Kortelainen CMSSW_4_2_3_patch2 Updated PAT tags
# 10.6.2011/M.Kortelainen CMSSW_4_2_4_patch1 
# 22.6.2011/M.Kortelainen CMSSW_4_2_5 Updated tau and PAT tags
# 25.6.2011/M.Kortelainen CMSSW_4_2_5 Updated tau tags
# 28.6.2011/M.Kortelainen CMSSW_4_2_5 Updated tau and PAT tags
# 1.7.2011/M.Kortelainen CMSSW_4_2_5 Updated PAT tags
# 4.7.2011/M.Kortelainen CMSSW_4_2_5 Reverted PAT tags (I accidentally launched the pattuple_v16 with an old version)
# 6.7.2011/M.Kortelainen CMSSW_4_2_5 Updated PAT tags back
# 12.8.2011/M.Kortelainen CMSSW_4_2_8_patch1 Updated PAT tags
# 28.9.2011/M.Kortelainen CMSSW_4_2_8_patch2 Added tags for calculating type I/II MET from PAT objects
# 3.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Bugfix from Christian for type I/II MET
# 5.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Updated LumiDB tag (bugfix)
# 6.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Another bugfix from Christian for type I/II MET
# 14.10.2011/M.Kortelainen CMSSW_4_2_8_patch6 Updated PAT tags
# 17.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Updated PU reweight tag for the updated recipe, lumi tag for minor bugfix (which is probably not relevant to us)
# 17.10.2011/M.Kortelainen CMSSW_4_2_8_patch6 Updated type I/II MET tags
# 21.12.2011/M.Kortelainen CMSSW_4_2_8_patch7 Updated PAT, tau and lumi tags
# 29.12.2011/S.Lehti       CMSSW_4_2_8_patch2 Commented removal of HiggsAnalysis/Skimming/python/earlyDataInterestingEvents_cff.py
# 16.1.2012/S.Lehti        CMSSW_4_4_2_patch9 Updated tags to 44x
# 19.1.2012/M.Kortelainen CMSSW_4_4_2_patch9 Updated PAT and tau tags
# 20.1.2012/M.Kortelainen CMSSW_4_4_2_patch10 Updated and fixed PAT tags
# 13.3.2012/M.Kortelainen CMSSW_4_4_4 Updated PAT, tau and lumi tags
# 16.3.2012/S.Lehti        CMSSW_4_2_8 Added tag for btagging scale factors
# 19.3.2012/M.Kortelainen CMSSW_4_2_8_patch2 Updated lumi tag to include the pixel lumi
# 28.3.2012/S.Lehti       CMSSW_4_4_4 Moved master to 444/ 444 tags
# 13.9.2012/M.Kortelainen CMSSW_4_4_4 Updated PAT and tau tags
# 17.9.2012/M.Kortelainen CMSSW_4_4_4 Cut-based electron ID tag
# 17.9.2012/S.Lehti       CMSSW_5_3_3 Update for 53X
# 12.10.2012/M.Kortelainen CMSSW_5_3_5 Updated PAT tags
# 25.10.2012/M.Kortelainen CMSSW_5_3_5 Updated for running runMEtUncertainties() multiple times
# 26.10.2012/M.Kortelainen CMSSW_5_3_5 Updated metUncertaintyTools

# addpkg requires cmsenv
eval $(scram runtime -sh)

# PAT
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X
addpkg DataFormats/PatCandidates V06-05-06-02
addpkg PhysicsTools/PatAlgos     V08-09-42
# We don't need the code (it's the same as in the release), but a ROOT
# file for jet smearing needs to be in the developer area at the moment
# (see )
addpkg PhysicsTools/PatUtils V03-09-27
# Needed for running runMEtUncertainties() multiple times, no tag yet
cvs up -r 1.25 PhysicsTools/PatUtils/python/tools/metUncertaintyTools.py
cvs up -r 1.19.8.1 PhysicsTools/PatAlgos/python/tools/helpers.py
rm PhysicsTools/PatUtils/plugins/MinPatMETProducer.cc

# Tau+PAT
# https://hypernews.cern.ch/HyperNews/CMS/get/tauid/252.html
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#2012_CMSSW_4_X_X_Recipe
#
# Tau
addpkg RecoTauTag/RecoTau         V01-04-17 #equivalent to 04-14
addpkg RecoTauTag/Configuration   V01-04-03
addpkg CondFormats/EgammaObjects  V00-04-01
addpkg PhysicsTools/IsolationAlgos # You need to recompile PAT packages which depend on DataFormats/TauReco
# PAT
##### New tau discriminators, electron MVA discriminator
cvs up -r 1.57 PhysicsTools/PatAlgos/python/tools/tauTools.py
cvs up -r 1.13 PhysicsTools/PatAlgos/python/producersLayer1/tauProducer_cff.py
cvs up -r 1.15 PhysicsTools/PatAlgos/python/recoLayer0/tauDiscriminators_cff.py
cvs up -r 1.5 RecoTauTag/Configuration/python/updateHPSPFTaus_cff.py

# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections
# https://twiki.cern.ch/twiki/bin/view/CMS/PileupMCReweightingUtilities


# btagging scale factors
# https://twiki.cern.ch/twiki/bin/view/CMS/BtagPerformanceDBV2
cvs co -r V00-04-11 RecoBTag/PerformanceDB

# Type I/II MET
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMetAnalysis#HeadingFive
# Nothing to add on 535, but let's keep the reference

# Luminosity
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiCalc
addpkg RecoLuminosity/LumiDB V04-01-09

# Electron ID
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaCutBasedIdentification
# https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentification
#
# Now, this is a bit complex. The recommended tag for MVA ID (which is
# produced in pattuple jobs) is V00-00-16 in the twiki abobe. However,
# the recommended tag for the cut-based ID is CutBasedId_V00-00-05.
# There seem to be non-trivial differences for the MVA-side between
# the tags (cut-based is newer), so we do the following
#
# 1. Check out the full package with the MVA tag
# 2. Check out classes needed for the cut-based id with the cut-based tag
cvs co -r V00-00-16 -d EGamma/EGammaAnalysisTools UserCode/EGamma/EGammaAnalysisTools
cvs up -r CutBasedId_V00-00-05 EGamma/EGammaAnalysisTools/src/EGammaCutBasedEleId.cc
cvs up -r CutBasedId_V00-00-05 EGamma/EGammaAnalysisTools/interface/EGammaCutBasedEleId.h

# This gives the updated EA isolation from recommendation of
# https://hypernews.cern.ch/HyperNews/CMS/get/higgs/1032.html
cvs up -r V00-00-31 EGamma/EGammaAnalysisTools/interface/ElectronEffectiveArea.h
# Patch ElectronEffectiveArea::kEleEAData2011 to ElectronEffectiveArea::kEleEAData2012
sed -i 's/2011/2012/g' EGamma/EGammaAnalysisTools/src/EGammaCutBasedEleId.cc

# EGammaCutBasedEleId.cc includes ElectronEffectiveArea.h, but the
# version is the same in both tags
#
# Get rid of compilation error with the following command
rm EGamma/EGammaAnalysisTools/test/ElectronIsoAnalyzer.cc 

# Higgs skimms
cvs co HiggsAnalysis/Skimming
