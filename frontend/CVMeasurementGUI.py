from backend.CVMeasurementBackEnd import CVMeasurementBackend
from frontend.MeasurementGUI import MeasurementGUI
from frontend.MeasurementGUI import LCR_ID, PAU_ID


class CVMeasurementGUI(MeasurementGUI):

    def __init__(self, combo_box_lcr, combo_box_pau,
                 line_edit_sensor_name, combo_box_col_num, combo_box_row_num,
                 line_edit_initial_voltage, line_edit_final_voltage,
                 line_edit_voltage_step, line_edit_frequency,
                 ac_level,
                 check_box_return_sweep, check_box_live_plot,
                 button_measure, label_status):

        super().__init__(line_edit_sensor_name, combo_box_col_num, combo_box_row_num,
                         line_edit_initial_voltage, line_edit_final_voltage,
                         line_edit_voltage_step, check_box_return_sweep, check_box_live_plot,
                         button_measure, label_status)

        # Widgets
        # lcr:
        # pau:
        self.combo_box_lcr = combo_box_lcr
        self.combo_box_pau = combo_box_pau

        self.button_measure.clicked.connect(self.control_measurement)

        # CV specific options
        self.line_edit_frequency = line_edit_frequency
        self.line_edit_ac_level = ac_level

        self.measurement = CVMeasurementBackend()

    def set_frequency(self, current):
        self.line_edit_frequency.setText(str(current))

    def set_ac_level(self, level):
        self.line_edit_ac_level.setText(str(level))

    def set(self, resource_map, sensor_name, initial_voltage, final_voltage, voltage_step,
            frequency, ac_level, live_plot, return_sweep):
        self.resource_map = resource_map
        self.set_combo_box_items(self.combo_box_lcr, self.combo_box_pau,
                                 LCR_ID, PAU_ID)
        self.set_common(sensor_name, initial_voltage, final_voltage, voltage_step,
                        live_plot, return_sweep)

        self.set_frequency(frequency)
        self.set_ac_level(ac_level)

    def get_lcr_visa_resource_name(self):
        idn = self.combo_box_lcr.currentText()
        return self.resource_map[idn]

    def get_pau_visa_resource_name(self):
        idn = self.combo_box_pau.currentText()
        return self.resource_map[idn]

    def get_frequency(self):
        return int(self.line_edit_frequency.text())

    def get_ac_level(self):
        return float(self.line_edit_ac_level.text())

    def get(self):
        smu = self.get_lcr_visa_resource_name()
        pau = self.get_pau_visa_resource_name()
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

    def init_measurement(self):
        self.measurement.initialize_measurement(pau_visa_resource_name=self.get_pau_visa_resource_name(), 
                                                lcr_visa_resource_name=self.get_lcr_visa_resource_name(),
                                                sensor_name=self.get_sensor_name())

    def set_measurement_options(self):
        self.measurement.set_measurement_options(initial_voltage=0, final_voltage=self.get_final_voltage(),
                                                 voltage_step=self.get_voltage_step(),
                                                 frequency=self.get_frequency(), ac_level=self.get_ac_level(),
                                                 return_sweep=self.get_return_sweep(),
                                                 col_number=self.get_col_number(), row_number=self.get_row_number(),
                                                 live_plot=self.get_live_plot())
