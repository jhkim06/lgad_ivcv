from drivers.Keithley6487 import Keithley6487
from drivers.WayneKerr4300 import WayneKerr4300
from drivers.liveplot import FuncAnimationDisposable

import os
import sys
import time
import threading
import numpy as np
import pyvisa
import signal
import matplotlib as mp
import pylab as plt
from util import mkdir, getdate

mp.rcParams.update({'font.size': 15})  # FIXME


# TODO make this module using Class
n_data_points = -1
Vpau_arr = []
Ipau_arr = []
CV_arr = []
RV_arr = []
_sensor_name = ''
_vi = 0
_vf = -50
_frequency = 1000
_lev_ac = 0.1
_npad = 1
_return_sweep = False
measurement_started = False
measurement_finished = False
thread_measurement = None
pau = None
lcr = None
out_dir = ''
date = None


def get_data():
    if len(CV_arr) == n_data_points:
        return None
    else:
        out = np.column_stack((Vpau_arr, Ipau_arr, RV_arr, CV_arr))
        return out


def get_out_dir_path():
    global out_dir
    return out_dir


def init(pau_addr, lcr_addr, sensor_name):
    global pau, lcr, _sensor_name
    global n_data_points
    global measurement_started, measurement_finished
    n_data_points = -1
    Vpau_arr.clear()
    Ipau_arr.clear()
    CV_arr.clear()
    RV_arr.clear()
    _sensor_name = sensor_name
    measurement_started = False
    measurement_finished = False

    make_out_dir()

    # Connect to source meters
    pau = Keithley6487()
    lcr = WayneKerr4300()
    pau.open(pau_addr)
    lcr.open(lcr_addr)

    # Initialize source meters
    pau.initialize()

    lcr.initialize()
    lcr.set_dc_voltage(0)

    # Communicate with source meters
    pau.get_idn()
    lcr.get_idn()
    return pau, lcr


def measure_cv(vi, vf, vstep, v0, v1, freq, lev_ac, return_sweep, npad, liveplot):
    global n_data_points, thread_measurement, _vi, _vf, _npad, _frequency, _lev_ac, _return_sweep
    global pau, lcr
    pau.set_current_limit(10e-6)
    _vi = vi
    _vf = vf
    _npad = npad
    _frequency = freq
    _return_sweep = return_sweep
#    lcr.read_termination  = '\n'  # FIXME
#    lcr.write_termination = '\n'


    # Safe escaper
    def handler(signum, frame):
        print("User interrupt... Turning off the output ...")
        pau.set_voltage(0)
        pau.set_output('OFF')
        pau.close()
        lcr.set_output('OFF')
        lcr.set_dc_voltage(0)
        lcr.close()
        print("WARNING: Please make sure the output is turned off!")
        exit(1)
    signal.signal(signal.SIGINT, handler)

    # Set range of voltage
    npts = abs(int(vf-vi))+1
    Varr = np.linspace(vi, vf, npts)
    if (v0 is not None) and (v1 is not None):   #FIXME
        if (v0 > vf) and (v1 > vf):
            VarrL = Varr[Varr > v0]
            VarrH = Varr[Varr < v1]
            VarrM = np.linspace(v0, v1, npts)
            Varr  = np.concatenate([VarrL, VarrM, VarrH])
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])
    print(Varr)
    n_data_points = len(Varr)

    # Turn on the source meter
    pau.set_voltage(0)
    pau.set_output('ON')
    lcr.set_output('ON')
    lcr.set_level(lev_ac)     #FIXME
    lcr.set_freq(freq)
    print('frequency: '+str(freq))
    time.sleep(1)

    # Read the data
    t0 = time.time()

    if liveplot:
        def init():
            points.set_data([], [])
            return points,

        def measure(Varr,
                    _Vpau_arr,
                    _Ipau_arr,
                    _CV_arr,
                    _RV_arr):
             #print("START MEASURE")
             global measurement_started, measurement_finished
             measurement_started = True
             for V in Varr:
                if V > 0:
                    print ("Warning: positive bias is not allowed. Set DC voltage to 0.")
                    V = 0

                pau.set_voltage(V)
                try:
                    # time.sleep(0.01)
                    # pau.query_delay = 10
                    Ipau, stat_pau, Vpau = pau.read().split(',')
                except Exception as exception:
                    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    print(type(exception).__name__)
                    # print("SESSION #", pau.session)
                    sys.exit(0)

                Vpau = float(Vpau)
                Ipau = float(Ipau[:-1])

                res = lcr.read_lcr()
                C0, R0 = lcr.read_lcr().split(',')
                try:
                    C0 = float(C0)
                    R0 = float(R0)
                except:
                    break

                _Vpau_arr.append(Vpau)
                _Ipau_arr.append(Ipau)
                _CV_arr.append(C0)
                _RV_arr.append(R0)

                print(V, Vpau, Ipau, C0, R0)
             measurement_finished = True

        def animate(frame, Vpau, CV):
            if len(Vpau) > 0:
                points.set_data(Vpau, CV)
                ax_rt.relim()
                ax_rt.autoscale()

            if len(Vpau) == len(Varr):
                raise StopIteration
            return points,

        thread_measurement = threading.Thread(target=measure,
                                              args=(Varr,
                                                    Vpau_arr,
                                                    Ipau_arr,
                                                    CV_arr,
                                                    RV_arr))
        thread_measurement.start()

        if __name__ == "__main__":
            fig_rt, ax_rt = plt.subplots()
            ax_rt.set_ylabel("Pad capacitance (F)")
            points, = ax_rt.plot([], [], 'o', color='black')

            ani_ = FuncAnimationDisposable(fig_rt,
                                           animate,
                                           frames=None,
                                           fargs=(Vpau_arr, CV_arr,),
                                           init_func=init,
                                           blit=False,
                                           repeat=False,
                                           auto_close=True)
            plt.show()
    else:
        for V in Varr:
            if V > 0:
                print('Warning: Positive bias is not allowed. Set DC voltage to 0.')
                V =0
            pau.set_voltage(V)
            time.sleep(0.01)
            Ipau, stat_pau, Vpau = pau.read().split(',')

            Vpau = float(Vpau)
            Ipau = float(Ipau[:-1])

            C0, R0 = lcr.read_lcr().split(',') #FIXME
            try:                          #FIXME
                C0 = float(C0)
                R0 = float(R0)
            except:
                break
            Vpau_arr.append(Vpau)
            Ipau_arr.append(Ipau)
            CV_arr.append(C0)
            RV_arr.append(R0)
            print(V, Vpau, Ipau, C0, R0)

    t1 = time.time()

