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
#sys.path.append(pathlib.Path(__file__).parent.resolve())

# TODO make this module using Class
n_data_points = -1
arr = []
_sensorname = ''
_vi = 0
_vf = -50
_npad = 1
measurement_started = False
measurement_finished = False
thread_measurement = None


def get_data():
    if len(arr) == n_data_points:
        return None
    else:
        return arr


def get_list_of_resources():
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()

    return rlist

def init(smu_addr, pau_addr):
    global smu, pau
    global n_data_points, arr
    global measurement_started, measurement_finished
    n_data_points = -1
    arr.clear()
    measurement_started = False
    measurement_finished = False

    # Connect to source meters
    smu = Keithley2400()
    pau = Keithley6487()
    smu.open(smu_addr)
    pau.open(pau_addr)

    # Initialize source meters
    smu.initialize()
    smu.set_voltage(0)
    smu.set_voltage_range(200)  #FIXME
#    smu.set_current_limit(10e-6)

    pau.reset()
    pau.set_zero() # current range is double counted
    #pau.set_current_range(f'auto')   #FIXME

    # Communicate with source meters
    smu.get_idn()
    pau.get_idn()
    return smu, pau


def measure_iv(smu, pau, vi, vf, vstep, compliance, return_sweep, sensorname, npad, liveplot):
    smu.set_current_limit(compliance)
    global n_data_points, thread_measurement, _sensorname, _vi, _vf, _npad, arr
    _sensorname = sensorname
    _vi = vi
    _vf = vf
    _npad = npad
    
    # Safe escaper
    def handler(signum, frame):
        print("User interrupt... Turning off the output ...")
        smu.set_voltage(0)
        smu.set_output('off')
        smu.close()
        pau.close()
        print("WARNING: Please make sure the output is turned off!")
        exit(1)
    signal.signal(signal.SIGINT, handler)

    # Set range of voltage
    npts = abs(int(vf-vi))+1
    Varr = np.linspace(vi, vf, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])
    print(Varr)
    n_data_points = len(Varr)
    print(n_data_points)

    # Turn on the source meter
    smu.set_voltage(0)
    smu.set_output('on')
    time.sleep(1)
    print ("\n")

    if liveplot:
        def init(): 
            points.set_data([], [])
            points_ratio.set_data([], [])
            return points, points_ratio,

        def measure(Varr, arr_):
            global measurement_started, measurement_finished
            measurement_started = True
            for V in Varr:
                smu.set_voltage(V)
                Vsmu, Ismu = smu.read().split(',')
                Ipau, _, _ = pau.read().split(',')
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

            if len(arr_) == len(Varr):
                raise StopIteration

            return points,

        thread_measurement = threading.Thread(target=measure, args=(Varr, arr))
        thread_measurement.start()

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
        for V in Varr:
            smu.set_voltage(V)

            Vsmu, Ismu = smu.read().split(',')   #FIXME
            Ipau, _, _ = pau.read().split(',')    #FIXME

            Vsmu = float(Vsmu)
            Ismu = float(Ismu)
            Ipau = float(Ipau[:-1])
        
            print(V, Vsmu, Ismu, Ipau)
            arr.append([V, Vsmu, Ismu, Ipau])


def save_results():
    global arr, _sensorname, _vi, _vf, _npad

    # Turn off the source meters
    smu.set_voltage(0)
    smu.set_output('off')
    smu.close()
    pau.close()

    # Save the data
    date  = getdate()
    cpath = r'C:\LGAD_test\I-V_test'

    fname = f'IV_SMU+PAU_{_sensorname}_{date}_{_vi}_{_vf}_pad{_npad}'
    outfname = os.path.join(cpath, f'{date}_{_sensorname}', fname)
    uniq = 1
    while os.path.exists(outfname+'.txt'):
        uniq += 1
        outfname = f'{outfname}_{uniq}'

    header = 'Vsmu(V)\tIsmu(A)\tIpau(A)'            #FIXME
    mkdir(os.path.join(cpath, f'{date}_{_sensorname}'))
    np.savetxt(outfname+'.txt', arr, header=header) #FIXME

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

    init(smu_addr='GPIB0::25::INSTR', pau_addr='GPIB0::22::INSTR')
    measure_iv(smu, pau,
               vi=0, vf=-30,
               vstep=1, compliance=10e-6,
               return_sweep=True, sensorname='FBK_2022v1_35_T9', npad=1, liveplot=True)
    plt.show()

