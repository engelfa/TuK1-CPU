
from utils.viz import generate_plots
from utils.storage import fake_results


n_cores = list(range(1, 80, 2))
gb_per_sec = list(range(2, 70, 2)) + [71, 72, 73, 71, 73, 70]

if __name__ == '__main__':
    data = fake_results(n_cores, gb_per_sec, 'n_cores', 'gb_per_sec')
    generate_plots(data)
