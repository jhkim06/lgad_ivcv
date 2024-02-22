from PyQt5.QtWidgets import QDialog
from LGADMeasurement_GUI import *

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

import pyvisa
from enum import Enum

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
        self.ui.comboBoxSwitch.setEnabled(True)
        # TODO request available switches and show them in the combo box
        self.ui.comboBoxSwitch.addItems(['1', '2', '3', '4', '2x2'])

        # initialize GUI for each experiment
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
        self.resource_list = get_list_of_resources()  # FIXME better to request backend
        self._init_gui_options(self.measurement_type)  # set default options
        self._init_gui_options(MeasurementType.CV)
        self.ui.tabWidget.setCurrentIndex(0)

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
        # TODO if switch is available, loop over all switches
        current_gui = None
        if self.measurement_type == MeasurementType.IV:
            # print("IV measurement.......")
            current_gui = self.iv_gui

        elif self.measurement_type == MeasurementType.CV:
            # print("CV measurement.......")
            current_gui = self.cv_gui
        else:
            pass
        current_gui.request_measurement()

        # result_path = self.measurement.get_out_dir_path()
        # self.ui.labelStatus.setText(result_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('images/KCMS.jpeg'))
    w = LGADMeasurement()
    w.show()
    sys.exit(app.exec_())
