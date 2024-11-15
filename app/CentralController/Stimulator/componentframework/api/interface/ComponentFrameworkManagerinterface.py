from abc import ABC, abstractmethod
from componentframework.api.ComponentManagerInterface import ComponentManagerInterface
from componentframework.api.ConfigManagerInterface import ConfigManagerInterface
from componentframework.api.ConnectManagerInterface import ConnectManagerInterface
from componentframework.api.MessageManagerInterface import MessageManagerInterface
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.model.ComponentStartupConfigurationModel import ComponentStartupConfigurationModel


class ComponentFrameworkManagerInterface(ABC):

    @abstractmethod
    def initial(self) -> None:
        """初始化"""
        pass

    @abstractmethod
    async def startup(self, component_startup_configuration: ComponentStartupConfigurationModel) -> StatusEnum:
        """启动"""
        # 返回值："启动成功通知"：枚举类型
        pass

    @abstractmethod
    def get_config_manager(self) -> ConfigManagerInterface:
        pass

    @abstractmethod
    def get_message_manager(self) -> MessageManagerInterface:
        pass

    @abstractmethod
    def get_component_manager(self) -> ComponentManagerInterface:
        pass

    @abstractmethod
    def get_connect_manager(self) -> ConnectManagerInterface:
        pass
