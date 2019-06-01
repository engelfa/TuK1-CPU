#include <memory>

#include "ScanConfig.h"
#include "BenchmarkConfig.h"

class Scan {
  public:
    Scan(std::shared_ptr<ScanConfig> conf, std::shared_ptr<std::vector<uint64_t>> input) : config(conf), input_column(input) {}
    ~Scan() = default;

    template<typename T, typename U>
    void execute(uint64_t runs, T&& in_loop, U&& before_loop) {
      if (!input_column) {
        throw std::logic_error("No input column set.");
      }

      for (size_t run = 0; run < runs; ++run) {
        before_loop();
        for (uint64_t i = 0; i < config->COLUMN_SIZE; ++i) {
          if ((*input_column)[i] == 0) {
            in_loop(i);
          }
        }
      }
    }

  std::shared_ptr<ScanConfig> config;
  std::shared_ptr<std::vector<uint64_t>> input_column;
};
