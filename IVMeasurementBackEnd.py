from drivers.Keithley2400 import Keithley2400
from drivers.Keithley6487 import Keithley6487
import signal
import numpy as np
import time


class IVMeasurementBackend:
    def __init__(self, smu_addr, pau_addr, sensor_name):
        self.smu = Keithley2400()
        self.pau = Keithley6487()

        self.sensor_name = sensor_name
        self.smu_address = smu_addr
        self.pau_address = pau_addr
        self.initial_voltage = 0
        self.final_voltage = -50
        self.voltage_step = 50
        self.data_points = -1
        self.pad_number = 1
        self.return_sweep = True
        self.live_plot = True
        self.current_compliance = 1e-5

        self.output_arr = []

        self.out_dir_path = ''

    def initialize_measurement(self):

        self.data_points = -1
        self.output_arr.clear()

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
        exit()

    def _make_voltage_array(self):
        n_measurement_points = abs(int(self.final_voltage - self.initial_voltage)) + 1
        voltage_array = np.linspace(self.initial_voltage, self.final_voltage,
                                    n_measurement_points)
        if self.return_sweep:
            voltage_array = np.concatenate([voltage_array, voltage_array[::-1]])

        self.n_measurement_points = len(voltage_array)
        return voltage_array

    def start_measurement(self):

        self.smu.set_current_limit(self.current_compliance)
        signal.signal(signal.SIGINT, self._safe_escaper)

        voltage_array = self._make_voltage_array()

        self.smu.set_voltage(0)
        self.smu.set_output('on')
        time.sleep(1)

        # if live_plot then use thread to measure else don't use thread
        # if thread used need to monitor if measurement is finished or not...
        # use callback function

    def make_out_dir(self):
        pass
