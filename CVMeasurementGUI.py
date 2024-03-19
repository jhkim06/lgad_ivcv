import time

from CVMeasurementBackEnd import CVMeasurementBackend
from LivePlotWindow import LivePlotWindow
from util import BaseThread


def test_func():
    print("test function")


class CVMeasurementGUI:

    def __init__(self, combo_box_lcr, combo_box_pau,
                 line_edit_sensor_name, line_edit_initial_voltage, line_edit_final_voltage,
                 line_edit_voltage_step, line_edit_frequency,
                 ac_level,
                 check_box_return_sweep, check_box_live_plot,
                 button_measure, label_status):

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
        self.button_measure = button_measure
        self.button_measure.setCheckable(True)
        self.button_measure.clicked.connect(self.control_measurement)
        self.label_status = label_status

        self.resource_map = None

        self.measurement = CVMeasurementBackend()
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

    def set(self, resource_map, sensor_name, initial_voltage, final_voltage, voltage_step,
            frequency, ac_level, live_plot, return_sweep):
        self.resource_map = resource_map
        self.set_combo_box_items([*self.resource_map.keys()])
        self.set_sensor_name(sensor_name)
        self.set_initial_voltage(initial_voltage)
        self.set_final_voltage(final_voltage)
        self.set_voltage_step(voltage_step)
        self.set_frequency(frequency)
        self.set_ac_level(ac_level)
        self.set_live_plot(live_plot)
        self.set_return_sweep(return_sweep)

    def get_lcr_addr(self):
        id_name = self.combo_box_lcr.currentText()
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

    def get_frequency(self):
        return int(self.line_edit_frequency.text())

    def get_ac_level(self):
        return float(self.line_edit_ac_level.text())

    def get_live_plot(self):
        return self.check_box_live_plot.isChecked()

    def get_return_sweep(self):
        return self.check_box_return_sweep.isChecked()

    def get(self):
        smu = self.get_lcr_addr()
        pau = self.get_pau_addr()
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

    def control_measurement(self):
        if self.button_measure.isChecked():
            print("start measurement btn clicked")
            self.measurement.initialize_measurement(pau_addr=self.get_pau_addr(), lcr_addr=self.get_lcr_addr(),
                                                    sensor_name=self.get_sensor_name())

            # TODO measurement according to switch selection
            self.measurement.set_measurement_options(initial_voltage=0, final_voltage=self.get_final_voltage(),
                                                     voltage_step=self.get_voltage_step(),
                                                     frequency=self.get_frequency(), ac_level=self.get_ac_level(),
                                                     return_sweep=self.get_return_sweep(),
                                                     pad_number=1, live_plot=self.get_live_plot())
            self.label_status.setText("Start measurement...")
            self.measurement.start_measurement()
            self.button_measure.setText("Stop Measurement")

            update_thread = BaseThread(target=self.update_status_label, callback=self.measure_btn_reset)
            update_thread.start()

            if self.get_live_plot():
                # TODO, pass position of main window and use it to draw graph beside the window
                self.w = LivePlotWindow(self.measurement)
            else:
                pass
        else:
            self.stop_measurement()
            self.button_measure.setText("Start Measurement")

    def update_status_label(self):
        status_str = ''
        while self.measurement.is_measurement_in_progress():
            temp_str = self.measurement.get_status_str()
            if status_str != temp_str:
                status_str = temp_str
                self.label_status.setText(status_str)
            time.sleep(0.1)
        self.label_status.setText("CV measurement DONE, output path: " + self.measurement.get_out_dir())

    def measure_btn_reset(self):
        current_text = self.button_measure.text()
        if current_text == "Stop Measurement":
            self.button_measure.setText("Start Measurement")
            self.button_measure.setChecked(False)

    def stop_measurement(self):
        self.measurement.stop_measurement()
        self.w.close()
        self.measure_btn_reset()
