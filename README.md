# TuK1-CPU

## Benchmark parameters

Parameter | Options | Meaning | Implemented
------------ | ------------- | ------------- | -------------
result_format | 0,1,2 | counter, position list, bitmask | yes
run_count | uint_64 | number of column scans to determine average runtime | yes
random_values | 0,1 | consecutive values, random | yes
column_size | uint_64 | column size | yes
selectivity | double | percentage of entries selected by scan | yes
clear_cache | 0,1 | clear cache after each run | yes
