from abc import ABC, abstractmethod
from typing import Union
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnGlobalConfigCallbackInterface


class ConfigManagerInterface(ABC):

    @abstractmethod
    async def get_global_config(self) -> dict[str, Union[str, dict]]:
        """
        2.2.1 全局配置读取
        """
        # 读取/core/config内容并返回配置（配置以dict[str, Union[str, dict]]的形式返回）
        # 实现代码
        pass

    @abstractmethod
    async def add_listener_on_global_config(self, callback: AddListenerOnGlobalConfigCallbackInterface) -> None:
        """
        2.2.2 全局参数配置更新回调注册
        """
        # 全局配置变更时处理方法注册
        # 输入参数：
        # - callback: 触发回调时的调用方法
        # 实现代码
        # callback的输入参数：config_dict :dict[str, Union[str, dict]]类型
        pass

    @abstractmethod
    async def update_global_config(self, config_dict: dict[str, Union[str, dict]]) -> StatusEnum:
        """
        2.2.3 手动更新全局配置
        """
        # 修改指定全局配置信息
        # 输入参数：
        # 修改指定全局配置信息
        # config_dict: dict[str, Union[str, dict]]
        # 返回值："配置修改成功通知"：枚举类型
        pass

    @abstractmethod
    async def cancel_add_listener_on_global_config(self) -> StatusEnum:
        """
        2.2.4 取消全局参数配置更新回调注册
        """
        pass

    @abstractmethod
    async def startup(self, component_startup_configuration):
        pass
