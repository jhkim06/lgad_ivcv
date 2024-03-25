from util import USBComm


class SwitchMatrixGUI:
    def __init__(self, combo_box, status_label):

        self.combo_box = combo_box
        self.status_label = status_label

        usb_port = "COM3"
        self.comm = USBComm(usb_port)
        if self.comm.is_connected():
            self.status_label.setText(usb_port + " is connected")
        else:
            self.status_label.setText("Switch matrix is not ready")
            self.combo_box.setEnabled(False)
