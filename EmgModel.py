import time
import joblib
import numpy as np
from numpy.fft import fft
from scipy.signal import butter, filtfilt
import sklearn
import include


fs = 200
data_len = 50
channel_num = 8


wn = 15  # 截止频率
wn1 = (2 * wn) / fs   # 归一化截止频率
b, a = butter(4, wn1, btype='highpass', analog=False, output='ba')


def HPF(data):
    temp = np.zeros(shape=(channel_num, data_len))
    for i in range(channel_num):
        temp[i] = filtfilt(b, a, data[i])
    return temp


def MAV(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        Sum = 0
        for j in range(data_len):
            Sum += abs(data[i][j])
        result = Sum / data_len
        temp[0][i] = result
    return temp


def RMS(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        Sum = 0
        for j in range(data_len):
            Sum += abs(data[i][j] ** 2)
        result = (Sum / data_len) ** 0.5
        temp[0][i] = result
    return temp


def WL(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        Sum = 0
        for j in range(data_len - 1):
            Sum += abs(data[i][j+1] - data[i][j])
        result = Sum
        temp[0][i] = result
    return temp


def ZO(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        tSignal = np.sign(data[i])
        tSignal[tSignal == 0] = -1  # replace zeros with -1
        zero_crossings = np.where(np.diff(tSignal))[0]
        temp[0][i] = len(zero_crossings)
    return temp


def SSC(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        Sum = 0
        for j in range(data_len-2):
            Sum += abs((data[i][j+1] - data[i][j]) * (data[i][j+1] - data[i][j+2]))
        result = Sum
        temp[0][i] = result
    data = temp
    return data


def MFP(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        data[i] = abs(fft(data[i]) ** 2 / data_len)
        sum1 = 0
        sum2 = 0
        for j in range(data_len):
            for freq in range(0, 100, 2):
                sum1 += (freq * data[i][j]) * 2
                sum2 += (data[i][j]) * 2
        temp[0][i] = sum1 / sum2
    return temp


def MF(data):
    temp = np.zeros(shape=(1, channel_num))
    for i in range(channel_num):
        data[i] = abs(fft(data[i]) ** 2 / data_len)
        sum1 = 0
        for j in range(data_len):
            for freq in range(0, 100, 2):
                sum1 += (data[i][j] * 2)
        temp[0][i] = sum1
    data = temp
    return data


# ss = preprocessing.StandardScaler()
# all_data = ss.fit_transform(all_data)


rf50 = joblib.load('MYO/RF50.model')


def GetGestureCode(flag):
    if flag:
        All_Mav = MAV(include.MyoDataFlow)
        All_RMS = RMS(include.MyoDataFlow)
        All_WL = WL(include.MyoDataFlow)
        # All_ZO = ZO(TestData)
        # All_SSC = SSC(TestData)
        # All_MF = MF(TestData)
        # All_MFP = MFP(TestData)
        all_features = np.concatenate((All_Mav, All_RMS, All_WL), axis=1)
        include.GestureCode = rf50.predict(all_features)[0]
        print(include.GestureCode)

