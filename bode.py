from read_data import read_data
from Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope
from jds6600_python.jds6600 import jds6600
from alive_progress import alive_bar
import numpy as np
import time, sys
import matplotlib.pyplot as plt

# ----------------------------
# Define the constants
# ----------------------------

MIN_FREQ = 10
MAX_FREQ = 1000000
NUM_DATAPOINTS = 100
AMPLITUDE = 5

MIN_Y = -30
MAX_Y = 5

# ----------------------------
# Setup the scope
# ----------------------------

SAMPLE_RATE_INDEX = 24
VOLTAGE_RANGE = 0x01
DATA_POINTS = 3 * 1024

scope = Oscilloscope()
scope.setup()
if not scope.open_handle():
    sys.exit()
scope.flash_firmware()
scope.set_interface(1) # choose ISO
scope.set_num_channels(1)
scope.set_sample_rate(SAMPLE_RATE_INDEX)
scope.set_ch1_voltage_range(VOLTAGE_RANGE)
time.sleep(1)


# ----------------------------
# Setup the signal generator
# ----------------------------

jds = jds6600("/dev/ttyUSB0")

jds.setchannelenable(True, False)

jds.setwaveform(1, "SINE")
jds.setoffset(1, 0)
jds.setdutycycle(1, 50)


# ----------------------------
# Define the frequency range
# ----------------------------

FREQS = np.logspace(np.log10(MIN_FREQ), np.log10(MAX_FREQ), NUM_DATAPOINTS)

data = {}
max_values = []

# ----------------------------
# Capture the data
# ----------------------------
with alive_bar(NUM_DATAPOINTS, title='Bode Plot samples') as bar:
    for freq in FREQS:
        jds.setfrequency(1, float(freq))
        
        dataSingle = read_data(scope, DATA_POINTS, VOLTAGE_RANGE, max(1, 20 / freq))
        
        bar()
        
        data[freq] = dataSingle
        max_values.append(np.max(np.abs(data[freq])))
        
        scope.stop_capture()
        
        time.sleep(0.1)

scope.close_handle()

jds.setchannelenable(False, False)

# ----------------------------
# Plot the data
# ----------------------------

fig, ax = plt.subplots()

ax.plot(FREQS, 20 * np.log10([(x * 2) / AMPLITUDE for x in max_values]), '-') # times 2 because the amplitude is peak-to-peak and the max value is peak

ax.set_xscale('log')
ax.set_yscale('linear')
ax.grid(True)
ax.set(xlabel='Frequency [Hz]', ylabel='Gain [dB]', title='Bode Diagram')
ax.set_xlim([MIN_FREQ, MAX_FREQ])
ax.set_ylim([MIN_Y, MAX_Y])

plt.show()
