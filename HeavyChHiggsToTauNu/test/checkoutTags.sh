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
# 6.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Another bugfix from Christian for type I/II MEt
# 17.10.2011/M.Kortelainen CMSSW_4_2_8_patch2 Updated PU reweight tag for the updated recipe, lumi tag for minor bugfix (which is probably not relevant to us)
# 29.12.2011/S.Lehti       CMSSW_4_2_8_patch2 Commented removal of HiggsAnalysis/Skimming/python/earlyDataInterestingEvents_cff.py

# addpkg requires cmsenv
eval $(scram runtime -sh)

# PAT
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes42X

# Tau+PAT
# https://hypernews.cern.ch/HyperNews/CMS/get/tauid/83/1/1/1/1.html
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Recommended_tags_for_2011_data_t
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideTauAnalysis#CMSSW_4_1_X_NOTE_Experimental_ve
#
# Tau
addpkg RecoTauTag/Configuration   V01-02-03
addpkg RecoTauTag/RecoTau         V01-02-07
addpkg RecoTauTag/TauTagTools     V01-02-00
# PAT
addpkg DataFormats/PatCandidates  V06-04-19-01
addpkg PhysicsTools/PatAlgos      V08-06-41
addpkg PhysicsTools/PatExamples   V00-05-22
addpkg PhysicsTools/SelectorUtils V00-03-17

# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections
addpkg RecoJets/Configuration     V02-04-17
# https://twiki.cern.ch/twiki/bin/view/CMS/PileupMCReweightingUtilities
addpkg PhysicsTools/Utilities     V08-03-10

# Type I/II MET
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMetAnalysis#HeadingFive
addpkg JetMETCorrections/Type1MET V04-05-04
addpkg PhysicsTools/PatUtils      b4_2_X_cvMEtCorr_06Oct11

addpkg DataFormats/METReco
cvs up -r 1.28 DataFormats/METReco/src/classes.h
cvs up -r 1.25 DataFormats/METReco/src/classes_def.xml

addpkg JetMETCorrections/Algorithms V02-03-00
rm -f JetMETCorrections/Algorithms/interface/L1JPTOffsetCorrector.h
rm -f JetMETCorrections/Algorithms/src/L1JPTOffsetCorrector.cc
addpkg JetMETCorrections/Objects V03-01-00
addpkg JetMETCorrections/Modules
cvs up -r 1.4 JetMETCorrections/Modules/plugins/JetCorrectorOnTheFly.cc
cvs up -r 1.6 JetMETCorrections/Modules/interface/JetCorrectionProducer.h

# Luminosity
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiCalc
addpkg RecoLuminosity/LumiDB      V03-03-02

# Electron ID
# https://twiki.cern.ch/twiki/bin/view/CMS/SimpleCutBasedEleID
#cvs co -r V00-03-01 ElectroWeakAnalysis/WENu

# Higgs skimms
cvs co HiggsAnalysis/Skimming
#rm HiggsAnalysis/Skimming/python/earlyDataInterestingEvents_cff.py
