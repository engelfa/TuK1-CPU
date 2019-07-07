import time
from copy import deepcopy

import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np

import locale
# Use dots for thousand steps and comma for decimal digits
locale.setlocale(locale.LC_ALL, 'en_US.utf-8')


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

PRESENTATION = True
"""
    Available y labels:
        result_format, run_count, clear_cache, cache_size, pcm_set, random_values,
        column_size, selectivity, reserve_memory, use_if, hits, duration,
        rows_per_sec, gb_per_sec, branch_mispredictions, stalled_cycles,
        simd_instructions, l1_cache_misses, l2_cache_misses, l3_cache_misses

    Presentation Mode:
    - No label or title (Added in slides for more readability)

    - Align twin axes
    - If present, keep the legend in a separate file
"""

PERCENTAGE_UNIT = ['selectivity']  # 'l1_cache_misses', 'l2_cache_misses', 'l3_cache_misses'

TEXT_MAPPING = {
    'result_format = 0': 'Counting',
    'result_format = 1': 'Position List',
    'result_format = 2': 'Char Bitmask',
    'result_format = 3': 'Boolean Bitmask',
}

# ---------- Config End ---------- #

# set pyplot style
style.use('seaborn-poster')
style.use('ggplot')
SEABORN_TICK_COLOR = '#555555'  # ax.get_yticklabels()[0].get_color()
# if PRESENTATION:
plt.rc('font', size=20)
plt.rc('xtick', labelsize=26)
plt.rc('ytick', labelsize=26)
# plt.rcParams.update({'ytick.labelsize': 30})
plt.rc('lines', linewidth=4)
plt.rc('grid', color='#DDDDDD', linestyle='--')


def find_y_min_max(data_array, lower_limit_is_0=True):
    y1_min = np.inf
    y1_max = -np.inf
    y2_min = np.inf
    y2_max = -np.inf
    # There is only one edge case: For multiple items in data_array, the entries
    # need only be similar for each run separately
    y1_all_equal = True
    y2_all_equal = True

    for data in data_array:
        for run in data['runs']:
            y1_min = min(*run.get('y1'), y1_min)
            y1_max = max(*run.get('y1'), y1_max)
            y1_all_equal = all([x == y1_min for x in run.get('y1')])

            if data.get('y2_label'):
                y2_min = min(*run.get('y2'), y2_min)
                y2_max = max(*run.get('y2'), y2_max)
                y2_all_equal = all([x == y2_min for x in run.get('y2')])

    def handle_equality_and_padding(all_equal, y_min, y_max):
        padding = 0.05 * (y_max - y_min)
        if all_equal:
            y_max *= 2
            y_min = 0
        else:
            y_max += padding
            y_min += padding
        return y_min, y_max

    y1_min, y1_max = handle_equality_and_padding(y1_all_equal, y1_min, y1_max)
    y2_min, y2_max = handle_equality_and_padding(y2_all_equal, y2_min, y2_max)

    if lower_limit_is_0:
        return (0, y1_max), (0, y2_max)
    else:
        return (y1_min, y1_max), (y2_min, y2_max)


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


# If separate equals true it will always prefer using multiple subplots than merging the lineplots in one
def generate_plots(data_array, y1_label=None, y2_label=None, separate=False, bars=False):
    # TODO: Create barchart
    data_array = transform_data(data_array, y1_label, y2_label)
    limits = find_y_min_max(data_array)
    for data in data_array:
        data['single_plot'] = (not y2_label and not separate) or len(data['parameters_config']) == 1
        log = data['parameters_config'][-1].get('log', False)
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

        path_without_extension = save_plot(fig, data['fixed_config'], data['y1_label'], data.get('y2_label'))

        if PRESENTATION and data['single_plot']:
            legend_items = [(run.get('label'), c) for c, run in zip(COLORS, data['runs']) if run.get('label')]
            if len(legend_items) != 0:
                export_legend(legend_items, f'{path_without_extension}-legend')
            else:
                print("WARNING: Could not generate legend file")


def create_plot(x, x_label, y1, y1_label, y2=None, y2_label=None, title='',
                label=None, y1_color='#037d95', y2_color='#ffa823', ax=None,
                y1_lim=None, y2_lim=None, log=False):
    if PRESENTATION:
        # By default show no labels in presentation mode
        label, title = [None]*2

    x, x_label, y1, y1_label, y2, y2_label, y1_lim, y2_lim = handle_units(
        x, x_label, y1, y1_label, y2, y2_label, y1_lim, y2_lim, log)
    # FIXME:
    # assert label is None or y2_label is None, 'No twin axes with multiple line plots'
    assert y1_color and y2_color

    add_to_axes(ax, x, y1, y1_color, y1_label, y1_lim)
    ax2 = None
    if y2:
        ax2 = ax.twinx()
        add_to_axes(ax2, x, y2, y2_color, y2_label, y2_lim)
    prettify_axes(ax, ax2)
    prettify_labels(ax, ax2, x_label, y1_label, y2_label, y1_color, y2_color, log)

    if label and not y2_label:
        ax.legend()
    if not log:
        delta = 0.01 * (x[-1] - x[0])
        ax.set_xlim(x[0] - delta, x[-1] + delta)
    else:
        ax.set_xscale('log')
    if not PRESENTATION:
        ax.set_xlabel(x_label)
        ax.set_title(title)
    elif x_label[0] == '[':
        ax.set_xlabel(x_label)


