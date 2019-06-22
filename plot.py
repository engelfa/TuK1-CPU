from utils.execution import set_default_parameters, generate_data
from utils.viz import generate_plots
from utils.storage import store_results, load_results

# If False execute one dummy benchmark
TEST = True


def execute_test_run():
    set_default_parameters(
        {'result_format': 0, 'run_count': 1, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
         'column_size': 100, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0})
    data = generate_data(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 1, 'xMax': 1000, 'stepSize': 100}],
        'gb_per_sec')  # 'selectivity'
    path = store_results(data)
    data = load_results(path)
    generate_plots(data)


def execute_test_plot():
    data = load_results()
    generate_plots(data)


def execute_benchmarks():
    set_default_parameters(
        {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
         'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0})
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 100000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l1_cache_misses')
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 100000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l2_cache_misses')
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 100000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l3_cache_misses')
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')

    set_default_parameters(
        {'result_format': 3, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
         'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0})
    generate_plots(
        [{'xParam': 'use_if', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')

    set_default_parameters(
        {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
         'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0})
    generate_plots(
        [{'xParam': 'reserve_memory', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 100000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l1_cache_misses')
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1}],
        'gb_per_sec', 'l1_cache_misses')


if __name__ == '__main__':
    if TEST:
        execute_test_run()
    else:
        execute_benchmarks()
