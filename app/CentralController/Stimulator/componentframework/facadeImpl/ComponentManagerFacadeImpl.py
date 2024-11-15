import asyncio
from typing import Any
import yaml
from injector import inject
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum
from componentframework.api.exception.ComponentNotExistException.ComponentNotExistException import \
    ComponentNotExistException
from componentframework.api.exception.ComponentNotExistException.ValueErrorException import ValueErrorException
from componentframework.api.model.MessageModel import ComponentModel
from componentframework.facade.RemoteProcedureCallFacade import RemoteProcedureCallFacade
from componentframework.facadeImpl.grpc_connector import GrpcConnector
from componentframework.facadeImpl.test_grpc import ComponmentManager_pb2_grpc, ComponmentManager_pb2
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.model.MessageOperateModel import AddListenerOnRegisterComponentModel, \
    AddListenerOnUpdateComponentInfoComponentModel, AddListenerOnUnregisterComponentModel, \
    AddListenerOnUpdateComponentStateModel


class ComponentManagerFacadeImpl(RemoteProcedureCallFacade):
    @inject
    def __init__(self, grpc_connector_forwarder: GrpcConnector):
        # 初始化操作，可以在这里进行一些初始化设置
        super().__init__()
        self.component_pattern = None
        self.cancel_add_listener_on_update_component_state_result = None
        self.cancel_add_listener_on_register_component_result = None
        self.cancel_add_listener_on_update_component_info_result = None
        self.cancel_add_listener_on_unregister_component_result = None
        self.update_component_state_result = None
        self.add_listener_on_update_component_state_model = None
        self.get_component_info_model = None
        self.get_all_component_result = None
        self.add_listener_on_unregister_component_model = None
        self.add_listener_on_update_component_info_model = None
        self.add_listener_on_register_component_model = None
        self.stub = None
        self.__grpc_connector_forwarder = grpc_connector_forwarder

    # def get_stub(self):
    #     self.stub = ComponmentManager_pb2_grpc.ComponentManagerServiceStub(
    #         self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类

    async def component_register(self, component_model: ComponentModel):
        """
        2.6.1 组件注册
        """
        # component_id: 本服务组件ID，默认可为空。如果为空则组件框架注册时自动生成32位UUID，并填入
        # component_type: 本服务组件类型，不可为空。例如用于标识具体某支赛队的算法，多个component_id可以对应同一种component_type。
        # component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
        # 返回component_id
        # 注册component时自动注册同名service，其配置信息与component_info完全相同，具体信息记录操作还是在zookeeper中service节点下进行
        component_info_yaml_str = yaml.dump(component_model.component_info)
        request = ComponmentManager_pb2.RegisterComponentRequest(componentType=component_model.component_type,
                                                                 componentInfo=component_info_yaml_str,
                                                                 componentID=component_model.component_id,
                                                                 componentPattern=self.component_pattern)
        response = await self.stub.RegisterComponent(request)
        return ComponentModel(response.componentID, response.componentType, response.componentInfo, )

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
        request = ComponmentManager_pb2.GetComponentInfoRequest(componentID=component_id)
        response = await self.stub.GetComponentInfo(request)
        self.get_component_info_model = ComponentModel()
        self.get_component_info_model.component_id = response.componentID
        self.get_component_info_model.component_type = response.componentType
        component_info_data = yaml.load(response.componentInfo, Loader=yaml.FullLoader)
        self.get_component_info_model.component_info = component_info_data
        return self.get_component_info_model

    async def add_listener_on_register_component(self, callback) -> None:
        """
        2.6.3 组件注册监听回调
        """
        # callback包含输入参数
        # component_id: str, component_type: str, component_info: dict[str, Union[str, dict]]
        # callback无需返回
        # add_listener_on_register_component_model = AddListenerOnRegisterComponentModel()
        request = ComponmentManager_pb2.AddListenerOnRegisterComponentRequest(request='componentId')
        add_listener_on_register_component_callback_stream = self.stub.AddListenerOnRegisterComponent(request)
        async for response in add_listener_on_register_component_callback_stream:
            self.add_listener_on_register_component_model = AddListenerOnRegisterComponentModel()
            self.add_listener_on_register_component_model.component_id = response.componentId
            self.add_listener_on_register_component_model.component_type = response.componentType
            add_listener_on_register_component_data = yaml.load(response.componentInfo, Loader=yaml.FullLoader)
            self.add_listener_on_register_component_model.component_info = add_listener_on_register_component_data
            result = await callback.run(self.add_listener_on_register_component_model)
            update_component_info_yaml_str = yaml.dump(result.component_info)
            request = ComponmentManager_pb2.ConfirmRegisterComponentRequest(componentID=result.component_id,
                                                                            componentType=result.component_type,
                                                                            componentInfo=update_component_info_yaml_str)
            await self.stub.ConfirmRegisterComponent(request)
            await asyncio.sleep(0)

    async def update_component_info(self, component_info: str, component_id: str = None) -> StatusEnum:
        """
        2.6.4 修改组件配置信息
        """
        # 修改component_info: dict，
        #  - component_id: 指定组件ID，如果为空，则指代本组件自身
        # component_info: dict[str, Union[str, dict]]
        # 更新的组件信息
        # 返回更新成功枚举
        request = ComponmentManager_pb2.UpdateComponentInfoRequest(componentID=component_id,
                                                                   componentInfo=component_info)
        response = await self.stub.UpdateComponentInfo(request)
        if response is not None:
            return StatusEnum.SUCCESS

    async def add_listener_on_update_component_info(self, callback, component_id) -> None:
        """
        2.6.5 监听组件组件配置信息更新回调
        """
        # callback包含输入参数
        # component_id: str, component_info: dict[str, Union[str, dict]]
        # callback
        # 无需返回
        request = ComponmentManager_pb2.AddListenerOnUpdateComponentInfoRequest(request='request',
                                                                                componentId=component_id)
        add_listener_on_update_component_info_callback_stream = self.stub.AddListenerOnUpdateComponentInfo(request)
        async for response in add_listener_on_update_component_info_callback_stream:
            self.add_listener_on_update_component_info_model = AddListenerOnUpdateComponentInfoComponentModel()
            self.add_listener_on_update_component_info_model.component_id = response.componentID
            add_listener_on_update_component_info_data = yaml.load(response.componentInfo, Loader=yaml.FullLoader)
            self.add_listener_on_update_component_info_model.component_info = add_listener_on_update_component_info_data
            await callback.run(self.add_listener_on_update_component_info_model)
            await asyncio.sleep(0)

    async def unregister_component(self) -> StatusEnum:
        """
        2.6.6 本组件注销
        """
        # 返回值：注销成功枚举
        request = ComponmentManager_pb2.UnregisterComponentRequest(request='request')
        response = await self.stub.UnregisterComponent(request)
        if response.response is not None:
            return StatusEnum.SUCCESS
        # unregister_component_result = self.__get_status_enum(response.response, StatusEnum)
        # if unregister_component_result is StatusEnum:
        #     return unregister_component_result
        # elif isinstance(unregister_component_result, ValueErrorException):
        #     raise unregister_component_result

    async def add_listener_on_unregister_component(self, callback) -> None:
        """
        2.6.7 组件注销监听
        """
        # 组件注销监听
        # callback包含输入参数
        # component_id : str, component_type: str, component_info : dict
        # callback 无需返回
        request = ComponmentManager_pb2.ComponentUnregisteredListenerRequest(request='request')
        add_listener_on_update_component_info_callback_stream = self.stub.AddListenerOnUnregisterComponent(
            request)
        async for response in add_listener_on_update_component_info_callback_stream:
            await asyncio.sleep(0)
            self.add_listener_on_unregister_component_model = AddListenerOnUnregisterComponentModel()
            self.add_listener_on_unregister_component_model.component_id = response.componentID
            self.add_listener_on_unregister_component_model.component_type = response.componentType
            add_listener_on_register_component_data = yaml.load(response.componentInfo, Loader=yaml.FullLoader)
            self.add_listener_on_unregister_component_model.component_info = add_listener_on_register_component_data
            await callback.run(self.add_listener_on_unregister_component_model)
            await asyncio.sleep(0)

    async def get_all_component(self) -> list:
        """
        2.6.8 获取所有组件信息
        """
        # 返回值：component_id的list列表
        request = ComponmentManager_pb2.GetAllComponentRequest(request='request')
        response = await self.stub.GetAllComponent(request)
        return response.componentID

    async def get_component_state(self, component_id) -> ComponentStatusEnum:
        request = ComponmentManager_pb2.GetComponentStateRequest(componentId=component_id)
        response = await self.stub.GetComponentState(request)
        for status in ComponentStatusEnum:
            if status.value == response.response:
                result = status
        return result
        # if response.response is "ComponentNotExists":
        #     raise ComponentNotExistException("ComponentNotExists")
        # get_component_state_result = self.__get_status_enum(response.response, ComponentStatusEnum)
        # if get_component_state_result is ComponentStatusEnum:
        #     return get_component_state_result
        # else:
        #     raise get_component_state_result

    async def add_listener_on_update_component_state(self, callback, component_id: str = None) -> None:
        request = ComponmentManager_pb2.AddListenerOnUpdateComponentStateRequest(componentId=component_id)
        add_listener_on_update_component_state = self.stub.AddListenerOnUpdateComponentState(request)
        async for response in add_listener_on_update_component_state:
            self.add_listener_on_update_component_state_model = AddListenerOnUpdateComponentStateModel()
            self.add_listener_on_update_component_state_model.component_id = response.componentID
            add_listener_on_update_component_state_enum = self.__get_status_enum(response.componentState,
                                                                                 ComponentStatusEnum)
            if add_listener_on_update_component_state_enum is ComponentStatusEnum:
                self.add_listener_on_update_component_state_model.component_state \
                    = add_listener_on_update_component_state_enum
            else:
                raise add_listener_on_update_component_state_enum
            await callback.run(self.add_listener_on_update_component_state_model)
            await asyncio.sleep(0)

    async def update_component_state(self, component_status: ComponentStatusEnum, component_id) -> StatusEnum:
        ComponentStatus = component_status.value
        request = ComponmentManager_pb2.UpdateComponentStateRequest(componentID=component_id,
                                                                    componentStatus=ComponentStatus)
        response = await self.stub.UpdateComponentState(request)
        if response is not None:
            return StatusEnum.SUCCESS
        # if response.response is "ComponentNotExists":
        #     raise ComponentNotExistException("ComponentNotExists")
        # update_component_state_result = self.__get_status_enum(response.response, StatusEnum)
        # if update_component_state_result is StatusEnum:
        #     return update_component_state_result
        # else:
        #     raise update_component_state_result

    async def cancel_add_listener_on_unregister_component(self, component_id: str = None) -> StatusEnum:
        request = ComponmentManager_pb2.CancelAddListenerOnUnregisterComponentRequest(componentId=component_id)
        response = await self.stub.CancelAddListenerOnUnregisterComponent(request)
        if response is not None:
            return StatusEnum.SUCCESS
        # cancel_add_listener_on_unregister_component_result = self.__get_status_enum(response.response, StatusEnum)
        # if cancel_add_listener_on_unregister_component_result is StatusEnum:
        #     return cancel_add_listener_on_unregister_component_result
        # else:
        #     raise cancel_add_listener_on_unregister_component_result

    async def cancel_add_listener_on_update_component_info(self, component_id: str = None) -> StatusEnum:
        request = ComponmentManager_pb2.CancelAddListenerOnUpdateComponentInfoRequest(componentId=component_id)
        response = await self.stub.CancelAddListenerOnUpdateComponentInfo(request)
        if response is not None:
            return StatusEnum.SUCCESS
        # cancel_add_listener_on_update_component_info_result = self.__get_status_enum(response.response, StatusEnum)
        # if cancel_add_listener_on_update_component_info_result is StatusEnum:
        #     return cancel_add_listener_on_update_component_info_result
        # else:
        #     raise cancel_add_listener_on_update_component_info_result

    async def cancel_add_listener_on_register_component(self, component_id: str = None) -> StatusEnum:
        request = ComponmentManager_pb2.CancelAddListenerOnRegisterComponentRequest(componentId=component_id)
        response = await self.stub.CancelAddListenerOnRegisterComponent(request)
        if response is not None:
            return StatusEnum.SUCCESS
        # cancel_add_listener_on_register_component_result = self.__get_status_enum(response.response, StatusEnum)
        # if cancel_add_listener_on_register_component_result is StatusEnum:
        #     return cancel_add_listener_on_register_component_result
        # else:
        #     raise cancel_add_listener_on_register_component_result

    async def cancel_add_listener_on_update_component_state(self, component_id: str = None) -> StatusEnum:
        request = ComponmentManager_pb2.CancelAddListenerOnUpdateComponentStateRequest(componentId=component_id)
        response = await self.stub.CancelAddListenerOnUpdateComponentState(request)
        if response is not None:
            return StatusEnum.SUCCESS
        # cancel_add_listener_on_update_component_state_result = self.__get_status_enum(response.response, StatusEnum)
        # if cancel_add_listener_on_update_component_state_result is StatusEnum:
        #     return cancel_add_listener_on_update_component_state_result
        # else:
        #     raise cancel_add_listener_on_update_component_state_result

    @staticmethod
    def __get_status_enum(character: str, enum) -> ValueErrorException | Any:
        for status in enum:
            if status.value == character:
                return status
        return ValueErrorException("{character} is not in {enum.__name__}")

    async def startup(self, component_startup_configuration):
        self.__grpc_connector_forwarder.set_grpc_connector_address(component_startup_configuration.server_address,
                                                                   component_startup_configuration.server_port)
        self.__grpc_connector_forwarder.connect()
        self.stub = ComponmentManager_pb2_grpc.ComponentManagerServiceStub(
            self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类
        self.component_pattern = component_startup_configuration.component_pattern.value
