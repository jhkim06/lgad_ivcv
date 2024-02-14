# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LGADMeasurement_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(723, 460)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(20, 30, 681, 371))
        self.tabWidget.setObjectName("tabWidget")
        self.tabIV = QtWidgets.QWidget()
        self.tabIV.setObjectName("tabIV")
        self.groupBoxIV = QtWidgets.QGroupBox(self.tabIV)
        self.groupBoxIV.setGeometry(QtCore.QRect(10, 20, 651, 311))
        self.groupBoxIV.setObjectName("groupBoxIV")
        self.widget = QtWidgets.QWidget(self.groupBoxIV)
        self.widget.setGeometry(QtCore.QRect(10, 30, 621, 271))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxSMU = QtWidgets.QComboBox(self.widget)
        self.comboBoxSMU.setObjectName("comboBoxSMU")
        self.gridLayout.addWidget(self.comboBoxSMU, 0, 2, 1, 2)
        self.label_10 = QtWidgets.QLabel(self.widget)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 4, 1, 1)
        self.comboBoxPAU = QtWidgets.QComboBox(self.widget)
        self.comboBoxPAU.setObjectName("comboBoxPAU")
        self.gridLayout.addWidget(self.comboBoxPAU, 0, 5, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        self.lineEditInitialVoltage = QtWidgets.QLineEdit(self.widget)
        self.lineEditInitialVoltage.setObjectName("lineEditInitialVoltage")
        self.gridLayout.addWidget(self.lineEditInitialVoltage, 4, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 4, 1, 1)
        self.lineEditFinalVoltage = QtWidgets.QLineEdit(self.widget)
        self.lineEditFinalVoltage.setObjectName("lineEditFinalVoltage")
        self.gridLayout.addWidget(self.lineEditFinalVoltage, 4, 5, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 2)
        self.label_7 = QtWidgets.QLabel(self.widget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 2)
        self.lineEditVoltageStep = QtWidgets.QLineEdit(self.widget)
        self.lineEditVoltageStep.setObjectName("lineEditVoltageStep")
        self.gridLayout.addWidget(self.lineEditVoltageStep, 6, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.widget)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 6, 4, 1, 1)
        self.lineEditCurrentCompliance = QtWidgets.QLineEdit(self.widget)
        self.lineEditCurrentCompliance.setObjectName("lineEditCurrentCompliance")
        self.gridLayout.addWidget(self.lineEditCurrentCompliance, 6, 5, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 7, 1, 1, 1)
        self.checkBoxReturnSweep = QtWidgets.QCheckBox(self.widget)
        self.checkBoxReturnSweep.setObjectName("checkBoxReturnSweep")
        self.gridLayout.addWidget(self.checkBoxReturnSweep, 8, 0, 1, 2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 9, 1, 1, 1)
        self.pushButtonStartMeasurement = QtWidgets.QPushButton(self.widget)
        self.pushButtonStartMeasurement.setEnabled(True)
        self.pushButtonStartMeasurement.setObjectName("pushButtonStartMeasurement")
        self.gridLayout.addWidget(self.pushButtonStartMeasurement, 10, 0, 1, 3)
        self.checkBoxLivePlot = QtWidgets.QCheckBox(self.widget)
        self.checkBoxLivePlot.setObjectName("checkBoxLivePlot")
        self.gridLayout.addWidget(self.checkBoxLivePlot, 8, 4, 1, 1)
        self.lineEditSensorName = QtWidgets.QLineEdit(self.widget)
        self.lineEditSensorName.setObjectName("lineEditSensorName")
        self.gridLayout.addWidget(self.lineEditSensorName, 2, 2, 1, 4)
        self.label_9 = QtWidgets.QLabel(self.widget)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 2)
        self.tabWidget.addTab(self.tabIV, "")
        self.tabCV = QtWidgets.QWidget()
        self.tabCV.setObjectName("tabCV")
        self.groupBoxIV_2 = QtWidgets.QGroupBox(self.tabCV)
        self.groupBoxIV_2.setGeometry(QtCore.QRect(10, 20, 651, 311))
        self.groupBoxIV_2.setObjectName("groupBoxIV_2")
        self.widget1 = QtWidgets.QWidget(self.groupBoxIV_2)
        self.widget1.setGeometry(QtCore.QRect(10, 30, 621, 271))
        self.widget1.setObjectName("widget1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget1)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem5 = QtWidgets.QSpacerItem(20, 7, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 1, 1, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.widget1)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 3)
        self.lineEditSensorName_CV = QtWidgets.QLineEdit(self.widget1)
        self.lineEditSensorName_CV.setObjectName("lineEditSensorName_CV")
        self.gridLayout_2.addWidget(self.lineEditSensorName_CV, 2, 3, 1, 5)
        spacerItem6 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem6, 3, 0, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.widget1)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 4)
        self.lineEditInitialVoltage_CV = QtWidgets.QLineEdit(self.widget1)
        self.lineEditInitialVoltage_CV.setObjectName("lineEditInitialVoltage_CV")
        self.gridLayout_2.addWidget(self.lineEditInitialVoltage_CV, 4, 4, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.widget1)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 4, 5, 1, 2)
        self.lineEditFinalVoltage_CV = QtWidgets.QLineEdit(self.widget1)
        self.lineEditFinalVoltage_CV.setObjectName("lineEditFinalVoltage_CV")
        self.gridLayout_2.addWidget(self.lineEditFinalVoltage_CV, 4, 7, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem7, 5, 0, 1, 2)
        self.label_13 = QtWidgets.QLabel(self.widget1)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 6, 0, 1, 3)
        self.label_14 = QtWidgets.QLabel(self.widget1)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 6, 5, 1, 2)
        self.lineEditFrequency_CV = QtWidgets.QLineEdit(self.widget1)
        self.lineEditFrequency_CV.setObjectName("lineEditFrequency_CV")
        self.gridLayout_2.addWidget(self.lineEditFrequency_CV, 6, 7, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem8, 7, 0, 1, 2)
        self.label_15 = QtWidgets.QLabel(self.widget1)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 8, 0, 1, 2)
        spacerItem9 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem9, 9, 0, 1, 2)
        self.checkBoxReturnSweep_CV = QtWidgets.QCheckBox(self.widget1)
        self.checkBoxReturnSweep_CV.setObjectName("checkBoxReturnSweep_CV")
        self.gridLayout_2.addWidget(self.checkBoxReturnSweep_CV, 10, 0, 1, 4)
        spacerItem10 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem10, 11, 0, 1, 3)
        self.comboBoxPAU_CV = QtWidgets.QComboBox(self.widget1)
        self.comboBoxPAU_CV.setObjectName("comboBoxPAU_CV")
        self.gridLayout_2.addWidget(self.comboBoxPAU_CV, 0, 7, 1, 1)
        self.checkBoxLivePlot_CV = QtWidgets.QCheckBox(self.widget1)
        self.checkBoxLivePlot_CV.setObjectName("checkBoxLivePlot_CV")
        self.gridLayout_2.addWidget(self.checkBoxLivePlot_CV, 10, 5, 1, 2)
        self.pushButtonStartMeasurement_CV = QtWidgets.QPushButton(self.widget1)
        self.pushButtonStartMeasurement_CV.setEnabled(True)
        self.pushButtonStartMeasurement_CV.setObjectName("pushButtonStartMeasurement_CV")
        self.gridLayout_2.addWidget(self.pushButtonStartMeasurement_CV, 12, 0, 1, 4)
        self.label_12 = QtWidgets.QLabel(self.widget1)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 0, 5, 1, 2)
        self.comboBoxLCR = QtWidgets.QComboBox(self.widget1)
        self.comboBoxLCR.setObjectName("comboBoxLCR")
        self.gridLayout_2.addWidget(self.comboBoxLCR, 0, 3, 1, 2)
        self.label_11 = QtWidgets.QLabel(self.widget1)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 3)
        self.lineEditVoltageStep_CV = QtWidgets.QLineEdit(self.widget1)
        self.lineEditVoltageStep_CV.setObjectName("lineEditVoltageStep_CV")
        self.gridLayout_2.addWidget(self.lineEditVoltageStep_CV, 6, 4, 1, 1)
        self.lineEditLevAC = QtWidgets.QLineEdit(self.widget1)
        self.lineEditLevAC.setObjectName("lineEditLevAC")
        self.gridLayout_2.addWidget(self.lineEditLevAC, 8, 4, 1, 1)
        self.tabWidget.addTab(self.tabCV, "")
        self.labelStatus = QtWidgets.QLabel(Dialog)
        self.labelStatus.setGeometry(QtCore.QRect(20, 410, 611, 26))
        self.labelStatus.setText("")
        self.labelStatus.setObjectName("labelStatus")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBoxIV.setTitle(_translate("Dialog", "IV measurement"))
        self.label_10.setText(_translate("Dialog", "PAU"))
        self.label_3.setText(_translate("Dialog", "Sensor Name"))
        self.label.setText(_translate("Dialog", "Initial Voltage (V)"))
        self.label_2.setText(_translate("Dialog", "Final Voltag (V)"))
        self.label_7.setText(_translate("Dialog", "Voltage Step"))
        self.label_8.setText(_translate("Dialog", "Current Compliance"))
        self.checkBoxReturnSweep.setText(_translate("Dialog", "Return Sweep"))
        self.pushButtonStartMeasurement.setText(_translate("Dialog", "Start Measurement"))
        self.checkBoxLivePlot.setText(_translate("Dialog", "Live Plot"))
        self.label_9.setText(_translate("Dialog", "SMU"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabIV), _translate("Dialog", "IV setup"))
        self.groupBoxIV_2.setTitle(_translate("Dialog", "CV measurement"))
        self.label_4.setText(_translate("Dialog", "Sensor Name"))
        self.label_5.setText(_translate("Dialog", "Initial Voltage (V)"))
        self.label_6.setText(_translate("Dialog", "Final Voltag (V)"))
        self.label_13.setText(_translate("Dialog", "Voltage Step"))
        self.label_14.setText(_translate("Dialog", "Frequency"))
        self.label_15.setText(_translate("Dialog", "lev_ac"))
        self.checkBoxReturnSweep_CV.setText(_translate("Dialog", "Return Sweep"))
        self.checkBoxLivePlot_CV.setText(_translate("Dialog", "Live Plot"))
        self.pushButtonStartMeasurement_CV.setText(_translate("Dialog", "Start Measurement"))
        self.label_12.setText(_translate("Dialog", "PAU"))
        self.label_11.setText(_translate("Dialog", "LCR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCV), _translate("Dialog", "CV setup"))
