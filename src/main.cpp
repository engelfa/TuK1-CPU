#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>
#include <algorithm>
#include <bitset>
#include <thread>
#include <limits>

#include "Scan.h"

#define IS_PAPI true

#if IS_PAPI
# include "papi.h"
#endif

enum ResultFormat {
  COUNTER,
  POSITION_LIST,
  VECTOR_CHAR,
  VECTOR_BOOL,
  BITSET
};

void print_result(const uint64_t duration, const BenchmarkConfig& benchmarkConfig, uint64_t counter, const std::shared_ptr<ScanConfig> scanConfig, long long *papi_counts) {
#if !(IS_PAPI)
  std::cout << "- WARNING! PAPI is not available" << std::endl;
#else
  std::cout << "- PAPI is available" << std::endl;
#endif
  std::cout << "- Took " << duration/(double)1e6 << " ms" << std::endl;
  std::cout << "result_format,run_count,clear_cache,cache_size,pcm_set,random_values,column_size,selectivity,"
                  "reserve_memory,use_if,hits,duration,rows_per_sec,gb_per_sec,";
  if (benchmarkConfig.PCM_SET == 1) {
    std::cout << "branch_mispredictions,stalled_cycles,simd_instructions" << std::endl;
  } else {
    std::cout << "l1_cache_misses,l2_cache_misses,l3_cache_misses" << std::endl;
  }

  std::cout << benchmarkConfig.RESULT_FORMAT<< ","
    << benchmarkConfig.RUN_COUNT << ","
    << benchmarkConfig.CLEAR_CACHE << ","
    << benchmarkConfig.CACHE_SIZE << ","
    << benchmarkConfig.PCM_SET << ","
    << scanConfig->RANDOM_VALUES << ","
    << scanConfig->COLUMN_SIZE << ","
    << scanConfig->SELECTIVITY << ","
    << scanConfig->RESERVE_MEMORY << ","
    << scanConfig->USE_IF << ","
    << counter << ","
    << duration/benchmarkConfig.RUN_COUNT << ","
    << scanConfig->COLUMN_SIZE/(duration/(double)(1e9 * (uint64_t)benchmarkConfig.RUN_COUNT)) << ","
    << (scanConfig->COLUMN_SIZE*4/(double)1e9)/(duration/(double)(1e9 * (uint64_t)benchmarkConfig.RUN_COUNT)) << ",";
  if (benchmarkConfig.PCM_SET == 1) {
    std::cout << papi_counts[0] << "," << papi_counts[1] << "," << papi_counts[2] << std::endl;
  } else {
    std::cout << papi_counts[0]/(double)scanConfig->COLUMN_SIZE << "," << papi_counts[1]/(double)scanConfig->COLUMN_SIZE << "," << papi_counts[2]/(double)scanConfig->COLUMN_SIZE << std::endl;
  }

}

uint64_t convert_duration(const BenchmarkConfig& benchmarkConfig, uint64_t duration, uint64_t cache_clear_duration) {
  if (benchmarkConfig.CLEAR_CACHE) {
    return duration;// - (cache_clear_duration * benchmarkConfig.RUN_COUNT);
  } else {
    return duration;
  }
}

void calculate_event_set() {

}

