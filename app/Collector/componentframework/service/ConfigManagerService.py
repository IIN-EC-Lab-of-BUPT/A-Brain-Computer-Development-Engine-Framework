import yaml
from injector import inject
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.common.config.componentframeworkconfig import AppConfig
from componentframework.facade.FacadeOperatorInterface import AddListenerOnGlobalConfigCallbackFacadeInterface
from componentframework.facadeImpl.ConfigManagerGrpcFacadeImpl import ConfigManagerGrpcFacadeImpl


class ConfigManagerService:
    @inject
    def __init__(self, config_forwarder: ConfigManagerGrpcFacadeImpl):
        self.send_preliminary_config_result = None
        self.__config_forwarder = config_forwarder

    async def get_global_config(self):
        """
        2.2.1 全局配置读取
        """
        # # 读取/core/config内容并返回配置(string)
        # # 实现代码
        global_config_str = await self.__config_forwarder.get_global_config()
        global_config_dict = yaml.load(global_config_str, Loader=yaml.FullLoader)
        return global_config_dict

    async def add_listener_on_global_config(self, callback):
        """
        2.2.3 全局参数配置更新回调注册
        """

        # 全局配置变更时处理方法注册
        # 输入参数：
        # - config_key: 指定配置更新configKey，可为空，表示监听对应服务所有配置变更
        # - change_type: 参数变化类型，包括创建、更新、删除三种类型，可为空，表示订阅全部情况
        # - callback: 触发回调时的调用方法
        # 实现代码
        # 检查是否已经存在相同的键值对，如果存在则不添加
        class AddListenerOnGlobalConfigCallbackOperatorOperator(AddListenerOnGlobalConfigCallbackFacadeInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        service_operator = AddListenerOnGlobalConfigCallbackOperatorOperator()
        await self.__config_forwarder.add_listener_on_global_config(service_operator)

    async def update_global_config(self, config_dict):
        """
        2.2.10 手动更新全局配置
        """
        # 修改指定全局配置信息
        # 输入参数：
        # - config_key: 指定配置更新configKey
        # - config_value: 修改的配置内容
        # 实现代码
        update_global_config_yaml_str = yaml.dump(config_dict)
        result = await self.__config_forwarder.update_global_config(update_global_config_yaml_str)
        return result

    async def cancel_add_listener_on_global_config(self) -> StatusEnum:
        cancel_add_listener_on_global_config_result = \
            await self.__config_forwarder.cancel_add_listener_on_global_config()
        return cancel_add_listener_on_global_config_result

    async def startup(self, component_startup_configuration):
        await self.__config_forwarder.startup(component_startup_configuration)
