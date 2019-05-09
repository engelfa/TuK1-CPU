#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>

//#include "Scan.h"

int main(int argc, char *argv[]) {

  if (argc < 6)
  {
    std::cout << "Usage: ./... <count_mode> <run_count> <search_value> <column_size> <distinct_values>" << std::endl;
    return 1;
  }

  //no search value but range of values or number of distinct values
  //selectivity as parameter
  //bit mask for output
  const size_t COUNT_MODE = atoi(argv[1]);
  const uint64_t RUN_COUNT = atoi(argv[2]);
  const uint64_t SEARCH_VALUE = atoi(argv[3]);
  const uint64_t COLUMN_SIZE = atoi(argv[4]);
  const uint64_t DISTINCT_VALUES = atoi(argv[5]);

  std::cout << "- Initialize input and output vectors" << std::endl;
  std::vector<uint32_t> input(COLUMN_SIZE), output(COLUMN_SIZE);
  uint64_t counter = 0;

  std::random_device rd;
  std::mt19937 e2(rd());
  int min = 0, max = DISTINCT_VALUES - 1;
  std::uniform_int_distribution<int> dist(min,max);

  //Scan column_scan = Scan();

  std::cout << "- Generate column data" << std::endl;

  for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
    input[i] = dist(e2);
  }

  std::cout << "- Start Benchmark" << std::endl;

  switch(COUNT_MODE) {
    case 0: {
      const auto before = std::chrono::steady_clock::now();
      for (uint64_t run = 0; run < RUN_COUNT; ++run) {
        for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
          if (input[i] == SEARCH_VALUE) {
            counter++;
          }
        }
      }
      const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - before);

      std::cout << "count_mode,run_count,search_value,column_size,distinct_values,hits,duration" << std::endl;
      std::cout << COUNT_MODE << "," << RUN_COUNT << "," << SEARCH_VALUE << "," << COLUMN_SIZE << "," << DISTINCT_VALUES << "," << counter << "," << duration.count()/RUN_COUNT << std::endl;

      break;
    }
    case 1: {
      const auto before = std::chrono::steady_clock::now();
      for (uint64_t run = 0; run < RUN_COUNT; ++run) {
        for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
          output.clear();
          if (input[i] == SEARCH_VALUE) {
            output.push_back(i);
          }
        }
      }
      const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - before);

      std::cout << "count_mode,run_count,search_value,column_size,distinct_values,hits,duration" << std::endl;
      std::cout << COUNT_MODE << "," << RUN_COUNT << "," << SEARCH_VALUE << "," << COLUMN_SIZE << "," << DISTINCT_VALUES << "," << counter << "," << duration.count()/RUN_COUNT << std::endl;

      break;
    }
    default:
      throw std::logic_error("Mode does not exist.");
      break;
  }

  // const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - before);

  // std::cout << "count_mode,run_count,search_value,column_size,distinct_values,duration" << std::endl;
  // std::cout << COUNT_MODE << "," << RUN_COUNT << "," << SEARCH_VALUE << "," << COLUMN_SIZE << "," << DISTINCT_VALUES << "," << duration.count()/RUN_COUNT << std::endl;
  return 0;
}