#include <vector>
#include <iostream>
#include <numeric>
#include <chrono>
#include <random>
#include <memory>

//#include "Scan.h"

int main(int argc, char *argv[]) {

  if (argc < 5)
  {
    std::cout << "Usage: ./... <run_count> <search_value> <column_size> <distinct_values>" << std::endl;
    return 1;
  }

// Distribution, Random
  // Config enum?
  const bool COUNT_MODE = atoi(argv[1]);
  const uint64_t RUN_COUNT = atoi(argv[2]);
  const uint64_t SEARCH_VALUE = atoi(argv[3]);
  const uint64_t COLUMN_SIZE = atoi(argv[4]);
  const uint64_t DISTINCT_VALUES = atoi(argv[5]);
  std::vector<uint64_t> input(COLUMN_SIZE), output(COLUMN_SIZE);
  uint64_t counter = 0;

  const size_t bigger_than_cachesize = 10 * 1024 * 1024;
  long *p = new long[bigger_than_cachesize];

  for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
    input[i] = i % DISTINCT_VALUES;
  }

  const auto before = std::chrono::system_clock::now();

  if (COUNT_MODE) {
    for (uint64_t run = 0; run < RUN_COUNT; ++run) {
      for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
        if (input[i] == SEARCH_VALUE) {
          counter++;
        }
      }

      for(uint64_t i = 0; i < bigger_than_cachesize; i++) {
         p[i] = rand();
      }
    }

  } else {
    for (uint64_t run = 0; run < RUN_COUNT; ++run) {
      for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
        if (input[i] == SEARCH_VALUE)
        {
          output.push_back(i);
        }
      }

      for(uint64_t i = 0; i < bigger_than_cachesize; i++) {
         p[i] = rand();
      }
    }
  }

  const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now() - before);
  
  std::cout << "run_count,search_value,column_size,distinct_values,duration" << std::endl;
  std::cout << RUN_COUNT << "," << SEARCH_VALUE << "," << COLUMN_SIZE << "," << DISTINCT_VALUES << "," << duration.count()/RUN_COUNT << std::endl;
  return 0;
}