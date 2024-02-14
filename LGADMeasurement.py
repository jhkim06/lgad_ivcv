from PyQt5.QtWidgets import QDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import IV_SMU_PAU as IVMeasurement
import CV_LCR_PAU as CVMeasurement
import numpy as np
import pyvisa
from enum import Enum


class MeasurementType(Enum):
    IV = 0
    CV = 1
    CF = 2


class FigureBase(QWidget):
    def __init__(self, measurement):
        super().__init__()

        # Default Figure Setting
        self._number_of_figures = 1
        self._time_scale = 10
        self.xs = list()
        self.ys = list()

        self._measurement = measurement

        self._init_draw()  # create sub plots and call FuncAnimation()
        self._init_ui()
        self.show()

    def __del__(self):
        plt.close()

    # override figure close event from QWidget
    def closeEvent(self, event):
        self.close()

    def _init_ui(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)
        # self.setGeometry(400, 300, 400, 600)

    def _init_draw(self):
        # for PyQt embedding
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # make figure list
        self._plots = list()
        for idx in range(0, self._number_of_figures):
            # able to draw n row 1 col fig
            self._plots.append({"FIGURE": self.fig.add_subplot(self._number_of_figures, 1, idx + 1),
                                'INDEX': list()})
            self._plots[idx]['FIGURE'].clear()

        self.ani = animation.FuncAnimation(fig=self.fig,
                                           func=self.animate,
                                           interval=10,
                                           blit=False,
                                           save_count=100)
        self.canvas.draw()

    def _before_drawing(self):
        raw_data = self._measurement.get_data()
        if raw_data is None:
            self.ani.event_source.stop()
            # request to save results
            self._measurement.save_results()
            self.close()
        else:
            raw_data = np.array(self._measurement.get_data())
            if len(raw_data) == 0:
                self.xs = [0]
                self.ys = [0]
            else:
                raw_data = raw_data.T
                self.xs = raw_data[0]
                self.ys = raw_data[3]  # NOTE input format!

    def animate(self, event):
        self._before_drawing()  # update data

        for item in self._plots:
            item['FIGURE'].clear()
            item['FIGURE'].grid(True)

            item['FIGURE'].plot(self.xs, self.ys)

    def pause(self):
        # self.ani.event_source.stop()
        self.ani.pause()

    def resume(self):
        # self.ani.event_source.start()
        self.ani.resume()

    def close(self):
        self.ani.event_source.stop()
        super().close()


def get_list_of_resources():
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()

    return rlist


