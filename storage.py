import pandas


"""
    Format:
     [{
        'single_plot': boolean,
        'fixed_config': global par variable,
        'parameters_config': p,
        'runs': [{
            'x': x_axis,
            'x_label': x_label,
            'y1': y_axis1,
            'y1_label': y_param1,
            'y2': y_axis2,
            'y2_label': y_param2,
            'label': label,
            'title': title,
        },
        { ... }],
    },
    { ... }]
"""
def store_results(data_array):
    pickle.store(data_array, 'temp.pkl')
