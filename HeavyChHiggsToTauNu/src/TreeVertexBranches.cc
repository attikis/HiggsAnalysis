#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TreeVertexBranches.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "TTree.h"

namespace HPlus {
  TreeVertexBranches::TreeVertexBranches(const edm::ParameterSet& iConfig):
    fVertexSrc(iConfig.getParameter<edm::InputTag>("vertexSrc"))
  {}
  TreeVertexBranches::~TreeVertexBranches() {}

  void TreeVertexBranches::book(TTree *tree) {
    tree->Branch("vertexCount", &fVertexCount);
  }
  void TreeVertexBranches::setValues(const edm::Event& iEvent) {
    edm::Handle<edm::View<reco::Vertex> > hvertices;
    iEvent.getByLabel(fVertexSrc, hvertices);

    fVertexCount = hvertices->size();
  }

  void TreeVertexBranches::reset() {
    fVertexCount = std::numeric_limits<unsigned>::max();
  }
}