int main(int argc, char *argv[]) {

  if (argc < 11) {
    std::cout << "Usage: ./... <result_format> <run_count> <clear_cache> <cache_size> <pcm_set> <random_values> <column_size> <selectivity> <reserve_memory> <use_if>" << std::endl;
    std::cout << "For example:  ./tuk_cpu 0 1000 0 10 0 0 100000 0.1 0 0" << std::endl;
    return 1;
  }

  BenchmarkConfig benchmarkConfig(atoi(argv[1]), atoi(argv[2]), atoi(argv[3]), atoi(argv[4]), atoi(argv[5]));

  // Create random generator
  std::random_device rd;
  std::minstd_rand e2(rd());

  const auto papi_before = std::chrono::steady_clock::now();
  long long papi_counts[3] = {};
#if IS_PAPI
  auto event_set = PAPI_NULL;

  std::cout << "- Initialize PAPI library" << std::endl;
  PAPI_library_init(PAPI_VER_CURRENT);
  PAPI_create_eventset(&event_set);

  if (benchmarkConfig.PCM_SET == 1) {
    PAPI_add_named_event(event_set,"PAPI_BR_MSP");
    PAPI_add_named_event(event_set,"PAPI_RES_STL");
    PAPI_add_named_event(event_set,"PAPI_VEC_SP");
  } else {
    PAPI_add_named_event(event_set,"PAPI_L1_DCM");
    PAPI_add_named_event(event_set,"PAPI_L2_DCM");
    PAPI_add_named_event(event_set,"PAPI_L3_TCM");
  }
  PAPI_reset(event_set);
#endif

  const auto papi_duration = std::chrono::duration_cast<std::chrono::nanoseconds>
      (std::chrono::steady_clock::now() - papi_before);
  std::cout << "- Took " << papi_duration.count()/(double)1e6 << " ms" << std::endl;

  unsigned available_num_cpus = std::thread::hardware_concurrency();
  std::cout << "- Available CPUs: " << available_num_cpus << std::endl;

  // TODO: Multiple scans / Combine scans afterwards
  // TODO: Multicore execution
  // TODO: Data type as argument (uint64_t, uint32_t, uint16_t)
  // TODO: Input column as parameter for execute function
  // TODO: If or && statement as parameter

  // TODO: graph -> comparison of different runs in one diagram
  // TODO: graph -> multiple scan support > write arguments in file

  const size_t cache_size = benchmarkConfig.CACHE_SIZE * 1024 * 1024;
  std::vector<long> p(cache_size, 3);
  uint64_t cache_clear_duration = 0;
  std::uniform_int_distribution<INT_COLUMN> cacheDist(0,std::numeric_limits<INT_COLUMN>::max() - 19999);
  auto clear_cache_lambda = [&cacheDist, &e2, &p, &cache_size] () {
                                                std::vector<uint32_t> clear = 
                                                          std::vector<uint32_t>(50 * 1000 * 1000, 1000000);
                                                for (uint i = 0; i < clear.size(); ++i) {
                                                    clear[i] += cacheDist(e2);
                                                }
                                                clear.resize(0);
                                              };
  size_t scan_count = 1;
  std::vector<Scan> scans;
  scans.reserve(scan_count);

  //for (auto scan = size_t(0); scan < scan_count; ++scan) {
  auto scan = 0;
  ScanConfig scanConfig(atoi(argv[6]), atoi(argv[7]), atof(argv[8]), atoi(argv[9]), atoi(argv[10]));

  INT_COLUMN min = 0, max = 19999;
  std::uniform_int_distribution<INT_COLUMN> dist(min,max);

  std::cout << "- Initialize Input Vector for Scan " << scan + 1 << std::endl;
  const auto initialize_before = std::chrono::steady_clock::now();
  std::vector<INT_COLUMN> input(scanConfig.COLUMN_SIZE);
  const auto initialize_duration = std::chrono::duration_cast<std::chrono::nanoseconds>
      (std::chrono::steady_clock::now() - initialize_before);
  std::cout << "- Took " << initialize_duration.count()/(double)1e6 << " ms" << std::endl;

  std::cout << "- Generate Column Data for Scan " << scan + 1 << std::endl;
  const auto generate_before = std::chrono::steady_clock::now();
  // Draw {col_size} times from a normal distribution with {distinct_val} steps
  if (scanConfig.RANDOM_VALUES) {
    auto values_for_selectivity = scanConfig.COLUMN_SIZE*scanConfig.SELECTIVITY;

    for (auto i = 0; i < values_for_selectivity; ++i) {
      input[i] = 20000;
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
  const auto generate_duration = std::chrono::duration_cast<std::chrono::nanoseconds>
      (std::chrono::steady_clock::now() - generate_before);
  std::cout << "- Took " << generate_duration.count()/(double)1e6 << " ms" << std::endl;
  scans.push_back(Scan(std::make_shared<ScanConfig>(scanConfig)));
  //}

  // if (benchmarkConfig.CLEAR_CACHE) {
  //   std::cout << "- Determine Cache Clearing Duration" << std::endl;
  //   const auto before = std::chrono::steady_clock::now();
  //   for (auto i = 0; i < benchmarkConfig.RUN_COUNT/10; ++i) {
  //     for(auto i = 0; i < cache_size; ++i) {
  //        p[i] = cacheDist(e2);
  //     }
  //   }
  //   const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
  //       (std::chrono::steady_clock::now() - before);
  //   cache_clear_duration = duration.count() / (benchmarkConfig.RUN_COUNT/10);
  //   std::cout << "- Took " << duration.count()/(double)1e6 << " ms" << std::endl;
  // }

  std::cout << "- Start Benchmark" << std::endl;
  switch(benchmarkConfig.RESULT_FORMAT) {

    // Iterate over whole data array and count the occurrences of 0
    case ResultFormat::COUNTER: {
      //std::vector<uint64_t> counters(scan_count, 0);
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {

        auto counter_before_lambda = [&counter, scan] () {counter = 0;};
        auto counter_lambda = [&counter, scan] (uint64_t i) {++counter;};
#if IS_PAPI
        PAPI_start(event_set);
#endif
        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, counter_lambda, counter_before_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, counter_lambda, counter_before_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
#if IS_PAPI
        PAPI_stop(event_set, papi_counts);
#endif
        clear_cache_lambda();
        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Return counters for first scan (since there is currently only one scan)
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config, papi_counts);
      }
      break;
    }
    // For each match (with 0), store the index in a indizes list
    case ResultFormat::POSITION_LIST: {
      //std::vector<std::vector<uint64_t>> positionLists(scan_count);
      std::vector<uint64_t> positionList;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        if (scans[scan].config->RESERVE_MEMORY) {
          //positionLists[scan].reserve(scans[scan].config->COLUMN_SIZE);
          positionList.reserve(scans[scan].config->COLUMN_SIZE);
        }
        auto positionList_lambda = [&positionList, scan] (uint64_t i) {positionList.push_back(i);};
        auto positionList_before_lambda = [&positionList, scan] () {positionList.clear();};
        uint64_t counter = 0;
#if IS_PAPI
        PAPI_start(event_set);
#endif
        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, positionList_lambda, positionList_before_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, positionList_lambda, positionList_before_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
#if IS_PAPI
        PAPI_stop(event_set, papi_counts);
#endif
        clear_cache_lambda();
        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Only first scan; counter is from last run only (it's cleared before every run)
        counter = positionList.size();
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config, papi_counts);
      }
      break;
    }
    case ResultFormat::VECTOR_CHAR: {
      //std::vector<std::vector<char>> bitmasks(scan_count, std::vector<char>(scans[0].config->COLUMN_SIZE, '0'));
      std::vector<char> bitmask(scans[0].config->COLUMN_SIZE, '0');
      //std::vector<char> result(scans[0].config->COLUMN_SIZE, '1');
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        auto bitmask_lambda = [&bitmask, scan] (uint64_t i) {bitmask[i] = '1';};
        auto bitmask_before_lambda = [&bitmask, scan] () {bitmask.clear();};
#if IS_PAPI
        PAPI_start(event_set);
#endif
        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, bitmask_lambda, bitmask_before_lambda);
        } else {
          scans[scan].execute(benchmarkConfig.RUN_COUNT, input, bitmask_lambda, bitmask_before_lambda);
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
#if IS_PAPI
        PAPI_stop(event_set, papi_counts);
#endif
        clear_cache_lambda();
        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // Manually count since count(bitmask.begin() ...) did not work.
        // Again only for first scan and last run
        for (uint64_t i = 0; i < scans[scan].config->COLUMN_SIZE; ++i) {
          if(bitmask[i] == '1')
            counter++;
        }
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config, papi_counts);
      }

      // for (auto entry = size_t(0); entry < scans[0].config->COLUMN_SIZE; ++entry) {
      //   for (auto scan = size_t(0); scan < scan_count; ++scan) {
      //     if (bitmasks[scan][entry] == '0') {
      //       result[entry] = '0';
      //     }
      //   }
      // }
      break;
    }
    case ResultFormat::VECTOR_BOOL: {
      std::vector<std::vector<bool>> bitmasks(scan_count, std::vector<bool>(scans[0].config->COLUMN_SIZE, false));
      std::vector<bool> bitmask(scans[0].config->COLUMN_SIZE, false);
      //std::vector<bool> result(scans[0].config->COLUMN_SIZE, true);
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        // Counter is only last run
        auto bitmask_lambda = [&bitmask, scan] (uint64_t i) {bitmask[i] = true;};
        auto bitmask_lambda_without_if = [&bitmask, &input, &scan] (uint64_t i) {bitmask[i] = input[i] == 20000;};
        auto bitmask_before_lambda = [&bitmask, scan] () {bitmask.clear();};
#if IS_PAPI
        PAPI_start(event_set);
#endif
        const auto before = std::chrono::steady_clock::now();
        if (benchmarkConfig.CLEAR_CACHE) {
          if (scans[scan].config->USE_IF) {
            scans[scan].execute(benchmarkConfig.RUN_COUNT, input, bitmask_lambda, bitmask_before_lambda);
          } else {
            scans[scan].execute_without_if(benchmarkConfig.RUN_COUNT, bitmask_lambda_without_if, bitmask_before_lambda);
          }
        } else {
          if (scans[scan].config->USE_IF) {
            scans[scan].execute(benchmarkConfig.RUN_COUNT, input, bitmask_lambda, bitmask_before_lambda);
          } else {
            scans[scan].execute_without_if(benchmarkConfig.RUN_COUNT, bitmask_lambda_without_if, bitmask_before_lambda);
          }
        }
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
#if IS_PAPI
        PAPI_stop(event_set, papi_counts);
#endif
        clear_cache_lambda();
        for (uint64_t i = 0; i < scans[scan].config->COLUMN_SIZE; ++i) {
          if(bitmask[i] == true)
            counter++;
        }

        auto converted_duration = convert_duration(benchmarkConfig, duration.count(), cache_clear_duration);

        // counter = std::count(bitmasks[scan].cbegin(), bitmasks[scan].cend(), true);
        print_result(converted_duration, benchmarkConfig, counter, scans[scan].config, papi_counts);
      }

      // for (auto entry = size_t(0); entry < scans[0].config->COLUMN_SIZE; ++entry) {
      //   for (auto scan = size_t(0); scan < scan_count; ++scan) {
      //     if (bitmasks[scan][entry] == false) {
      //       result[entry] = false;
      //     }
      //   }
      // }
      break;
    }
    default:
      throw std::logic_error("Mode does not exist.");
      break;
  }

  return 0;
}
