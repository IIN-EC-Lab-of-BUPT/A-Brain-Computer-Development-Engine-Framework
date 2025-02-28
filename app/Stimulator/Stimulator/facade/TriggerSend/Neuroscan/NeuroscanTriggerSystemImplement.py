import ctypes
import time
import os
import threading
from ctypes import windll
from typing import Union

from Stimulator.facade.interface.TriggerSystemInterface import TriggerSendInterface, TriggerSystemInterface


class NeuroscanTriggerSystemImplement(TriggerSendInterface):

    async def shutdown(self) -> None:
        pass

    def __init__(self):
        """
        :param port: neuroscan并口端口号,如:16376
        """
        # 端口
        self.port = None

        # 初始输出trigger
        self.initialOutCode = 0

        self.event = threading.Event()
        self.runFlag = True
        self.timer = threading.Thread(target=self.__reset, args=(self.event,))
        self.__config_dict = {}
        # dll路径
        currentPath = os.path.dirname(__file__)
        self.dllPath = os.path.join(os.path.dirname(currentPath), r'inpoutx64.dll')
        # 加载dll
        try:
            self.parallelPort = windll.LoadLibrary(self.dllPath)
            print('DLL loaded successfully')
        except Exception as e:
            print(f"Failed to load DLL: {e}")



    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)
        self.port = self.__config_dict.get('port', 20472)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)


    async def open(self):
        if self.parallelPort.IsInpOutDriverOpen():
            print('InpOut driver is opened successfully')
        else:
            print('Failed to open InpOut driver')
            return
        self.parallelPort.DlPortWritePortUchar(self.port, self.initialOutCode)
        time.sleep(0.001)
        self.timer.start()


    async def send(self, event):
        """
        :param event: 输入想要输出的trigger值，trigger值应为1~255之间的整数
        :return: None
        """

        try:
            # 拉高电平
            self.parallelPort.DlPortWritePortUchar(self.port, event)
            self.event.set()
            # 短暂延迟，确保信号被检测到
            # time.sleep(0.0001)
            # 拉低电平
            self.parallelPort.DlPortWritePortUchar(self.port, self.initialOutCode)
        except Exception as e:
            print(e)

    async def close(self):
        """
        关闭端口，停止线程
        :return: None
        """
        self.runFlag = False
        self.event.set()

    def __reset(self, event):
        while True:
            event.wait()
            if not self.runFlag:
                break
            time.sleep(0.01)
            self.parallelPort.DlPortWritePortUchar(self.port, self.initialOutCode)
            event.clear()
