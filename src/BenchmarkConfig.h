struct BenchmarkConfig {
  BenchmarkConfig(uint64_t output_format, uint64_t run_count) : OUTPUT_FORMAT(output_format), RUN_COUNT(run_count) {}
  const uint64_t OUTPUT_FORMAT;
  const uint64_t RUN_COUNT;
};