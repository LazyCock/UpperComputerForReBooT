# -*- coding: utf-8 -*-
import time
import win32gui
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QWindow, QPixmap
from threading import Thread
from multiprocessing import Process
import sys
import EmgModel
from FlappyBird import flappy
import serial
import MYO
import include
from MyoController import Myo, EmgCollector
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import subprocess


class MySignals(QObject):
    Progress_activate = pyqtSignal(bool, QProgressBar, int)
    GameFlappy_activate = pyqtSignal(bool, int)
    Serial_activate = pyqtSignal(bool, bool)
    MyoVisual_activate = pyqtSignal(bool)
    DevicesDetect_activate = pyqtSignal(bool, bool, bool)
    TxComplete_activate = pyqtSignal(bool)


class MyoQtFigure(FigureCanvas):
    def __init__(self, DataLen):
        self.DataLen = DataLen
        self.figure = plt.figure(figsize=(13, 4.2), dpi=50)
        FigureCanvas.__init__(self, self.figure)  # 初始化父类
        self.figure.subplots_adjust(left=0.1, bottom=None, right=None, top=None, wspace=0.02, hspace=0.2)
        self.CH1 = self.figure.add_subplot(421)
        self.graphs1 = self.CH1.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH2 = self.figure.add_subplot(422)
        self.graphs2 = self.CH2.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH3 = self.figure.add_subplot(423)
        self.graphs3 = self.CH3.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH4 = self.figure.add_subplot(424)
        self.graphs4 = self.CH4.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH5 = self.figure.add_subplot(425)
        self.graphs5 = self.CH5.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH6 = self.figure.add_subplot(426)
        self.graphs6 = self.CH6.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH7 = self.figure.add_subplot(427)
        self.graphs7 = self.CH7.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.CH8 = self.figure.add_subplot(428)
        self.graphs8 = self.CH8.plot(np.arange(self.DataLen), np.zeros(self.DataLen))[0]
        self.FigureList = [self.graphs1, self.graphs2, self.graphs3, self.graphs4,
                           self.graphs5, self.graphs6, self.graphs7, self.graphs8]
        self.axes = [self.CH1, self.CH2, self.CH3, self.CH4, self.CH5, self.CH6, self.CH7, self.CH8]
        [(ax.set_ylim([-100, 100])) for ax in self.axes]
        [ax.set_xticks([]) for ax in self.axes]
        [ax.set_yticks([]) for ax in self.axes]

    def DrawPlot(self):
        for i in range(8):
            self.FigureList[i].set_ydata(include.MyoDataFlow[i])
        plt.draw()

    def ViewEmg(self, flag):
        if flag:
            self.DrawPlot()


