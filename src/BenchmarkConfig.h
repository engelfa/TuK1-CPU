struct BenchmarkConfig {
  BenchmarkConfig(uint64_t result_format, uint64_t run_count, bool clear_cache, uint64_t cache_size) : 
    RESULT_FORMAT(result_format), RUN_COUNT(run_count), CLEAR_CACHE(clear_cache), CACHE_SIZE(cache_size) {}
  const uint64_t RESULT_FORMAT;
  const uint64_t RUN_COUNT;
  const bool CLEAR_CACHE;
  const uint64_t CACHE_SIZE;
};