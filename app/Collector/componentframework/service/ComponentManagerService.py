import asyncio
from typing import Union
import yaml
from injector import inject
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum
from componentframework.api.model.MessageModel import ComponentModel
from componentframework.common.config.componentframeworkconfig import AppConfig
from componentframework.facade.FacadeOperatorInterface import AddListenerOnRegisterComponentCallbackFacadeInterface, \
    AddListenerOnUpdateComponentInfoCallbackFacadeInterface, AddListenerOnUnregisterComponentCallbackFacadeInterface, \
    AddListenerOnUpdateComponentStateCallbackFacadeInterface
from componentframework.facadeImpl.ComponentManagerFacadeImpl import ComponentManagerFacadeImpl
from componentframework.api.Enum.StatusEnum import StatusEnum


class ComponentManagerService(object):
    @inject
    def __init__(self, component_forwarder: ComponentManagerFacadeImpl):
        # 初始化操作，可以在这里进行一些初始化设置
        self.cancel_add_listener_on_update_component_state_result = None
        self.cancel_add_listener_on_register_component_result = None
        self.cancel_add_listener_on_update_component_info_result = None
        self.cancel_add_listener_on_unregister_component_result = None
        self.update_component_state_result = None
        self.get_component_state_result = None
        self.get_all_component_result = None
        self.unregister_component_result = None
        self.update_component_info_result = None
        self.get_component_info_result = None
        self.component_register_result = None
        self.__component_forwarder = component_forwarder
        self.app_config = AppConfig()

    async def component_register(self, component_model: ComponentModel):
        """
        2.6.1 组件注册
        """
        # component_id: 本服务组件ID，默认可为空。如果为空则组件框架注册时自动生成32位UUID，并填入
        # component_type: 本服务组件类型，不可为空。例如用于标识具体某支赛队的算法，多个component_id可以对应同一种component_type。
        # component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
        # 返回component_id
        # 注册component时自动注册同名service，其配置信息与component_info完全相同，具体信息记录操作还是在zookeeper中service节点下进行
        # if component_model.component_id is None:
        #     # 如果component_id为None，则在组件框架注册时自动生成一个32位的UUID作为component_id
        #     component_id = uuid4().hex
        self.app_config.set_component_id(component_model.component_id)
        # component_info_yaml_str = yaml.dump(component_model.component_info)
        # component_model.component_info = component_info_yaml_str
        self.component_register_result = await self.__component_forwarder.component_register(component_model)
        return self.component_register_result

    async def get_component_info(self, component_id: str = None) -> ComponentModel:
        """
        2.6.2 获取指定组件信息
        """
        # 注册中心中，获取指定组件信息
        # 输入参数：
        # - component_id: 指定组件ID，如果为空，则指代本组件自身
        # 返回参数：
        # - GetComponentInfoModel:
        # component_id: 本服务组件ID，默认可为空。如果为空则组件框架注册时自动生成32位UUID，并填入
        # component_type: 本服务组件类型，不可为空。例如用于标识具体某支赛队的算法，多个component_id可以对应同一种component_type。
        # component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
        if component_id is None:
            component_id = self.app_config.component_id
        self.get_component_info_result = await self.__component_forwarder.get_component_info(component_id)
        # component_info_back_data = yaml.load(self.get_component_info_result, Loader=yaml.FullLoader)
        return self.get_component_info_result

    async def add_listener_on_register_component(self, callback) -> None:
        """
        2.6.3 组件注册监听回调
        """

        # callback包含输入参数
        # component_id: str, component_type: str, component_info: dict[str, Union[str, dict]]
        # callback无需返回
        class AddListenerOnRegisterComponentCallbackOperator(AddListenerOnRegisterComponentCallbackFacadeInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                final_result = await self.__operator.run(result)
                return final_result

        operator = AddListenerOnRegisterComponentCallbackOperator()
        await self.__component_forwarder.add_listener_on_register_component(operator)

    async def update_component_info(self, component_info: dict[str, Union[str, dict]],
                                    component_id: str = None) -> StatusEnum:
        """
        2.6.4 修改组件配置信息
        """
        # 修改component_info: dict，
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # component_info: dict[str, Union[str, dict]]
        # 更新的组件信息
        # 返回更新成功枚举
        if component_id is None:
            component_id = self.app_config.component_id
        update_component_info_yaml_str = yaml.dump(component_info)
        self.update_component_info_result = await self.__component_forwarder.update_component_info(
            update_component_info_yaml_str, component_id)
        return self.update_component_info_result

    async def add_listener_on_update_component_info(self, callback, component_id=None) -> None:
        """
        2.6.5 监听组件组件配置信息更新回调
        """

        # callback包含输入参数
        # component_id: str, component_info: dict[str, Union[str, dict]]
        # callback
        # 无需返回
        class AddListenerOnUpdateComponentInfoCallbackOperator(AddListenerOnUpdateComponentInfoCallbackFacadeInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        operator = AddListenerOnUpdateComponentInfoCallbackOperator()
        if component_id is None:
            component_id = self.app_config.component_id
        await self.__component_forwarder.add_listener_on_update_component_info(operator, component_id)

    async def unregister_component(self) -> StatusEnum:
        """
        2.6.6 本组件注销
        """
        # 返回值：注销成功枚举
        self.unregister_component_result = await self.__component_forwarder.unregister_component()
        return self.unregister_component_result

    async def add_listener_on_unregister_component(self, callback):
        """
        2.6.7 组件注销监听
        """

        # 组件注销监听
        # callback包含输入参数
        # component_id : str, component_type: str, component_info : dict
        # callback 无需返回
        class AddListenerOnUnregisterComponentCallbackOperator(AddListenerOnUnregisterComponentCallbackFacadeInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        operator = AddListenerOnUnregisterComponentCallbackOperator()
        asyncio.create_task(
            self.__component_forwarder.add_listener_on_unregister_component(operator))

    async def get_all_component(self) -> list:
        """
        2.6.8 获取所有组件信息
        """
        # 返回值：component_id的list列表
        self.get_all_component_result = await self.__component_forwarder.get_all_component()
        return self.get_all_component_result

    async def get_component_state(self, component_id: str = None) -> ComponentStatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.get_component_state_result = await self.__component_forwarder.get_component_state(component_id)
        return self.get_component_state_result

    async def add_listener_on_update_component_state(self, callback, component_id: str = None) -> None:
        class AddListenerOnUpdateComponentStateOperator(AddListenerOnUpdateComponentStateCallbackFacadeInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        operator = AddListenerOnUpdateComponentStateOperator()
        if component_id is None:
            component_id = self.app_config.component_id
        asyncio.create_task(
            self.__component_forwarder.add_listener_on_update_component_state(operator, component_id))

    async def update_component_state(self, component_status: ComponentStatusEnum,
                                     component_id: str = None) -> StatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.update_component_state_result = await self.__component_forwarder.update_component_state(component_status,
                                                                                                     component_id)
        return self.update_component_state_result

    async def cancel_add_listener_on_unregister_component(self, component_id: str = None) -> StatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.cancel_add_listener_on_unregister_component_result = await (self.__component_forwarder.
                                                                         cancel_add_listener_on_unregister_component
                                                                         (component_id))
        return self.cancel_add_listener_on_unregister_component_result

    async def cancel_add_listener_on_update_component_info(self, component_id: str = None) -> StatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.cancel_add_listener_on_update_component_info_result = await (self.__component_forwarder.
                                                                          cancel_add_listener_on_update_component_info
                                                                          (component_id))
        return self.cancel_add_listener_on_update_component_info_result

    async def cancel_add_listener_on_register_component(self, component_id: str = None) -> StatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.cancel_add_listener_on_register_component_result = await (self.__component_forwarder.
                                                                       cancel_add_listener_on_register_component
                                                                       (component_id))
        return self.cancel_add_listener_on_register_component_result

    async def cancel_add_listener_on_update_component_state(self, component_id: str = None) -> StatusEnum:
        if component_id is None:
            component_id = self.app_config.component_id
        self.cancel_add_listener_on_update_component_state_result = await (self.__component_forwarder.
                                                                           cancel_add_listener_on_update_component_state
                                                                           (component_id))
        return self.cancel_add_listener_on_update_component_state_result

    async def startup(self, component_startup_configuration):
        await self.__component_forwarder.startup(component_startup_configuration)
