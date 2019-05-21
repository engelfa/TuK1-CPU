// Maybe add id, toString method for easier printing
struct ScanConfig {
  ScanConfig(bool random_values, uint64_t search_value, uint64_t column_size, uint64_t distinct_values) :
      RANDOM_VALUES(random_values), SEARCH_VALUE(search_value),
      COLUMN_SIZE(column_size), DISTINCT_VALUES(distinct_values) {}
  const bool RANDOM_VALUES;
  const uint64_t SEARCH_VALUE;
  const uint64_t MIN_RANGE = 0;
  const uint64_t MAX_RANGE = 0;
  const uint64_t COLUMN_SIZE;
  const uint64_t DISTINCT_VALUES;
};
