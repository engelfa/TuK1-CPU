#include <memory>

#include "HitStrategy.h"

class Scan {
  public:
    Scan();
    ~Scan();
    
    void setInput(std::shared_ptr<std::vector<int>> input_table) {
      _input_table = input_table;
    }

    void setMode(std::shared_ptr<HitStrategy> strategy) {
      _strategy = strategy;
    }

    int execute() {
      if (_strategy)
      {
        *_strategy();
      } else {
        throw std::logic_error("No strategy set.");
      }
    }

  private:
    std::shared_ptr<std::vector<int>> _input_table;
    std::shared_ptr<HitStrategy> _strategy;
};