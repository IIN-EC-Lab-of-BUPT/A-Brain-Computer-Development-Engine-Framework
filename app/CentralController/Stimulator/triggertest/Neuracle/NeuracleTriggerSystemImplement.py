import sys
import os
from TriggerSystemInterface import TriggerSystemInterface
from Neuracle.triggerBox import *
import time
import threading
from ctypes import *


class NeuracleTriggerSystemImplement(TriggerSystemInterface):

    def __init__(self, triggerBoxHandle:str, port):
        """
        :param triggerBoxHandle: 串口请输入'serial',并口请输入'parallel',输入为字符串格式
        :param port: 串口/并口所对应的端口,如:串口输入'COM3'(字符串格式),并口输入32760
        """
        # trigger box的串口或者并口选择
        self.triggerBoxHandle = triggerBoxHandle

        # 端口
        self.port = port

        # 初始trigger
        self.initialOutCode = 0

        # 串口trigger
        self.serialTrigger = None

        if self.triggerBoxHandle.lower() == 'parallel':
            self.event = threading.Event()
            self.runFlag = True
            self.timer = threading.Thread(target=self.__reset, args=(self.event,))

            currentPath = os.path.dirname(__file__)
            self.dllPath = os.path.join(os.path.dirname(currentPath), r'inpoutx64.dll')
            self.parallelPort = windll.LoadLibrary(self.dllPath)

    def open(self):
        """
        打开串口/并口
        :return: None
        """
        if self.triggerBoxHandle.lower() == 'serial':
            self.serialTrigger = TriggerBox(self.port)
        if self.triggerBoxHandle.lower() == 'parallel':
            if self.parallelPort.IsInpOutDriverOpen():
                print('InpOut driver is opened successfully')
            self.parallelPort.DlPortWritePortUchar(self.port, self.initialOutCode)
            time.sleep(0.02)
            self.timer.start()

    def send(self, event):
        """
        :param event: 输入想要输出的trigger值，trigger值应为1~255之间的整数
        :return: None
        """
        try:
            if self.triggerBoxHandle.lower() == 'serial':
                self.serialTrigger.output_event_data(event)
            if self.triggerBoxHandle.lower() == 'parallel':
                self.parallelPort.DlPortWritePortUchar(self.port, event)
                self.event.set()
        except Exception as e:
            print(e)

    def close(self):
        """
        关闭端口，停止线程
        :return: None
        """
        if self.triggerBoxHandle.lower() == 'serial':
            self.serialTrigger.closeSerial()
        if self.triggerBoxHandle.lower() == 'parallel':
            self.runFlag = False
            self.event.set()

    def __reset(self, event):
        while True:
            event.wait()
            if not self.runFlag:
                break
            time.sleep(0.02)
            self.parallelPort.DlPortWritePortUchar(self.port, self.initialOutCode)
            event.clear()
