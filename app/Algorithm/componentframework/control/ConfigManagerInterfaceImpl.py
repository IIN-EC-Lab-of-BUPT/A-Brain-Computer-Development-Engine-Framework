import asyncio
from typing import Union
from injector import inject
from componentframework.api.ConfigManagerInterface import ConfigManagerInterface
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnGlobalConfigCallbackInterface
from componentframework.service.ConfigManagerService import ConfigManagerService
from componentframework.service.serviceInterface.ServiceOperatorInterface import \
    AddListenerOnGlobalConfigCallbackServiceInterface


class ConfigManagerInterfaceImpl(ConfigManagerInterface):

    @inject
    def __init__(self, config_forwarder: ConfigManagerService):
        self.get_global_config_result = None
        self.__config_forwarder = config_forwarder

    async def get_global_config(self) -> dict[str, Union[str, dict]]:
        """
        2.2.1 全局配置读取
        """
        # 读取/core/config内容并返回配置（配置以dict[str, Union[str, dict]]的形式返回）
        # 实现代码
        self.get_global_config_result = await self.__config_forwarder.get_global_config()
        return self.get_global_config_result

    async def add_listener_on_global_config(self, callback: AddListenerOnGlobalConfigCallbackInterface) -> None:
        """
        2.2.2 全局参数配置更新回调注册
        """

        # 全局配置变更时处理方法注册
        # 输入参数：
        # - callback: 触发回调时的调用方法
        # 实现代码
        # callback的输入参数：config_dict :dict[str, Union[str, dict]]类型
        class AddListenerOnGlobalConfigCallbackOperator(AddListenerOnGlobalConfigCallbackServiceInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        operator = AddListenerOnGlobalConfigCallbackOperator()
        asyncio.create_task(self.__config_forwarder.add_listener_on_global_config(operator))

    async def update_global_config(self, config_dict: dict[str, Union[str, dict]]) -> StatusEnum:
        """
        2.2.3 手动更新全局配置
        """
        # 修改指定全局配置信息
        # 输入参数：
        # 修改指定全局配置信息
        # config_dict: dict[str, Union[str, dict]]
        # 返回值："配置修改成功通知"：枚举类型
        update_global_config_result = await self.__config_forwarder.update_global_config(config_dict)
        return update_global_config_result

    async def cancel_add_listener_on_global_config(self) -> StatusEnum:
        cancel_add_listener_on_global_config_result = \
            await self.__config_forwarder.cancel_add_listener_on_global_config()
        return cancel_add_listener_on_global_config_result

    async def startup(self, component_startup_configuration):
        await self.__config_forwarder.startup(component_startup_configuration)
