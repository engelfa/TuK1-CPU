import time
import subprocess
import shutil
import os

import matplotlib.pyplot as plt
import matplotlib.style as style
import sys
from tqdm import tqdm

PROGRAM_NAME = os.path.abspath("./build/tuk_cpu")
PLOTS_PATH = "./plots/"
PLOT_FORMAT = "jpg"  # requires PIL/pillow to be installed
DEBUG = False


if DEBUG:
    tqdm = lambda x, **y: x


def dlog(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')

if len(sys.argv) == 2:
    if sys.argv[1] == "--clear" and os.path.isdir(PLOTS_PATH):
        shutil.rmtree(PLOTS_PATH)

if not os.path.exists(PLOTS_PATH):
    os.makedirs(PLOTS_PATH)


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


def generatePlot(p, yParam):
    if(len(p) == 1):
        xaxis = []
        yaxis = []
        for i in tqdm(range(p[0]['xMin'],p[0]['xMax']+1,p[0]['stepSize']), ascii=True):
            par[p[0]['xParam']] = i
            results = run(list(par.values()))
            dlog(results)
            yaxis.append(int(results[yParam]))
            xaxis.append(i)
        plt.plot(xaxis,yaxis)
        plt.ylabel(yParam)
        plt.xlabel(p[0]['xParam'])
        plt.title(str(par) + '\n', fontsize=13)
        timestamp = time.strftime('%Y-%m-%d-%H%M%S')
        filename = '-'.join([f'{k}-{v}' for k, v in par.items()])
        plt.savefig(PLOTS_PATH + filename + '-' + timestamp + '.' + PLOT_FORMAT)
        plt.clf()
    else:
        for i in range(p[0]['xMin'],p[0]['xMax']+1, p[0]['stepSize']):
            par[p[0]['xParam']] = i
            generatePlot(p[1:], yParam)


# set default values
par = {'result_format': 0, 'run_count': 2000, 'random_values': 1,
       'search_value':  1000, 'column_size': 1000, 'distinct_values': 2000}

generatePlot(
    [{'xParam': 'random_values', 'xMin': 0, 'xMax': 1, 'stepSize': 1},
     {'xParam': 'column_size', 'xMin': 1000, 'xMax': 10000, 'stepSize': 1000}],
    'duration')
