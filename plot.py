import time
import subprocess
import shutil
import os
import glob

import matplotlib.pyplot as plt
import matplotlib.style as style
import sys
from tqdm import tqdm

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


def execute():
    global par

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
                'column_size': 200000, 'selectivity': 0.01, 'reserve_memory': 0}
    generate_plots(
        [{'xParam': 'result_format', 'xMin': 0, 'xMax': 2, 'stepSize': 1},
        {'xParam': 'column_size', 'xMin': 0, 'xMax': 1000, 'stepSize': 10}],
        'duration')


def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def run(par):
    cmd_call = PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par])
    proc = subprocess.Popen(
        cmd_call,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    so, se = proc.communicate()
    so = so.decode("utf-8")
    if len(so) == 0:
        print(f'Calling `{cmd_call}` failed')
        print('Error response: ', se.decode("utf-8"))
        raise ValueError('No response from subprocess!')
    dlog(so.split('\n'))
    so = list(filter(lambda x: x != '' and x[0] != '-', so.split('\n')))
    dlog(so[0])
    dlog(so[1])
    results = dict(zip(so[0].split(','), so[1].split(',')))
    return results


def gather_plot_data(query_params, y_param):
    x_axis = []
    y_axis = []
    parameters = frange(query_params['xMin'], query_params['xMax'], query_params['stepSize'])
    for i in tqdm(parameters, total=query_params['xMax'] / query_params['stepSize'] + 1, ascii=True):
        par[query_params['xParam']] = i
        results = run(list(par.values()))
        dlog(results)
        y_axis.append(int(results[y_param]))
        x_axis.append(i)
    return x_axis, y_axis


def frange(start, stop, step):
    r = start
    i = 0
    while r <= stop:
        yield r
        i += 1
        r = i * step + start


def generate_plots(p, y_param):
    if len(p) == 1:
        x_axis, y_axis = gather_plot_data(p[0], y_param)

        fixed_parameters = dict(par)
        fixed_parameters.pop(p[0]['xParam'])

        plt.plot(x_axis, y_axis)
        plt.ylabel(y_param)
        plt.xlabel(p[0]['xParam'])
        plt.title(str(fixed_parameters) + '\n', fontsize=13)

        save_plot(y_param)
    elif len(p) == 2:
        parameters = frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize'])

        for count, parameter in enumerate(parameters):
            par[p[0]['xParam']] = parameter
            x_axis, y_axis = gather_plot_data(p[1], y_param)

            plot_style = PLOT_STYLES[count % len(PLOT_STYLES)]
            plt.plot(x_axis, y_axis, plot_style, label="{} = {}".format(p[0]['xParam'], parameter))

        fixed_parameters = dict(par)
        fixed_parameters.pop(p[0]['xParam'])
        fixed_parameters.pop(p[1]['xParam'])

        plt.ylabel(y_param)
        plt.xlabel(p[1]['xParam'])
        plt.legend()
        plt.title(str(fixed_parameters), fontsize=13)

        save_plot(y_param)
    else:
        for i in frange(p[0]['xMin'], p[0]['xMax'], p[0]['stepSize']):

            par[p[0]['xParam']] = i
            generate_plots(p[1:], y_param)


def save_plot(y_param):
    timestamp = time.strftime('%m%d-%H%M%S')
    filename = '-'.join([f'{k}-{v}' for k, v in par.items()]) + ';' + y_param
    plt.savefig(f'{PLOTS_PATH}{timestamp}-{filename}.{PLOT_FORMAT}')
    plt.clf()

# Default colors: blue green and orange yellow
def twin_plot(x, y1, y2, y1_label='Y1', y2_label='Y2',
              y1_color='#037d95', y2_color='#ffa823', title='Title'):
    ax = plt.plot(x, y1, color=y1_color)
    fig = ax.get_figure()
    # Make the y-axis label, ticks and tick labels match the line color.
    ax.set_ylabel(y1_label, color=y1_color)
    ax.tick_params('y', colors=y1_color)
    ax.yaxis.grid(linestyle='dashed')

    ax2 = ax.twinx()
    ax2.plot(x, y2, colors=y2_color)  # orange yellow
    ax2.set_ylabel(y2_label, colors=y2_color)
    ax2.tick_params('y', colors=y2_color)

    ax2.set_title(title)
    # ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax.get_yticks())))

    fig.tight_layout()
    

if __name__ == '__main__':
    execute()
