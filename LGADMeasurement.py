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


class MeasurementType():
    IV = (0, 'IV')
    CV = (1, 'CV')
    CF = (2, 'CF')


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
        self._init_UI()
        self.show()

    def __del__(self):
        plt.close()

    # override figure close event from QWidget
    def closeEvent(self, event):
        self.close()

    def _init_UI(self):
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
            self.close()
            # request to save results
            self._measurement.save_results()
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


class LGADMeasurement(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # connect button to function
        self.ui.pushButtonStartMeasurement.clicked.connect(self._measure)
        self.ui.pushButtonStartMeasurement_CV.clicked.connect(self._measure)
        # TODO set measurement_type by the current tab
        # print(self.ui.tabWidget.currentWidget().objectName())
        self.ui.tabWidget.currentChanged.connect(self._current_tab_changed)
        # self.get_list_of_resource()

        # default measurement
        self.measurement_type = MeasurementType.IV[0]
        self.measurement = IVMeasurement
        self.resource_list = self.measurement.get_list_of_resources()
        self._init_options(self.measurement_type)
        self._init_options(MeasurementType.CV[0])
        self.ui.tabWidget.setCurrentIndex(0)
        self.w = None

        self.show()

    def set_iv_gui(self):
        self.ui.comboBoxSMU.addItems(self.resource_list)
        self.ui.comboBoxPAU.addItems(self.resource_list)
        self.ui.lineEditSensorName.setText(self.sensor_name)
        self.ui.lineEditInitialVoltage.setText(str(self.initial_voltage))
        self.ui.lineEditFinalVoltage.setText(str(self.final_voltage))
        self.ui.lineEditVoltageStep.setText(str(self.voltage_step))
        self.ui.lineEditCurrentCompliance.setText(str(self.current_compliance))
        self.ui.checkBoxReturnSweep.setChecked(self.return_sweep)
        self.ui.checkBoxLivePlot.setChecked(self.live_plot)

    def set_cv_gui(self):
        self.ui.comboBoxLCR.addItems(self.resource_list)
        self.ui.comboBoxPAU_CV.addItems(self.resource_list)
        self.ui.lineEditSensorName_CV.setText(self.sensor_name)
        self.ui.lineEditInitialVoltage_CV.setText(str(self.initial_voltage))
        self.ui.lineEditFinalVoltage_CV.setText(str(self.final_voltage))
        self.ui.lineEditVoltageStep_CV.setText(str(self.voltage_step))
        self.ui.lineEditFrequency_CV.setText(str(self.frequency))
        self.ui.lineEditLevAC.setText(str(self.lev_ac))
        self.ui.checkBoxReturnSweep_CV.setChecked(self.return_sweep)
        self.ui.checkBoxLivePlot_CV.setChecked(self.live_plot)

    def _init_options(self, measurement_type):

        self.sensor_name = "FBK"
        self.return_sweep = True
        self.live_plot = True
        self.voltage_step = 1
        self.frequency = 1000
        self.lev_ac = 0.1

        if measurement_type == MeasurementType.IV[0]:
            self.initial_voltage = 0
            self.final_voltage = -250
            self.current_compliance = 1e-5

            self.set_iv_gui()

        elif measurement_type == MeasurementType.CV[0]:
            self.initial_voltage = 0
            self.final_voltage = -60

            self.set_cv_gui()
        else:
            print("Unknown measurement type")

    def _current_tab_changed(self):
        current_index = self.ui.tabWidget.currentIndex()
        if current_index == 0:
            self.measurement_type = MeasurementType.IV[0]
            self.measurement = IVMeasurement
        elif current_index == 1:
            self.measurement_type = MeasurementType.CV[0]
            self.measurement = CVMeasurement
        elif current_index == 2:
            self.measurement_type = MeasurementType.CF[0]
        else:
            self.measurement_type = MeasurementType.IV[0]
            print("invalid index")
    
    def set_measurement_type(self, name):
        if name == MeasurementType.IV[1]:
            self.measurement_type = MeasurementType.IV[0]
        elif name == MeasurementType.CV[1]:
            self.measurement_type = MeasurementType.CV[0]
        elif name == MeasurementType.CF[1]:
            self.measurement_type = MeasurementType.CF[0]
        else:
            print(name, " is not a valid")

    def _measure(self):
        print('cuurent type', self.measurement_type)
        if self.measurement_type == MeasurementType.IV[0]:
            print("IV measurment.......")
            # update parameters before starting measurement
            smu_str = self.ui.comboBoxSMU.currentText()
            pau_str = self.ui.comboBoxPAU.currentText()

            # TODO make as function
            self.sensor_name = self.ui.lineEditSensorName.text()
            self.initial_voltage = int(self.ui.lineEditInitialVoltage.text())
            self.final_voltage = int(self.ui.lineEditFinalVoltage.text())
            self.voltage_step = int(self.ui.lineEditVoltageStep.text())
            self.return_sweep = self.ui.checkBoxReturnSweep.isChecked()
            self.live_plot = self.ui.checkBoxLivePlot.isChecked()

            # TODO make as function
            number_str = self.ui.lineEditCurrentCompliance.text()
            exponent = int(number_str.split('e')[1])
            compliance = pow(10, exponent)
            self.current_compliance = compliance

            smu, pau = self.measurement.init(smu_addr=smu_str, pau_addr=pau_str)
            # if liveplot == True, a thread is used for measurement
            self.measurement.measure_iv(smu, pau,
                                        vi=0, vf=self.final_voltage,
                                        vstep=self.voltage_step, compliance=self.current_compliance,
                                        return_sweep=self.return_sweep,
                                        sensorname=self.sensor_name,
                                        npad=1, liveplot=self.live_plot)
        elif self.measurement_type == MeasurementType.CV[0]:
            print("CV measurment.......")
            lcr_str = self.ui.comboBoxLCR.currentText()
            pau_str = self.ui.comboBoxPAU_CV.currentText()

            # TODO make as function
            self.sensor_name = self.ui.lineEditSensorName_CV.text()
            self.initial_voltage = int(self.ui.lineEditInitialVoltage_CV.text())
            self.final_voltage = int(self.ui.lineEditFinalVoltage_CV.text())
            self.voltage_step = int(self.ui.lineEditVoltageStep_CV.text())
            self.frequency = int(self.ui.lineEditFrequency_CV.text())
            self.lev_ac = float(self.ui.lineEditLevAC.text())
            self.return_sweep = self.ui.checkBoxReturnSweep_CV.isChecked()
            self.live_plot = self.ui.checkBoxLivePlot_CV.isChecked()

            pau, lcr = self.measurement.init(pau_addr=pau_str, lcr_addr=lcr_str)
            # if liveplot == True, a thread is used for measurement
            self.measurement.measure_cv(pau, lcr,
                                        vi=0, vf=self.final_voltage,
                                        vstep=self.voltage_step, v0=-15, v1=-25,
                                        freq=self.frequency, lev_ac=self.lev_ac,
                                        return_sweep=self.return_sweep,
                                        sensorname=self.sensor_name,
                                        npad=1, liveplot=self.live_plot)

        if self.live_plot:
            self.w = FigureBase(self.measurement)  # show live plot, it request to save results when finished
        else:
            # request to save results
            self.measurement.save_results()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())