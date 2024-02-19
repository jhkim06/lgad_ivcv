from PyQt5.QtWidgets import QDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

import IV_SMU_PAU as IVMeasurement
import CV_LCR_PAU as CVMeasurement
import pyvisa
from enum import Enum

from LivePlotWindow import LivePlotWindow
from IVMeasurementGUI import IVMeasurementGUI
from CVMeasurementGUI import CVMeasurementGUI


class MeasurementType(Enum):
    IV = 0
    CV = 1
    CF = 2


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
        self.measurement_type = MeasurementType.IV
        self.measurement = None
        self.resource_list = get_list_of_resources()  # FIXME better to request backend
        self._init_gui_options(self.measurement_type)  # set default options
        self._init_gui_options(MeasurementType.CV)
        self.ui.tabWidget.setCurrentIndex(0)

        self.w = None
        self.live_plot = False

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
            # TODO self.iv_gui.request_measurement()
            self.measurement = IVMeasurement
            options = self.iv_gui.get()

            self.measurement.init(smu_addr=options[0], pau_addr=options[1],
                                  sensor_name=options[2])
            self.measurement.measure_iv(vi=0, vf=options[4],
                                        vstep=options[5], compliance=options[6],
                                        return_sweep=options[7],
                                        npad=1, liveplot=options[8])
            self.live_plot = options[8]

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
            self.live_plot = options[9]

        result_path = self.measurement.get_out_dir_path()
        self.ui.labelStatus.setText(result_path)

        if self.live_plot:
            self.w = LivePlotWindow(self.measurement)  # show live plot, it requests to save results when finished
        else:
            # request to save results
            self.measurement.save_results()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('images/KCMS.jpeg'))
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())
