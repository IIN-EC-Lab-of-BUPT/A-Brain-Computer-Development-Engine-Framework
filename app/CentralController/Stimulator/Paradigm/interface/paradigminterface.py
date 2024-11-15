from abc import ABC, abstractmethod
from typing import Union

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Common.model.CommonMessageModel import ResultPackageModel, ScorePackageModel
from Stimulator.Paradigm.interface.ProxyInterface import ProxyInterface
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel
from Stimulator.facade.interface.TriggerSystemInterface import TriggerSystemInterface


class ParadigmInterface(ABC):

    def __init__(self):
        self._trigger_send = None
        self._proxy = None

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        """
        初始化刺激文件路径
        获取当次实验起始block_id
        打开触发器
        """
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        """
        修改配置信息
        """
        pass

    @abstractmethod
    async def prepare(self):
        """
        完成一个block实验的准备工作，如：初始化psychopy窗口，生成block的刺激序列等
        """
        pass

    @abstractmethod
    async def run(self):
        """
        完成一个block的范式运行，如：进行40个trial的SSVEP实验等
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        调用该方法可以中断正在运行的run方法
        """
        pass

    @abstractmethod
    async def end(self):
        """
        做一些block结束的善后工作，如发送block结束trigger等
        """
        pass

    @abstractmethod
    async def close(self):
        """
        回收实验初始化时创建的资源，如：Psychopy窗口等
        """
        pass

    @abstractmethod
    async def receive_feedback_message(self, feedback_message: ScorePackageModel):
        """
        接收反馈信息
        """
        pass

    @abstractmethod
    async def receive_random_number_seeds(self, random_number_seeds: RandomNumberSeedsModel):
        """
        接收随机数种子
        """
        pass

    @abstractmethod
    async def set_component_framework(self, component_framework: ComponentFrameworkInterface):
        """
        可以通过self._proxy得到当前实验起始的block
        """
        pass

    async def set_trigger_send(self, trigger_send: TriggerSystemInterface):
        """
        设置触发器发送器
        """
        self._trigger_send = trigger_send

    async def set_proxy(self, proxy: ProxyInterface):
        """
        可以通过self._proxy得到当前实验起始的block
        """
        self._proxy = proxy
