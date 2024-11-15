import asyncio

from injector import inject
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.facade.ConnectManagerFacade import ConnectManagerFacade
from componentframework.facadeImpl.grpc_connector import GrpcConnector
from componentframework.facadeImpl.test_grpc import ConnectManager_pb2_grpc, ConnectManager_pb2


class ConnectManagerFacadeImpl(ConnectManagerFacade):
    @inject
    def __init__(self, grpc_connector_forwarder: GrpcConnector):
        # 初始化操作，可以在这里进行一些初始化设置
        super().__init__()
        self.cancel_add_listener_on_request_component_stop_result = None
        self.context = None
        self.component_framework_manager = None
        self.stub = None
        self.__grpc_connector_forwarder = grpc_connector_forwarder
        self.shutdown_result = None
        self.unsubscribe_source_result = None

    # def get_stub(self):
    #     self.stub = ConnectManager_pb2_grpc.ConnectManagerServiceStub(
    #         self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类

    async def shutdown(self):
        """关闭连接"""
        # 返回值："关闭连接成功通知"：str类型
        request = ConnectManager_pb2.ShutDownRequest(request="request")
        self.shutdown_result = await self.stub.ShutDown(request)
        if self.shutdown_result:
            await self.__grpc_connector_forwarder.disconnect()
            return StatusEnum.SUCCESS

    async def add_listener_on_request_component_stop(self, callback) -> None:
        """
        2.6.7 监听请求组件停止
        """

        # 监听请求组件停止
        # callback包含输入参数
        # request : str
        # callback 无需返回
        request = ConnectManager_pb2.AddListenerOnRequestComponentStopRequest(request="request")
        subscribe_topic_response_stream = self.stub.AddListenerOnRequestComponentStop(request)
        async for response in subscribe_topic_response_stream:
            await callback.run(response.response)
            confirm_request = ConnectManager_pb2.ConfirmRequestComponentStopRequest(request="confirm_request")
            self.stub.ConfirmRequestComponentStop(confirm_request)
            await asyncio.sleep(0)

    async def cancel_add_listener_on_request_component_stop(self) -> StatusEnum:
        request = ConnectManager_pb2.CancelAddListenerOnRequestComponentStopRequest(request="request")
        self.cancel_add_listener_on_request_component_stop_result = \
            await self.stub.CancelAddListenerOnRequestComponentStop(request)
        if self.cancel_add_listener_on_request_component_stop_result:
            return StatusEnum.SUCCESS

    async def startup(self, component_startup_configuration):
        self.__grpc_connector_forwarder.set_grpc_connector_address(component_startup_configuration.server_address,
                                                                   component_startup_configuration.server_port)
        self.__grpc_connector_forwarder.connect()
        self.stub = ConnectManager_pb2_grpc.ConnectManagerServiceStub(
            self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类
