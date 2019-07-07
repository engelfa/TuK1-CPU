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
  std::uniform_int_distribution<INT_COLUMN> dist(1,999999);

  std::vector<std::thread> thread_list;
  thread_list.reserve(240);

  std::vector<INT_COLUMN> input(20000000, 0);

  for (size_t i = 0; i < 20000000*0.9; ++i) {
    input[i] = dist(e2);
  }
  for (size_t i = 20000000*0.9; i < 20000000; ++i) {
    input[i] = 1000000;
  }


  // #pragma omp parallel for schedule(static)
  INT_COLUMN* inputs = new INT_COLUMN[224*(uint64_t)20000000];
  for (auto i = 0; i < 224; i += 4) {
    std::shuffle(input.begin(), input.end(), e2);
    for(auto j = 0; j < 20000000; ++j)
      inputs[i*(uint64_t)20000000+j] = input[j];
  }

  uint64_t counters[224] = {};

  for (uint64_t max_cores = 1; max_cores < 224; max_cores += 4) {
    thread_list.clear();
    std::atomic<std::uint64_t> whole{0};
    
    const auto before = std::chrono::steady_clock::now();
    
    for (int core = 0; core < max_cores; ++core) {
      thread_list.push_back(std::thread([&inputs, core, &counters, &whole] () {

        //for (int runs = 0; runs < 50; ++runs) {
          uint64_t counter = 0;
          // #pragma omp parallel for schedule(static)
          for (int line = 0; line < 20000000; ++line) {
            if (inputs[core*20000000+line] == 1000000){
              counter++;
            }
          //}
          counters[core] += counter;
        }

      }));
    }
    
    for (auto& thread : thread_list) {
      thread.join();
    }
    const auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
        (std::chrono::steady_clock::now() - before);

    auto result_time = (duration.count()/(double) 1e9);
    auto gb = ((uint64_t)20000000 * 4) / (double) 1e9;
    std::cout << (max_cores*gb) / result_time << std::endl;
  }
  for(auto counter : counters)
    std::cout << counter << std::endl;
  for (uint64_t max_cores = 1; max_cores < 224; max_cores += 4) {
    std::cout << max_cores << std::endl;
  }
  delete [] inputs;
}