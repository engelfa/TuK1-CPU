#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>
#include <algorithm>

#include "Scan.h"

void print_result(const std::chrono::duration<long long int, std::ratio<1, 1000000000>> duration, size_t output_format, uint64_t counter, ScanConfig scanConfig) {
  std::cout << "output_format,run_count,random_values,search_value,column_size,distinct_values,hits,duration" << std::endl;
  std::cout << output_format << "," << scanConfig.RUN_COUNT << "," << scanConfig.SEARCH_VALUE << "," << scanConfig.COLUMN_SIZE << "," << scanConfig.DISTINCT_VALUES << "," << counter << "," << duration.count()/scanConfig.RUN_COUNT << std::endl;
}

int main(int argc, char *argv[]) {

  if (argc < 7)
  {
    std::cout << "Usage: ./... <output_format> <run_count> <random_values> <search_value> <column_size> <distinct_values>" << std::endl;
    return 1;
  }

  //no search value but range of values or number of distinct values
  ScanConfig scanConfig = ScanConfig(atoi(argv[2]), atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), atoi(argv[6]));
  const size_t OUTPUT_FORMAT = atoi(argv[1]);
  uint64_t counter = 0;

  // Create random generator
  std::random_device rd;
  std::mt19937 e2(rd());
  int min = 0, max = scanConfig.DISTINCT_VALUES - 1;
  std::uniform_int_distribution<int> dist(min,max);

  Scan scan(std::make_shared<ScanConfig>(scanConfig));

  std::cout << "- Initialize input and output vectors" << std::endl;  
  std::vector<uint32_t> input(scanConfig.COLUMN_SIZE), positionList;
  std::vector<char> bitmask(scanConfig.COLUMN_SIZE);
  positionList.reserve(scanConfig.COLUMN_SIZE);

  std::cout << "- Generate column data" << std::endl;
  if (scanConfig.RANDOM_VALUES)
  {
    for (uint64_t i = 0; i < scanConfig.COLUMN_SIZE; ++i) {
      input[i] = dist(e2);
    }
  } else {
    for (uint64_t i = 0; i < scanConfig.DISTINCT_VALUES; ++i)
    {
      for (uint64_t j = 0; j < scanConfig.COLUMN_SIZE; ++j) {
        input[j] = i;
      }
    }
  }

  auto counter_lambda = [&counter] (uint64_t i) {counter++;};
  auto positionList_lambda = [&positionList] (uint64_t i) {positionList.push_back(i);};
  auto bitmask_lambda = [&bitmask] (uint64_t i) {bitmask[i] = '1';};

  // It is also possible to only set an offset and calculate the average hits
  auto counter_before_lambda = [&counter] () {counter = 0;};
  auto positionList_before_lambda = [&positionList] () {positionList.clear();};
  auto bitmask_before_lambda = [&bitmask] () {bitmask.clear();};

  scan.setInput(std::make_shared<std::vector<uint32_t>>(input));

  std::cout << "- Start Benchmark" << std::endl;
  switch(OUTPUT_FORMAT) {
    case 0: {
      const auto before = std::chrono::steady_clock::now();
      scan.execute(counter_lambda, counter_before_lambda);
      const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
          (std::chrono::steady_clock::now() - before);
      print_result(duration, OUTPUT_FORMAT, counter, scanConfig);
      break;
    }
    case 1: {
      const auto before = std::chrono::steady_clock::now();
      scan.execute(positionList_lambda, positionList_before_lambda);
      const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
          (std::chrono::steady_clock::now() - before);
      counter = positionList.size();
      print_result(duration, OUTPUT_FORMAT, counter, scanConfig);
      break;
    }
    case 2: {
      const auto before = std::chrono::steady_clock::now();
      scan.execute(bitmask_lambda, bitmask_before_lambda);
      const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
          (std::chrono::steady_clock::now() - before);
      for (uint64_t i = 0; i < scanConfig.COLUMN_SIZE; ++i) {
        if(bitmask[i] == '1')
          counter++;
      }
      // counter = std::count(bitmask.cbegin(), bitmask.cend(), '1');
      print_result(duration, OUTPUT_FORMAT, counter, scanConfig);
      break;
    }
    default:
      throw std::logic_error("Mode does not exist.");
      break;
  }
  return 0;
}