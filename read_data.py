#!/usr/bin/python3

from Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope
import matplotlib.pyplot as plt
import sys
import time
import numpy as np
from collections import deque



def read_data(scope: Oscilloscope, data_points: int, voltage_range: int, capture_time: int = 1) -> list:

    data = deque(maxlen=2*1024*1024)
    data_extend = data.extend

    def extend_callback(ch1_data, _):
        data_extend(ch1_data)

    start_time = time.time()
    scope.start_capture()
    shutdown_event = scope.read_async(extend_callback, data_points, outstanding_transfers=10, raw=True)
    while time.time() - start_time < capture_time:
        scope.poll()
    scope.stop_capture()
    
    shutdown_event.set()
    time.sleep(0.1)
    
    scaled_data = scope.scale_read_data(data, voltage_range)
    return scaled_data
    
# plt.plot(np.fft.fft(scaled_data).real)

