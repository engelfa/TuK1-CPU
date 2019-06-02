#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>
#include <algorithm>
#include <bitset>

#include "Scan.h"

enum ResultFormat {
  COUNTER,
  POSITION_LIST,
  VECTOR_CHAR,
  VECTOR_BOOL,
  BITSET
};

void print_result(const uint64_t duration, const BenchmarkConfig& benchmarkConfig, uint64_t counter, std::shared_ptr<ScanConfig> scanConfig) {
  std::cout << "result_format,run_count,random_values,column_size,selectivity,hits,duration,rows_per_sec,gb_per_sec" << std::endl;
  std::cout << benchmarkConfig.RESULT_FORMAT << "," << benchmarkConfig.RUN_COUNT << "," 
    << scanConfig->RANDOM_VALUES << "," << scanConfig->COLUMN_SIZE << "," 
    << scanConfig->SELECTIVITY << "," << counter << "," 
    << duration/benchmarkConfig.RUN_COUNT << "," 
    << scanConfig->COLUMN_SIZE/((duration/(double)1e9)/benchmarkConfig.RUN_COUNT) << "," 
    << (scanConfig->COLUMN_SIZE*8)/((duration/(double)1e9)/benchmarkConfig.RUN_COUNT) << std::endl;
}

uint64_t convert_duration(const BenchmarkConfig& benchmarkConfig, uint64_t duration, uint64_t cache_clear_duration) {
  if (benchmarkConfig.CLEAR_CACHE) {
    return duration - (cache_clear_duration * benchmarkConfig.RUN_COUNT);
  } else {
    return duration;
  }
}

