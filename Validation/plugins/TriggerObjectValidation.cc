#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/Common/interface/Handle.h"

#include "DQMServices/Core/interface/DQMStore.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "DQMServices/Core/interface/MonitorElement.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"

#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "DataFormats/HLTReco/interface/TriggerObject.h"

#include <iostream>
using namespace std;

class TriggerObjectValidation : public edm::EDAnalyzer {
    public:
	TriggerObjectValidation(const edm::ParameterSet&);
	~TriggerObjectValidation();

	void beginRun(const edm::Run&,const edm::EventSetup&);
	void beginJob();
	void analyze( const edm::Event&, const edm::EventSetup&);
	void endJob();
	void endRun(const edm::Run&,const edm::EventSetup&);

    private:
	edm::InputTag triggerResults;
	std::string triggerBit;
	edm::InputTag triggerObjects;
	int triggerObjectId;

	edm::InputTag hltPathFilter;

  	DQMStore *dbe;

        MonitorElement *nEvt;
  	MonitorElement *Pt, *Eta, *Phi;
	MonitorElement *EtaPhi;
//	MonitorElement *Z;
//	MonitorElement *EtaZ;
};

TriggerObjectValidation::TriggerObjectValidation(const edm::ParameterSet& iConfig):
    triggerResults(iConfig.getParameter<edm::InputTag>("triggerResults")),
    triggerBit(iConfig.getParameter<std::string>("triggerBit")),
    triggerObjects(iConfig.getParameter<edm::InputTag>("triggerObjects")),
    triggerObjectId(iConfig.getParameter<int>("triggerObjectId")),
    hltPathFilter(iConfig.getParameter<edm::InputTag>("hltPathFilter"))
{
  dbe = 0;
  dbe = edm::Service<DQMStore>().operator->();
}

TriggerObjectValidation::~TriggerObjectValidation() {}

void TriggerObjectValidation::beginJob(){}

void TriggerObjectValidation::beginRun(const edm::Run& iRun,const edm::EventSetup& iSetup){
  if(dbe){
    ///Setting the DQM top directories
    dbe->setCurrentFolder("Validation/TriggerObjects");

    // Number of analyzed events
    nEvt    = dbe->book1D("nEvt "+hltPathFilter.label()+" "+triggerBit, "n analyzed Events", 2, 0., 2.);

    //Kinematics
    Pt          = dbe->book1D("Pt "+hltPathFilter.label()+" "+triggerBit,"pT", 100 ,0,100);
    Eta         = dbe->book1D("Eta "+hltPathFilter.label()+" "+triggerBit,"eta", 100 ,-2.5,2.5);
    Phi		= dbe->book1D("Phi "+hltPathFilter.label()+" "+triggerBit,"phi", 100 ,-3.14,3.14);

    EtaPhi	= dbe->book2D("Eta Phi "+hltPathFilter.label()+" "+triggerBit,"eta phi", 100 ,-2.5,2.5, 100 ,-3.14,3.14);

//    Z		= dbe->book1D("Vertex Z "+hltPathFilter.label()+" "+triggerBit,"vertex Z", 100 ,-25.,25.);
//    EtaZ	= dbe->book2D("Eta Z "+hltPathFilter.label()+" "+triggerBit,"eta Z", 100 ,-2.5,2.5, 100 ,-25.,25.);

    std::cout << "Trigger bit: " << triggerBit << std::endl;
    std::cout << "Trigger path: " << hltPathFilter.label() << std::endl;
  }
}
void TriggerObjectValidation::endRun(const edm::Run& iRun,const edm::EventSetup& iSetup){}

void TriggerObjectValidation::analyze( const edm::Event& iEvent, const edm::EventSetup& iSetup){

    nEvt->Fill(0.5);

    edm::Handle<edm::TriggerResults> hltHandle;
    if(triggerBit != ""){
      iEvent.getByLabel(triggerResults,hltHandle);

      bool passedTrigger = false;

      const edm::TriggerNames & triggerNames = iEvent.triggerNames(*hltHandle);
      for (unsigned int i=0; i<triggerNames.size(); i++) {
	//std::cout << "trigger path= " << triggerNames.triggerName(i) << std::endl;
	if(triggerBit == triggerNames.triggerName(i) && hltHandle->accept(i)){
		passedTrigger = true;
		i = triggerNames.size();
	}
      }

      if(!passedTrigger) return;
    }

    nEvt->Fill(1.5);

    edm::Handle<trigger::TriggerEvent> triggerObjs;
    if(iEvent.getByLabel(triggerObjects,triggerObjs)){
        const trigger::TriggerObjectCollection objs(triggerObjs->getObjects());

	size_t index = triggerObjs->filterIndex(hltPathFilter);

	if(index < triggerObjs->sizeFilters()){
	  const trigger::Keys& KEYS(triggerObjs->filterKeys(index));

	  for(size_t i = 0;i<KEYS.size();++i){
		const trigger::TriggerObject& TO(objs[KEYS[i]]);
//                if(TO.id() != triggerObjectId) continue;

                Pt->Fill(TO.pt());
		Eta->Fill(TO.eta());
		Phi->Fill(TO.phi());

		EtaPhi->Fill(TO.eta(),TO.phi());
	  }
	}else{
	  if(triggerBit != ""){
	    std::cout << "hltPathFilter " << hltPathFilter.encode() << std::endl;
	    for(size_t i = 0; i < triggerObjs->sizeFilters(); ++i){
	    	std::cout << "    tag " << triggerObjs->filterTag(i).encode() << std::endl;
	    }
	  }
	}
    }
}

void TriggerObjectValidation::endJob(){}

DEFINE_FWK_MODULE(TriggerObjectValidation);
