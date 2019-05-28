#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>
#include <algorithm>

#include "Scan.h"

void print_result(const std::chrono::duration<long long int, std::ratio<1, 1000000000>> duration, const BenchmarkConfig& benchmarkConfig, uint64_t counter, std::shared_ptr<ScanConfig> scanConfig) {
  std::cout << "result_format,run_count,random_values,search_value,column_size,distinct_values,hits,duration" << std::endl;
  std::cout << benchmarkConfig.RESULT_FORMAT << "," << benchmarkConfig.RUN_COUNT << "," << scanConfig->RANDOM_VALUES << "," << scanConfig->SEARCH_VALUE << "," << scanConfig->COLUMN_SIZE << "," << scanConfig->DISTINCT_VALUES << "," << counter << "," << duration.count()/benchmarkConfig.RUN_COUNT << std::endl;
}

int main(int argc, char *argv[]) {

  if (argc < 7)
  {
    std::cout << "Usage: ./... <result_format> <run_count> <random_values> <search_value> <column_size> <distinct_values>" << std::endl;
    std::cout << "For example:  ./tuk_cpu.exe 0 1000 0 5 100000 100" << std::endl;
    return 1;
  }

  // TODO: No search value but range of values or number of distinct values
  // TODO: Combine scans afterwards
  // TODO: Include cache clear
  // TODO: graph -> all output formats in one diagram
  // TODO: graph -> comparison of different runs in one diagram
  // TODO: graph -> normalization rows/s
  BenchmarkConfig benchmarkConfig(atoi(argv[1]), atoi(argv[2]));

  size_t scan_count = 1;
  std::vector<Scan> scans;
  scans.reserve(scan_count);

  for (auto scan = size_t(0); scan < scan_count; ++scan) {
    ScanConfig scanConfig(atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), atoi(argv[6]));

    // Create random generator
    std::random_device rd;
    std::mt19937 e2(rd());
    uint64_t min = 0, max = scanConfig.DISTINCT_VALUES - 1;
    std::uniform_int_distribution<uint64_t> dist(min,max);

    std::cout << "- Initialize Input Vector for Scan " << scan + 1 << std::endl;
    std::vector<uint64_t> input(scanConfig.COLUMN_SIZE);

    std::cout << "- Generate Column Data for Scan " << scan + 1 << std::endl;
    if (scanConfig.RANDOM_VALUES) {
      for (auto i = 0; i < scanConfig.COLUMN_SIZE; ++i) {
        input[i] = dist(e2);
      }
    } else {
      uint64_t ratio = floor(scanConfig.COLUMN_SIZE/scanConfig.DISTINCT_VALUES) < 1 ? 1 : floor(scanConfig.COLUMN_SIZE/scanConfig.DISTINCT_VALUES);
      for (auto i = 0; i < scanConfig.DISTINCT_VALUES; ++i) {
        for (auto j = 0; j < scanConfig.COLUMN_SIZE/scanConfig.DISTINCT_VALUES; ++j) {
          input[(i*ratio)+j] = i;
        }
      }
    }

    scans.push_back(Scan(std::make_shared<ScanConfig>(scanConfig), std::make_shared<std::vector<uint64_t>>(input)));
  }

  std::cout << "- Start Benchmark" << std::endl;
  switch(benchmarkConfig.RESULT_FORMAT) {
    case 0: {
      std::vector<uint64_t> counters(scan_count, 0);

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        auto counter_before_lambda = [&counters, scan] () {counters[scan] = 0;};
        auto counter_lambda = [&counters, scan] (uint64_t i) {counters[scan]++;};

        const auto before = std::chrono::steady_clock::now();
        scans[scan].execute(benchmarkConfig.RUN_COUNT, counter_lambda, counter_before_lambda);
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
          //std::cout << counters[scan] << std::endl;

        print_result(duration, benchmarkConfig, counters[0], scans[scan].config);
      }
      break;
    }
    case 1: {
      std::vector<std::vector<uint64_t>> positionLists(scan_count);

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        // Counter is only last run
        positionLists[scan].reserve(scans[scan].config->COLUMN_SIZE);
        auto positionList_lambda = [&positionLists, scan] (uint64_t i) {positionLists[scan].push_back(i);};
        auto positionList_before_lambda = [&positionLists, scan] () {positionLists[scan].clear();};
        uint64_t counter = 0;

        const auto before = std::chrono::steady_clock::now();
        scans[scan].execute(benchmarkConfig.RUN_COUNT, positionList_lambda, positionList_before_lambda);
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
        counter = positionLists[0].size();
        print_result(duration, benchmarkConfig, counter, scans[scan].config);
      }
      break;
    }
    case 2: {
      std::vector<std::vector<char>> bitmasks(scan_count, std::vector<char>(scans[0].config->COLUMN_SIZE, '0'));
      std::vector<char> result(scans[0].config->COLUMN_SIZE, '1');
      uint64_t counter = 0;

      for (auto scan = size_t(0); scan < scan_count; ++scan) {
        // Counter is only last run
        auto bitmask_lambda = [&bitmasks, scan] (uint64_t i) {bitmasks[scan][i] = '1';};
        auto bitmask_before_lambda = [&bitmasks, scan] () {bitmasks[scan].clear();};

        const auto before = std::chrono::steady_clock::now();
        scans[scan].execute(benchmarkConfig.RUN_COUNT, bitmask_lambda, bitmask_before_lambda);
        const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
            (std::chrono::steady_clock::now() - before);
        for (uint64_t i = 0; i < scans[scan].config->COLUMN_SIZE; ++i) {
          if(bitmasks[scan][i] == '1')
            counter++;
        }
        // counter = std::count(bitmask.cbegin(), bitmask.cend(), '1');
        print_result(duration, benchmarkConfig, counter, scans[scan].config);
      }

      for (auto entry = size_t(0); entry < scans[0].config->COLUMN_SIZE; ++entry) {
        for (auto scan = size_t(0); scan < scan_count; ++scan) {
          if (bitmasks[scan][entry] == '0') {
            result[entry] = '0';
            //std::cout << "result" << result[entry] << std::endl;
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
