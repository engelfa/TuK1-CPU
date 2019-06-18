from math import sqrt
from joblib import Parallel, delayed
import multiprocessing  
from tqdm import tqdm  
import time

for i in range(1, 20):
  deltas = []
  for run in range(20):
    before = time.time()
    result = Parallel(n_jobs=i)(delayed(sqrt)(i ** 2) for i in range(100000))
    deltas.append(time.time() - before)
  print(i, round(sum(deltas)/len(deltas), 2))


# My outcome: Best value at 2
# 1 5.39
# 2 3.81
# 3 3.93
# 4 4.08
# 5 4.14
# 6 4.26
# 7 4.3
# 8 4.36
# 9 4.35
# 10 4.45
# 11 4.45
# 12 4.53
