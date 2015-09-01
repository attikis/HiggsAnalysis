#ifndef METNoiseFilterDumper_h
#define METNoiseFilterDumper_h

#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/Common/interface/Handle.h"

#include "TTree.h"

#include <vector>
#include <string>

namespace edm {
  class TriggerResults;
}

class METNoiseFilterDumper {
public:
  METNoiseFilterDumper(edm::ConsumesCollector&& iConsumesCollector, const edm::ParameterSet& pset);
  ~METNoiseFilterDumper();

  void book(TTree*);
  bool fill(edm::Event&, const edm::EventSetup&);
  void reset();

private:
  void printAvailableFilters(edm::Event& iEvent, edm::Handle<edm::TriggerResults>& trgResults);
  
  bool filter();
  bool useFilter;
  bool booked;

  TTree* theTree;

  edm::EDGetTokenT<edm::TriggerResults> trgResultsToken;
  
  //const edm::InputTag edm::InputTag triggerObjects;
  //const edm::InputTag edm::InputTag l1extra;
  const bool bPrintTriggerResultsList;
  bool bTriggerResultsListPrintedStatus;
  
  // https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2
  const std::vector<std::string> fFilters;
  // Note: HBHENoiseFilter is run separately as a python fragment
  
  // Data objects for ttree
  bool *bFilters;
};
#endif