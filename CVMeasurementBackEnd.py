from drivers.Keithley6487 import Keithley6487
from drivers.WayneKerr4300 import WayneKerr4300

import os
import sys
import signal
import numpy as np
import time
from util import mkdir, getdate, make_unique_name
from util import BaseThread


CURRENT_COMPLIANCE = 10e-6


class CVMeasurementBackend:
    def __init__(self, pau_addr, lcr_addr, sensor_name):
        self.pau = Keithley6487()
        self.lcr = WayneKerr4300()

        self.sensor_name = sensor_name
        self.lcr_address = lcr_addr
        self.pau_address = pau_addr
        self.initial_voltage = 0
        self.final_voltage = -50
        self.initial_voltage_more_points = None
        self.final_voltage_more_points = None
        self.voltage_step = 50
        self.data_points = -1
        self.ac_level = 0.1
        self.frequency = 1000
        self.pad_number = 1
        self.return_sweep = True
        self.live_plot = True

        self.measurement_arr = []
        self.output_arr = []

        self.out_txt_header = 'Vpau(V)\tC(F)\tR(Ohm)\tIpau(A)'
        self.base_path = r'C:\LGAD_test\C-V_test'
        self.date = ''
        self.out_dir_path = ''

    def _make_out_dir(self):
        self.date = getdate()
        self.out_dir_path = os.path.join(self.base_path, f'{self.date}_{self.sensor_name}')
        mkdir(self.out_dir_path)

    def initialize_measurement(self):

        self.data_points = -1

        self.measurement_arr = []
        self.output_arr.clear()

        self._make_out_dir()

        self.lcr.open(self.lcr_address)
        self.lcr.initialize()
        self.lcr.set_dc_voltage(0)

        self.pau.open(self.pau_address)
        self.pau.initialize()

        self.lcr.get_idn()
        self.pau.get_idn()

    def set_measurement_options(self, initial_voltage, final_voltage, voltage_step,
                                ac_level, frequency, return_sweep, pad_number, live_plot):

        self.initial_voltage = initial_voltage
        self.final_voltage = final_voltage
        self.voltage_step = voltage_step
        self.ac_level = ac_level
        self.frequency = frequency
        self.return_sweep = return_sweep
        self.live_plot = live_plot
        self.pad_number = pad_number

    def _safe_escaper(self, signum, frame):
        print("User interrupt... Turning off the output ...")
        self.pau.set_voltage(0)
        self.pau.set_output('OFF')
        self.pau.close()
        self.lcr.set_output('OFF')
        self.lcr.set_dc_voltage(0)
        self.lcr.close()
        print("WARNING: Please make sure the output is turned off!")
        exit(1)

    def _make_voltage_array(self):
        n_measurement_points = abs(int(self.final_voltage - self.initial_voltage)) + 1
        voltage_array = np.linspace(self.initial_voltage, self.final_voltage,
                                    n_measurement_points)

        if self.initial_voltage_more_points is not None and self.final_voltage_more_points is not None:
            if (self.initial_voltage_more_points > self.final_voltage and
                    self.final_voltage_more_points > self.final_voltage):
                voltage_arr_low = voltage_array[voltage_array > self.initial_voltage_more_points]
                voltage_arr_high = voltage_array[voltage_array < self.final_voltage_more_points]
                voltage_arr_medium = np.linspace(self.initial_voltage_more_points, self.final_voltage_more_points,
                                                 n_measurement_points)
                voltage_array = np.concatenate([voltage_arr_low, voltage_arr_medium, voltage_arr_high])

        if self.return_sweep:
            voltage_array = np.concatenate([voltage_array, voltage_array[::-1]])

        self.n_measurement_points = len(voltage_array)
        return voltage_array

    def _measure(self, voltage_array):
        for voltage in voltage_array:
            if voltage > 0:
                print("Warning: positive bias is not allowed. Set DC voltage to 0.")
                voltage = 0
            self.pau.set_voltage(voltage)
            try:
                current_pau, stat_pau, voltage_pau = self.pau.read().split(',')
            except Exception as exception:
                print(type(exception).__name__)
                sys.exit(0)

            voltage_pau = float(voltage_pau)
            current_pau = float(current_pau[:-1])

            res = self.lcr.read_lcr()
            capacitance, resistance = self.lcr.read_lcr().split(',')
            try:
                capacitance = float(capacitance)
                resistance = float(resistance)
            except Exception as exception:
                print(type(exception).__name__)
                break

            self.measurement_arr.append([voltage_pau, capacitance, resistance, current_pau])
            self.output_arr.append([voltage_pau, capacitance])

    def start_measurement(self):
        self.pau.set_current_limit(CURRENT_COMPLIANCE)
        signal.signal(signal.SIGINT, self._safe_escaper)

        voltage_array = self._make_voltage_array()

        self.pau.set_voltage(0)
        self.pau.set_output('ON')
        self.lcr.set_output('ON')
        self.lcr.set_level(self.ac_level)
        self.lcr.set_freq(self.frequency)
        time.sleep(1)

        if self.live_plot:
            measurement_thread = BaseThread(target=self._measure, args=(voltage_array,),
                                            callback=self.save_results)
            measurement_thread.start()
        else:
            pass

    def save_results(self):
        # TODO use verbose level
        if (self.initial_voltage_more_points is not None) and (self.final_voltage_more_points is not None):
            print(f"   * Bias sweep of {self.n_measurement_points} meas between {self.initial_voltage} "
                  f"and {self.final_voltage} "
                  f"with {self.n_measurement_points} meas "
                  f"between {self.initial_voltage_more_points} and {self.final_voltage_more_points}")
        else:
            print(f"   * Bias sweep of {self.n_measurement_points} meas "
                  f"between {self.initial_voltage} and {self.final_voltage} ")
        print(f"   * Return sweep: {self.return_sweep}")

        self.pau.set_output('OFF')
        self.pau.close()
        self.lcr.set_output('OFF')
        self.lcr.set_dc_voltage(0)
        self.lcr.close()

        file_name = (f'CV_LCR+PAU_{self.sensor_name}_{self.date}_{self.initial_voltage}_{self.final_voltage}_'
                     f'{self.frequency}Hz_pad{self.pad_number}')
        out_file_name = os.path.join(self.out_dir_path, file_name)
        out_file_name = make_unique_name(out_file_name)

        np.savetxt(out_file_name + '.txt', self.measurement_arr, header=self.out_txt_header)
