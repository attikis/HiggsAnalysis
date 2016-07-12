#include "FWCore/Framework/interface/MakerMacros.h"
#include "CommonTools/UtilAlgos/interface/ObjectSelector.h"
#include "CommonTools/UtilAlgos/interface/SortCollectionSelector.h"
#include "CommonTools/UtilAlgos/interface/SingleObjectSelector.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/PtComparator.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Tau.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

//#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TauIsolationSelectorOld.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TauIsolationSelector.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/FirstObjectSelector.h"
#include "HiggsAnalysis/HeavyChHiggsToTauNu/interface/TriggerMatchSelector.h"

#include<vector>

namespace {
  template <typename T>
  double relIso(const T& obj) {
    return (obj.isolationR03().emEt+obj.isolationR03().hadEt+obj.isolationR03().sumPt)/obj.pt();
  }

  template <typename T>
  struct LessByRelIso {
    typedef T first_argument_type;
    typedef T second_argument_type;
    bool operator()(const T& t1, const T& t2) const {
      return relIso(t1) < relIso(t2);
    }
  };

  template <typename T>
  struct GreaterByRelIso {
    typedef T first_argument_type;
    typedef T second_argument_type;
    bool operator()(const T& t1, const T& t2) const {
      return relIso(t1) > relIso(t2);
    }
  };

  template <typename T>
  struct ViewToVectorAdder {
    void operator()(std::vector<T>& dst, edm::Handle<edm::View<T> >& src, size_t index) {
      dst.push_back(src->at(index));
    }
  };
}


typedef SingleObjectSelector<
  edm::View<pat::Muon>,
  StringCutObjectSelector<pat::Muon>,
  edm::PtrVector<pat::Muon>
  > PATMuonViewPtrSelector;

DEFINE_FWK_MODULE( PATMuonViewPtrSelector );


typedef ObjectSelector<
  SortCollectionSelector<
    std::vector<pat::Muon>,
    LessByRelIso<pat::Muon>
    >
  > HPlusSmallestRelIsoPATMuonSelector;

typedef ObjectSelector<
  SortCollectionSelector<
    edm::View<pat::Muon>,
    LessByRelIso<pat::Muon>,
    std::vector<pat::Muon>
    >,
  std::vector<pat::Muon>
  > HPlusSmallestRelIsoPATMuonViewSelector;

typedef ObjectSelector<
  SortCollectionSelector<
    edm::View<pat::Muon>,
    LessByRelIso<pat::Muon>,
    edm::PtrVector<pat::Muon>
    >,
  edm::PtrVector<pat::Muon>
  > HPlusSmallestRelIsoPATMuonViewPtrSelector;

DEFINE_FWK_MODULE( HPlusSmallestRelIsoPATMuonSelector );
DEFINE_FWK_MODULE( HPlusSmallestRelIsoPATMuonViewSelector );
DEFINE_FWK_MODULE( HPlusSmallestRelIsoPATMuonViewPtrSelector );


typedef ObjectSelector<
  SortCollectionSelector<
    std::vector<pat::Muon>,
    GreaterByPt<pat::Muon>
    >
  > HPlusLargestPtPATMuonSelector;

typedef ObjectSelector<
  SortCollectionSelector<
    edm::View<pat::Muon>,
    GreaterByPt<pat::Muon>,
    std::vector<pat::Muon>
    >,
  std::vector<pat::Muon>
  > HPlusLargestPtPATMuonViewSelector;

typedef ObjectSelector<
  SortCollectionSelector<
    edm::View<pat::Muon>,
    GreaterByPt<pat::Muon>,
    edm::PtrVector<pat::Muon>
    >,
  edm::PtrVector<pat::Muon>
  > HPlusLargestPtPATMuonViewPtrSelector;

typedef ObjectSelector<
  SortCollectionSelector<
    edm::View<reco::Candidate>,
    GreaterByPt<reco::Candidate>,
    edm::PtrVector<reco::Candidate>
    >,
  edm::PtrVector<reco::Candidate>
  > HPlusLargestPtCandViewPtrSelector;

DEFINE_FWK_MODULE( HPlusLargestPtPATMuonSelector );
DEFINE_FWK_MODULE( HPlusLargestPtPATMuonViewSelector );
DEFINE_FWK_MODULE( HPlusLargestPtPATMuonViewPtrSelector );
DEFINE_FWK_MODULE( HPlusLargestPtCandViewPtrSelector );


typedef HPlus::TauIsolationSelector<
  edm::View<reco::Candidate>,
  edm::PtrVector<reco::Candidate>
  > HPlusTauIsolationCandViewPtrSelector;

typedef HPlus::TauIsolationSelector<
  edm::View<pat::Muon>,
  edm::PtrVector<pat::Muon>
  > HPlusTauIsolationPATMuonViewPtrSelector;

typedef HPlus::TauIsolationSelector<
  std::vector<pat::Muon>,
  edm::RefVector<std::vector<pat::Muon> >
  > HPlusTauIsolationPATMuonRefSelector;

DEFINE_FWK_MODULE( HPlusTauIsolationCandViewPtrSelector );
DEFINE_FWK_MODULE( HPlusTauIsolationPATMuonViewPtrSelector );
DEFINE_FWK_MODULE( HPlusTauIsolationPATMuonRefSelector );


typedef HPlus::FirstObjectSelector<reco::Vertex, reco::VertexCollection> HPlusFirstVertexSelector;
typedef HPlus::FirstObjectSelector<reco::Candidate, edm::PtrVector<reco::Candidate> > HPlusFirstCandidateSelector;
typedef HPlus::FirstObjectSelector<reco::GenParticle, reco::GenParticleCollection> HPlusFirstGenParticleSelector;

DEFINE_FWK_MODULE( HPlusFirstVertexSelector );
DEFINE_FWK_MODULE( HPlusFirstCandidateSelector );
DEFINE_FWK_MODULE( HPlusFirstGenParticleSelector );


typedef HPlus::TriggerMatchSelector<
  edm::View<pat::Tau>,
  std::vector<pat::Tau>,
  ViewToVectorAdder<pat::Tau>
  > HPlusTriggerMatchPATTauSelector;

//DEFINE_FWK_MODULE( HPlusTriggerMatchPATTauViewSelector );
