from drivers import gpibbase
from drivers import WayneKerr4300
from drivers import Keithley6487
from drivers import liveplot
import os
import numpy as np
import pylab as plt
import pyvisa
import time
import signal
import matplotlib as mp
from util import mkdir, getdate

mp.rcParams.update({'font.size':15})  #FIXME

def init(pau_addr, lcr_addr):
    global pau, lcr

    # Connect to source meters
#    rm = pyvisa.ResourceManager()
#    rlist = rm.list_resources()
    pau = Keithley6487()
    lcr = WayneKerr4300()
    pau.open(pau_addr)
    lcr.open(lcr_addr)

    pau.initialize()
    pau.write("CURR:RANG 2e-6")
    pau.write("SOUR:VOLT:STAT off")
    pau.write("SOUR:VOLT:RANG 500")
    pau.write("SOUR:VOLT:ILIM 2.5e-5")
    pau.write("FORM:ELEM READ,UNIT,STAT,VSO")

    lcr.write(":MEAS:NUM-OF-TESTS 1")
    lcr.initialize()
    lcr.write(":MEAS:EQU-CCT PAR")
    lcr.write(":MEAS:SPEED MED")
    lcr.set_dc_voltage(0)
    lcr.set_freq(1000)

    pau.get_idn()
    lcr.get_idn()
    return pau, lcr

def measure_cv(pau, lcr, vi, vf, vstep, v0, v1, freq, lev_ac, return_sweep, sensorname, npad, liveplot):
    #FIXME compliance?
    lcr.read_termination  = '\n'  #FIXME
    lcr.write_termination = '\n'

    # Safe escaper
    def handler(signum, frame):
        print ("User interrupt... Turning off the output ...")
        pau.write(":SOUR:VOLT:LEV 0")
        pau.write(":SOUR:VOLT:LEV off")
        lcr.write(":MEAS:BIAS OFF")
        lcr.write(":MEAS:V-BIAS 0V")
        lcr.close()
        print ("WARNING: Please make sure the output is turned off!")
        exit(1)
    signal.signal(signal.SIGINT, handler)

    # Set range of voltage
    npts = abs(int((vf-v1)/2))+1
    Varr = np.linspace(vi, vf, npts)
    if (v0 is not None) and (v1 is not None):   #FIXME
        if (v0 > vf) and (v1 > vf):
            VarrL = Varr[Varr > V2]
            VarrH = Varr[Varr < V3]
            VarrM = np.linspace(V2, V3, npts1)
            Varr  = np.concatenate([VarrL, VarrM, VarrH])
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])
    print(Varr)

    # Turn on the source meter
    pau.write(':SOUR:VOLT 0')
    pau.write(':SOUR:VOLT:STAT ON')
    lcr.write(':MEAS:V-BIAS 0V')
    lcr.write('MEAS:BIAS ON')
    lcr.set_level(lev_ac)     #FIXME  I can't find manual of Wayne kerr 4300
    time.sleep(1)

    # Read the data
    Vpau_arr = []      #FIXME
    Ipau_arr = []
    CV_arr = []
    RV_arr = []
    t0 = time.time()
    for Vdc in Varr:
        if Vdc > 0:
            print('Warning: Positive bias is not allowed. Set DC voltage to 0.')
            Vdc = 0

        pau.write(f':SOUR:VOLT {Vdc}')
        time.sleep(0.01)
        Ipau, stat_pau, Vpau = pau.query(':READ?').split(',')

        Vpau = float(Vpau)
        Ipau = float(Ipau[:-1])

        res = lcr.query('MEAS:TRIG?') #FIXME
        C0, R0 = res.split(',')
        try:                          #FIXME
            C0 = float(C0)
            R0 = float(R0)
        except:
            break
        Vpau_arr.append(Vpau)
        Ipau_arr.append(Ipau)
        CV_arr.append(C0)
        RV_arr.append(R0)

        print(Vdc, Vpau, Ipau, C0, R0)

    t1 = time.time()
    if (v0 is not None) and (v1 is not None):
        print(f"   * Bias sweep of {npts} meas between {vi} and {vf} with {npts} meas between {v0} and {v1}")
    else:
        print(f"   * Bias sweep of {npts} meas between {vi} and {vf}")
    print(f"   * Return sweep: {return_sweep}")
    print(f"   * Elapsed time = {t1-t0} s")

    # Turn off the source meters
    pau.write(':SOUR:VOLT:STAT OFF')
    pau.write(':SOUR:VOLT:STAT OFF')
    pau.close()
    lcr.write(':MEAS:BIAS OFF')
    lcr.write(':MEAS:V-BIAS 0V')
    lcr.close()

    # Save the data
    date  = getdate()
    cpath = r'C:\LGAD_test\C-V_test'

    fname = f'CV_LCR+PAU_{sensorname}_{date}_{vi}_{vf}_{freq}Hz_pad{npad}'
    outfname = os.path.join(cpath, f'{date}_{sensorname}', fname)
    uniq = 1
    while os.path.exists(outfname):
        outfname = f'{outfname}_{uniq}'
        uniq += 1

    header = 'Vpau(V)\tC(F)\tR(Ohm)\tIpau(A)'                  #FIXME
    np.savetxt(outfname+'.txt', np.array([Vpau_arr, CV_arr, RV_arr, Ipau_arr]).T, header=header) #FIXME

    cvplot(arr)
    plt.savefig(outfname+'.png')


def cvplot(fname, freq=None):
    try:
        V, C, R    = np.genfromtxt(fname).T
    except:
        V, C, R, I = np.genfromtxt(fname).T
    fig, ax1 = plt.subplots()

    if (V[1] < 0):
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


if __name__=='__main__':

    init(pau_addr='GPIB0::22::INSTR', lcr_addr='USB0::0x0B6A::0x5346::21436652::INSTR')
    measure_cv(pau, lcr, vi=0, vf=-60, vstep=1, v0=None, v1=None, freq=1000, lev_ac=0.1, return_sweep=True, sensorname='FBK_2022v1_35_T9', npad=1, liveplot=True)
    plt.show()
