#include <memory>

#include "ScanConfig.h"
#include "BenchmarkConfig.h"

using INT_COLUMN = uint32_t;

class Scan {
  public:
    Scan(std::shared_ptr<ScanConfig> conf) : config(conf) {}
    ~Scan() = default;

    template<typename T, typename U>
    void execute(uint64_t runs, std::vector<INT_COLUMN>& input_column, T&& in_loop, U&& before_loop) {
      for (size_t run = 0; run < runs; ++run) {
        before_loop();
        for (uint64_t i = 0; i < config->COLUMN_SIZE; ++i) {
          if (input_column[i] == std::numeric_limits<INT_COLUMN>::max()) {
            in_loop(i);
          }
        }
      }
    }

    template<typename T, typename U>
    void execute_without_if(uint64_t runs, T&& in_loop, U&& before_loop) {
      for (size_t run = 0; run < runs; ++run) {
        before_loop();
        for (uint64_t i = 0; i < config->COLUMN_SIZE; ++i) {
            in_loop(i);
        }
      }
    }

  std::shared_ptr<ScanConfig> config;
};
