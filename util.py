import os
import datetime
import threading
import serial
import re
import numpy as np


def mkdir(path):
    path = os.path.normpath(path)
    path1 = path.split(os.sep) 
    
    for i, _ in enumerate(path1):
        ptmp = os.path.join('c:\\', *(path1[1:i+1]))
        print(ptmp)
        try: 
            os.mkdir(ptmp)
        except: 
            pass
    return


def getdate():
    date = datetime.datetime.today().isoformat()[:10]
    return date


def make_unique_name(file_name):
    uniq = 0
    while os.path.exists(file_name + '.txt'):
        uniq += 1
        file_name = f'{file_name}_{uniq}'
    return file_name


def round_to_significant_figures(x, sig_figs):
    if x == 0:
        return 0
    return round(x, sig_figs - int(np.floor(np.log10(abs(x)))) - 1)


def parse_voltage_steps(input_str):
    # Normalize the input by removing all spaces
    input_str = input_str.replace(' ', '')

    # Define the regular expression pattern
    # The pattern below captures the mandatory number and any number of tuples
    pattern = re.compile(r'^(\d+)(?:,(.*))?$')

    # Match the input string with the pattern
    match = pattern.match(input_str)

    if not match:
        raise ValueError("The input string does not match the expected format.")

    # Extract the mandatory number
    mandatory_number = int(match.group(1))

    # Extract the optional tuples part, if they exist
    tuple_values = []
    if match.group(2):
        tuples_str = match.group(2)
        # Split the tuples_str by '),(' to separate individual tuples
        tuples_str = tuples_str.strip()
        tuples_str = tuples_str.split('),(')

        # Clean up the first and last tuple to remove extra parentheses
        tuples_str[0] = tuples_str[0].strip('(')
        tuples_str[-1] = tuples_str[-1].strip(')')

        # Process each tuple string to convert it into a tuple of integers
        for t_str in tuples_str:
            numbers = list(map(float, t_str.split(',')))
            tuple_values.append(tuple(numbers))

    return mandatory_number, tuple_values

# thread with callback function
class BaseThread(threading.Thread):
    def __init__(self, target, args=(), callback=None, callback_args=()):
        super().__init__(target=self.target_with_callback)
        self.target = target
        self.target_args = args
        self.callback = callback
        self.callback_args = callback_args

    def target_with_callback(self):
        self.target(*self.target_args)
        if self.callback is not None:
            self.callback(*self.callback_args)


class USBComm:

    def __init__(self, port):
        self.port = port
        self.ser = None
        self._connect(self.port)

        self.ser_list = []

    def _connect(self, port):
        try:
            self.ser = serial.Serial(port=port, baudrate=115200, timeout=1)
        except serial.serialutil.SerialException:
            print(port, " is not connected")

    def is_connected(self):
        if self.ser is not None:
            return True
        else:
            return False

    def send_data(self, data):
        self.ser.write(f"{data}\r".encode())
        mes = self.ser.read_until().strip()
        return mes.decode()
