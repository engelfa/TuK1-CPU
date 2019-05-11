#include <memory>

#include "ScanConfig.h"

class Scan {
  public:
    Scan(std::shared_ptr<ScanConfig> config) : _config(config) {}
    ~Scan() = default;
    
    void setInput(std::shared_ptr<std::vector<uint32_t>> input_column) {
      _input_column = input_column;
    }

    template<typename T, typename U>
    void execute(T&& in_loop, U&& before_loop) {
      if (!_input_column) {
        throw std::logic_error("No input column set.");
      }
      
      for (uint64_t run = 0; run < _config->RUN_COUNT; ++run) {
        before_loop();
        for (uint64_t i = 0; i < _config->COLUMN_SIZE; ++i) {
          if ((*_input_column)[i] == _config->SEARCH_VALUE) {
            in_loop(i);
          }
        }
      }
    }

  private:
    std::shared_ptr<std::vector<uint32_t>> _input_column;
    std::shared_ptr<ScanConfig> _config;
};