class ReBooT(QMainWindow):
    def __init__(self):
        super().__init__()
        # 载入UI界面
        self.gui = uic.loadUi("TestUI.ui")

        # 载入游戏类
        self.GameFlappy = flappy.FlappyBird()

        # 载入设备监听器
        self.DataLen = include.DataLen
        self.listener = EmgCollector()
        self.Myo = Myo(self.DataLen, self.listener)

        # 预设超参数
        self.impedance_flag = False
        self.emotion_flag = False
        self.progress_flag = False
        self.flappy_flag = False
        self.TxComplete_flag = False
        self.RxComplete_flag = False
        self.difficulty = 1

        # 生成信号簇
        self.ProgressBar_signal = MySignals()
        self.ProgressBar_signal.Progress_activate.connect(self.progressBar_handler)
        self.GameFlappy_signal = MySignals()
        self.GameFlappy_signal.GameFlappy_activate.connect(self.flappy_process)
        self.Serial_signal = MySignals()
        self.Serial_signal.Serial_activate.connect(self.Rx_handler)
        self.MyoVisual_signal = MySignals()
        self.MyoVisual_signal.MyoVisual_activate.connect(self.myo_visual_handler)
        self.DevicesDetect_signal = MySignals()
        self.DevicesDetect_signal.DevicesDetect_activate.connect(self.devices_detect_handler)
        self.TxComplete_signal = MySignals()
        self.TxComplete_signal.TxComplete_activate.connect(self.Tx_handler)

        # 添加多任务窗口
        self.TabWindow = QTabWidget(self.gui)
        self.TabWindow.resize(900, 840)
        self.TabWindow.move(30, 10)

        self.extern_exe = win32gui.FindWindowEx(0, 0, 'pygame', 'pygame window')
        self.task1_window = QWindow.fromWinId(self.extern_exe)
        self.task1_window = QWidget.createWindowContainer(self.task1_window)

        # self.tab_1 = QWidget()
        # self.tab_2 = QWidget()
        # self.tab_3 = QWidget()
        # self.tab_4 = QWidget()

        self.TabWindow.addTab(self.task1_window, 'Task1')
        # self.TabWindow.addTab(self.tab_2, 'Task2')
        # self.TabWindow.addTab(self.tab_3, 'Task3')
        # self.TabWindow.addTab(self.tab_4, 'Task4')

        # 暂时不用
        # self.mdi_1 = QMdiArea()
        # self.mdi_2 = QMdiArea()
        # self.mdi_3 = QMdiArea()
        # self.mdi_4 = QMdiArea()
        # self.mdi_1.autoFillBackground()
        # self.mdi_2.autoFillBackground()
        # self.mdi_3.autoFillBackground()
        # self.mdi_4.autoFillBackground()

        # self.sub_window1 = QMdiSubWindow()
        # self.sub_window2 = QMdiSubWindow()
        # self.sub_window3 = QMdiSubWindow()
        # self.sub_window4 = QMdiSubWindow()

        # self.sub_window1.autoFillBackground()
        # self.sub_window2.autoFillBackground()
        # self.sub_window3.autoFillBackground()
        # self.sub_window4.autoFillBackground()

        # self.mdi_1.addSubWindow(self.task1_window)
        # # self.mdi_1.addSubWindow(self.sub_window1)
        # self.mdi_2.addSubWindow(self.sub_window2)
        # self.mdi_3.addSubWindow(self.sub_window3)
        # self.mdi_4.addSubWindow(self.sub_window4)

        # self.tab_1_layout = QFormLayout()
        # self.tab_2_layout = QFormLayout()
        # self.tab_3_layout = QFormLayout()
        # self.tab_4_layout = QFormLayout()

        # self.tab_1_layout.addWidget(self.mdi_1)
        # self.tab_1.setLayout(self.tab_1_layout)

        # 主界面交互控件
        self.gui.button_1.setEnabled(True)
        self.gui.button_2.setEnabled(False)
        self.gui.button_1.clicked.connect(self.button_1_handler)
        self.gui.button_2.clicked.connect(self.button_2_handler)
        self.gui.checkBox_1.stateChanged.connect(self.impedance_handler)
        self.gui.checkBox_2.stateChanged.connect(self.emotion_handler)

        # 难度调整滑块
        self.slider = QSlider(self.gui)
        self.slider.resize(30, 136)
        self.slider.move(1200, 128)
        self.slider.setMinimum(1)
        self.slider.setMaximum(4)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.slider_handler)

        # 设备状态监测类
        self.gui.MainIconLabel.setPixmap(QPixmap(r'Images/MainIcon.png'))
        self.gui.MainIconLabel.setScaledContents(True)
        self.gui.RoboHandIconLabel.setPixmap(QPixmap(r'Images/RoboHand.png'))
        self.gui.RoboHandIconLabel.setScaledContents(True)
        self.gui.RoboHandStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))
        self.gui.RoboHandStateLabel.setScaledContents(True)
        self.gui.MyoIconLabel.setPixmap(QPixmap(r'Images/MYO.png'))
        self.gui.MyoIconLabel.setScaledContents(True)
        self.gui.MyoStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))
        self.gui.MyoStateLabel.setScaledContents(True)
        self.gui.EmotivIconLabel.setPixmap(QPixmap(r'Images/EMOTIV .png'))
        self.gui.EmotivIconLabel.setScaledContents(True)
        self.gui.EmotivStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))
        self.gui.EmotivStateLabel.setScaledContents(True)

        # 初始化实时作图类
        self.MyoQtFigure = MyoQtFigure(include.DataLen)
        self.MyoScene = QGraphicsScene()
        self.MyoScene.addWidget(self.MyoQtFigure)
        self.gui.graphicsView_2.setScene(self.MyoScene)
        self.gui.graphicsView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平方向滚动条
        self.gui.graphicsView_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭竖直方向滚动条
        self.gui.graphicsView_2.show()

        # 下位机通讯接口
        self.SerialPort = serial.Serial('COM7',
                                        baudrate=115200,
                                        bytesize=8,
                                        parity='N',
                                        stopbits=1,
                                        xonxoff=True,
                                        timeout=0.2)
        self.Activation = 100
        self.Emotion = 25
        self.Fd = 60
        self.GestureCode = include.GestureCode
        self.SendList = bytes([221, 221, self.Emotion, self.GestureCode, self.Activation, self.Fd, 255, 255])
        self.ReceiveList = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # 创建多线程
        self.DevicesDetectThread = Thread(target=self.device_detect_thread)
        self.DevicesDetectThread.start()
        self.EmgVisualThread = Thread(target=self.myo_visual_thread)
        self.EmgVisualThread.start()
        self.TxThread = Thread(target=self.Tx_thread)
        self.TxThread.start()
        self.RxThread = Thread(target=self.Rx_thread)
        self.RxThread.start()
        # self.TaskRunThread = Thread(target=self.task_run)
        # self.TaskRunThread.start()
        self.MyoThread = Thread(target=self.myo_thread)
        self.MyoThread.start()

        # 创建多进程
        self.FlappyProcess = Process(target=self.flappy_process, args=(self.flappy_flag, self.difficulty))
        self.FlappyProcess.daemon = True

    # 重定向打印函数
    def printf(self, info):
        self.gui.textBrowser.append(info)
        self.gui.cursor = self.gui.textBrowser.textCursor()
        self.gui.textBrowser.moveCursor(self.gui.cursor.End)
        QtWidgets.QApplication.processEvents()

    # 离线训练模型
    def eeg_model_thread(self):
        if self.emotion_flag:
            pass

    def myo_visual_thread(self):
        while True:
            self.MyoVisual_signal.MyoVisual_activate.emit(True)
            time.sleep(0.1)

    def myo_visual_handler(self, flag):
        self.MyoQtFigure.ViewEmg(flag)

    # 读取MYO数据流
    def myo_thread(self):
        MYO.init(sdk_path=r'D:\嵌入式\ReBooT上位机\myo-sdk-win-0.9.0')
        hub = MYO.Hub()
        with hub.run_in_background(self.listener.on_event):
            self.Myo.GetEmg()

    def button_1_handler(self):
        self.gui.button_1.setEnabled(False)
        self.gui.button_2.setEnabled(True)
        self.gui.checkBox_1.setEnabled(False)
        self.gui.checkBox_2.setEnabled(False)
        self.progress_flag = True
        self.flappy_flag = True
        processBarThread = Thread(target=self.progressBar_thread)
        processBarThread.start()
        FlappyThread = Thread(target=self.flappy_thread)
        FlappyThread.start()
        self.printf('Emotiv未连接.')
        # MyoVisualThread = Thread(target=self.myo_visual_thread)
        # MyoVisualThread.start()
        # MyoThread = Thread(target=self.myo_thread)
        # MyoThread.start()
        self.FlappyProcess.run()

    def button_2_handler(self):
        self.gui.button_2.setEnabled(False)
        self.gui.button_1.setEnabled(True)
        self.gui.checkBox_1.setEnabled(True)
        self.gui.checkBox_2.setEnabled(True)
        self.progress_flag = False
        self.flappy_flag = False
        self.FlappyProcess.run()

    def impedance_handler(self):
        if self.gui.checkBox_1.isChecked():
            self.impedance_flag = True
        else:
            self.impedance_flag = False

    def emotion_handler(self):
        if self.gui.checkBox_2.isChecked():
            self.emotion_flag = True
        else:
            self.emotion_flag = False

    def TaskRun(self, signal):
        pass

    def slider_handler(self):
        if self.emotion_flag:
            if self.slider.value() == 1:
                self.difficulty = 1
            if self.slider.value() == 2:
                self.difficulty = 2
            if self.slider.value() == 3:
                self.difficulty = 3
            if self.slider.value() == 4:
                self.difficulty = 4
        self.GameFlappy_signal.GameFlappy_activate.emit(self.flappy_flag, self.difficulty)

    def progressBar_thread(self):
        i = 0
        while self.progress_flag:
            if i < 300:
                self.ProgressBar_signal.Progress_activate.emit(self.progress_flag, self.gui.progressBar, i)
                i += 1
                time.sleep(0.1)
            if i >= 300:
                self.progress_flag = False
                self.flappy_flag = False
                self.ProgressBar_signal.Progress_activate.emit(self.progress_flag, self.gui.progressBar, i)
                self.GameFlappy_signal.GameFlappy_activate.emit(self.flappy_flag, self.difficulty)
                sys.exit()
        else:
            sys.exit()

    def progressBar_handler(self, count_flag, slot_position, count):
        if count_flag:
            slot_position.setValue(count / 3)
        if not count_flag:
            slot_position.setValue(0)
            self.gui.button_2.setEnabled(False)
            self.gui.button_1.setEnabled(True)
            self.gui.checkBox_1.setEnabled(True)
            self.gui.checkBox_2.setEnabled(True)
            self.GameFlappy_signal.GameFlappy_activate.emit(self.flappy_flag, self.difficulty)

    def flappy_process(self, flag, diff):
        self.GameFlappy.FlappyStart(flag, diff)

    def flappy_thread(self):
        self.GameFlappy_signal.GameFlappy_activate.emit(self.flappy_flag, self.difficulty)

    def Tx_thread(self):
        if self.SerialPort.isOpen():
            include.RoboHand_flag = True
            while True:
                # self.Models()
                self.Activation = 100
                self.Emotion = 25
                self.Fd = 60
                self.GestureCode = include.GestureCode
                SendList = bytes([221, 221, self.Emotion, self.GestureCode, self.Activation, self.Fd, 255, 255])
                self.SerialPort.write(SendList)
                self.TxComplete_flag = True
                self.TxComplete_signal.TxComplete_activate.emit(self.TxComplete_flag)
                if not self.SerialPort.isOpen():
                    include.RoboHand_flag = False
                    break
                time.sleep(0.8)

    def Tx_handler(self, flag):
        EmgModel.GetGestureCode(flag)

    def Rx_thread(self):
        header = 0
        BufferList = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        while True:
            if self.SerialPort.isOpen():
                if self.SerialPort.in_waiting > 0:
                    ReceiveData = int.from_bytes(self.SerialPort.read(), 'little')
                    if ReceiveData == 85:
                        header += 1
                        if header == 2:
                            header = 0
                            for j in range(9):
                                BufferList[j] = int.from_bytes(self.SerialPort.read(), 'little')
                            if BufferList[7] == BufferList[8] == 255:
                                self.ReceiveList = BufferList
                                self.RxComplete_flag = True
                                # print(self.ReceiveList)
            if not self.SerialPort.isOpen():
                include.RoboHand_flag = False
                break

    def Rx_handler(self, RxComplete_flag):
        pass

    def device_detect_thread(self):
        while True:
            self.DevicesDetect_signal.DevicesDetect_activate.emit(include.RoboHand_flag, include.Myo_flag, include.Emotiv_flag)
            time.sleep(3)

    def devices_detect_handler(self, RoboHandFlag, MyoFlag, EmotivFlag):
        if RoboHandFlag:
            self.gui.RoboHandStateLabel.setPixmap(QPixmap(r'Images/enabled.png'))
        if not RoboHandFlag:
            self.gui.RoboHandStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))
        if MyoFlag:
            self.gui.MyoStateLabel.setPixmap(QPixmap(r'Images/enabled.png'))
        if not MyoFlag:
            self.gui.MyoStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))
        if EmotivFlag:
            self.gui.EmotivStateLabel.setPixmap(QPixmap(r'Images/enabled.png'))
        if not EmotivFlag:
            self.gui.EmotivStateLabel.setPixmap(QPixmap(r'Images/disabled.png'))

    def task_run(self):
        if self.impedance_flag is True and self.emotion_flag is True:
            pass
        if self.impedance_flag is True and self.emotion_flag is False:
            pass
        if self.impedance_flag is False and self.emotion_flag is True:
            pass
        if self.impedance_flag is False and self.emotion_flag is False:
            pass


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("icon.png"))
    reboot = ReBooT()
    reboot.gui.show()
    app.exec_()
