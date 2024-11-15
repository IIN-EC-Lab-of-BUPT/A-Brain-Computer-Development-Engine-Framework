import asyncio

import yaml
from injector import inject
from componentframework.facade.RemoteProcedureCallFacade import RemoteProcedureCallFacade
from componentframework.facadeImpl.grpc_connector import GrpcConnector
from componentframework.facadeImpl.test_grpc import ConfigManager_pb2, ConfigManager_pb2_grpc
from componentframework.api.Enum.StatusEnum import StatusEnum


class ConfigManagerGrpcFacadeImpl(RemoteProcedureCallFacade):
    @inject
    def __init__(self, grpc_connector_forwarder: GrpcConnector):
        super().__init__()
        self.__grpc_connector_forwarder = grpc_connector_forwarder
        self.stub = None
        self.callback = None
        self.service_operator = None

    # def get_stub(self):
    #     self.stub = ConfigManager_pb2_grpc.ConfigManagerServiceStub(
    #         self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类

    async def get_global_config(self) -> str:
        """
        2.2.1 全局配置读取
        """
        # 读取/core/config内容并返回配置树（xml节点树）
        # 实现代码
        # 调用远程方法
        request = ConfigManager_pb2.ReadGlobalConfigRequest(request="get global config")
        response = await self.stub.ReadGlobalConfig(request)
        return response.response

    async def add_listener_on_global_config(self, callback):
        """
        2.2.3 全局参数配置更新回调注册
        """
        # 全局配置变更时处理方法注册
        # 输入参数：
        # - callback: 触发回调时的调用方法
        # 实现代码
        # callback的输入参数：config_dict :dict[str, Union[str, dict]]类型
        request = ConfigManager_pb2.RegisterGlobalConfigUpdateCallbackRequest(request='request')
        global_config_response_stream = self.stub.RegisterGlobalConfigUpdateCallback(request)
        async for response in global_config_response_stream:
            add_listener_on_register_component_data = yaml.load(response.callback, Loader=yaml.FullLoader)
            await callback.run(add_listener_on_register_component_data)
            await asyncio.sleep(0)

    async def update_global_config(self, config_dict):
        """
        2.2.10 手动更新全局配置
        """
        # 修改指定全局配置信息
        # 输入参数：
        # - config_key: 指定配置更新configKey
        # - config_value: 修改的配置内容
        # 实现代码
        request = ConfigManager_pb2.UpdateGlobalConfigRequest(request=config_dict)
        response = await self.stub.UpdateGlobalConfig(request)
        if response.response is not None:
            return StatusEnum.SUCCESS

    async def cancel_add_listener_on_global_config(self) -> StatusEnum:
        request = ConfigManager_pb2.CancelAddListenerOnGlobalConfigRequest(request="request")
        response = await self.stub.CancelAddListenerOnGlobalConfig(request)
        if response.response is not None:
            return StatusEnum.SUCCESS

    async def startup(self, component_startup_configuration):
        self.__grpc_connector_forwarder.set_grpc_connector_address(component_startup_configuration.server_address,
                                                                   component_startup_configuration.server_port)
        self.__grpc_connector_forwarder.connect()
        self.stub = ConfigManager_pb2_grpc.ConfigManagerServiceStub(
            self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类
