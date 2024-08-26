import os 
import re
import argparse
from Plotter import Plotter


def get_file_list(directory, measurement_name, date):
    # Define the regex pattern to match the file name with col# and pad#
    pattern = re.compile(rf'IV_SMU\+PAU_{re.escape(measurement_name)}_col(\d+)_'
                         rf'{re.escape(date)}_pad(\d+)_v0\.txt')

    # List to store tuples of (filename, col number, pad number)
    matching_files_with_numbers = []

    # Iterate over files in the directory and match the pattern
    for f in os.listdir(directory):
        match = pattern.match(f)
        if match:
            matching_files_with_numbers.append(f)

    return matching_files_with_numbers

def get_col_pad_number(file_name):
    pattern = r'col(\d+).*_pad(\d+)'
    match = re.search(pattern, file_name)
    if match:
        col_num = int(match.group(1))
        pad_num = int(match.group(2))
        return col_num, pad_num
    else:
        print("Pattern not found.")

def get_extended_tab10_colors(num_colors):
    # Get the original tab10 colormap
    tab10 = plt.get_cmap('tab10')
    colors = [tab10(i) for i in range(10)]
    
    # Generate extended colors by modifying brightness/saturation
    extended_colors = []
    for i in range(num_colors):
        base_color = colors[i % 10]
        # Slightly adjust the brightness and saturation
        factor = 0.9 + 0.1 * (i // 10)  # Change factor for every new cycle
        new_color = tuple(min(1, c * factor) for c in base_color)
        extended_colors.append(new_color)
    
    return extended_colors

# TODO enable to draw comparison between different sensors
parser = argparse.ArgumentParser(description='I-V and C-V plotter.')
parser.add_argument('sensor_name',
                    help='measured sensor_name. used to determine directory and input file name')
parser.add_argument('measurement_date', help='YYYY-MM-DD')
parser.add_argument('pad_name', default='0')
parser.add_argument('use_col_name', default=False)
parser.add_argument('col_name', default='0')
parser.add_argument('draw_all', default=False)
parser.add_argument('measurement_version', default='0')
parser.add_argument('measurement_descr', default='',
                    help='used to determine data file name.')

args = parser.parse_args()

measurement_type = 'I-V_test'
input_txt_prefix = 'IV_SMU+PAU'
base_input_dir = f'C:/LGAD_test/{measurement_type}/'

# determine directory name and file name
sensor_name = args.sensor_name  # sensor name will be printed in plot
measurement_description = args.measurement_descr  # explain measurement condition
date = args.measurement_date

# determine file name
if measurement_description == '':
    measurement_name = f'{sensor_name}'
else:
    measurement_name = f'{sensor_name}_{measurement_description}'
pad_name = args.pad_name
version = args.measurement_version  # pair file_name_postfix and pad_name

input_dir = base_input_dir + sensor_name + '/'
if args.draw_all:
    # make list of input files
    # also pad and col number to label plot
    input_txt_file_names = get_file_list(input_dir, measurement_name, date)
else:
    if args.use_col_name:
        input_txt_file_names = [f'{input_txt_prefix}_{measurement_name}_col{args.col_name}_{date}_pad{pad_name}_v{version}.txt']
    else:
        input_txt_file_names = [f'{input_txt_prefix}_{measurement_name}_{date}_pad{pad_name}_v{version}.txt']

# create Plotter
plotter = Plotter('CMS', input_dir)

colors = plotter.get_n_colors(len(input_txt_file_names))
kwargs = {"linewidth": 2, "draw_half": True, "y_scale": 1e3}  # common arguments

for index, input_txt_file_name in enumerate(input_txt_file_names):
    label = f'Pad {pad_name}'
    if args.draw_all:
        col, row = get_col_pad_number(input_txt_file_name) 
        if col < 14:
            continue
        label = f'Row {row}, Col {col}'
    print(input_txt_file_name)
    # draw pad current
    #plotter.add_input_data(input_dir + input_txt_file_name,
    #                       label=label,
    #                       y_index=3,
    #                       color=colors[index],
    #                       linestyle='--', flip_y=True, **kwargs)

    # label = f'Total (' + label + ')'
    # draw total current
    plotter.add_input_data(input_dir + input_txt_file_name,
                           label=label,
                           y_index=2,
                           color=colors[index],
                           flip_y=True, **kwargs)

plotter.create_subplots(rows=1, cols=1, figsize=(15, 10), left=0.15)
plotter.draw(remove_offset=False, flip_x=True)

# plotter.do_get_renderer()
plotter.set_experiment_label(location=(0, 0), label=sensor_name, fontsize=20)
plotter.get_current_axis().set_yscale('log')
plotter.show_legend(loc='best', ncol=2)

plotter.set_axis_label_font_size(20)
plotter.set_y_lim((1e-9, 0.9))
plotter.set_current_axis()
plotter.current_axis.grid(axis='y')
plotter.current_axis.grid(axis='x')
plotter.set_y_label("Total current [mA]")
plotter.set_x_label("Bias voltage [V]")

plotter.save_fig(out_name=f'IV_{measurement_name}_{date}_pad{pad_name}_v{version}')
