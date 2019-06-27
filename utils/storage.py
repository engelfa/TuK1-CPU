import pickle
import time
import os

# --------- Config Start --------- #

PICKLES_PATH = "./output/results/v1/"
PICKLE_FORMAT = "pkl"

# ---------- Config End ---------- #


"""
    Format:
     [{
        'single_plot': boolean,
        'fixed_config': global par variable,
        'parameters_config': p,
        'x_label': x_label,
        'y1_label?': y_param1,
        'y2_label'?: y_param2,
        'runs': [{
            'x': x_axis,
            'y1'?: y_axis1,
            'y2'?: y_axis2,
            'results'?: y_axis2,  // y1 or results need to be defined
            'label?': label,
            'title?': title,
        }, { ... }],
    }, { ... }]
"""


def store_results(data_array):
    paths = []
    for data in data_array:
        for variable_param in data['parameters_config']:
            data['fixed_config'].pop(variable_param['xParam'])
        timestamp = time.strftime('%m%d-%H%M%S')
        filename = '-'.join([f'{k}-{v}' for k, v in data['fixed_config'].items()])
        if 'y1_label' in data:
            filename += ';' + data['y1_label']
        if 'y2_label' in data:
            filename += f", {data['y2_label']}"
        path = f'{PICKLES_PATH}{timestamp}-{filename}.{PICKLE_FORMAT}'
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f'Data is stored at: {path}')
        paths.append(path)
    return paths


def load_results(paths=None):
    if paths is None:
        paths = [select_results()]
    if not isinstance(paths, list) and not isinstance(paths, tuple):
        paths = [paths]
    data_array = []
    for path in paths:
        if not isinstance(path, str):
            path = select_results(path)
        with open(path, 'rb') as f:
            data_array.append(pickle.load(f))
        print('Parameter Config in loaded data: ', data_array[-1]['parameters_config'])
    return data_array


def select_results(idx=None):
    result_files = [p for p in os.listdir(PICKLES_PATH)
                    if os.path.isfile(os.path.join(PICKLES_PATH, p))]
    result_files = sorted(result_files)
    assert len(result_files), 'No result files are available in the pickles directory'
    if idx is None:
        print("Select from the stored results below:")
        print("\n".join([f'> {i+1}: {p}' for i, p in enumerate(result_files)]))
        idx = int(input("Insert the number of the file you want to load from: "))
    else:
        idx += 1
    if idx < 0:
        idx += len(result_files)
    if idx <= 0 or idx > len(result_files):
        raise ValueError(f'Invalid item with id {idx} selected')
    selected = os.path.join(PICKLES_PATH, result_files[idx-1])
    print(f'Selected result file: {selected}')
    return selected
