from PyQt5.QtWidgets import QDialog, QInputDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import IV_SMU_PAU as IVMeasurement
# import test_2 as live_plot
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
                self.ys = raw_data[3]

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

        self.measurement_type = MeasurementType.IV[0]
        self.ui.lineEditMeasurementType.setText(MeasurementType.IV[1])
        self.ui.labelStatus.setText(MeasurementType.IV[1] + " Measurement")

        self.ui.pushButtonMeasurementType.clicked.connect(self.dispmessage)
        self.ui.pushButtonStartMeasurement.clicked.connect(self.measure)
        self.measurement = IVMeasurement
        self.sensor_name = "FBK"
        self.initial_voltage = 0
        self.final_voltage = -250
        self.return_sweep = True
        self.live_plot = True

        self.w = None

        self.show()

    def dispmessage(self):
        measurement_type = (MeasurementType.IV[1], MeasurementType.CV[1], MeasurementType.CF[1])
        measurement_name, ok = QInputDialog.getItem(self, "InputDialog", "List of Measurement",
                                                    measurement_type, 0, False)
        if ok and measurement_name:
            self.ui.lineEditMeasurementType.setText(measurement_name)
            self.ui.labelStatus.setText(measurement_name + " Measurement")
            self.set_measurement_type(measurement_name)

    def set_measurement_type(self, name):
        if name == MeasurementType.IV[1]:
            self.measurement_type = MeasurementType.IV[0]
        elif name == MeasurementType.CV[1]:
            self.measurement_type = MeasurementType.CV[0]
        elif name == MeasurementType.CF[1]:
            self.measurement_type = MeasurementType.CF[0]
        else:
            print(name, " is not a valid")

    def measure(self):

        smu, pau = self.measurement.init(smu_addr='GPIB0::25::INSTR', pau_addr='GPIB0::22::INSTR')
        self.measurement.measure_iv(smu, pau,
                                    vi=0, vf=-10,
                                    vstep=1, compliance=10e-6,
                                    return_sweep=True, sensorname='FBK_2022v1_35_T9', npad=1, liveplot=True)
        self.w = FigureBase(self.measurement)
        # print("Measure...", self.measurement_type)
        # if live_plot == true,
        # request data from live_plot and draw it


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())