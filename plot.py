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
        # execute_plotting()
        # return
        # execute_benchmarks()
        try:
            execute_cache_misses()
        except:
            pass
        try:
            execute_cache_misses(10)
        except:
            pass
        try:
            execute_stalled()
        except:
            pass
        try:
            execute_stalled(10)
        except:
            pass
        try:
            execute_selectivity()
        except:
            pass
        try:
            execute_not_evenly_distributed()
        except:
            pass

        # Validation Run
        try:
            execute_cache_misses()
        except:
            pass
        try:
            execute_cache_misses(10)
        except:
            pass
        try:
            execute_stalled()
        except:
            pass
        try:
            execute_stalled(10)
        except:
            pass
        try:
            execute_selectivity()
        except:
            pass
        try:
            execute_not_evenly_distributed()
        except:
            pass


def execute_plotting():
    # Cache Misses:
    data = load_results()
    generate_plots(data, y1_label='gb_per_sec')
    generate_plots(data, y1_label='l1_cache_misses')
    generate_plots(data, y1_label='l2_cache_misses')
    generate_plots(data, y1_label='l3_cache_misses')

    # Stalled Cycles:
    data = load_results()
    generate_plots(data, y1_label='gb_per_sec')  # Slide 42
    generate_plots(data, y1_label='branch_mispredictions')
    generate_plots(data, y1_label='stalled_cycles')  # Slide 41

    # Branch Predictions on Selectivity:
    data = load_results()
    generate_plots(data, y1_label='branch_mispredictions')  # Slide 27
    generate_plots(data, y1_label='gb_per_sec', y2_label='branch_mispredictions')  # Slide 28
    # Out of curiosity:
    generate_plots(data, y1_label='gb_per_sec', y2_label='stalled_cycles')

    # Random Values = 0
    data = load_results()
    generate_plots(data, y1_label='branch_mispredictions')  # Slide 30
    generate_plots(data, y1_label='gb_per_sec', y2_label='branch_mispredictions')  # Slide 30


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


def execute_not_evenly_distributed():
    announce_experiment(f'Consecutive Values (Random Values = 0)')
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 1, 'random_values': 0,
         'column_size': 2e8, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 2, 'jobs_per_core': 1})
    data = generate_data(
         [{'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': 0.01}])
    store_results(data)
    # data = load_results(path)
    generate_plots(data, y1_label='gb_per_sec', y2_label='branch_mispredictions')


def execute_selectivity():
    announce_experiment(f'Selectivity (Bell Plot)')
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 1, 'random_values': 1,
         'column_size': 2e8, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 2, 'jobs_per_core': 1})
    data = generate_data(
         [{'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': 0.01}])
    store_results(data)
    # data = load_results(path)
    generate_plots(data, y1_label='gb_per_sec', y2_label='branch_mispredictions')


def execute_stalled(jobs=1):
    announce_experiment(f'Stalled Cycles (jpc={jobs})')
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 1, 'random_values': 1,
         'column_size': 2e8, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 2, 'jobs_per_core': jobs})
    data = generate_data(
         [{'xParam': 'n_cores', 'xMin': 1, 'xMax': 70, 'stepSize': 3}])
    store_results(data)
    # data = load_results(path)
    generate_plots(data, y1_label='gb_per_sec')
    generate_plots(data, y1_label='branch_mispredictions')
    generate_plots(data, y1_label='stalled_cycles')


def execute_cache_misses(jobs=1):
    announce_experiment(f'Cache Misses (cm={jobs})')
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'pcm_set': 0, 'random_values': 1,
         'column_size': 2e8, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0, 'n_cores': 2, 'jobs_per_core': jobs})
    data = generate_data(
         [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
          {'xParam': 'n_cores', 'xMin': 1, 'xMax': 70, 'stepSize': 3}])
    store_results(data)
    # data = load_results(path)
    generate_plots(data, y1_label='gb_per_sec')
    generate_plots(data, y1_label='l1_cache_misses')
    generate_plots(data, y1_label='l2_cache_misses')
    generate_plots(data, y1_label='l3_cache_misses')
    # generate_plots(data, y1_label='gb_per_sec', y2_label='stalled_cycles')



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
