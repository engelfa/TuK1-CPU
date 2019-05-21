struct BenchmarkConfig {
  BenchmarkConfig(uint64_t result_format, uint64_t run_count) : RESULT_FORMAT(result_format), RUN_COUNT(run_count) {}
  const uint64_t RESULT_FORMAT;
  const uint64_t RUN_COUNT;
};