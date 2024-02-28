from drivers.Keithley2400 import Keithley2400
from drivers.Keithley6487 import Keithley6487
import os
import signal
import numpy as np
import time
from util import mkdir, getdate
from util import BaseThread


class IVMeasurementBackend:
    def __init__(self, smu_addr, pau_addr, sensor_name):
        self.smu = Keithley2400()
        self.pau = Keithley6487()

        self.sensor_name = sensor_name
        self.smu_address = smu_addr
        self.pau_address = pau_addr
        self.initial_voltage = 0
        self.final_voltage = -250
        self.voltage_step = 250
        self.data_points = -1
        self.pad_number = 1
        self.return_sweep = True
        self.live_plot = True
        self.current_compliance = 1e-5

        self.measurement_arr = []
        self.output_arr = []

        self.out_txt_header = 'Vsmu(V)\tIsmu(A)\tIpau(A)'
        self.base_path = r'C:\LGAD_test\I-V_test'
        self.date = ''
        self.out_dir_path = ''

    def _make_out_dir(self):
        self.date = getdate()
        self.out_dir_path = os.path.join(self.base_path, f'{self.date}_{self.sensor_name}')
        mkdir(self.out_dir_path)

    def initialize_measurement(self):

        self.measurement_arr.clear()
        self.output_arr.clear()
        self.data_points = -1
        self._make_out_dir()

        self.smu.open(self.smu_address)
        self.smu.initialize()
        self.smu.set_voltage(0)
        self.smu.set_voltage_range(200)

        self.pau.open(self.pau_address)
        self.pau.reset()
        self.pau.set_zero()

        self.smu.get_idn()
        self.pau.get_idn()

    def set_measurement_options(self, initial_voltage, final_voltage, voltage_step,
                                current_compliance, return_sweep, pad_number, live_plot):
        self.initial_voltage = initial_voltage
        self.final_voltage = final_voltage
        self.voltage_step = voltage_step
        self.current_compliance = current_compliance
        self.return_sweep = return_sweep
        self.live_plot = live_plot
        self.pad_number = pad_number

    def _safe_escaper(self, signumm, frame):
        print("User interrupt...")
        self.smu.set_voltage(0)
        self.smu.set_output('off')
        self.smu.close()
        self.pau.close()
        print("WARNING: Please make sure the output is turned off!")
        exit(1)

    def _make_voltage_array(self):
        n_measurement_points = abs(int(self.final_voltage - self.initial_voltage)) + 1
        voltage_array = np.linspace(self.initial_voltage, self.final_voltage,
                                    n_measurement_points)
        if self.return_sweep:
            voltage_array = np.concatenate([voltage_array, voltage_array[::-1]])

        self.n_measurement_points = len(voltage_array)
        return voltage_array

    def _measure(self, voltage_array):
        for voltage in voltage_array:
            self.smu.set_voltage(voltage)
            voltage_smu, current_smu = self.smu.read().split(',')
            current_pau, _, _ = self.pau.read().split(',')
            voltage_smu = float(voltage_smu)
            current_smu = float(current_smu)
            current_pau = float(current_pau[:-1])
            print(voltage, voltage_smu, current_smu, current_pau)  # TODO use verbose level
            self.measurement_arr.append([voltage, voltage_smu, current_smu, current_pau])
            self.output_arr.append([voltage, current_pau])

    def start_measurement(self):

        self.smu.set_current_limit(self.current_compliance)
        signal.signal(signal.SIGINT, self._safe_escaper)

        voltage_array = self._make_voltage_array()

        self.smu.set_voltage(0)
        self.smu.set_output('on')
        time.sleep(1)

        # if live_plot then use thread to measure else don't use thread
        if self.live_plot:
            measurement_thread = BaseThread(target=self._measure, args=(voltage_array,),
                                            callback=self.save_results)
            measurement_thread.start()

        else:
            self._measure(voltage_array)
            self.save_results()

    def get_data(self):
        if len(self.output_arr) == self.n_measurement_points:
            return None
        else:
            # TODO use generator?
            return self.output_arr

    def get_out_dir(self):
        return self.out_dir_path

    def save_results(self):
        self.smu.set_voltage(0)
        self.smu.set_output('off')
        self.smu.close()
        self.pau.close()

        file_name = (f'IV_SMU+PAU_{self.sensor_name}_{self.date}_{self.initial_voltage}_{self.final_voltage}'
                     f'_pad{self.pad_number}')
        out_file_name = os.path.join(self.out_dir_path, file_name)

        uniq = 1
        while os.path.exists(out_file_name + '.txt'):
            uniq += 1
            out_file_name = f'{out_file_name}_{uniq}'

        np.savetxt(out_file_name + '.txt', self.measurement_arr, header=self.out_txt_header)
