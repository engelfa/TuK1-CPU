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
  std::uniform_int_distribution<INT_COLUMN> dist(1,19999);

  std::vector<std::thread> thread_list;
  thread_list.reserve(80);

  std::vector<INT_COLUMN> input(200000000, 0);

  for (size_t i = 0; i < 200000000*0.9; ++i) {
    input[i] = dist(e2);
  }
  for (size_t i = 200000000*0.9; i < 200000000; ++i) {
    input[i] = 20000;
  }

  std::shuffle(input.begin(), input.end(), e2);

  std::vector<std::vector<INT_COLUMN>> inputs(80);
  for (auto i = 0; i < inputs.size(); ++i) {
    inputs[i] = input;
  }

  uint64_t counters[80] = {};

  for (uint64_t max_cores = 1; max_cores < 80; max_cores += 2) {
    thread_list.clear();
    std::atomic<std::uint64_t> whole{0};
    
    const auto before = std::chrono::steady_clock::now();
    
    for (int core = 0; core < max_cores; ++core) {
      thread_list.push_back(std::thread([&inputs, core, &counters, &whole] () {

        for (int runs = 0; runs < 20; ++runs) {
          uint64_t counter = 0;
          for (int line = 0; line < 200000000; ++line) {
            if (inputs[core][line] == 20000){
              counter++;
            }
          }
          counters[core] += counter;
        }

      }));
      cpu_set_t cpuset;
      CPU_ZERO(&cpuset);
      CPU_SET(core, &cpuset);
      int rc = pthread_setaffinity_np(thread_list[core].native_handle(),
                                      sizeof(cpu_set_t), &cpuset);
    }
    
    for (auto& thread : thread_list) {
      thread.join();
    }
    const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
        (std::chrono::steady_clock::now() - before);

    auto result_time = (duration.count() / (double) (1e9));
    auto gb = (20 * (uint64_t)200000000 * 4) / (double) 1e9;
    std::cout << (gb / result_time) * max_cores << std::endl;
    
    //std::cout << "seconds per run per core" << result_time << std::endl;
    //std::cout << "GB " << gb*max_cores << std::endl;
  }
  std::cout << counters << std::endl;
}