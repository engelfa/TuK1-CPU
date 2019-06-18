import os
import time
import sys
import glob
import shutil

import matplotlib.pyplot as plt
import matplotlib.style as style
from joblib import Parallel, delayed
from tqdm import tqdm

import proc_utils as proc

# --------- Config Start --------- #

DEBUG = False

CONCURRENCY = -1  # Simultaneously running jobs
USE_THREADING = False  # or use multiprocessing
PROGRAM_NAME = os.path.abspath("./build/tuk_cpu")
PLOTS_PATH = "./plots/"
PLOT_FORMAT = "jpg"  # requires PIL/pillow to be installed
# PLOT_FORMAT = "pdf"  # gives HQ plots
FIGSIZE = (7, 5)

C_PRIMARY = '#037d95'  # blue green
C_SECONDARY = '#ffa823'  # orange yellow
C_TERNARY = '#c8116b'  # red violet
COLORS = (C_PRIMARY, C_SECONDARY, C_TERNARY)

# ---------- Config End ---------- #

if DEBUG:
    # If there are debug logs, do not show a progress bar
    tqdm = lambda x, **y: x  # noqa: F811, E731

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')

par = None


def prepare_execution():
    # Ensure that the program exists
    assert glob.glob(f'{PROGRAM_NAME}*'), \
        'The benchmark code must be compiled and placed at ./build/tuk_cpu'

    # If defined, remove and recreate the plots directory
    if len(sys.argv) == 2:
        if sys.argv[1] == "--clear" and os.path.isdir(PLOTS_PATH):
            print('[DEBUG] Clear plotting directory')
            shutil.rmtree(PLOTS_PATH)
    # Prepare plotting directory
    os.makedirs(PLOTS_PATH, exist_ok=True)

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
    backend = "threading" if USE_THREADING else "multiprocessing"
    # Use all CPUs
    # os.system(f'taskset -p 0xff {os.getpid()}')
    # Parameters
    processes_per_core = 2
    x_axis = frange(query_params['xMin'], query_params['xMax'], query_params['stepSize'])
    cpu_affinities = (i // processes_per_core for i in range(len(x_axis)))
    # n_jobs=-1 (all CPUs) ->
    # n_jobs=10 -> 5.79 it/s
    results = Parallel(n_jobs=CONCURRENCY, backend=backend)(
        delayed(single_run)(dict(par), query_params['xParam'], x_val, y_param1, y_param2, affinity)
        for x_val, affinity in tqdm(list(zip(x_axis, cpu_affinities)), ascii=True))
    assert all(x[0] <= y[0] for x, y in zip(results, results[1:])), \
        "Multithreaded results are in right order"
    if y_param2:
        _, y_axis1, y_axis2 = zip(*results)
    else:
        _, y_axis1 = zip(*results)
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


def generate_plots(p, y_param1, y_param2=None):
    if len(p) == 1:
        x_axis, y_axis1, y_axis2 = gather_plot_data(p[0], y_param1, y_param2)
        fig, ax = plt.subplots(figsize=FIGSIZE)
        create_plot(x_axis, p[0]['xParam'], y_axis1, y_param1, y_axis2, y_param2, ax=ax)
        save_plot(fig, p, y_param1, y_param2)
    elif len(p) == 2 and y_param2 is None:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])
        fig, ax = plt.subplots(figsize=FIGSIZE)

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, _ = gather_plot_data(p[1], y_param1)
            label = "{} = {}".format(p[0]['xParam'], parameter)
            create_plot(x_axis, p[1]['xParam'], y_axis1, y_param1, ax=ax, y1_color=COLORS[count], label=label)
        save_plot(fig, p, y_param1)
    elif len(p) == 2:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])
        assert len(parameters) <= 5, 'I do not want to create more than five plots in one graphic'
        figsize = (FIGSIZE[0], FIGSIZE[1] * len(parameters))
        fig, axes = plt.subplots(len(parameters), figsize=figsize)

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, y_axis2 = gather_plot_data(p[1], y_param1, y_param2)
            # Not all params are shown since they exceed the plot size by far (instead see filename)
            title = "{} = {}".format(p[0]['xParam'], parameter)
            create_plot(x_axis, p[1]['xParam'], y_axis1, y_param1, y_axis2, y_param2, title, ax=axes[count])
        save_plot(fig, p, y_param1, y_param2)
    else:
        # Recursively call ths function (creating multiple files)
        for i in frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize']):
            par[p[0]['xParam']] = i
            generate_plots(p[1:], y_param1, y_param2)


def create_plot(x, x_label, y1, y1_label, y2=None, y2_label=None, title='',
                label=None, y1_color='#037d95', y2_color='#ffa823', ax=None):
    assert label is None or y2_label is None, 'No twin axes with multiple line plots'
    ax.plot(x, y1, color=y1_color, label=label)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y1_label, color=y1_color)
    plt.tick_params('y', color=y1_color)
    if y2_label:
        ax2 = ax.twinx()
        ax2.plot(x, y2, color=y2_color)  # orange yellow
        ax2.set_ylabel(y2_label, color=y2_color)
        ax2.tick_params('y', color=y2_color)
    else:
        ax.legend()
    ax.set_title(title)


def save_plot(fig, p, y_param1, y_param2=None):
    fixed_parameters = dict(par)
    for variable_param in p:
        fixed_parameters.pop(variable_param['xParam'])
    timestamp = time.strftime('%m%d-%H%M%S')
    filename = '-'.join([f'{k}-{v}' for k, v in fixed_parameters.items()]) + ';' + y_param1
    if y_param2:
        filename += y_param2
    fig.tight_layout()
    fig.savefig(f'{PLOTS_PATH}{timestamp}-{filename}.{PLOT_FORMAT}')
    # Vanish plots
    plt.close()
    fig = None
