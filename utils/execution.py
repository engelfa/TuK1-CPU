import os
import time
import sys
import glob
import shutil

import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

from .viz import PLOTS_PATH
from .storage import PICKLES_PATH
from . import proc

# --------- Config Start --------- #

DEBUG = False

# Only used if n_cores is not defined in set_default_parameters
CONCURRENCY = 40  # Simultaneously running jobs
JOBS_PER_CORE = 10  # Subprocesses running on one CPU
N_CORES = CONCURRENCY // JOBS_PER_CORE

PROGRAM_NAME = os.path.abspath("./build/tuk_cpu")

# ---------- Config End ---------- #

if DEBUG:
    # If there are debug logs, do not show a progress bar
    tqdm = lambda x, **y: x  # noqa: F811, E731

par = None
is_first_run = True


def prepare_execution():
    global is_first_run
    if is_first_run:
        is_first_run = False
    else:
        return
    # Ensure that the program exists
    assert glob.glob(f'{PROGRAM_NAME}*'), \
        'The benchmark code must be compiled and placed at ./build/tuk_cpu'

    # If defined, remove and recreate the plots directory
    if len(sys.argv) == 2:
        if sys.argv[1] == "--clear" and os.path.isdir(PLOTS_PATH):
            print('[DEBUG] Clear plotting directory')
            shutil.rmtree(PLOTS_PATH)
            shutil.rmtree(PICKLES_PATH)
    # Prepare plotting directory
    os.makedirs(PLOTS_PATH, exist_ok=True)
    os.makedirs(PICKLES_PATH, exist_ok=True)

    print('[INFO] Overall cache size [Bit]: ', proc.get_cache_size())
    print('[INFO] CPU Core Temperatures [C]: ', ', '.join(
        map(str, proc.get_cpu_core_temperatures())))


def set_default_parameters(new_par):
    global par
    par = new_par
    # Ensure that this value is always defined
    par['n_cores'] = new_par.get('n_cores', N_CORES)
    par['jobs_per_core'] = new_par.get('jobs_per_core', JOBS_PER_CORE)


def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def generate_data(p, y_param1=None, y_param2=None):
    global par
    prepare_execution()
    if len(p) == 1:

        x_axis, y_axis1, y_axis2 = gather_plot_data(p[0], y_param1, y_param2)
        key_name = 'y1' if y_param1 else 'results'
        data = [{
            'single_plot': True,
            'fixed_config': dict(par),
            'parameters_config': p,
            'x_label': p[0]['xParam'],
            'runs': [{
                'x': x_axis,
                key_name: y_axis1
            }],
        }]
        if y_param2:
            data['y2_label'] = y_param2
            data[0]['y2'] = y_axis2
        if y_param1:
            data['y1_label'] = y_param1
        return data
    elif len(p) == 2 and y_param2 is None:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])
        runs_data = []

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, _ = gather_plot_data(p[1], y_param1)
            key_name = 'y1' if y_param1 else 'results'
            runs_data.append({
                'x': x_axis,
                key_name: y_axis1,
                'label': "{} = {}".format(p[0]['xParam'], parameter),
            })
        data = [{
            'single_plot': True,
            'fixed_config': dict(par),
            'parameters_config': p,
            'x_label': p[1]['xParam'],
            'runs': runs_data,
        }]
        if y_param1:
            data['y1_label'] = y_param1
        return data
    elif len(p) == 2:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])
        assert len(parameters) <= 5, 'I do not want to create more than five plots in one graphic'
        runs_data = []

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, y_axis2 = gather_plot_data(p[1], y_param1, y_param2)
            runs_data.append({
                'x': x_axis,
                'y1': y_axis1,
                'y2': y_axis2,
                # Not all params are shown since they exceed the plot size by far (instead see filename)
                'title': "{} = {}".format(p[0]['xParam'], parameter),
            })

        return [{
            'single_plot': False,
            'fixed_config': dict(par),
            'parameters_config': p,
            'x_label': p[1]['xParam'],
            'y1_label': y_param1,
            'y2_label': y_param2,
            'runs': runs_data,
        }]
    else:
        # Recursively call this function (creating multiple files)
        data = []
        for i in frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize']):
            par[p[0]['xParam']] = i
            data.append(generate_data(p[1:], y_param1, y_param2))
        return data


def get_result_column_names(is_pcm_set):
    DEFAULT_COLUMNS = [
        "result_format", "run_count", "clear_cache", "cache_size", "pcm_set",
        "random_values", "column_size", "selectivity", "reserve_memory",
        "use_if", "hits", "duration", "rows_per_sec", "gb_per_sec"]
    if is_pcm_set:
        return DEFAULT_COLUMNS + [
            "branch_mispredictions", "stalled_cycles", "simd_instructions"]
    return DEFAULT_COLUMNS + [
        "l1_cache_misses", "l2_cache_misses", "l3_cache_misses"]


