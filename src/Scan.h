#include <memory>

template<typename T>
class Scan {
  public:
    Scan();
    ~Scan();
    
    void setInput(std::shared_ptr<std::vector<int>> input_table) {
      _input_table = input_table;
    }

    int execute(T&& strategy) {
      for (uint64_t run = 0; run < RUN_COUNT; ++run) {
        for (uint64_t i = 0; i < COLUMN_SIZE; ++i) {
          if (input[i] == SEARCH_VALUE) {
            strategy();
          }
        }
      }
    }

  private:
    std::shared_ptr<std::vector<int>> _input_table;
};