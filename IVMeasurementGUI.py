import IV_SMU_PAU as IVMeasurement
from LivePlotWindow import LivePlotWindow


class IVMeasurementGUI:

    def __init__(self, combo_box_smu, combo_box_pau,
                 line_edit_sensor_name, line_edit_initial_voltage, line_edit_final_voltage,
                 line_edit_voltage_step, line_edit_current_compliance,
                 check_box_return_sweep, check_box_live_plot):

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

        self.measurement = IVMeasurement
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

    def set(self, resource_items, sensor_name, initial_voltage, final_voltage, voltage_step,
            current_compliance, live_plot, return_sweep):
        self.set_combo_box_items(resource_items)
        self.set_sensor_name(sensor_name)
        self.set_initial_voltage(initial_voltage)
        self.set_final_voltage(final_voltage)
        self.set_voltage_step(voltage_step)
        self.set_current_compliance(current_compliance)
        self.set_live_plot(live_plot)
        self.set_return_sweep(return_sweep)

    def get_smu_name(self):
        return self.combo_box_smu.currentText()

    def get_pau_name(self):
        return self.combo_box_pau.currentText()

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
        smu = self.get_smu_name()
        pau = self.get_pau_name()
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

        self.measurement.init(smu_addr=self.get_smu_name(), pau_addr=self.get_pau_name(),
                              sensor_name=self.set_sensor_name())
        self.measurement.measure_iv(vi=0, vf=self.get_final_voltage(),
                                    vstep=self.get_voltage_step(), compliance=self.get_current_compliance(),
                                    return_sweep=self.get_return_sweep(), npad=1, liveplot=self.get_live_plot())

        if self.get_live_plot():
            self.w = LivePlotWindow(self.measurement)
        else:
            self.measurement.save_results()
