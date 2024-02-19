from PyQt5.QtWidgets import QDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import IV_SMU_PAU as IVMeasurement
import CV_LCR_PAU as CVMeasurement
import numpy as np
import pyvisa
from enum import Enum

from IVMeasurementGUI import IVMeasurementGUI
from CVMeasurementGUI import CVMeasurementGUI


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

        self._init_draw()  # create sub-plots and call FuncAnimation()
        self._init_ui()
        self.show()

    def __del__(self):
        plt.close()

    # override figure close event from QWidget
    def close_event(self, event):
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
        self.setWindowTitle("LGAD Measurements")

        # connect button to function
        self.ui.pushButtonStartMeasurement.clicked.connect(self._measure)
        self.ui.pushButtonStartMeasurement_CV.clicked.connect(self._measure)
        # connect function for tab change
        self.ui.tabWidget.currentChanged.connect(self._current_tab_changed)

        # TODO check if switch is available
        self.ui.comboBoxSwitch.setEnabled(False)
        self.ui.comboBoxSwitch.addItems(['1', '2', '3', '4'])

        self.iv_gui = IVMeasurementGUI(self.ui.comboBoxSMU, self.ui.comboBoxPAU,
                                       self.ui.lineEditSensorName,
                                       self.ui.lineEditInitialVoltage, self.ui.lineEditFinalVoltage,
                                       self.ui.lineEditVoltageStep, self.ui.lineEditCurrentCompliance,
                                       self.ui.checkBoxReturnSweep, self.ui.checkBoxLivePlot)

        self.cv_gui = CVMeasurementGUI(self.ui.comboBoxLCR, self.ui.comboBoxPAU_CV,
                                       self.ui.lineEditSensorName_CV,
                                       self.ui.lineEditInitialVoltage_CV, self.ui.lineEditFinalVoltage_CV,
                                       self.ui.lineEditVoltageStep_CV, self.ui.lineEditFrequency_CV,
                                       self.ui.lineEditLevAC,
                                       self.ui.checkBoxReturnSweep_CV, self.ui.checkBoxLivePlot_CV)

        # default measurement
        # TODO class for measurement GUI
        # self.IV_GUI
        # backend object
        self.measurement_type = MeasurementType.IV
        self.measurement = None
        self.resource_list = get_list_of_resources()  # FIXME better to request backend
        self._init_gui_options(self.measurement_type)  # set default options
        self._init_gui_options(MeasurementType.CV)
        self.ui.tabWidget.setCurrentIndex(0)
        self.w = None

        self.show()

    def _init_gui_options(self, measurement_type):

        if measurement_type == MeasurementType.IV:
            self.iv_gui.set(self.resource_list, "FBK", 0, -250, 1,
                            1e-5, True, True)

        elif measurement_type == MeasurementType.CV:
            self.cv_gui.set(self.resource_list, "FBK", 0, -60, 1,
                            1000, 0.1, True, True)
        else:
            print("Unknown measurement type")

    # show options in GUI
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
    
    def _measure(self):
        print('current type', self.measurement_type)
        if self.measurement_type == MeasurementType.IV:
            # print("IV measurement.......")
            self.measurement = IVMeasurement
            # update parameters before starting measurement
            options = self.iv_gui.get()

            self.measurement.init(smu_addr=options[0], pau_addr=options[1],
                                  sensor_name=options[2])
            self.measurement.measure_iv(vi=0, vf=options[4],
                                        vstep=options[5], compliance=options[6],
                                        return_sweep=options[7],
                                        npad=1, liveplot=options[8])
        elif self.measurement_type == MeasurementType.CV:
            # print("CV measurement.......")
            self.measurement = CVMeasurement
            options = self.cv_gui.get()

            self.measurement.init(pau_addr=options[1], lcr_addr=options[0],
                                  sensor_name=options[2])
            self.measurement.measure_cv(vi=0, vf=options[4],
                                        vstep=options[5], v0=-15, v1=-25,
                                        freq=options[6], lev_ac=options[7],
                                        return_sweep=options[8],
                                        npad=1, liveplot=options[9])

        result_path = self.measurement.get_out_dir_path()
        self.ui.labelStatus.setText(result_path)
        if self.live_plot:
            self.w = FigureBase(self.measurement)  # show live plot, it requests to save results when finished
        else:
            # request to save results
            self.measurement.save_results()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('images/KCMS.jpeg'))
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())
