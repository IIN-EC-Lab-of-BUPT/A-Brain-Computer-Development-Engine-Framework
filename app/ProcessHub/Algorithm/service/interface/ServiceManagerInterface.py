from abc import ABC, abstractmethod
from typing import Union

from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface


class ServiceManagerInterface(ABC):
    """
    服务管理器接口
    """

    @abstractmethod
    async def initial_system(self, config_dict: dict[str, Union[str, dict]] = None):
        pass

    async def receive_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
        # 赛题端提供配置初始化时所调用的方法
        pass

    async def get_config(self) -> dict[str, Union[str, dict]]:
        # 赛题端递归获取当前配置信息，并构建配置树
        pass

    @abstractmethod
    async def startup(self) -> None:
        # 启动服务
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        # 关闭服务
        pass


class ConfigManagerInterface(ServiceManagerInterface):
    """
    配置管理器接口
    """

    @abstractmethod
    def set_config_file_path(self, config_file_path: str) -> None:
        pass

    @abstractmethod
    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        pass


class BusinessManagerInterface(ServiceManagerInterface):
    """
    业务管理器接口
    """

    @abstractmethod
    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        pass


class MethodManagerInterface(ServiceManagerInterface):
    """
    方法管理器接口
    """

    @abstractmethod
    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        pass


class CoreControllerInterface(ServiceManagerInterface):
    """
    核心控制器接口
    """
    @abstractmethod
    async def exit(self):
        """
        彻底退出Algorithm进程
        :return:
        """

    @abstractmethod
    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        pass

    @abstractmethod
    def get_service_status(self) -> ServiceStatusEnum:
        """
        获取当前服务的状态
        :return:
        """
        pass
