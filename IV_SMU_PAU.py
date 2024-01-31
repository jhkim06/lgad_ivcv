#import drivers.gpibbase
from drivers.gpibbase import GPIBBase
#from drivers import gpibbase
from drivers.Keithley2400 import Keithley2400
#import drivers.Keithley2400
from drivers.Keithley6487 import Keithley6487
#import drivers.Keithley6487
from drivers.liveplot import FuncAnimationDisposable
#import drivers.liveplot
import os
import sys
import time
import pathlib
#import threading


sys.path.append(pathlib.Path(__file__).parent.resolve())

import numpy as np
import pyvisa
from matplotlib import pyplot as plt
import signal
from util import mkdir, getdate

from matplotlib import animation as ani



def init(smu_addr, pau_addr):
    global smu, pau

    # Connect to source meters
    smu = Keithley2400()
    pau = Keithley6487()
    smu.open(smu_addr)
    pau.open(pau_addr)

    # Initialize source meters
    smu.initialize()
    smu.set_voltage(0)
    smu.set_voltage_range(200)    #FIXME
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
    
    # Safe escaper
    def handler(signum, frame):
        print("User interrupt... Turning off the output ...")
        smu.write(':SOUR:VOLT:LEV 0')
        smu.write('OUTP OFF')
        smu.close()
        pau.close()
        print("WARNING: Please make sure the output is turned off!")
        exit (1)
    signal.signal(signal.SIGINT, handler)

    # Set range of voltage
    npts = abs(int(vf-vi))+1
    Varr = np.linspace(vi, vf, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])
    print(Varr)

    # Trun on the source meter
    smu.write(':SOUR:VOLT:LEV 0')
    smu.write('OUTP ON')
    time.sleep(1)
    print ("\n")

    # Read the data
    arr  = []
    for V in Varr:
        smu.write(f':SOUR:VOLT:LEV {V}')

        Vsmu, Ismu = smu.query(':READ?').split(',')   #FIXME
        Ipau, _, _ = pau.query('READ?').split(',')    #FIXME

        Vsmu = float(Vsmu)
        Ismu = float(Ismu)
        Ipau = float(Ipau[:-1])
        
        print(V, Vsmu, Ismu, Ipau)
        arr.append([V, Vsmu, Ismu, Ipau])

        # Draw live plot
        if liveplot:
            fig_rt, ax_rt = plt.subplots()
            ax_ratio_rt = ax_rt.twinx()
            ax_rt.set_ylabel("Pad current")
            ax_ratio_rt.set_ylabel("Pad Current / Total current")
            ax_ratio_rt.set_ylim(0.0, 1.0)
            points, = ax_rt.plot([], [], 'o', color='black')
            points_ratio, = ax_ratio_rt.plot([], [], 's', color='red')

            def init():
                points.set_data([], [])
                points_ratio.set_data([], [])
                return points, points_ratio,
            def animate(frame, arr):
                if len(arr) > 0:
                    arr_t = np.array(arr).T
                    points.set_data(arr_t[0], arr_t[3])
                    ax_rt.relim()
                    ax_rt.autoscale()

                    ratio = arr_t[3]/arr_t[2]
                    points_ratio.set_data(arr_t[0], ratio)
                    ax_ratio_rt.relim()
                    ax_ratio_rt.autoscale(axis='x')
                if len(arr) == len(Varr):
                    raise StopIteration

                return points,
            ani_ = FuncAnimationDisposable(fig_rt,
                                           animate,
                                           frames=None,
                                           fargs=(arr,),
                                           init_func=init,
                                           blit=False,
                                           repeat=False,
                                           auto_close=True)
            plt.show()

    # Turn off the source meters
    smu.write(':SOUR:VOLT:LEV 0')
    smu.write('OUTP OFF')
    smu.close()
    pau.close()

    # Save the data
    date  = getdate()
    cpath = r'C:\LGAD_test\I-V_test'

    fname = f'IV_SMU+PAU_{sensorname}_{date}_{vi}_{vf}_pad{npad}'
    outfname = os.path.join(cpath, f'{date}_{sensorname}', fname)
    uniq = 1
    while os.path.exists(outfname):
        outfname = f'{outfname}_{uniq}'
        uniq += 1

    header = 'Vsmu(V)\tIsmu(A)\tIpau(A)'            #FIXME
    mkdir(os.path.join(cpath, f'{date}_{sensorname}'))
    np.savetxt(outfname+'.txt', arr, header=header) #FIXME

    ivplot(arr)
    plt.savefig(outfname+'.png')
    plt.figure()
    ivplot(arr, yrange=(-2e-8, 0.5e-8))
    plt.savefig(outfname+'_zoom.png')

def ivplot(arr, yrange=None):
    arr = np.array(arr).T
    V = arr[0]
    I = arr[3]
    I[I>1e37] = min(I)
    plt.plot(arr[0], arr[3])
    if yrange:
        plt.ylim(yrange)


if __name__=='__main__':

    print('HI')
    init(smu_addr='GPIB0::25::INSTR', pau_addr='GPIB0::22::INSTR')
    measure_iv(smu, pau, vi=0, vf=-300, vstep=1, compliance=10e-6, return_sweep=True, sensorname='FBK_2022v1_35_T9', npad=1, liveplot=False)
    plt.show()