int main(int argc, char *argv[]) {

  if (argc < 6) {
    std::cout << "Usage: ./... <result_format> <run_count> <clear_cache> <random_values> <column_size> <selectivity>" << std::endl;
    std::cout << "For example:  ./tuk_cpu.exe 0 1000 0 0 100000 0.1" << std::endl;
    return 1;
  }

  // Create random generator
  std::random_device rd;
  std::mt19937 e2(rd());
  const size_t bigger_than_cachesize = 10 * 1024 * 1024;
  long p[bigger_than_cachesize] = {0};
  uint64_t cache_clear_duration = 0;
  std::uniform_int_distribution<uint64_t> cacheDist(0,1e12);
  auto clear_cache_lambda = [&cacheDist, &e2, &p, &bigger_than_cachesize] () {
                              for(auto i = 0; i < bigger_than_cachesize; ++i) {
                                p[i] = cacheDist(e2);
                              };
                            };
  auto keep_cache_lambda = [] () {};                          

  // TODO: Multiple scans / Combine scans afterwards
  // TODO: Multicore execution
  // TODO: PMCs => Branch Prediction / Cache Misses

  // TODO: graph -> all output formats in one diagram
  // TODO: graph -> comparison of different runs in one diagram
  // TODO: graph -> multiple scan support > write arguments in file
  BenchmarkConfig benchmarkConfig(atoi(argv[1]), atoi(argv[2]), atoi(argv[3]));

  size_t scan_count = 1;
  std::vector<Scan> scans;
  scans.reserve(scan_count);

  for (auto scan = size_t(0); scan < scan_count; ++scan) {
    ScanConfig scanConfig(atoi(argv[4]), atoi(argv[5]), atof(argv[6]));

    uint64_t min = 1, max = scanConfig.COLUMN_SIZE;
    std::uniform_int_distribution<uint64_t> dist(min,max);

    std::cout << "- Initialize Input Vector for Scan " << scan + 1 << std::endl;
    std::vector<uint64_t> input(scanConfig.COLUMN_SIZE);

    std::cout << "- Generate Column Data for Scan " << scan + 1 << std::endl;
    // Draw {col_size} times from a normal distribution with {distinct_val} steps
    if (scanConfig.RANDOM_VALUES) {
      auto values_for_selectivity = scanConfig.COLUMN_SIZE*scanConfig.SELECTIVITY;

      for (auto i = 0; i < values_for_selectivity; ++i) {
        input[i] = 0;
      }
      for (auto i = values_for_selectivity; i < scanConfig.COLUMN_SIZE; ++i) {
        input[i] = dist(e2);
      }
    // Sequentially insert each value from [0, distinct_val] for
    // {col_size//distinct_val} times. This requires col_size > distinct_val.
    std::shuffle(input.begin(), input.end(), e2);
    } else {
      auto values = floor(1/scanConfig.SELECTIVITY) < 1 ? 1 : floor(1/scanConfig.SELECTIVITY);
      auto value_count = floor(scanConfig.COLUMN_SIZE/values);

      for (auto i = 0; i < values; ++i) {
        for (auto j = 0; j < value_count; ++j) {
          input[(i*value_count)+j] = i;
        }
      }
    }
    scans.push_back(Scan(std::make_shared<ScanConfig>(scanConfig), std::make_shared<std::vector<uint64_t>>(input)));
  }

  if (benchmarkConfig.CLEAR_CACHE) {
    std::cout << "- Determine Cache Clearing Duration" << std::endl;

    const auto before = std::chrono::steady_clock::now();
    for (auto i = 0; i < benchmarkConfig.RUN_COUNT/10; ++i) {
      for(auto i = 0; i < bigger_than_cachesize; ++i) {
         p[i] = cacheDist(e2);
      }
    }
    const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
        (std::chrono::steady_clock::now() - before);
    cache_clear_duration = duration.count() / (benchmarkConfig.RUN_COUNT/10);
  }

  std::cout << "- Start Benchmark" << std::endl;
  switch(benchmarkConfig.RESULT_FORMAT) {
    // Iterate over whole data array and count the occurrences of 0
    case ResultFormat::COUNTER: {
      std::vector<uint64_t> counters(scan_count, 0);

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        
        auto counter_before_lambda = [&counters, scan] () {counters[scan] = 0;};
        auto counter_lambda = [&counters, scan] (uint64_t i) {++counters[scan];};

        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, counter_lambda, counter_before_lambda, clear_cache_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, counter_lambda, counter_before_lambda, keep_cache_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);

        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Return counters for first scan (since there is currently only one scan)
        print_result(converted_duration, benchmarkConfig, counters[0], scans[scan].config);
      }
      break;
    }
    // For each match (with 0), store the index in a indizes list
    case ResultFormat::POSITION_LIST: {
      std::vector<std::vector<uint64_t>> positionLists(scan_count);

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        positionLists[scan].reserve(scans[scan].config->COLUMN_SIZE);
        auto positionList_lambda = [&positionLists, scan] (uint64_t i) {positionLists[scan].push_back(i);};
        auto positionList_before_lambda = [&positionLists, scan] () {positionLists[scan].clear();};
        uint64_t counter = 0;

        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, positionList_lambda, positionList_before_lambda, clear_cache_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, positionList_lambda, positionList_before_lambda, keep_cache_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);

        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Only first scan; counter is from last run only (it's cleared before every run)
        counter = positionLists[0].size();
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config);
      }
      break;
    }
    case ResultFormat::VECTOR_CHAR: {
      std::vector<std::vector<char>> bitmasks(scan_count, std::vector<char>(scans[0].config->COLUMN_SIZE, '0'));
      std::vector<char> result(scans[0].config->COLUMN_SIZE, '1');
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        auto bitmask_lambda = [&bitmasks, scan] (uint64_t i) {bitmasks[scan][i] = '1';};
        auto bitmask_before_lambda = [&bitmasks, scan] () {bitmasks[scan].clear();};

        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, bitmask_lambda, bitmask_before_lambda, clear_cache_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, bitmask_lambda, bitmask_before_lambda, keep_cache_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);

        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Manually count since count(bitmask.begin() ...) did not work.
        // Again only for first scan and last run
        for (uint64_t i = 0; i < scans[scan].config->COLUMN_SIZE; ++i) {
          if(bitmasks[scan][i] == '1')
            counter++;
        }
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config);
      }

      for (auto entry = size_t(0); entry < scans[0].config->COLUMN_SIZE; ++entry) {
        for (auto scan = size_t(0); scan < scan_count; ++scan) {
          if (bitmasks[scan][entry] == '0') {
            result[entry] = '0';
          }
        }
      }
      break;
    }
    case ResultFormat::VECTOR_BOOL: {
      std::vector<std::vector<bool>> bitmasks(scan_count, std::vector<bool>(scans[0].config->COLUMN_SIZE, false));
      std::vector<bool> result(scans[0].config->COLUMN_SIZE, true);
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        // Counter is only last run
        auto bitmask_lambda = [&bitmasks, scan] (uint64_t i) {bitmasks[scan][i] = true;};
        auto bitmask_before_lambda = [&bitmasks, scan] () {bitmasks[scan].clear();};

        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, bitmask_lambda, bitmask_before_lambda, clear_cache_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, bitmask_lambda, bitmask_before_lambda, keep_cache_lambda);          
        } 
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);

        for (uint64_t i = 0; i < scans[scan].config->COLUMN_SIZE; ++i) {
          if(bitmasks[scan][i] == true)
            counter++;
        }

        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // counter = std::count(bitmasks[scan].cbegin(), bitmasks[scan].cend(), true);
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config);
      }

      for (auto entry = size_t(0); entry < scans[0].config->COLUMN_SIZE; ++entry) {
        for (auto scan = size_t(0); scan < scan_count; ++scan) {
          if (bitmasks[scan][entry] == false) {
            result[entry] = false;
          }
        }
      }
      break;
    }
    default:
      throw std::logic_error("Mode does not exist.");
      break;
  }

  return 0;
}