def gather_plot_data(query_params, y_param1=None, y_param2=None):
    global par

    concurrency = par['jobs_per_core'] * par['n_cores']
    jobs_per_core = par['jobs_per_core']
    if par['jobs_per_core'] == -1:
        concurrency = -1
    cpp_par = dict(par)
    del cpp_par['jobs_per_core']
    del cpp_par['n_cores']

    x_axis = frange(query_params['xMin'], query_params['xMax'], query_params['stepSize'])
    if query_params['xParam'] in ['jobs_per_core', 'n_cores']:
        y_axis1, y_axis2 = [], [] if y_param2 else None
        all_results = [dict([(key, []) for key in get_result_column_names(cpp_par['pcm_set'])]) for _ in x_axis]
        for i, x_val in enumerate(x_axis):
            if query_params['xParam'] == 'jobs_per_core':
                jobs_per_core = x_val
            if query_params['xParam'] == 'n_cores':
                concurrency = x_val
            cpu_affinities = [i // jobs_per_core for i in range(x_val)]
            executors = (delayed(run_single_job)(dict(cpp_par), y_param1, y_param2, affinity)
                         for affinity in tqdm(cpu_affinities, ascii=True))
            temp_results = Parallel(n_jobs=concurrency, backend="multiprocessing")(executors)
            if y_param2:
                _, temp_y_axis1, temp_y_axis2 = zip(*temp_results)
                y_axis1.append(np.sum(temp_y_axis1))
                y_axis2.append(np.sum(temp_y_axis2))
            elif y_param1:
                _, temp_y_axis1 = zip(*temp_results)
                y_axis1.append(np.sum(temp_y_axis1))
            else:
                _, temp_results = zip(*temp_results)
                for run_result in temp_results:
                    for key in run_result:
                        all_results[i][key] += run_result[key]
    else:
        cpu_affinities = (i // jobs_per_core for i in range(len(x_axis)))
        executors = (delayed(run_single_job)(dict(cpp_par), y_param1, y_param2, affinity, query_params['xParam'], x_val)
                     for x_val, affinity in tqdm(list(zip(x_axis, cpu_affinities)), ascii=True))
        results = Parallel(n_jobs=concurrency, backend="multiprocessing")(executors)
        assert all(x[0] <= y[0] for x, y in zip(results, results[1:])), \
            "Multithreaded results are in right order"
        if y_param2 and y_param2:
            _, y_axis1, y_axis2 = zip(*results)
        else:  # y_param1 is not None and y_param2 is None or both are None
            _, y_axis1 = zip(*results)
            y_axis2 = None

    print("You may cancel this python run (waiting for one second)")
    time.sleep(1)
    # print('[INFO] Allocated Memory: ', par['column_size'], par['result_format'])
    return x_axis, y_axis1, y_axis2


def run_single_job(local_par, y_param1, y_param2, affinity, x_var=None, x_value=None):
    pid = os.getpid()
    dlog(f'{x_value} - PID: {pid}, Set CPU affinity: {affinity}')
    so, se = proc.run_command(f'taskset -cp {affinity} {pid}')
    so, se = proc.run_command(f'taskset -cp {pid}')
    dlog(so)
    if x_var is not None and x_value is not None:
        local_par[x_var] = x_value
    results = run_cpp_code(list(local_par.values()))
    core_temps = proc.get_cpu_core_temperatures()
    for i in range(len(core_temps)):
        results[f'cpu_temp_{i}'] = core_temps[i]
    dlog(results)
    if y_param2:
        return (x_value, float(results[y_param1]), float(results[y_param2]))
    if y_param1:
        return (x_value, float(results[y_param1]))
    return (x_value, results)


def run_cpp_code(par):
    cmd_call = PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par])
    so, se = proc.run_command(cmd_call)
    if len(so) == 0 or len(se) > 0:
        print(f'Calling `{cmd_call}` failed')
        print('Error response: ', se)
        raise ValueError('No response from subprocess!')
    dlog(so.split('\n'))
    so = list(filter(lambda x: x != '' and x[0] != '-', so.split('\n')))
    dlog(so[0])
    dlog(so[1])
    results = dict(zip(so[0].split(','), so[1].split(',')))
    return results


# TODO: The same as np.arange?
def frange(start, stop, step):
    values = [start]
    while values[-1] <= stop-step:
        values.append(values[-1] + step)
    return values
