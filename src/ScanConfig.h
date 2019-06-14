// Maybe add id, toString method for easier printing
struct ScanConfig {
  ScanConfig(bool random_values, uint64_t column_size, double selectivity, bool reserve_memory, bool use_if) :
      RANDOM_VALUES(random_values), COLUMN_SIZE(column_size), SELECTIVITY(selectivity),
      RESERVE_MEMORY(reserve_memory), USE_IF(use_if) {}
  const bool RANDOM_VALUES;
  const uint64_t COLUMN_SIZE;
  const double SELECTIVITY;
  const bool RESERVE_MEMORY;
  const bool USE_IF;
};
