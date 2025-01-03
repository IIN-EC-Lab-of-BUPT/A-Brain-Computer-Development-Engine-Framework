from abc import ABC, abstractmethod
from typing import Union


class ControllerInterface(ABC):
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


class CommandControllerInterface(ControllerInterface, ABC):
    """
    命令控制器接口
    """
    pass


class ExternalTriggerControllerInterface(ControllerInterface, ABC):
    """
    外部触发控制器接口
    """
    pass


class RPCControllerInterface(ControllerInterface, ABC):
    """
    RPC控制器接口
    """
    pass
