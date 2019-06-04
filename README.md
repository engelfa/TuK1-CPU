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

```bash
  mkdir build
  cd build
  cmake ..
  make
```

## Setup PAPI

Use stable 5.7 version since the High Level API somehow changed in 5.7.1.
See: https://bitbucket.org/icl/papi/branches/compare/master%0Dstable-5.7#Lsrc/papi.hF1123

```bash
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

### Troubleshooting

For the [online example](http://icl.cs.utk.edu/projects/papi/wiki/PAPITopics:Getting_Started) using PAPI_flops, I've faced the following error:

```
  PAPI_flops.c    FAILED
  Line # 44
  Error in PAPI_flops: Component containing event is disabled
```

Solution:

```bash
  sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
```

### Run CMAKE with PAPI

```bash
  PAPI=1 cmake ..
  # or:
  export PAPI=1  # $env:PAPI=0 on Windows
```
