import time
import matplotlib.pyplot as plt
import matplotlib.style as style
from copy import deepcopy

# --------- Config Start --------- #

PLOTS_PATH = "./output/plots/v1/"
PLOT_FORMAT = "jpg"  # requires PIL/pillow to be installed
# PLOT_FORMAT = "pdf"  # gives HQ plots
FIGSIZE = (9, 6)

C_PRIMARY = '#037d95'  # blue green
C_SECONDARY = '#ffa823'  # orange yellow
C_TERNARY = '#c8116b'  # red violet
C4 = '#50ff50'  # green
COLORS = (C_PRIMARY, C_SECONDARY, C_TERNARY, C4)  # We have four different result_formats

# ---------- Config End ---------- #

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')


# FIXME: I tried with selectivity being the same for every point and the scaling is broken (all values are shown at the top)
def find_y_min_max(data_array, lower_limit_is_0=True):
    y1_min = None
    y1_max = None
    y2_min = None
    y2_max = None

    for data in data_array:
        for run in data['runs']:
            temp_y1_min = min(run.get('y1'))
            temp_y1_max = max(run.get('y1'))
            if(data.get('y2_label')):
                temp_y2_min = min(run.get('y2'))
                temp_y2_max = max(run.get('y2'))

            if(y1_min == None or temp_y1_min < y1_min):
                y1_min = temp_y1_min
            if(y1_max == None or temp_y1_max > y1_max):
                y1_max = temp_y1_max
            if(data.get('y2_label') and (y2_min == None or temp_y2_min < y2_min)):
                y2_min = temp_y2_min
            if(data.get('y2_label') and (y2_max == None or temp_y2_max > y2_max)):
                y2_max = temp_y2_max

    if(lower_limit_is_0):
        return [(0, y1_max),(0, y2_max)]
    else:
        return [(y1_min, y1_max),(y2_min, y2_max)]


def transform_data(data_array, y1_label=None, y2_label=None):
    if data_array[0].get('y1_label'):
        return data_array
    assert y1_label is not None, 'If no label is in the data specified, '\
        'you need to define at least one during plotting'
    # Do not directly change the parameter to avoid side effects for multiple generate_plots calls
    data_array = deepcopy(data_array)
    for i, data in enumerate(data_array):
        # data_array[i]['single_plot'] = True
        data_array[i]['y1_label'] = y1_label
        data_array[i]['y2_label'] = y2_label
        for j, run in enumerate(data['runs']):
            data_array[i]['runs'][j]['y1'] = [float(x[y1_label]) for x in run['results']]
            if y2_label:
                data_array[i]['runs'][j]['y2'] = [float(x[y2_label]) for x in run['results']]
            del data_array[i]['runs'][j]['results']
    return data_array


def generate_plots(data_array, y1_label=None, y2_label=None):
    data_array = transform_data(data_array, y1_label, y2_label)
    limits = find_y_min_max(data_array)
    for data in data_array:
        log = data['parameters_config'][-1]['log']
        if data['single_plot']:
            fig, axes = plt.subplots(figsize=FIGSIZE)
        else:
            figsize = (FIGSIZE[0], FIGSIZE[1] * len(data['runs']))
            fig, axes = plt.subplots(len(data['runs']), figsize=figsize)

        for i, run in enumerate(data['runs']):
            color = COLORS[i] if data['single_plot'] else COLORS[0]
            ax = axes if data['single_plot'] else axes[i]
            create_plot(
                run['x'], data['x_label'], run['y1'], data['y1_label'],
                run.get('y2'), data.get('y2_label'), title=run.get('title'),
                label=run.get('label'), ax=ax, y1_color=color, y1_lim=limits[0], y2_lim=limits[1], log=log)

        for variable_param in data['parameters_config']:
            # If stored results are used those parametes are already removed
            if variable_param['xParam'] in data['fixed_config']:
                data['fixed_config'].pop(variable_param['xParam'])
        save_plot(fig, data['fixed_config'], data['y1_label'], data.get('y2_label'))


def create_plot(x, x_label, y1, y1_label, y2=None, y2_label=None, title='',
                label=None, y1_color='#037d95', y2_color='#ffa823', ax=None, y1_lim=None, y2_lim=None, log=False):
    # FIXME:
    # assert label is None or y2_label is None, 'No twin axes with multiple line plots'
    assert y1_color is not None
    assert y2_color is not None
    if len(x) == 2:
        ax.bar(x, y1, color=y1_color, label=label)
    else:
        ax.plot(x, y1, color=y1_color, label=label)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y1_label)


    if(log):
        ax.set_xscale('log')
    else:
        ax.ticklabel_format(axis='both', style='plain', useOffset=False)

    if(y1_lim and y1_lim != (None, None)):
        ax.set_ylim(y1_lim[0],y1_lim[1])

    if y2_label:
        ax.set_ylabel(y1_label, color=y1_color)
        ax.tick_params('y', color=y1_color)

        ax2 = ax.twinx()
        if len(x) == 2:
            ax2.bar(x, y2, color=y2_color)  # orange yellow
        else:
            ax2.plot(x, y2, color=y2_color)  # orange yellow
        ax2.set_ylabel(y2_label, color=y2_color)
        ax2.tick_params('y', color=y2_color)
        ax.ticklabel_format(axis='both', style='plain', useOffset=False)
        if(y2_lim and y2_lim != (None, None)):
            ax2.set_ylim(y2_lim[0],y2_lim[1])
    elif label is not None:
        ax.legend()
    ax.set_title(title)


def save_plot(fig, fixed_parameters, y_param1, y_param2=None):
    timestamp = time.strftime('%m%d-%H%M%S')
    filename = '-'.join([f'{k}-{v}' for k, v in fixed_parameters.items()]) + ';' + y_param1
    if y_param2:
        filename += y_param2
    fig.tight_layout()
    fig.savefig(f'{PLOTS_PATH}{timestamp}-{filename}.{PLOT_FORMAT}')
    # Vanish plots
    plt.close()
    fig = None
