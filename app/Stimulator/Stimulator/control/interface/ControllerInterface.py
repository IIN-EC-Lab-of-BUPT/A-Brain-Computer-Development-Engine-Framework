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


class FeedbackControllerInterface(ControllerInterface, ABC):
    """
    反馈控制器接口
    """
    pass


class RandomNumberSeedsControllerInterface(ControllerInterface, ABC):
    """
    反馈控制器接口
    """
    pass
