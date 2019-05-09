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

// Distribution, Random
  const size_t COUNT_MODE = atoi(argv[1]);
  const uint64_t RUN_COUNT = atoi(argv[2]);
  const uint64_t SEARCH_VALUE = atoi(argv[3]);
  const uint64_t COLUMN_SIZE = atoi(argv[4]);
  const uint64_t DISTINCT_VALUES = atoi(argv[5]);
  std::vector<uint64_t> input(COLUMN_SIZE), output(COLUMN_SIZE);
  uint64_t counter = 0;

  //Scan column_scan = Scan();

  for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
    input[i] = i % DISTINCT_VALUES;
  }

  const auto before = std::chrono::system_clock::now();

  switch(COUNT_MODE) {
    case 0:
      for (uint64_t run = 0; run < RUN_COUNT; ++run) {
        for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
          if (input[i] == SEARCH_VALUE) {
            counter++;
          }
        }
      }
      break;
    case 1:
      for (uint64_t run = 0; run < RUN_COUNT; ++run) {
        for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
          if (input[i] == SEARCH_VALUE) {
            output.push_back(i);
          }
        }
      }
      break;
    default:
      throw std::logic_error("Mode does not exist.");
      break;
  }

  const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now() - before);

  std::cout << "count_mode,run_count,search_value,column_size,distinct_values,duration" << std::endl;
  std::cout << COUNT_MODE << "," << RUN_COUNT << "," << SEARCH_VALUE << "," << COLUMN_SIZE << "," << DISTINCT_VALUES << "," << duration.count()/RUN_COUNT << std::endl;
  return 0;
}