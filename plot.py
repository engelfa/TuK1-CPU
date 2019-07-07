import sys

from utils.execution import set_default_parameters, generate_data
from utils.viz import generate_plots
from utils.storage import store_results, load_results

# If False execute one dummy benchmark
TEST = False

"""
    Parameters For Python Execution:
    - n_cores: Across how many cores are the jobs distributed
    - jobs_per_core: How many are simultaneously dispatched for one core.
      If equals -1, dispatch all process immediately.
      --> n_cores * jobs_per_core python subprocesses are dispatched at a time

    If n_cores and jobs_per_core are defined as parameter of generate_data,
    each core is executing jobs_per_core runs. For each setting of n_cores the
    same execution will then be triggered multiple times.
"""


def execute():
    if TEST:
        execute_test_run()
    else:
        if "--plot" in sys.argv:
            announce_experiment('Plot Results')
            execute_plotting()
            return
        execute_cache_misses()
        execute_selectivity()
        # execute_multicore(runs=500)
        # execute_benchmarks()


def execute_plotting():
    # Cache Misses: Visualize the drops in cache hierarchy
    try:
        print("Cache Misses Cycles: ")
        data = load_results()
        # print(data)
        # assert False
        generate_plots(data, 'gb_per_sec', 'l1_cache_misses')
        generate_plots(data, 'gb_per_sec', 'l2_cache_misses')
        generate_plots(data, 'gb_per_sec', 'l3_cache_misses')
    except KeyboardInterrupt:
        pass

    # Branch Predictions: See Branch Predictions in Action (depending on selectivity)
    try:
        print("Selectivity (incl. use_if=0 and use_if=1): ")
        data = load_results()
        generate_plots(data, 'branch_mispredictions')  # Slide 27
        generate_plots(data, 'gb_per_sec', 'branch_mispredictions')  # Slide 28
        generate_plots(data, 'gb_per_sec', 'stalled_cycles')
    except KeyboardInterrupt:
        pass

    # Multicore: Run across as many cores as possible so we exceed the processors overall bandwith limit
    try:
        print("Multicore: ")
        data = load_results()
        generate_plots(data, 'gb_per_sec')  # Slide 42
        # generate_plots(data, 'gb_per_sec', 'branch_mispredictions')
        # generate_plots(data, 'gb_per_sec', 'stalled_cycles')  # Slide 41
    except KeyboardInterrupt:
        pass

    # Result Formats: Compare performance of our formats in a bar chart
    try:
        print("Result Formats: ")
        data = load_results()
        generate_plots(data, 'gb_per_sec', bars=True)
    except KeyboardInterrupt:
        pass


def execute_test_run():
    set_default_parameters(
        {'result_format': 1, 'run_count': 100, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 0, 'random_values': 1,
         'column_size': 20000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})
    data = generate_data(
         [{'xParam': 'result_format', 'xMin': 0, 'xMax': 2, 'stepSize': 1},
          {'xParam': 'n_cores', 'xMin': 1, 'xMax': 3, 'stepSize': 1, 'n_runs': 1}],
        #  {'xParam': 'column_size', 'xMin': 1, 'xMax': 1000, 'stepSize': 100 }],
        )
    path = store_results(data)
    # path = None
    data = load_results(path)
    generate_plots(data, y1_label='gb_per_sec')


def execute_cache_misses():
    announce_experiment(f'Cache Misses')
    # TESTME: use_if=1 should increase the effect since no preloading should be possible
    set_default_parameters(
        {'result_format': 0, 'run_count': 500, 'clear_cache': 1, 'cache_size': 40, 'pcm_set': 0, 'random_values': 1,
         'column_size': 2e8, 'selectivity': 0.1, 'reserve_memory': 1, 'use_if': 1, 'n_cores': 1, 'jobs_per_core': 1})
    data = generate_data(
        [{'xParam': 'column_size', 'xMin': 2, 'xMax': 8, 'stepSize': 1e5, 'log': True, 'logSamples': 20}])
    store_results(data)


