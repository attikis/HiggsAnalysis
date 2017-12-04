#include "HiggsAnalysis/MiniAOD2TTree/interface/ElectronDumper.h"
#include "HiggsAnalysis/MiniAOD2TTree/interface/MiniIsolation.h"

#include <algorithm>

ElectronDumper::ElectronDumper(edm::ConsumesCollector&& iConsumesCollector, std::vector<edm::ParameterSet>& psets)
: genParticleToken(iConsumesCollector.consumes<reco::GenParticleCollection>(edm::InputTag("prunedGenParticles"))) {
    inputCollections = psets;

    pt  = new std::vector<double>[inputCollections.size()];
    eta = new std::vector<double>[inputCollections.size()];    
    phi = new std::vector<double>[inputCollections.size()];    
    e   = new std::vector<double>[inputCollections.size()];    

    //p4   = new std::vector<reco::Candidate::LorentzVector>[inputCollections.size()];                                                                                                          
    //pdgId = new std::vector<short>[inputCollections.size()];

    relIsoDeltaBetaCorrected = new std::vector<float>[inputCollections.size()];
    effAreaIsoDeltaBetaCorrected = new std::vector<float>[inputCollections.size()];

    MCelectron = new FourVectorDumper[inputCollections.size()];
    
    nDiscriminators = inputCollections[0].getParameter<std::vector<std::string> >("discriminators").size();
    discriminators = new std::vector<bool>[inputCollections.size()*nDiscriminators];
    electronToken = new edm::EDGetTokenT<pat::ElectronCollection>[inputCollections.size()];
    //    electronToken = new edm::EDGetTokenT<edm::View<pat::Electron>>[inputCollections.size()];
    gsfElectronToken = new edm::EDGetTokenT<edm::View<reco::GsfElectron>>[inputCollections.size()];
    rhoToken = new edm::EDGetTokenT<double>[inputCollections.size()];
//    electronIDToken = new edm::EDGetTokenT<edm::ValueMap<bool>>[inputCollections.size()*nDiscriminators];

    // Marina - Start
    pfcandsToken      = new edm::EDGetTokenT<edm::View<pat::PackedCandidate>>[inputCollections.size()];
    relMiniIso        = new std::vector<float>[inputCollections.size()];
    effAreaMiniIso    = new std::vector<float>[inputCollections.size()];
    electronMVAToken  = new edm::EDGetTokenT<edm::ValueMap<float> >[inputCollections.size()];
    electronMVA       = new std::vector<float>[inputCollections.size()];
    rhoMiniIsoToken   = new edm::EDGetTokenT<double>[inputCollections.size()];
    // Marina - End


    for(size_t i = 0; i < inputCollections.size(); ++i){
        edm::InputTag inputtag = inputCollections[i].getParameter<edm::InputTag>("src");
	electronToken[i] = iConsumesCollector.consumes<pat::ElectronCollection>(inputtag);
        //electronToken[i] = iConsumesCollector.consumes<edm::View<pat::Electron>>(inputtag);
        gsfElectronToken[i] = iConsumesCollector.consumes<edm::View<reco::GsfElectron>>(inputtag);
        edm::InputTag rhoSource = inputCollections[i].getParameter<edm::InputTag>("rhoSource");
        rhoToken[i] = iConsumesCollector.consumes<double>(rhoSource);
        //std::string IDprefix = inputCollections[i].getParameter<std::string>("IDprefix");
        std::vector<std::string> discriminatorNames = inputCollections[i].getParameter<std::vector<std::string> >("discriminators");
	/*
        for (size_t j = 0; j < discriminatorNames.size(); ++j) {
            edm::InputTag discrTag(IDprefix, discriminatorNames[j]);
            electronIDToken[i*discriminatorNames.size()+j] = iConsumesCollector.consumes<edm::ValueMap<bool>>(discrTag);
        }
        */
	
	// Marina - Start
	edm::InputTag pfcandinputtag = inputCollections[i].getParameter<edm::InputTag>("pfcands");
	pfcandsToken[i] = iConsumesCollector.consumes<edm::View<pat::PackedCandidate>>(pfcandinputtag);
	
	edm::InputTag rhoSourceMiniIso = inputCollections[i].getParameter<edm::InputTag>("rhoSourceMiniIso");
	rhoMiniIsoToken[i] = iConsumesCollector.consumes<double>(rhoSourceMiniIso);
	
	edm::InputTag electronMVATag = inputCollections[i].getParameter<edm::InputTag>("ElectronMVA");
	electronMVAToken[i] = iConsumesCollector.consumes<edm::ValueMap<float> >(electronMVATag);
	// Marina - end
    }
    
    useFilter = false;
    for(size_t i = 0; i < inputCollections.size(); ++i){
	bool param = inputCollections[i].getUntrackedParameter<bool>("filter",false);
        if(param) useFilter = true;
    }
}
ElectronDumper::~ElectronDumper(){}

