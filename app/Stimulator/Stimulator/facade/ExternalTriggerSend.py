import asyncio
from asyncio import Queue
from typing import Union
from injector import inject
from Collector.api.protobuf import ExternalTriggerService_pb2_grpc
from Stimulator.facade.GrpcConnect import GrpcConnector
from Stimulator.facade.converter.ExternalTriggerMessageConverter import ExternalTriggerMessageConverter
from Stimulator.facade.interface.TriggerSystemInterface import ExternalTriggerSendInterface
# from Stimulator.facade.protobuf.out import ExternalTriggerService_pb2_grpc
from google.protobuf.empty_pb2 import Empty


class ExternalTriggerSend(ExternalTriggerSendInterface):
    @inject
    def __init__(self):
        # 初始化操作，可以在这里进行一些初始化设置
        super().__init__()
        self.__report_message_queue = Queue()
        self.__config_dict = {}
        self.stub = None
        self.__grpc_connector_forwarder = GrpcConnector()

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__config_dict.update(config_dict)
        await self.__grpc_connector_forwarder.initial(self.__config_dict)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__config_dict = config_dict
        await self.__grpc_connector_forwarder.update(self.__config_dict)

    async def open(self) -> None:
        await self.__grpc_connector_forwarder.open()
        if self.stub is None:
            self.stub = ExternalTriggerService_pb2_grpc.ExternalTriggerServiceStub(
                self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类
            self.stub.connect(Empty())
        else:
            self.stub = self.stub
        pass

    async def shutdown(self) -> None:
        await self.__grpc_connector_forwarder.shutdown()
        self.__grpc_connector_forwarder = None

    async def send(self, event):
        request = ExternalTriggerMessageConverter.model_to_protobuf(event)
        await self.stub.trigger(request)

    # async def send(self, event):
    #     await self.__report_message_queue.put(event)
    #     request_iterator = self.connect()
    #     await self.stub.trigger(request_iterator)
    #
    # async def connect(self):
    #     message = await self.__report_message_queue.get()  # 使用异步get方法获取待发送消息
    #     await asyncio.sleep(0.1)
    #     request = ExternalTriggerMessageConverter.model_to_protobuf(message)
    #     yield request
