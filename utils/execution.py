import os
import time
import sys
import glob
import shutil

from joblib import Parallel, delayed
from tqdm import tqdm

from .viz import PLOTS_PATH
from .storage import PICKLES_PATH
from . import proc

# --------- Config Start --------- #

DEBUG = False

CONCURRENCY = 40  # Simultaneously running jobs
PROCESSES_PER_CORE = 10  # Subprocesses running on one CPU
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


def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def run(par):
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


def gather_plot_data(query_params, y_param1, y_param2=None):
    x_axis = frange(query_params['xMin'], query_params['xMax'], query_params['stepSize'])
    cpu_affinities = (i // PROCESSES_PER_CORE for i in range(len(x_axis)))
    results = Parallel(n_jobs=CONCURRENCY, backend="multiprocessing")(
        delayed(single_run)(dict(par), query_params['xParam'], x_val, y_param1, y_param2, affinity)
        for x_val, affinity in tqdm(list(zip(x_axis, cpu_affinities)), ascii=True))
    assert all(x[0] <= y[0] for x, y in zip(results, results[1:])), \
        "Multithreaded results are in right order"
    if y_param2:
        _, y_axis1, y_axis2 = zip(*results)
    else:
        _, y_axis1 = zip(*results)
        y_axis2 = None
    print("You may cancel this python run (waiting for one second)")
    time.sleep(1)
    # print('[INFO] Allocated Memory: ', par['column_size'], par['result_format'])
    return x_axis, y_axis1, y_axis2


def single_run(local_par, x_var, x_value, y_param1, y_param2, affinity):
    pid = os.getpid()
    dlog(f'{x_value} - PID: {pid}, Set CPU affinity: {affinity}')
    so, se = proc.run_command(f'taskset -cp {affinity} {pid}')
    so, se = proc.run_command(f'taskset -cp {pid}')
    dlog(so)
    local_par[x_var] = x_value
    results = run(list(local_par.values()))
    core_temps = proc.get_cpu_core_temperatures()
    for i in range(len(core_temps)):
        results[f'cpu_temp_{i}'] = core_temps[i]
    dlog(results)
    if y_param2:
        return (x_value, float(results[y_param1]), float(results[y_param2]))
    return (x_value, float(results[y_param1]))


def frange(start, stop, step):
    values = [start]
    while values[-1] <= stop-step:
        values.append(values[-1] + step)
    return values


def generate_data(p, y_param1, y_param2=None):
    prepare_execution()
    if len(p) == 1:
        x_axis, y_axis1, y_axis2 = gather_plot_data(p[0], y_param1, y_param2)
        return [{
            'single_plot': True,
            'fixed_config': dict(par),
            'parameters_config': p,
            'x_label': p[0]['xParam'],
            'y1_label': y_param1,
            'y2_label': y_param2,
            'runs': [{
                'x': x_axis,
                'y1': y_axis1,
                'y2': y_axis2,
            }],
        }]
    elif len(p) == 2 and y_param2 is None:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])
        runs_data = []

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, _ = gather_plot_data(p[1], y_param1)
            runs_data.append({
                'x': x_axis,
                'y1': y_axis1,
                'label': "{} = {}".format(p[0]['xParam'], parameter),
            })

        return [{
            'single_plot': True,
            'fixed_config': dict(par),
            'parameters_config': p,
            'x_label': p[1]['xParam'],
            'y1_label': y_param1,
            'runs': runs_data,
        }]
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
