# TuK1-CPU

## Benchmark parameters

| Parameter       | Options | Meaning                                             | Implemented |
| --------------- | ------- | --------------------------------------------------- | ----------- |
| result_format   | 0,1,2   | counter, position list, bitmask                     | yes         |
| run_count       | uint_64 | number of column scans to determine average runtime | yes         |
| random_values   | 0,1     | consecutive values, random                          | yes         |
| search_value    | uint_64 | scan value                                          | yes         |
| column_size     | uint_64 | column size                                         | yes         |
| distinct_values | uint_64 | number of distinct values in uniform distribution   | yes         |
| min_range       | uint_64 | min value for search range in column                | no          |
| max_range       | uint_64 | max value for search range in column                | no          |
| clear_cache     | 0,1     | clear cache after each run                          | no          |

## Setup this repo

```
  mkdir build
  cd build
  cmake ..
  make
```

## Setup PAPI

```
  git clone https://bitbucket.org/icl/papi
  cd papi/src
  ./configure
  sudo make install
  # If you want to check what functionality works on your system
  make test
```
