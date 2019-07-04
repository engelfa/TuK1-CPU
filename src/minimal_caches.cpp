#include <chrono>
#include <vector>
#include <random>
#include <iostream>
#include <algorithm>
#include <atomic>

using INT_COLUMN = uint32_t;

int main(int argc, char *argv[]) {

  std::random_device rd;
  std::minstd_rand e2(rd());
  std::uniform_int_distribution<INT_COLUMN> dist(1,19999);

  uint64_t hits = 0;
  uint64_t _SIZE = 10000000;

  for (uint64_t size = 1000; size < _SIZE; size *= 1.2) {

    std::vector<INT_COLUMN> input(size, 0);

    for (size_t i = 0; i < size*0.9; ++i) {
      input[i] = dist(e2);
    }
    for (size_t i = size*0.9; i < size; ++i) {
      input[i] = 20000;
    }
    
    std::shuffle(input.begin(), input.end(), e2);
    
    const auto before = std::chrono::steady_clock::now();

    for (int run = 0; run < ((_SIZE) / size); ++run) {
      
      for (int line = 0; line < size; ++line) {
        if (input[line] == 20000) {
          ++hits;
        }
      }
    }

    const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
                              (std::chrono::steady_clock::now() - before);
    
    auto result_time = duration.count()/(double)(((_SIZE) / size) * 1e9);
    auto gb = (size) / (double) 1e9;
    std::cout << gb / result_time << std::endl;
  }

  std::vector<uint32_t> clear = std::vector<uint32_t>();
  clear.resize(100 * 1000 * 1000, 3);
  for (uint i = 1; i < clear.size(); i+=2) {
      clear[i] += dist(e2);
  }
  clear.resize(0);

  for (uint64_t size = 1000; size < _SIZE; size *=1.2)
    std::cout << size << std::endl;
  std::cout << hits << std::endl;  
}