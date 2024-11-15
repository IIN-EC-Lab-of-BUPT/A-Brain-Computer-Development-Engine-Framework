from abc import ABC, abstractmethod
from typing import Union

from Algorithm.service.interface.ServiceManagerInterface import CoreControllerInterface
from Task.challenge.interface.ChallengeInterface import ChallengeInterface
from Task.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Task.common.model.SourceModel import SourceModel
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface
from Task.strategies.interface.StrategyInterface import StrategyInterface


class ServiceManagerInterface(ABC):
    """
    服务管理器接口
    """

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass


class StrategyManagerInterface(ServiceManagerInterface):
    """
    策略管理器业务接口
    """

    @abstractmethod
    def get_current_strategy(self) -> StrategyInterface:
        # 获取当前策略
        pass

    @abstractmethod
    def set_core_controller(self, core_controller: CoreControllerInterface):
        pass


class MessageForwarderInterface(MessageForwardApplicationInterface, ServiceManagerInterface):
    """
    数据转发器控制接口
    """

    @abstractmethod
    def set_subscribe_source(self, source_list: list[SourceModel]) -> None:
        pass

    @abstractmethod
    def set_transfer_source(self, source_list: list[SourceModel]) -> None:
        pass

    @abstractmethod
    def set_current_strategy(self, strategy: StrategyInterface):
        pass
    # @abstractmethod
    # def set_system_connector(self, system_connector: SystemConnectorInterface) -> None:
    #     pass
    #
    # @abstractmethod
    # def set_rpc_controller(self, rpc_controller: RpcControllerApplicationInterface) -> None:
    #     pass


class ChallengeManagerInterface(ServiceManagerInterface):
    """
    赛题管理器业务接口
    """

    @abstractmethod
    def get_current_challenge(self) -> ChallengeInterface:
        pass


class CoreControllerInterface(ServiceManagerInterface):
    """
    核心控制器业务接口
    """

    @abstractmethod
    def get_service_status(self) -> ServiceStatusEnum:
        pass

    @abstractmethod
    async def shutdown_and_close_algorithm_system(self):
        pass
