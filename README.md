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

Use stable 5.7 version since the High Level API somehow changed in 5.7.1.
See: https://bitbucket.org/icl/papi/branches/compare/master%0Dstable-5.7#Lsrc/papi.hF1123

```
  git clone https://bitbucket.org/icl/papi.git -b stable-5.7
  cd papi/src
  sudo ./configure
  sudo make
  sudo make install
  # If you want to check what functionality works on your system
  make test

  # If you want to remove PAPI
   sudo rm /usr/local/lib/libpapi*
   sudo rm /usr/local/include/*papi*
```

## Run with PAPI

```bash
  PAPI=1 cmake ..
  # or:
  export PAPI=1  # $env:PAPI=0 on Windows
```
