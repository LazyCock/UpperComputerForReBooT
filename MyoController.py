from collections import deque
from threading import Lock
from matplotlib import pyplot as plt
import MYO
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import include


class EmgCollector(MYO.DeviceListener):
    def __init__(self):
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=include.DataLen)

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)

    def on_connected(self, event):
        event.device.stream_emg(True)
        include.Myo_flag = True

    def on_emg(self, event):
        with self.lock:
            self.emg_data_queue.append((event.timestamp, event.emg))


class Myo(object):
    def __init__(self, DataLen, listener):
        # self.MyoDataFlow = np.zeros(shape=(8, 50))
        self.DataLen = DataLen
        self.listener = listener

    def LoadEmgData(self):
        i = 0
        emg_data = self.listener.get_emg_data()
        emg_data = np.array([x[1] for x in emg_data]).T
        for data in emg_data:
            if len(data) < self.DataLen:
                # Fill the left side with zeroes.
                data = np.concatenate([np.zeros(self.DataLen - len(data)), data])
            # include.MyoDataFlow[i].extend(data)
            include.MyoDataFlow[i] = data
            i += 1
            if i == 8:
                i = 0

    def GetEmg(self):
        while True:
            self.LoadEmgData()


def MyoPlot():
    MYO.init(sdk_path=r'D:\嵌入式\ReBooT上位机\myo-sdk-win-0.9.0')
    hub = MYO.Hub()
    listener = EmgCollector()
    with hub.run_in_background(listener.on_event):
        Myo(DataLen=include.DataLen, listener=listener).GetEmg()


# MyoPlot()
