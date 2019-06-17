import time
import shutil
import os
import glob

import matplotlib.pyplot as plt
import matplotlib.style as style
import sys
from tqdm import tqdm

import proc_utils as proc

DEBUG = False

PROGRAM_NAME = os.path.abspath("./build/tuk_cpu")
PLOTS_PATH = "./plots/"
PLOT_FORMAT = "jpg"  # requires PIL/pillow to be installed
# PLOT_FORMAT = "pdf"  # gives HQ plots
FIGSIZE = (7, 5)

C_PRIMARY = '#037d95'  # blue green
C_SECONDARY = '#ffa823'  # orange yellow
C_TERNARY = '#c8116b'  # red violet
COLORS = (C_PRIMARY, C_SECONDARY, C_TERNARY)

if DEBUG:
    # If there are debug logs, do not show a progress bar
    tqdm = lambda x, **y: x  # noqa: F811, E731

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')

par = None


def execute():
    global par

    print('[INFO] Overall cache size [Bit]: ', proc.get_cache_size())
    print('[INFO] CPU Core Temperatures [C]: ', ', '.join(
        map(str, proc.get_cpu_core_temperatures())))

    # If defined, remove and recreate the plots directory
    if len(sys.argv) == 2:
        if sys.argv[1] == "--clear" and os.path.isdir(PLOTS_PATH):
            shutil.rmtree(PLOTS_PATH)
    # Prepare plotting directory
    os.makedirs(PLOTS_PATH, exist_ok=True)
    # Ensure that the program exists
    assert glob.glob(f'{PROGRAM_NAME}*'), \
        'The benchmark code must be compiled and placed at ./build/tuk_cpu'

    # set default values
    par = {'result_format': 0, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
           'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0}
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
    par = {'result_format': 3, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
           'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0}
    generate_plots(
        [{'xParam': 'use_if', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'selectivity', 'xMin': 0, 'xMax': 1, 'stepSize': .1}],
        'gb_per_sec', 'branch_mispredictions')
    par = {'result_format': 1, 'run_count': 25, 'clear_cache': 0, 'cache_size': 10, 'random_values': 1,
           'column_size': 100000000, 'selectivity': 0.1, 'reserve_memory': 0, 'use_if': 0}
    generate_plots(
        [{'xParam': 'reserve_memory', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 10000000, 'xMax': 100000000, 'stepSize': 10000000}],
        'gb_per_sec', 'l1_cache_misses')
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 3, 'stepSize': 1},
         {'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1}],
        'gb_per_sec', 'l1_cache_misses')

def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def run(par):
    cmd_call = PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par])
    so, se = proc.run_command(cmd_call)
    # print(so)
    if len(so) == 0:
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
    # Parameters
    x_axis = list(frange(query_params['xMin'], query_params['xMax'], query_params['stepSize']))
    y_axis1 = []
    y_axis2 = []
    for x_val in tqdm(x_axis, ascii=True):
        # print('[INFO] Allocated Memory: ', par['column_size'], par['result_format'])
        par[query_params['xParam']] = x_val
        results = run(list(par.values()))
        core_temps = proc.get_cpu_core_temperatures()
        for i in range(len(core_temps)):
            results[f'cpu_temp_{i}'] = core_temps[i]
        dlog(results)
        y_axis1.append(float(results[y_param1]))
        if(y_param2):
            y_axis2.append(float(results[y_param2]))
    # print(x_axis, y_axis1)
    return x_axis, y_axis1, y_axis2


# Allows floats in range
def frange(start, stop, step):
    r = start
    i = 0
    while r <= stop:
        yield r
        i += 1
        r = i * step + start

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
        parameters = list(frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize']))
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


if __name__ == '__main__':
    execute()
