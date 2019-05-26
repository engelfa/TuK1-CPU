import subprocess
import matplotlib.pyplot as plt
import matplotlib.style as style
import os
import shutil
import sys

PROGRAM_NAME = "./build/tuk_cpu"
PLOTS_PATH = "./plots/"
PLOT_FORMAT = "jpg"

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')

if len(sys.argv) == 2:
    if sys.argv[1] == "--clear" and os.path.isdir(PLOTS_PATH):
        shutil.rmtree(PLOTS_PATH)

if not os.path.exists(PLOTS_PATH):
    os.makedirs(PLOTS_PATH)

def run(par):
    proc = subprocess.Popen(PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par]),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)

    so, se = proc.communicate()

    print(so.decode("utf-8").split('\n'))
    so = list(filter(lambda x: x != '' and x[0]!='-', so.decode("utf-8").split('\n')))
    print(so[0])
    print(so[1])
    results = dict(zip(so[0].split(','), so[1].split(',')))
    return results

def generatePlot(p, yParam):

    if(len(p) == 1):
        xaxis = []
        yaxis = []

        for i in range(p[0]['xMin'],p[0]['xMax']+1,p[0]['stepSize']):
            par[p[0]['xParam']] = i

            results = run(list(par.values()))
            print(results)

            yaxis.append(int(results[yParam]))
            
            xaxis.append(i)
        
        plt.plot(xaxis,yaxis)
        plt.ylabel(yParam)
        plt.xlabel(p[0]['xParam'])
        plt.title(str(par) + '\n', fontsize=13)
        plt.savefig(PLOTS_PATH + str(par) + '.' + PLOT_FORMAT)
        plt.clf()
    
    else:
        for i in range(p[0]['xMin'],p[0]['xMax']+1,p[0]['stepSize']):
            par[p[0]['xParam']] = i

            generatePlot(p[1:], yParam)


# set default values
par = {'result_format':0, 'run_count':2000, 'random_values':1, 'search_value': 1000, 'column_size':1000, 'distinct_values':2000}

generatePlot([{'xParam':'random_values', 'xMin':0, 'xMax':1, 'stepSize':1},{'xParam':'column_size', 'xMin':1000, 'xMax':10000, 'stepSize':1000}],'duration')