def execute_selectivity():
    announce_experiment(f'Selectivity (Bell Plot)')
    # Not working for result_format=0
    # TESTME: Higher stepSize for selectivity
    # TESTME: Compare all result_formats
    set_default_parameters(
        {'result_format': 2, 'run_count': 500, 'clear_cache': 0, 'cache_size': 40, 'pcm_set': 1, 'random_values': 1,
         'column_size': 1e8, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 1, 'n_cores': 80, 'jobs_per_core': 1})
    data = generate_data(
         [{'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
          {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': 0.05}])
    store_results(data)


def execute_multicore(runs=500):
    announce_experiment(f'Multicore')
    # result_format=0 is the fastest one
    # TESTME: Run with higher column size and/or run_count
    set_default_parameters(
        {'result_format': 1, 'run_count': runs, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 1, 'random_values': 1,
         'column_size': 2e9, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 1, 'n_cores': 2, 'jobs_per_core': 1})
    data = generate_data([{'xParam': 'n_cores', 'xMin': 1, 'xMax': 80, 'stepSize': 1}])
    # data = generate_data([{'xParam': 'n_cores', 'xMin': 1, 'xMax': 20, 'stepSize': 1}])

    store_results(data)


def execute_result_formats():
    announce_experiment(f'Result Formats')
    set_default_parameters(
        {'run_count': 25, 'clear_cache': 1, 'cache_size': 50, 'pcm_set': 1, 'random_values': 1,
         'column_size': 2e7, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 1, 'n_cores': 1, 'jobs_per_core': 1})
    data = generate_data(
            [{'xParam': 'result_format', 'xMin': 0, 'xMax': 2, 'stepSize': 1}])
    store_results(data)


def execute_benchmarks():
    # cache misses over column size
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10,
         'pcm_set': 0, 'random_values': 1, 'column_size': 200000000, 'selectivity': 0.1,
         'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})

    data1 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l1_cache_misses')
    store_results(data1)
    generate_plots(data1)

    data2 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l2_cache_misses')
    store_results(data2)
    generate_plots(data2)

    data3 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l3_cache_misses')
    store_results(data3)
    generate_plots(data3)

    # cache misses comparison random vs not random
    data4 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1}],
        'gb_per_sec', 'l1_cache_misses')
    store_results(data4)
    generate_plots(data4)

    data5 = generate_data(
    [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
     {'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1}],
    'gb_per_sec', 'l2_cache_misses')
    store_results(data5)
    generate_plots(data5)

    data6 = generate_data(
    [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
     {'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1}],
    'gb_per_sec', 'l3_cache_misses')
    store_results(data6)
    generate_plots(data6)

    # cache misses for reserve memory
    set_default_parameters(
        {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10,
        'pcm_set': 0, 'random_values': 1, 'column_size': 200000000, 'selectivity': 0.1,
        'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})

    data7 = generate_data(
        [{'xParam': 'reserve_memory', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l1_cache_misses')
    store_results(data7)
    generate_plots(data7)

    data8 = generate_data(
        [{'xParam': 'reserve_memory', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l2_cache_misses')
    store_results(data8)
    generate_plots(data8)

    data9 = generate_data(
        [{'xParam': 'reserve_memory', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 200000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l3_cache_misses')
    store_results(data9)
    generate_plots(data9)

    # branch predictions for selectivity
    set_default_parameters(
        {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10,
        'pcm_set': 1, 'random_values': 1, 'column_size': 200000000, 'selectivity': 0.1,
        'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})

    data10 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')
    store_results(data10)
    generate_plots(data10)

    # branch predictions and stalled cycles for selectivity
    data11 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'branch_mispredictions', 'stalled_cycles')
    store_results(data11)
    generate_plots(data11)

    # branch predictions for selectivity with values at beginning
    set_default_parameters(
        {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10,
        'pcm_set': 1, 'random_values': 0, 'column_size': 200000000, 'selectivity': 0.1,
        'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})

    data12 = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')
    store_results(data12)
    generate_plots(data12)

    # branch mispredictions with if
    set_default_parameters(
        {'result_format': 3, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10,
        'pcm_set': 1, 'random_values': 1, 'column_size': 200000000, 'selectivity': 0.1,
        'reserve_memory': 0, 'use_if': 0, 'n_cores': 1, 'jobs_per_core': 1})

    data13 = generate_data(
        [{'xParam': 'use_if', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')
    store_results(data13)
    generate_plots(data13)

    # accumulate gb for increasing cores
    set_default_parameters(
        {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 1, 'random_values': 1,
         'column_size': 20000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 2, 'jobs_per_core': 1})
    data14 = generate_data(
         [{'xParam': 'n_cores', 'xMin': 1, 'xMax': 70, 'stepSize': 4}],
        'gb_per_sec', 'stalled_cycles')  # 'selectivity'
    store_results(data14)
    generate_plots(data14)

    data15 = generate_data(
         [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'n_cores', 'xMin': 1, 'xMax': 70, 'stepSize': 4}],
        'gb_per_sec', 'stalled_cycles')  # 'selectivity'
    store_results(data15)
    generate_plots(data15)


def announce_experiment(title: str, dashes: int = 70):
    print(f'\n###{"-"*dashes}###')
    message = f'Experiment: {title}'
    before = (dashes - len(message)) // 2
    after = dashes - len(message) - before
    print(f'###{"-"*before}{message}{"-"*after}###')
    print(f'###{"-"*dashes}###\n')


if __name__ == '__main__':
    execute()
