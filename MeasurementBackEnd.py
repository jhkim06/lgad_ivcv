import os
from util import mkdir, getdate
import matplotlib.pyplot as plt
import numpy as np


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
        self.voltage_step = 250
        self.data_points = -1
        self.pad_number = 1
        self.return_sweep = True
        self.live_plot = True

        self.n_measurement_points = 0
        self.data_index_to_draw = 0
        self.measurement_arr = []  # to save as output txt
        self.output_arr = []  # for live plot

        self.out_txt_header = ''
        self.base_path = ''
        self.date = ''
        self.out_dir_path = ''

        self.y_axis_label = ''
        self.x_axis_label = ''

    def _make_out_dir(self):
        self.date = getdate()
        self.out_dir_path = os.path.join(self.base_path, f'{self.date}_{self.sensor_name}')
        mkdir(self.out_dir_path)

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
                return data_to_draw
            else:
                return self.output_arr[self.data_index_to_draw-1]
        else:
            return [None, None]

    def get_out_dir(self):
        return self.out_dir_path

    def get_status(self):
        pass

    def all_data_drawn(self):
        if self.data_index_to_draw == self.n_measurement_points:
            return True
        else:
            return False

    def save_as_plot(self, out_file_name):
        plt.ioff()
        fig = plt.Figure()
        ax = fig.add_subplot()
        output_arr_trans = np.array(self.output_arr).T
        ax.plot(output_arr_trans[0], output_arr_trans[1])
        fig.savefig(out_file_name)
        plt.close()
