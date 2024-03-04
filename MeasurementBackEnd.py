import os
from util import mkdir, getdate


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
        self.measurement_arr = []
        self.output_arr = []

        self.out_txt_header = ''
        self.base_path = ''
        self.date = ''
        self.out_dir_path = ''

    def _make_out_dir(self):
        self.date = getdate()
        self.out_dir_path = os.path.join(self.base_path, f'{self.date}_{self.sensor_name}')
        mkdir(self.out_dir_path)

    def get_data(self):
        if len(self.output_arr) == self.n_measurement_points:
            return None
        else:
            return self.output_arr

    def get_data_point(self):
        if len(self.output_arr) > 0:  # measurement started and data exists
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

    def all_data_drawn(self):
        if self.data_index_to_draw == self.n_measurement_points:
            return True
        else:
            return False
