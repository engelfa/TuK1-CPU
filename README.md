# TuK1-CPU

Presentation Slides: https://bit.ly/2MLJlC2

## Benchmark input parameters

| Parameter       | Options | Meaning                                                   | Implemented |
| --------------- | ------- | --------------------------------------------------------- | ----------- |
| result_format   | 0,1,2   | counter, position list, bitmask                           | yes         |
| run_count       | uint_64 | number of column scans to determine average runtime       | yes         |
| random_values   | 0,1     | consecutive values, random                                | yes         |
| column_size     | uint_64 | column size                                               | yes         |
| selectivity     | double  | percentage of entries selected by scan                    | yes         |
| clear_cache     | 0,1     | clear cache after each run                                | yes         |
| cache_size      | uint_64 | size of cache                                             | yes         |
| use_if          | 0,1     | 0 means use logical operation instead of branch           | yes         |
| pcm_set         | uint_64 | usage of performance counter set (0: cache, 1: other)     | yes         |
| search_value    | uint_64 | scan value                                                | no          |
| distinct_values | uint_64 | number of distinct values in uniform distribution         | no          |
| min_range       | uint_64 | min value for search range in column                      | no          |
| max_range       | uint_64 | max value for search range in column                      | no          |

## Benchmark output parameters

| Parameter                  | Meaning                                             | Implemented |
| -------------------------- | --------------------------------------------------- | ----------- |
| result_format              | counter, position list, bitmask                     | yes         |
| run_count                  | number of column scans to determine average runtime | yes         |
| random_values              | consecutive values, random                          | yes         |
| column_size                | column size                                         | yes         |
| selectivity                | percentage of entries selected by scan              | yes         |
| hits                       | matching rows                                       | yes         |
| duration                   | nanoseconds per run                                 | yes         |
| rows_per_sec               | scanned rows per second                             | yes         |
| gb_per_sec                 | data scanned per second (gb)                        | yes         |
| l1_cache_misses            |                                                     | yes         |
| l2_cache_misses            |                                                     | yes         |
| l3_cache_misses            |                                                     | yes         |
| branch_mispredictions      | branch mispredictions                               | yes         |
| stalled_cycles             | CPU cycles stalled on any resource                  | yes         |



## Setup this repo

```bash
  mkdir build
  cd build
  PAPI=1 cmake ..  #  -G "Unix Makefiles" on Windows & Mac
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
