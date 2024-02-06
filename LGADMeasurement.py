from PyQt5.QtWidgets import QDialog, QInputDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# import IV_SMU_PAU as IVMeasurement
import test_2 as live_plot
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
        else:
            raw_data = np.array(self._measurement.get_data())
            if len(raw_data) == 0:
                self.xs = [0]
                self.ys = [0]
            else:
                raw_data = raw_data.T
                self.xs = raw_data[0]
                self.ys = raw_data[1]

    def animate(self, event):
        self._before_drawing()  # update data

        for item in self._plots:
            item['FIGURE'].clear()
            item['FIGURE'].grid(True)

            item['FIGURE'].plot(self.xs,
                                self.ys)

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
        # TODO set measurement_type by the current tab
        # print(self.ui.tabWidget.currentWidget().objectName())
        self.ui.tabWidget.currentChanged.connect(self._currentChanged)

        # default measurement
        self.measurement_type = MeasurementType.IV[0]
        self._init_options(None)
        self.w = None

        self.show()

    def _init_options(self, measurement_type):

        self.measurement = live_plot
        self.sensor_name = "FBK"
        self.initial_voltage = 0
        self.final_voltage = 10
        self.return_sweep = True
        self.live_plot = True

        self.ui.lineEditSensorName.setText(self.sensor_name)
        self.ui.lineEditInitialVoltage.setText(str(self.initial_voltage))
        self.ui.lineEditFinalVoltage.setText(str(self.final_voltage))
        self.ui.checkBoxReturnSweep.setChecked(self.return_sweep)

    def _currentChanged(self):
        current_index = self.ui.tabWidget.currentIndex()
        if current_index == 0:
            self.measurement_type = MeasurementType.IV[0]
            # TODO update self.measurement also
        elif current_index == 1:
            self.measurement_type = MeasurementType.CV[0]
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

        self.final_voltage = int(self.ui.lineEditFinalVoltage.text())
        self.return_sweep = self.ui.checkBoxReturnSweep.isChecked()
        self.measurement.measurement_thread(final_value=self.final_voltage,
                                            return_sweep=self.return_sweep)
        self.w = FigureBase(self.measurement)
        # print("Measure...", self.measurement_type)
        # if live_plot == true,
        # request data from live_plot and draw it


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())