class LGADMeasurement(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # connect button to function
        self.ui.pushButtonStartMeasurement.clicked.connect(self._measure)
        self.ui.pushButtonStartMeasurement_CV.clicked.connect(self._measure)
        self.ui.tabWidget.currentChanged.connect(self._current_tab_changed)

        # default measurement
        self.measurement_type = MeasurementType.IV
        self.measurement = None
        self.resource_list = get_list_of_resources()  # FIXME better to request backend
        self.resource1_str = ''
        self.resource2_str = ''
        self._init_gui_options(self.measurement_type)  # set default options
        self._init_gui_options(MeasurementType.CV)
        self.ui.tabWidget.setCurrentIndex(0)
        self.w = None

        self.show()

    def _init_gui_options(self, measurement_type):

        self.sensor_name = "FBK"
        self.voltage_step = 1
        self.return_sweep = True
        self.live_plot = True

        if measurement_type == MeasurementType.IV:
            self.initial_voltage = 0
            self.final_voltage = -250
            self.current_compliance = 1e-5
            self.set_iv_gui_options()

        elif measurement_type == MeasurementType.CV:
            self.initial_voltage = 0
            self.final_voltage = -60
            self.frequency = 1000
            self.lev_ac = 0.1
            self.set_cv_gui_options()
        else:
            print("Unknown measurement type")

    def set_iv_gui_options(self):

        self.set_common_gui_options(self.ui.comboBoxSMU,
                                    self.ui.comboBoxPAU,
                                    self.ui.lineEditSensorName,
                                    self.ui.lineEditInitialVoltage,
                                    self.ui.lineEditFinalVoltage,
                                    self.ui.lineEditVoltageStep,
                                    self.ui.checkBoxReturnSweep,
                                    self.ui.checkBoxLivePlot)
        self.ui.lineEditCurrentCompliance.setText(str(self.current_compliance))

    def set_cv_gui_options(self):

        self.set_common_gui_options(self.ui.comboBoxLCR,
                                    self.ui.comboBoxPAU_CV,
                                    self.ui.lineEditSensorName_CV,
                                    self.ui.lineEditInitialVoltage_CV,
                                    self.ui.lineEditFinalVoltage_CV,
                                    self.ui.lineEditVoltageStep_CV,
                                    self.ui.checkBoxReturnSweep_CV,
                                    self.ui.checkBoxLivePlot_CV)
        self.ui.lineEditFrequency_CV.setText(str(self.frequency))
        self.ui.lineEditLevAC.setText(str(self.lev_ac))

    def set_common_gui_options(self, combobox1, combobox2, sensor_name, initial_voltage, final_voltage,
                               voltage_step, return_sweep, live_plot):

        combobox1.addItems(self.resource_list)
        combobox2.addItems(self.resource_list)
        sensor_name.setText(self.sensor_name)
        initial_voltage.setText(str(self.initial_voltage))
        final_voltage.setText(str(self.final_voltage))
        voltage_step.setText(str(self.voltage_step))
        return_sweep.setChecked(self.return_sweep)
        live_plot.setChecked(self.live_plot)

    def _current_tab_changed(self):
        current_index = self.ui.tabWidget.currentIndex()
        if current_index == 0:
            self.measurement_type = MeasurementType.IV
        elif current_index == 1:
            self.measurement_type = MeasurementType.CV
        elif current_index == 2:
            self.measurement_type = MeasurementType.CF
        else:
            self.measurement_type = MeasurementType.IV
            print("invalid measurement index, set IV measurement")
    
    def _get_common_gui_options(self, combobox1, combobox2, sensor_name, initial_voltage, final_voltage,
                                voltage_step, return_sweep, live_plot):

        self.resource1_str = combobox1.currentText()
        self.resource2_str = combobox2.currentText()
        self.sensor_name = sensor_name.text()
        self.initial_voltage = int(initial_voltage.text())
        self.final_voltage = int(final_voltage.text())
        self.voltage_step = int(voltage_step.text())
        self.return_sweep = return_sweep.isChecked()
        self.live_plot = live_plot.isChecked()

    def _measure(self):
        print('cuurent type', self.measurement_type)
        if self.measurement_type == MeasurementType.IV:
            # print("IV measurment.......")
            self.measurement = IVMeasurement
            # update parameters before starting measurement
            self._get_common_gui_options(self.ui.comboBoxSMU, self.ui.comboBoxPAU,
                                         self.ui.lineEditSensorName,
                                         self.ui.lineEditInitialVoltage,
                                         self.ui.lineEditFinalVoltage,
                                         self.ui.lineEditVoltageStep,
                                         self.ui.checkBoxReturnSweep,
                                         self.ui.checkBoxLivePlot)
            # TODO handle unexpected input cases ex. number string without 'e'
            number_str = self.ui.lineEditCurrentCompliance.text()
            exponent = int(number_str.split('e')[1])
            compliance = pow(10, exponent)
            self.current_compliance = compliance

            self.measurement.init(smu_addr=self.resource1_str, pau_addr=self.resource2_str,
                                  sensor_name=self.sensor_name)
            # show out dir path
            self.measurement.measure_iv(vi=0, vf=self.final_voltage,
                                        vstep=self.voltage_step, compliance=self.current_compliance,
                                        return_sweep=self.return_sweep,
                                        npad=1, liveplot=self.live_plot)
        elif self.measurement_type == MeasurementType.CV:
            # print("CV measurment.......")
            self.measurement = CVMeasurement
            self._get_common_gui_options(self.ui.comboBoxLCR, self.ui.comboBoxPAU_CV,
                                         self.ui.lineEditSensorName_CV,
                                         self.ui.lineEditInitialVoltage_CV,
                                         self.ui.lineEditFinalVoltage_CV,
                                         self.ui.lineEditVoltageStep_CV,
                                         self.ui.checkBoxReturnSweep_CV,
                                         self.ui.checkBoxLivePlot_CV)
            self.frequency = int(self.ui.lineEditFrequency_CV.text())
            self.lev_ac = float(self.ui.lineEditLevAC.text())

            self.measurement.init(pau_addr=self.resource2_str, lcr_addr=self.resource1_str,
                                  sensor_name=self.sensor_name)
            self.measurement.measure_cv(vi=0, vf=self.final_voltage,
                                        vstep=self.voltage_step, v0=-15, v1=-25,
                                        freq=self.frequency, lev_ac=self.lev_ac,
                                        return_sweep=self.return_sweep,
                                        npad=1, liveplot=self.live_plot)

        result_path = self.measurement.get_out_dir_path()
        self.ui.labelStatus.setText(result_path)
        if self.live_plot:
            self.w = FigureBase(self.measurement)  # show live plot, it requests to save results when finished
        else:
            # request to save results
            self.measurement.save_results()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())
