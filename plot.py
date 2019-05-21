import subprocess
import argparse
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Test and plot CPU runtime for lookup')
args = parser.parse_args()

xaxis = []
yaxis = []

PROGRAM_NAME = "./build/tuk_cpu"

def run(par):
    proc = subprocess.Popen(PROGRAM_NAME + ' ' + ' '.join([str(x) for x in par]),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)

    so, se = proc.communicate()

    '''
    if(se != ''):
        raise Exception("Error occured in " + PROGRAM_NAME + ": " + se);
    '''
    print(so.decode("utf-8").split('\n'))
    so = list(filter(lambda x: x != '' and x[0]!='-', so.decode("utf-8").split('\n')))
    print(so[0])
    print(so[1])
    results = dict(zip(so[0].split(','), so[1].split(',')))
    return results


# <cound_mode> <run_count> <search_value> <column_size> <distinct_values>

par = {'result_format':0, 'run_count':2000, 'random_values':1, 'search_value': 1000, 'column_size':1000, 'distinct_values':2000}
print(par.values)

def generatePlot(xParam, yParam, xMin, xMax, StepSize):
    for i in range(xMin,xMax+1,StepSize):
        par[xParam] = i

        results = run(list(par.values()))
        print(results)

        yaxis.append(int(results[yParam]))
        
        xaxis.append(i)

    plt.plot(xaxis,yaxis)
    plt.ylabel(yParam)
    plt.xlabel(xParam)
    plt.title(str(par), fontsize=9)
    plt.show()



generatePlot('column_size','duration', 1000, 10000, 1000)




