// -*- c++ -*-
#ifndef HiggsAnalysis_HeavyChHiggsToTauNu_EventCounter_h
#define HiggsAnalysis_HeavyChHiggsToTauNu_EventCounter_h

#include <boost/utility.hpp>
#include <utility>
#include <vector>
#include <string>
#include <map>

// Forward declarations
namespace edm {
  class EDProducer;
  class EDFilter;
  class LuminosityBlock;
  class EventSetup;
}

namespace HPlus {
  class Count;

  // Prevent copying
  class EventCounter: private boost::noncopyable {
    struct CountValue {
      CountValue(const std::string& n, const std::string& i, int v, double w);
      bool equalName(std::string n) const;
      template <typename T>
      void produces(T *producer) const;
      void produce(edm::LuminosityBlock *block) const;
      void reset();

      std::string name;
      std::string instance;
      std::string instanceWeights;
      std::string instanceWeightsSquared;
      int value;
      double weight;
      double weightSquared;
    };
    typedef std::vector<CountValue> CountVector;
  public:

    EventCounter();
    ~EventCounter();

    Count addCounter(const std::string& name);
    Count addSubCounter(const std::string& base, const std::string& name);

    void incrementCount(size_t index, int value) {
      counter_[index].value += value;
      counter_[index].weight += *eventWeightPointer;
      counter_[index].weightSquared += *eventWeightPointer * *eventWeightPointer;
    }
    void setWeightPointer(const double* ptr) { eventWeightPointer = ptr; }

    void produces(edm::EDProducer *producer) const;
    void produces(edm::EDFilter *producer) const;

    void beginLuminosityBlock(edm::LuminosityBlock& iBlock, const edm::EventSetup& iSetup);
    void endLuminosityBlock(edm::LuminosityBlock& iBlock, const edm::EventSetup& iSetup) const;

  private:
    template <typename T>
    void producesInternal(T *producer) const;

    CountVector counter_;
    std::map<std::string, uint32_t> counterIndices; // yes, map<string, ...> is BAD for performance,
                                                    // but this is used only at the construction time of the analysis, 
                                                    // so it should be more or less okay
    mutable bool finalized;
    const double* eventWeightPointer;
  };

  class Count {
  public:
    friend class EventCounter;

    // Construction is by the default copy constructor
    ~Count();

    void increment(int value=1) {
      check();
      counter_->incrementCount(index_, value);
    }

  private:
    // No default construction
    Count(); // NOT IMPLEMENTED

    // Prevent construction outside HPlusEventCounter
    Count(EventCounter *counter, size_t index);

    void check() const;

    EventCounter *counter_;
    size_t index_;
  };

  inline
  void increment(Count& count, int value=1) {
    count.increment(value);
  }
}

#endif