void ElectronDumper::book(TTree* tree){
    booked = true;
    for(size_t i = 0; i < inputCollections.size(); ++i){
        std::string name = inputCollections[i].getUntrackedParameter<std::string>("branchname","");
        if(name.length() == 0) name = inputCollections[i].getParameter<edm::InputTag>("src").label();
    
        tree->Branch((name+"_pt").c_str(),&pt[i]);
        tree->Branch((name+"_eta").c_str(),&eta[i]);
        tree->Branch((name+"_phi").c_str(),&phi[i]);
        tree->Branch((name+"_e").c_str(),&e[i]);

        tree->Branch((name+"_relIsoDeltaBeta").c_str(),&relIsoDeltaBetaCorrected[i]);
        tree->Branch((name+"_effAreaIsoDeltaBeta").c_str(),&effAreaIsoDeltaBetaCorrected[i]);

        MCelectron[i].book(tree, name, "MCelectron");
	
	// Marina - start
	tree->Branch((name+"_relMiniIso").c_str(), &relMiniIso[i]);
	tree->Branch((name+"_effAreaMiniIso").c_str(), &effAreaMiniIso[i]);
	tree->Branch((name+"_MVA").c_str(), &electronMVA[i]);
	// Marina - end
	
        std::vector<std::string> discriminatorNames = inputCollections[i].getParameter<std::vector<std::string> >("discriminators");
        for(size_t iDiscr = 0; iDiscr < discriminatorNames.size(); ++iDiscr) {
            // Convert dashes into underscores
            std::replace(discriminatorNames[iDiscr].begin(), discriminatorNames[iDiscr].end(),'-','_');
            tree->Branch((name+"_"+discriminatorNames[iDiscr]).c_str(),&discriminators[inputCollections.size()*iDiscr+i]);
        }
    }
}

bool ElectronDumper::fill(edm::Event& iEvent, const edm::EventSetup& iSetup){
    if (!booked) return true;  
  
    edm::Handle <reco::GenParticleCollection> genParticlesHandle;
    if (!iEvent.isRealData())
      iEvent.getByToken(genParticleToken, genParticlesHandle);
    
    for(size_t ic = 0; ic < inputCollections.size(); ++ic){
        //edm::Handle<edm::View<pat::Electron>> electronHandle;
        edm::Handle<pat::ElectronCollection>  electronHandle;
        iEvent.getByToken(electronToken[ic], electronHandle);
	
	// Marina - start
	edm::Handle<edm::View<pat::PackedCandidate> > pfcandHandle;
        iEvent.getByToken(pfcandsToken[ic], pfcandHandle);
	// Electron MVA
	edm::Handle<edm::ValueMap<float> > electronMVAHandle;
	iEvent.getByToken(electronMVAToken[ic], electronMVAHandle);
	// Marina - end
	
	if(electronHandle.isValid()){
	    // Setup also handle for GsfElectrons (needed for ID)
            edm::Handle<edm::View<reco::GsfElectron>> gsfHandle;
            iEvent.getByToken(gsfElectronToken[ic], gsfHandle);
            // Setup handles for rho
            edm::Handle<double> rhoHandle;
            iEvent.getByToken(rhoToken[ic], rhoHandle);
            double rho = *(rhoHandle.product());
	    
	    // Marina - start
	    edm::Handle<double> rhoMiniIsoHandle;
	    iEvent.getByToken(rhoMiniIsoToken[ic], rhoMiniIsoHandle);
	    //double rhoMiniIso = *(rhoMiniIsoHandle.product());
	    // Marina - end
	    
	    // Setup handles for ID
            std::vector<edm::Handle<edm::ValueMap<bool>>> IDhandles;
            std::vector<std::string> discriminatorNames = inputCollections[ic].getParameter<std::vector<std::string> >("discriminators");
/*
            for (size_t j = 0; j < discriminatorNames.size(); ++j) {
              edm::Handle<edm::ValueMap<bool>> IDhandle;
              iEvent.getByToken(electronIDToken[ic*inputCollections.size()+j], IDhandle);
              IDhandles.push_back(IDhandle);
            }
*/
	    for(size_t i=0; i<electronHandle->size(); ++i) {
    		const pat::Electron& obj = electronHandle->at(i);
		
		// Get Electron Ref
		edm::RefToBase<pat::Electron> ref ( edm::Ref<pat::ElectronCollection >(electronHandle, i));

		pt[ic].push_back(obj.p4().pt());
                eta[ic].push_back(obj.p4().eta());
                phi[ic].push_back(obj.p4().phi());
                e[ic].push_back(obj.p4().energy());

		//p4[ic].push_back(obj.p4());

                // Calculate relative isolation for the electron (delta beta)
                double isolation = obj.pfIsolationVariables().sumChargedHadronPt 
                  + std::max(obj.pfIsolationVariables().sumNeutralHadronEt 
                             + obj.pfIsolationVariables().sumPhotonEt
                             - 0.5 * obj.pfIsolationVariables().sumPUPt, 0.0);
                double relIso = isolation / obj.pt();
                relIsoDeltaBetaCorrected[ic].push_back(relIso);
                
                // Calculate relative isolation with effective area https://indico.cern.ch/event/369239/contributions/874575/attachments/1134761/1623262/talk_effective_areas_25ns.pdf
		double ea = 0.;
		if ( fabs(obj.p4().eta()) < 1.0 ) ea= 0.1752 ;
		else if (fabs(obj.p4().eta()) < 1.479 ) ea = 0.1862 ;
		else if (fabs(obj.p4().eta()) < 2.0 ) ea = 0.1411 ;
		else if (fabs(obj.p4().eta()) < 2.2 ) ea = 0.1534 ;
		else if (fabs(obj.p4().eta()) < 2.3 ) ea = 0.1903 ;
		else if (fabs(obj.p4().eta()) < 2.4 ) ea = 0.2243 ;
		else if (fabs(obj.p4().eta()) < 2.5 ) ea = 0.2687 ;

		double eaisolation = obj.pfIsolationVariables().sumChargedHadronPt 
                  + std::max(obj.pfIsolationVariables().sumNeutralHadronEt
		  + obj.pfIsolationVariables().sumPhotonEt
                  - rho * ea, 0.0);
                double eaIso = eaisolation / obj.pt();
                effAreaIsoDeltaBetaCorrected[ic].push_back(eaIso);
		
		// Marina - start
		relMiniIso[ic].push_back(getMiniIsolation_DeltaBeta(pfcandHandle, dynamic_cast<const reco::Candidate *>(&obj), 0.05, 0.2, 10., false));
		effAreaMiniIso[ic].push_back(getMiniIsolation_EffectiveArea(pfcandHandle, dynamic_cast<const reco::Candidate *>(&obj), 0.05, 0.2, 10., false, false, *rhoMiniIsoHandle));
		// Get electron MVA
		electronMVA[ic].push_back((*electronMVAHandle)[ref]);
		//float mva = (*electronMVAHandle)[ref];
		//std::cout<<"mva = "<<mva<<std::endl;
		// Marina - end
		

		/*                
		for(size_t iDiscr = 0; iDiscr < discriminatorNames.size(); ++iDiscr) {
                  // https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2
                  discriminators[inputCollections.size()*iDiscr+ic].push_back((*(IDhandles[iDiscr]))[gsfHandle->ptrAt(i)]);
		}
                */
                for(size_t iDiscr = 0; iDiscr < discriminatorNames.size(); ++iDiscr) {
                  discriminators[inputCollections.size()*iDiscr+ic].push_back(obj.electronID(discriminatorNames[iDiscr]));
                }
                /*
                const std::vector< std::pair<std::string,float>  > eleIDs = obj.electronIDs();
		for(uint iDiscr = 0; iDiscr < eleIDs.size(); ++iDiscr) {
                  std::cout << "check ele ids " << eleIDs[iDiscr].first << " " << eleIDs[iDiscr].second << std::endl;
                }
                */
		// MC match info
		if (!iEvent.isRealData())
                  fillMCMatchInfo(ic, genParticlesHandle, obj);
            }
        }
    }
    return filter();
}

