import subprocess
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Test and plot CPU runtime for lookup')
args = parser.parse_args()

xaxis = []
yaxis = []

PROGRAM_NAME = "./speedtest"

def run(param):
    proc = subprocess.Popen(PROGRAM_NAME + ' ' + ' '.join([str(x) for x in param]),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)

    so, se = proc.communicate()

    '''
    if(se != ''):
        raise Exception("Error occured in " + PROGRAM_NAME + ": " + se);
    '''

    so = so.decode("utf-8").split('\n')
    print(so[0])
    print(so[1])
    results = dict(zip(so[0].split(','), so[1].split(',')))
    return results

def plotData():
    plt.plot(xaxis,yaxis)
    plt.ylabel('time')
    plt.show()

for i in range(10,20,2):
    parameters = [i, 5, 100, 10000]
    results = run(parameters)
    yaxis.append(results['duration'])
    xaxis.append(i)
    
plotData()
