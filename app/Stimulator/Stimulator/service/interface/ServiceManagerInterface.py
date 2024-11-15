from abc import ABC, abstractmethod
from typing import Union

from Stimulator.Paradigm.interface.ProxyInterface import ProxyInterface
from Stimulator.Paradigm.interface.paradigminterface import ParadigmInterface
from Stimulator.facade.interface.TriggerSystemInterface import TriggerSystemInterface


class ServiceManagerInterface(ABC):
    """
    服务管理器接口
    """

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        # 启动服务
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        # 关闭服务
        pass


class ConfigManagerInterface(ServiceManagerInterface, ABC):
    """
    配置管理器接口
    """
    pass


class ParadigmManagerInterface(ServiceManagerInterface):
    """
    预处理管理器接口
    """

    @abstractmethod
    def get_paradigm(self) -> ParadigmInterface:
        pass


class TriggerManagerInterface(ServiceManagerInterface):
    """
    接收器管理器接口
    """

    @abstractmethod
    def get_trigger_sender(self) -> TriggerSystemInterface:
        pass


class BusinessManagerInterface(ProxyInterface, ServiceManagerInterface):
    """
    业务管理器接口
    """

    @abstractmethod
    async def start_stimulation_system(self) -> None:
        pass

    @abstractmethod
    async def stop_stimulation_system(self):
        pass

    @abstractmethod
    async def set_feedback_control_message(self, FeedbackControlModel):
        pass

    @abstractmethod
    def set_paradigm_manager(self, paradigm_manager: ParadigmManagerInterface):
        pass

    @abstractmethod
    def set_trigger_manager(self, trigger_manager: TriggerManagerInterface):
        pass

    @abstractmethod
    async def set_random_number_seeds(self, random_number_seeds_model):
        pass