def make_out_dir():
    global out_dir, date, _sensor_name
    cpath = r'C:\LGAD_test\C-V_test'
    date = getdate()
    out_dir = os.path.join(cpath, f'{date}_{_sensor_name}')
    mkdir(out_dir)
    return out_dir

def save_results():
    global pau, lcr, out_dir, date
    global Vpau_arr, CV_arr, RV_arr, Ipau_arr, _sensor_name, _vi, _vf, _npad, _frequency, _return_sweep
    npts = 0
    v0 = 0
    v1 = 1
    if (v0 is not None) and (v1 is not None):
        print(f"   * Bias sweep of {npts} meas between {_vi} and {_vf} with {npts} meas between {v0} and {v1}")
    else:
        print(f"   * Bias sweep of {npts} meas between {_vi} and {_vf}")
    print(f"   * Return sweep: {_return_sweep}")
    # print(f"   * Elapsed time = {t1-t0} s")

    # Turn off the source meters
    pau.set_output('OFF')
    pau.close()
    lcr.set_output('OFF')
    lcr.set_dc_voltage(0)
    lcr.close()

    # Save the data
    fname = f'CV_LCR+PAU_{_sensor_name}_{date}_{_vi}_{_vf}_{_frequency}Hz_pad{_npad}'
    outfname = os.path.join(out_dir, fname)
    uniq = 1
    while os.path.exists(outfname+'.txt'):
        uniq += 1
        outfname = f'{outfname}_{uniq}'

    header = 'Vpau(V)\tC(F)\tR(Ohm)\tIpau(A)'                  # FIXME
    np.savetxt(outfname+'.txt', np.array([Vpau_arr, CV_arr, RV_arr, Ipau_arr]).T, header=header)  # FIXME

    cvplot(outfname+'.txt', _frequency)
    plt.savefig(outfname+'.png')


def cvplot(fname, freq=None):
    try:
        V, C, R = np.genfromtxt(fname).T
    except:
        V, C, R, I = np.genfromtxt(fname).T
    fig, ax1 = plt.subplots()

    if V[1] < 0:
        V = -1 * V
    
    ax1.plot(V, C*1e9, 'x-', color='tab:blue', markersize=5, linewidth=0.5, label="$C$")
    ax1.set_xlabel('Bias (V)')
    ax1.set_ylabel('C (nF)', color='tab:blue')
    ax2 = ax1.twinx()
    ax2.plot(V, R, 'x-', color='tab:red')
    ax2.set_ylabel('R (Ohm)', color='tab:red')
    ax2.set_yscale('log')
    ax3 = ax1.twinx()
    ax3.plot(V, 1/(C)**2, 'x-', color='tab:green', markersize=5, linewidth = 0.5, label="$1/C^2$")
    ax3.set_ylabel('$1/C^2 ($F$^{-2})$', color='tab:green')
    ax3.set_yscale('log')

    fig.tight_layout()


if __name__ == '__main__':

    init(pau_addr='GPIB0::22::INSTR', lcr_addr='USB0::0x0B6A::0x5346::21436652::INSTR')
    measure_cv(vi=0, vf=-60, vstep=1, v0=-15, v1=-25,
               freq=1000, lev_ac=0.1, return_sweep=True, sensorname='FBK_2022v1_35_T9', npad=1, liveplot=True)
    plt.show()