def add_to_axes(ax, x, y, color, label, limits):
    if len(x) == 2:
        ax.bar(x, y, color=color, label=label)
    else:
        ax.plot(x, y, color=color, label=label)

    if limits and limits != (None, None):
        ax.set_ylim(limits[0], limits[1])


def prettify_axes(ax, ax2):
    ax.set_facecolor('white')
    ax.grid(False)
    ax.yaxis.grid(True)
    ax.spines['left'].set_color(SEABORN_TICK_COLOR)
    ax.spines['bottom'].set_color(SEABORN_TICK_COLOR)
    if ax2:
        ax2.grid(False)
        ax2.spines['left'].set_color(ax.get_yticklines()[0].get_color())
        ax2.spines['bottom'].set_color(SEABORN_TICK_COLOR)
        ax2.spines['right'].set_color(ax2.get_yticklines()[0].get_color())


def prettify_labels(ax, ax2, x_label, y1_label, y2_label, y1_color, y2_color, log):
    if not PRESENTATION:
        ax.set_ylabel(y1_label)
    if y2_label:
        if not PRESENTATION or y1_label[0] == '[':
            ax.set_ylabel(y1_label, color=y1_color)
        if not PRESENTATION or y2_label[0] == '[':
            ax2.set_ylabel(y2_label, color=y2_color)
        # ax.tick_params('y', color=y1_color)
        # ax2.tick_params('y', color=y2_color)

        # Align ticks of y2 and y1
        ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax.get_yticks())))
        ax.set_yticks(np.linspace(ax.get_yticks()[0], ax.get_yticks()[-1], len(ax.get_yticks())))
        # if PRESENTATION:
        #     ax2.ticklabel_format(axis='yaxis', style='plain', useOffset=False)

    # if PRESENTATION:
        # TODO: Do we still need this since we already use format() below
        # ax.ticklabel_format(axis='yaxis' if log else 'both', style='plain', useOffset=False)
    if y1_label in PERCENTAGE_UNIT:
        ax.set_yticklabels([f'{float(x) * 100:,.1f}%' for x in ax.get_yticks()])
    else:
        step_size = abs(ax.get_yticks()[0] - ax.get_yticks()[1])
        has_integer_step_size = int(step_size) == step_size
        ytick_labels = [locale.format('%d' if has_integer_step_size else '%.2f', x, 1) for x in ax.get_yticks()]
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(ytick_labels)
    if y2_label in PERCENTAGE_UNIT:
        ax2.set_yticklabels([f'{float(x) * 100:,.1f}%' for x in ax2.get_yticks()])
    elif y2_label:
        step_size = abs(ax2.get_yticks()[0] - ax2.get_yticks()[1])
        has_integer_step_size = int(step_size) == step_size
        # %.3g to allow up to three signs
        ytick2_labels = [locale.format('%d' if has_integer_step_size else '%.2f', x, 1) for x in ax2.get_yticks()]
        ax2.set_yticks(ax2.get_yticks())
        ax2.set_yticklabels(ytick2_labels)
    if x_label == 'selectivity':
        xtick_labels = [f'{float(x) * 100:,.1f}%' for x in ax.get_xticks()]
        if all([x[-3:] == '.0%' for x in xtick_labels]):
            xtick_labels = [f'{x[:-3]}%' for x in xtick_labels]
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(xtick_labels)


def handle_units(x, x_label, y1, y1_label, y2=None, y2_label=None, y1_lim=None, y2_lim=None, log=False):
    if PRESENTATION:
        if not log and max(x) >= 1e9:
            x = [x / 1e9 for x in x]
            x_label = '[Bio]'
        elif not log and max(x) >= 1e6:
            x = [x / 1e6 for x in x]
            x_label = '[Mio]'
        if max(*y1, *y1_lim) >= 1e9:
            y1 = [x / 1e9 for x in y1]
            if y1_lim:
                y1_lim = [x / 1e9 for x in y1_lim]
            y1_label = '[Bio]'
        elif max(*y1, *y1_lim) >= 1e6:
            y1 = [x / 1e6 for x in y1]
            if y1_lim:
                y1_lim = [x / 1e6 for x in y1_lim]
            y1_label = '[Mio]'
        if y2 and max(*y2, *y2_lim) >= 1e9:
            y2 = [x / 1e9 for x in y2]
            if y2_lim:
                y2_lim = [x / 1e9 for x in y2_lim]
            y2_label = '[Bio]'
        elif y2 and max(*y2, *y2_lim) >= 1e6:
            y2 = [x / 1e6 for x in y2]
            if y2_lim:
                y2_lim = [x / 1e6 for x in y2_lim]
            y2_label = '[Mio]'
    return x, x_label, y1, y1_label, y2, y2_label, y1_lim, y2_lim


def export_legend(items, filepath="legend", expand=[-4, -4, 4, 4]):
    labels, colors = zip(*items)
    labels = [TEXT_MAPPING.get(x, x) for x in labels]
    handles = [plt.Line2D([], [], linewidth=3, color=colors[i]) for i in range(len(colors))]
    legend = plt.legend(handles, labels, loc=3, framealpha=0, frameon=False, ncol=1)
    plt.axis('off')
    fig = legend.figure
    fig.canvas.draw()
    bbox = legend.get_window_extent()
    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    # timestamp = time.strftime('%m%d-%H%M%S')
    path = f'{filepath}.{PLOT_FORMAT}'
    fig.savefig(path, dpi="figure", bbox_inches=bbox)


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
    return f'{PLOTS_PATH}{timestamp}-{filename}'
