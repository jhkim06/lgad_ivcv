import CV_LCR_PAU as CVMeasurement
from LivePlotWindow import LivePlotWindow


class CVMeasurementGUI:

    def __init__(self, combo_box_lcr, combo_box_pau,
                 line_edit_sensor_name, line_edit_initial_voltage, line_edit_final_voltage,
                 line_edit_voltage_step, line_edit_frequency,
                 ac_level,
                 check_box_return_sweep, check_box_live_plot):

        # Widgets
        self.combo_box_lcr = combo_box_lcr
        self.combo_box_pau = combo_box_pau
        self.line_edit_sensor_name = line_edit_sensor_name
        self.line_edit_initial_voltage = line_edit_initial_voltage
        self.line_edit_final_voltage = line_edit_final_voltage
        self.line_edit_voltage_step = line_edit_voltage_step
        self.line_edit_frequency = line_edit_frequency
        self.line_edit_ac_level = ac_level
        self.check_box_return_sweep = check_box_return_sweep
        self.check_box_live_plot = check_box_live_plot

        self.measurement = CVMeasurement
        self.w = None

    def set_combo_box_items(self, items):
        self.combo_box_lcr.addItems(items)
        self.combo_box_pau.addItems(items)

    def set_sensor_name(self, name):
        self.line_edit_sensor_name.setText(name)

    def set_initial_voltage(self, voltage):
        self.line_edit_initial_voltage.setText(str(voltage))

    def set_final_voltage(self, voltage):
        self.line_edit_final_voltage.setText(str(voltage))

    def set_voltage_step(self, step):
        self.line_edit_voltage_step.setText(str(step))

    def set_frequency(self, current):
        self.line_edit_frequency.setText(str(current))

    def set_ac_level(self, level):
        self.line_edit_ac_level.setText(str(level))

    def set_live_plot(self, live_plot):
        self.check_box_live_plot.setChecked(live_plot)

    def set_return_sweep(self, return_sweep):
        self.check_box_return_sweep.setChecked(return_sweep)

    def set(self, resource_items, sensor_name, initial_voltage, final_voltage, voltage_step,
            frequency, ac_level, live_plot, return_sweep):
        self.set_combo_box_items(resource_items)
        self.set_sensor_name(sensor_name)
        self.set_initial_voltage(initial_voltage)
        self.set_final_voltage(final_voltage)
        self.set_voltage_step(voltage_step)
        self.set_frequency(frequency)
        self.set_ac_level(ac_level)
        self.set_live_plot(live_plot)
        self.set_return_sweep(return_sweep)

    def get_lcr_name(self):
        return self.combo_box_lcr.currentText()

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

    def get_frequency(self):
        return int(self.line_edit_frequency.text())

    def get_ac_level(self):
        return float(self.line_edit_ac_level.text())

    def get_live_plot(self):
        return self.check_box_live_plot.isChecked()

    def get_return_sweep(self):
        return self.check_box_return_sweep.isChecked()

    def get(self):
        smu = self.get_lcr_name()
        pau = self.get_pau_name()
        sensor_name = self.get_sensor_name()
        initial_voltage = self.get_initial_voltage()
        final_voltage = self.get_final_voltage()
        step = self.get_voltage_step()
        compliance = self.get_frequency()
        ac_level = self.get_ac_level()
        live_plot = self.get_live_plot()
        return_sweep = self.get_return_sweep()

        return (smu, pau, sensor_name, initial_voltage, final_voltage, step,
                compliance, ac_level, return_sweep, live_plot)

    def request_measurement(self):

        self.measurement.init(pau_addr=self.get_pau_name(), lcr_addr=self.get_lcr_name(),
                              sensor_name=self.get_sensor_name())
        self.measurement.measure_cv(vi=0, vf=self.get_final_voltage(),
                                    vstep=self.get_voltage_step(), v0=-15, v1=-25,
                                    freq=self.get_frequency(), lev_ac=self.get_ac_level(),
                                    return_sweep=self.get_return_sweep(), npad=1, liveplot=self.get_live_plot())

        if self.get_live_plot():
            self.w = LivePlotWindow(self.measurement)
        else:
            self.measurement.save_results()
