import time

from IVMeasurementBackEnd import IVMeasurementBackend
from LivePlotWindow import LivePlotWindow


class IVMeasurementGUI:

    def __init__(self, combo_box_smu, combo_box_pau,
                 line_edit_sensor_name, line_edit_initial_voltage, line_edit_final_voltage,
                 line_edit_voltage_step, line_edit_current_compliance,
                 check_box_return_sweep, check_box_live_plot,
                 button_measure, label_status):

        # Widgets
        self.combo_box_smu = combo_box_smu
        self.combo_box_pau = combo_box_pau
        self.line_edit_sensor_name = line_edit_sensor_name
        self.line_edit_initial_voltage = line_edit_initial_voltage
        self.line_edit_final_voltage = line_edit_final_voltage
        self.line_edit_voltage_step = line_edit_voltage_step
        self.line_edit_current_compliance = line_edit_current_compliance
        self.check_box_return_sweep = check_box_return_sweep
        self.check_box_live_plot = check_box_live_plot
        self.button_measure = button_measure
        self.button_measure.clicked.connect(self.request_measurement)
        self.label_status = label_status

        self.resource_map = None

        # IVMeasurement()
        self.measurement = IVMeasurementBackend()
        self.w = None

    def set_combo_box_items(self, items):
        self.combo_box_smu.addItems(items)
        self.combo_box_pau.addItems(items)

    def set_sensor_name(self, name):
        self.line_edit_sensor_name.setText(name)

    def set_initial_voltage(self, voltage):
        self.line_edit_initial_voltage.setText(str(voltage))

    def set_final_voltage(self, voltage):
        self.line_edit_final_voltage.setText(str(voltage))

    def set_voltage_step(self, step):
        self.line_edit_voltage_step.setText(str(step))

    def set_current_compliance(self, current):
        self.line_edit_current_compliance.setText(str(current))

    def set_live_plot(self, live_plot):
        self.check_box_live_plot.setChecked(live_plot)

    def set_return_sweep(self, return_sweep):
        self.check_box_return_sweep.setChecked(return_sweep)

    def set(self, resource_map, sensor_name, initial_voltage, final_voltage, voltage_step,
            current_compliance, live_plot, return_sweep):
        self.resource_map = resource_map
        self.set_combo_box_items([*self.resource_map.keys()])
        self.set_sensor_name(sensor_name)
        self.set_initial_voltage(initial_voltage)
        self.set_final_voltage(final_voltage)
        self.set_voltage_step(voltage_step)
        self.set_current_compliance(current_compliance)
        self.set_live_plot(live_plot)
        self.set_return_sweep(return_sweep)

    def get_smu_addr(self):
        id_name = self.combo_box_smu.currentText()
        return self.resource_map[id_name]

    def get_pau_addr(self):
        id_name = self.combo_box_pau.currentText()
        return self.resource_map[id_name]

    def get_sensor_name(self):
        return self.line_edit_sensor_name.text()

    def get_initial_voltage(self):
        return int(self.line_edit_initial_voltage.text())

    def get_final_voltage(self):
        return int(self.line_edit_final_voltage.text())

    def get_voltage_step(self):
        return int(self.line_edit_voltage_step.text())

    def get_current_compliance(self):
        number_str = self.line_edit_current_compliance.text()
        exponent = int(number_str.split('e')[1])
        compliance = pow(10, exponent)
        return compliance

    def get_live_plot(self):
        return self.check_box_live_plot.isChecked()

    def get_return_sweep(self):
        return self.check_box_return_sweep.isChecked()

    def get(self):
        smu = self.get_smu_addr()
        pau = self.get_pau_addr()
        sensor_name = self.get_sensor_name()
        initial_voltage = self.get_initial_voltage()
        final_voltage = self.get_final_voltage()
        step = self.get_voltage_step()
        compliance = self.get_current_compliance()
        live_plot = self.get_live_plot()
        return_sweep = self.get_return_sweep()

        return (smu, pau, sensor_name, initial_voltage, final_voltage, step,
                compliance, return_sweep, live_plot)

    def request_measurement(self, switch=None):

        # initialise measurement
        self.measurement.initialize_measurement(smu_addr=self.get_smu_addr(), pau_addr=self.get_pau_addr(),
                                                sensor_name=self.get_sensor_name())
        # TODO measurement according to switch selection
        self.measurement.set_measurement_options(initial_voltage=0, final_voltage=self.get_final_voltage(),
                                                 voltage_step=self.get_voltage_step(),
                                                 current_compliance=self.get_current_compliance(),
                                                 return_sweep=self.get_return_sweep(),
                                                 pad_number=1, live_plot=self.get_live_plot())
        self.label_status.setText("Start measurement...")
        self.measurement.start_measurement()

        # UpdateStatus(self.measurement)
        if self.get_live_plot():
            self.w = LivePlotWindow(self.measurement)

    def update_status_label(self):

        status_str = ''
        while self.measurement.is_measurement_in_progress():
            temp_str = self.measurement.get_status_str()
            if status_str != temp_str:
                status_str = temp_str
                self.label_status.setText(status_str)
            time.sleep(0.1)
        self.label_status.setText("IV measurement DONE, output path: " + self.measurement.get_out_dir())