void ElectronDumper::fillMCMatchInfo(size_t ic, edm::Handle<reco::GenParticleCollection>& genParticles, const pat::Electron& ele) {
  double deltaRBestMatch = 9999.0;
  reco::Candidate::LorentzVector p4BestMatch(0,0,0,0);
  if(genParticles.isValid()){
    for (size_t iMC=0; iMC < genParticles->size(); ++iMC) {
      const reco::Candidate & gp = (*genParticles)[iMC];
      if (abs(gp.pdgId()) != 11) continue;
      reco::Candidate::LorentzVector p4 = gp.p4();
      double DR = deltaR(p4,ele.p4());
      if (DR < 0.1 && DR < deltaRBestMatch) {
        deltaRBestMatch = DR;
        p4BestMatch = p4;
      }
    }
  }
  MCelectron[ic].add(p4BestMatch.pt(), p4BestMatch.eta(), p4BestMatch.phi(), p4BestMatch.energy());
}

void ElectronDumper::reset(){                                                                                                                                           
  if(booked){                                                                                                                                                     
    for(size_t ic = 0; ic < inputCollections.size(); ++ic){                                                                                                       
                                                                                                                                                                  
      pt[ic].clear();                                                                                                                                             
      eta[ic].clear();                                                                                                                                            
      phi[ic].clear();                                                                                                                                            
      e[ic].clear();                                                                                                                                              
                                                                                                                                                                  
      relIsoDeltaBetaCorrected[ic].clear();
      effAreaIsoDeltaBetaCorrected[ic].clear();

      MCelectron[ic].reset();
      
      // Marina - start
      relMiniIso[ic].clear();
      effAreaMiniIso[ic].clear();
      electronMVA[ic].clear();
      // Marina - end
    }                                                                                                                                             
    for(size_t ic = 0; ic < inputCollections.size()*nDiscriminators; ++ic){                                                                                       
      discriminators[ic].clear();                                                                                                                                 
    }                                                                                                                                                            
  }                                                                                                                                                             
}
