# TuK1-CPU

## Benchmark parameters

| Parameter       | Options | Meaning                                             | Implemented |
| --------------- | ------- | --------------------------------------------------- | ----------- |
| result_format   | 0,1,2   | counter, position list, bitmask                     | yes         |
| run_count       | uint_64 | number of column scans to determine average runtime | yes         |
| random_values   | 0,1     | consecutive values, random                          | yes         |
| column_size     | uint_64 | column size                                         | yes         |
| selectivity     | double  | percentage of entries selected by scan              | yes         |
| clear_cache     | 0,1     | clear cache after each run                          | yes         |
| search_value    | uint_64 | scan value                                          | no          |
| distinct_values | uint_64 | number of distinct values in uniform distribution   | no          |
| min_range       | uint_64 | min value for search range in column                | no          |
| max_range       | uint_64 | max value for search range in column                | no          |

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

## Run with PAPI

```bash
  PAPI=1 cmake ..
  # or:
  export PAPI=1  # $env:PAPI=0 on Windows
```
