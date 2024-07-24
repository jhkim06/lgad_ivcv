import os
from util import mkdir, getdate
import matplotlib.pyplot as plt
import numpy as np
from threading import Event


class MeasurementBackend:
    def __init__(self):
        self.smu = None
        self.pau = None
        self.lcr = None

        self.sensor_name = ''
        self.smu_address = None
        self.pau_address = None
        self.lcr_address = None
        self.initial_voltage = 0
        self.final_voltage = -250
        self.voltage_step = 1
        self.data_points = -1
        self.pad_number = 1
        self.return_sweep = True
        self.live_plot = True
        self.resources_closed = True
        self.voltage_array = None

        self.event = Event()  # to control measurement thread
        self.measurement_thread = None

        self.n_measurement_points = 0
        self.data_index_to_draw = 0
        self.n_data_drawn = 0
        self.measurement_arr = []  # to save as output txt
        self.output_arr = []  # for live plot

        self.return_sweep_started = False
        self.measurement_in_progress = False
        self.status = ''
        self.out_txt_header = ''
        self.base_path = r'C:\LGAD_test'
        self.date = ''
        self.out_dir_path = ''

        # for live plot
        self.y_axis_label = ''
        self.x_axis_label = ''

    def _make_out_dir(self):
        self.date = getdate()
        self.out_dir_path = os.path.join(self.base_path, f'{self.date}_{self.sensor_name}')
        mkdir(self.out_dir_path)

    def get_status_str(self):
        return self.status

    def is_measurement_in_progress(self):
        return self.measurement_in_progress

    def is_return_sweep_started(self):
        return self.return_sweep_started

    def get_data(self):
        if len(self.output_arr) == self.n_measurement_points:
            return None
        else:
            return self.output_arr

    def get_x_axis_label(self):
        return self.x_axis_label

    def get_y_axis_label(self):
        return self.y_axis_label

    def is_data_exists(self):
        if len(self.output_arr) > 0:
            return True
        else:
            return False

    def get_data_point(self):
        if self.is_data_exists():
            if self.data_index_to_draw < len(self.output_arr):
                data_to_draw = self.output_arr[self.data_index_to_draw]
                self.data_index_to_draw += 1
                self.n_data_drawn += 1
                return data_to_draw
            else:
                return self.output_arr[self.data_index_to_draw-1]
        else:
            return [None, None]

    def get_out_dir(self):
        return self.out_dir_path

    def all_data_drawn(self):
        if self.n_data_drawn == self.n_measurement_points:
            return True
        else:
            return False

    def set_status_str(self, index, forced_return_sweep=False):
        self.status = f'{index + 1}/{len(self.voltage_array)} processed'
        if forced_return_sweep:
            self.return_sweep_started = True
        else:
            if self.return_sweep and index > len(self.voltage_array) / 2:
                self.return_sweep_started = True

    def save_as_plot(self, out_file_name):
        plt.ioff()
        fig = plt.Figure()
        ax = fig.add_subplot()
        output_arr_trans = np.array(self.output_arr).T
        ax.plot(output_arr_trans[0], output_arr_trans[1])
        fig.savefig(out_file_name)
        plt.close()
