#include <thread>
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
  std::uniform_int_distribution<INT_COLUMN> dist(1,39999);

  std::vector<std::thread> thread_list;
  thread_list.reserve(80);

  std::vector<INT_COLUMN> input(40000000, 0);

  for (size_t i = 0; i < 40000000*0.9; ++i) {
    input[i] = dist(e2);
  }
  for (size_t i = 40000000*0.9; i < 40000000; ++i) {
    input[i] = 40000;
  }

  std::shuffle(input.begin(), input.end(), e2);

  std::vector<std::vector<INT_COLUMN>> inputs(80);
  for (auto i = 0; i < inputs.size(); ++i) {
    inputs[i] = input;
  }

  for (uint64_t max_cores = 1; max_cores < 81; max_cores += 2) {
    thread_list.clear();
    
    const auto before = std::chrono::steady_clock::now();
    
    for (int core = 0; core < max_cores; ++core) {
      thread_list.push_back(std::thread([&input, core] () {

        for (int run = 0; run < 20; ++run) {
          uint64_t counter = 0;

          for (int line = 0; line < 40000000; ++line) {
            if (input[line] == 40000){
              counter++;
            }
          }
        }

      }));
    }
    
    for (auto& thread : thread_list) {
      thread.join();
    }

    const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
        (std::chrono::steady_clock::now() - before);

    auto result_time = (duration.count()/ (double) max_cores) / 1e9;
    auto gb = (20 * (uint64_t) 40000000 * 4) / (double) 1e9;
    std::cout << gb / result_time << std::endl;
  }
  std::cout << counter << std::endl;
}