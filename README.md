# TuK1-CPU

## Benchmark parameters

Parameter | Options | Meaning | Implemented
------------ | ------------- | ------------- | -------------
result_format | 0,1,2 | counter, position list, bitmask | yes
run_count | uint_64 | number of column scans to determine average runtime | yes
random_values | 0,1 | consequetive values, random | yes
search_value | uint_64 | value that we scan for | yes
column_size | uint_64 | column size | yes
distinct_values | uint_64 | number of distinct values in uniform distribution | yes
min_range | uint_64 | search for range of values in column | no
max_range | uint_64 | search for range of values in column | no
