from drivers.gpibbase import GPIBBase
from drivers.Keithley2400 import Keithley2400
from drivers.Keithley6487 import Keithley6487
from drivers.liveplot import FuncAnimationDisposable

import os
import sys
import time
import pathlib
import threading
import numpy as np
import pyvisa
import signal
from matplotlib import animation as ani
from matplotlib import pyplot as plt
from util import mkdir, getdate
# sys.path.append(pathlib.Path(__file__).parent.resolve())

# TODO make this module using Class
n_data_points = -1
arr = []
_sensor_name = ''
_vi = 0
_vf = -50
_npad = 1
measurement_started = False
measurement_finished = False
thread_measurement = None
_smu = None
_pau = None
out_dir = ''
date = None


def get_data():
    if len(arr) == n_data_points:
        return None
    else:
        return arr


def get_out_dir_path():
    global out_dir
    return out_dir


def init(smu_addr, pau_addr, sensor_name):
    global _smu, _pau, _sensor_name
    global n_data_points, arr
    global measurement_started, measurement_finished
    n_data_points = -1
    arr.clear()
    _sensor_name = sensor_name
    measurement_started = False
    measurement_finished = False

    make_out_dir()

    # Connect to source meters
    _smu = Keithley2400()
    _pau = Keithley6487()
    _smu.open(smu_addr)
    _pau.open(pau_addr)

    # Initialize source meters
    _smu.initialize()
    _smu.set_voltage(0)
    _smu.set_voltage_range(200)  # FIXME
#    smu.set_current_limit(10e-6)

    _pau.reset()
    _pau.set_zero()  # current range is double counted
    # pau.set_current_range(f'auto')   # FIXME

    # Communicate with source meters
    _smu.get_idn()
    _pau.get_idn()
    return _smu, _pau


def measure_iv(vi, vf, vstep, compliance, return_sweep, npad, liveplot):
    global n_data_points, thread_measurement, _sensor_name, _vi, _vf, _npad, arr
    global _smu, _pau
    _smu.set_current_limit(compliance)
    _vi = vi
    _vf = vf
    _npad = npad
    
    # Safe escaper
    def handler(signum, frame):
        print("User interrupt... Turning off the output ...")
        _smu.set_voltage(0)
        _smu.set_output('off')
        _smu.close()
        _pau.close()
        print("WARNING: Please make sure the output is turned off!")
        exit(1)
    signal.signal(signal.SIGINT, handler)

    # Set range of voltage
    npts = abs(int(vf-vi))+1
    v_arr = np.linspace(vi, vf, npts)
    if return_sweep:
        v_arr = np.concatenate([v_arr, v_arr[::-1]])
    print(v_arr)
    n_data_points = len(v_arr)
    print(n_data_points)

    # Turn on the source meter
    _smu.set_voltage(0)
    _smu.set_output('on')
    time.sleep(1)
    print("\n")

    if liveplot:
        def init(): 
            points.set_data([], [])
            points_ratio.set_data([], [])
            return points, points_ratio,

        def measure(v_arr_, arr_):
            global measurement_started, measurement_finished
            measurement_started = True
            for V in v_arr_:
                _smu.set_voltage(V)
                Vsmu, Ismu = _smu.read().split(',')
                Ipau, _, _ = _pau.read().split(',')
                Vsmu = float(Vsmu)
                Ismu = float(Ismu)
                Ipau = float(Ipau[:-1])
                print(V, Vsmu, Ismu, Ipau)
                arr_.append([V, Vsmu, Ismu, Ipau])
            measurement_finished = True

        def animate(frame, arr_):
            # print('length ', len(arr))
            if len(arr_) > 0:
                arr_t = np.array(arr_).T
                points.set_data(arr_t[0], arr_t[3])
                ax_rt.relim()
                ax_rt.autoscale()

                ratio = arr_t[3]/arr_t[2]
                points_ratio.set_data(arr_t[0], ratio)
                ax_ratio_rt.relim()
                ax_ratio_rt.autoscale(axis='x')

            if len(arr_) == len(v_arr):
                raise StopIteration

            return points,

        thread_measurement = threading.Thread(target=measure, args=(v_arr, arr))
        thread_measurement.start()
        # call back!!

        # thread to save results?

        if __name__ == "__main__":
            fig_rt, ax_rt = plt.subplots()
            ax_ratio_rt = ax_rt.twinx()
            ax_rt.set_ylabel("Pad current")
            ax_ratio_rt.set_ylabel("Pad current / Total current")
            ax_ratio_rt.set_ylim(0.0, 1.0)
            points, = ax_rt.plot([], [], 'o', color='black')
            points_ratio, = ax_ratio_rt.plot([], [], 's', color='red')

            ani_ = FuncAnimationDisposable(fig_rt,
                                        animate,
                                        frames=None,
                                        fargs=(arr,),
                                        init_func=init,
                                        blit=False,
                                        repeat=False,
                                        auto_close=True)
            # ani_.save('test.gif', fps=30)
            plt.show()

    else:
        for V in v_arr:
            _smu.set_voltage(V)

            Vsmu, Ismu = _smu.read().split(',')   #FIXME
            Ipau, _, _ = _pau.read().split(',')    #FIXME

            Vsmu = float(Vsmu)
            Ismu = float(Ismu)
            Ipau = float(Ipau[:-1])
        
            print(V, Vsmu, Ismu, Ipau)
            arr.append([V, Vsmu, Ismu, Ipau])


def make_out_dir():
    global out_dir, date, _sensor_name
    cpath = r'C:\LGAD_test\I-V_test'
    date = getdate()
    out_dir = os.path.join(cpath, f'{date}_{_sensor_name}')
    mkdir(out_dir)
    return out_dir


def save_results():
    global arr, _sensor_name, _vi, _vf, _npad, out_dir, date

    # Turn off the source meters
    _smu.set_voltage(0)
    _smu.set_output('off')
    _smu.close()
    _pau.close()

    fname = f'IV_SMU+PAU_{_sensor_name}_{date}_{_vi}_{_vf}_pad{_npad}'
    outfname = os.path.join(out_dir, fname)
    uniq = 1
    while os.path.exists(outfname+'.txt'):
        uniq += 1
        outfname = f'{outfname}_{uniq}'

    header = 'Vsmu(V)\tIsmu(A)\tIpau(A)'            # FIXME
    np.savetxt(outfname+'.txt', arr, header=header)  # FIXME

    plt.figure()
    ivplot(arr)
    plt.savefig(outfname+'.png')
    plt.close()
    plt.figure()
    ivplot(arr, yrange=(-2e-8, 0.5e-8))
    plt.savefig(outfname+'_zoom.png')
    plt.close()


def ivplot(arr, yrange=None):
    arr = np.array(arr).T
    V = arr[0]
    I = arr[3]
    I[I>1e37] = min(I)
    plt.plot(arr[0], arr[3])
    if yrange:
        plt.ylim(yrange)


if __name__=='__main__':

    init(smu_addr='GPIB0::25::INSTR', pau_addr='GPIB0::22::INSTR', sensor_name='FBK')
    measure_iv(vi=0, vf=-30,
               vstep=1, compliance=10e-6,
               return_sweep=True, npad=1, liveplot=True)
    plt.show()
