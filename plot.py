import time
import shutil
import os
import glob

import matplotlib.pyplot as plt
import matplotlib.style as style
import sys
from tqdm import tqdm

import proc_utils as proc

PROGRAM_NAME = os.path.abspath("./build/tuk_cpu")
PLOTS_PATH = "./plots/"
PLOT_FORMAT = "jpg"  # requires PIL/pillow to be installed
DEBUG = False

PLOT_STYLES = ['b', 'g', 'r', 'c', 'm', 'y', 'k']


if DEBUG:
    # If there are debug logs, do not show a progress bar
    tqdm = lambda x, **y: x  # noqa: F811, E731

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')

par = None

# Stored globally to share lineplots in one figure
fig, ax = None, None


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
    par = {'result_format': 0, 'run_count': 2000, 'clear_cache': 0, 'cache_size': 10, 'random_values': 0,
           'column_size': 200000, 'selectivity': 0.01, 'reserve_memory': 0, 'use_if': 0}
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 2, 'stepSize': 1},
         {'xParam': 'column_size', 'xMin': 0, 'xMax': 1000, 'stepSize': 10}],
        'duration', 'selectivity')


def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def run(par):
    cmd_call = PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par])
    so, se = proc.run_command(cmd_call)
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
    x_axis = []
    y_axis1 = []
    y_axis2 = []
    parameters = frange(query_params['xMin'], query_params['xMax'], query_params['stepSize'])
    for i in tqdm(parameters, total=query_params['xMax'] / query_params['stepSize'] + 1, ascii=True):
        #print('[INFO] Allocated Memory: ', par['column_size'], par['result_format'])
        par[query_params['xParam']] = i
        results = run(list(par.values()))
        dlog(results)
        x_axis.append(i)
        y_axis1.append(float(results[y_param1]))
        if(y_param2):
            y_axis2.append(float(results[y_param2]))

    return x_axis, y_axis1, y_axis2

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

        fixed_parameters = dict(par)
        fixed_parameters.pop(p[0]['xParam'])

        create_plot(x_axis, p[0]['xParam'], 'b', y_axis1, y_param1, str(fixed_parameters) + '\n', 13, y_axis2, y_param2, None)

        save_plot(y_param1, y_param2)
    elif len(p) == 2:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis1, y_axis2 = gather_plot_data(p[1], y_param1, y_param2)

            plot_style = PLOT_STYLES[count % len(PLOT_STYLES)]

            fixed_parameters = dict(par)
            fixed_parameters.pop(p[0]['xParam'])
            fixed_parameters.pop(p[1]['xParam'])

            label="{} = {}".format(p[0]['xParam'], parameter)
            create_plot(x_axis, p[1]['xParam'], plot_style, y_axis1, y_param1, str(fixed_parameters), 13, y_axis2, y_param2, label)

        ax.legend()
        save_plot(y_param1, y_param2)
    else:
        for i in frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize']):

            par[p[0]['xParam']] = i
            generate_plots(p[1:], y_param1, y_param2)


def save_plot(y_param1, y_param2=None):
    timestamp = time.strftime('%m%d-%H%M%S')
    if not y_param2:
        filename = '-'.join([f'{k}-{v}' for k, v in par.items()]) + ';' + y_param1
    else:
        filename = '-'.join([f'{k}-{v}' for k, v in par.items()]) + ';' + y_param1 + y_param2
    plt.savefig(f'{PLOTS_PATH}{timestamp}-{filename}.{PLOT_FORMAT}')
    plt.clf()


def create_plot(x, x_label, plot_style, y1, y1_label, title, fontsize=13, y2=None, y2_label=None, label=None, y1_color='#037d95', y2_color='#ffa823'):
    global fig, ax
    # Use same figure (and axes) if already created
    if fig == None:
        fig, ax = plt.subplots()
    ax.plot(x, y1, plot_style, label=label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y1_label, color=y1_color)
    plt.tick_params('y', color=y1_color)

    if y2:
        ax2 = ax.twinx()
        ax2.plot(x, y2, color=y2_color)  # orange yellow
        ax2.set_ylabel(y2_label, color=y2_color)
        ax2.tick_params('y', color=y2_color)

    fig.tight_layout()


if __name__ == '__main__':
    execute()
