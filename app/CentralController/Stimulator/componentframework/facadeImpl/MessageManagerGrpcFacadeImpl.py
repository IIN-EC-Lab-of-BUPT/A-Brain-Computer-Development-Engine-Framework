import asyncio
from injector import inject
from asyncio import Queue
from componentframework.api.model.MessageModel import MessageModel
from componentframework.facadeImpl.grpc_connector import GrpcConnector
from componentframework.facade.RemoteProcedureCallFacade import RemoteProcedureCallFacade
from componentframework.facadeImpl.test_grpc import MessageManager_pb2, MessageManager_pb2_grpc
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.model.MessageOperateModel import AddListenerOnBindMessageModel


class MessageManagerGrpcFacadeImpl(RemoteProcedureCallFacade):
    @inject
    def __init__(self, grpc_connector_forwarder: GrpcConnector):
        # 初始化操作，可以在这里进行一些初始化设置
        super().__init__()
        self.component_pattern = None
        self.__report_message_queue = Queue()
        self.add_listener_on_bind_message_model = None
        self.stub = None
        self.__grpc_connector_forwarder = grpc_connector_forwarder

    # def get_stub(self):
    #     self.stub = MessageManager_pb2_grpc.MessageManagerServiceStub(
    #         self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类

    async def bind_message(self, message_model: MessageModel):
        """
        2.4.1 话题创建
        """
        # 创建指定服务的指定话题
        # 向注册中心写入/config/service-event/messageKey
        # 守护进程或中央控制器填入具体topic，也可写入明确的topic
        # 输入参数：
        # - service_id: 指定服务ID，该参数可为空，表示创建本服务事件
        # - message_key: 指定messageKey
        # - topic: 指定topic，该参数可为空，表示由中控填写指定topic
        # 返回参数：事件结构体，包含service_id、message_key、topic
        request = MessageManager_pb2.BindMessageRequest(messageKey=message_model.message_key,
                                                        serviceID=message_model.component_id,
                                                        topic=message_model.topic,
                                                        componentPattern=self.component_pattern)
        response = await self.stub.BindMessage(request)
        bind_message_model = MessageModel()
        bind_message_model.message_key = response.messageKey
        bind_message_model.service_id = response.serviceID
        bind_message_model.topic = response.topic
        return bind_message_model

    async def add_listener_on_bind_message(self, callback) -> None:
        """
        2.4.2 话题绑定监听
        """
        # callback包含输入参数
        # service_id, message_key, topic
        # callback
        # 无需返回
        request = MessageManager_pb2.AddListenerOnBindMessageRequest(request='request')
        subscribe_topic_response_stream = self.stub.AddListenerOnBindMessage(request)
        async for response in subscribe_topic_response_stream:
            print(asyncio.all_tasks())
            print(response)
            self.add_listener_on_bind_message_model = AddListenerOnBindMessageModel()
            self.add_listener_on_bind_message_model.message_key = response.messageKey
            self.add_listener_on_bind_message_model.component_id = response.serviceID
            self.add_listener_on_bind_message_model.topic = response.topic
            confirm_response = await callback.run(self.add_listener_on_bind_message_model)
            confirm_request = MessageManager_pb2.ConfirmBindMessageRequest(messageKey=confirm_response.message_key,
                                                                           serviceID=confirm_response.component_id,
                                                                           topic=confirm_response.topic)
            self.stub.ConfirmBindMessage(confirm_request)
            await asyncio.sleep(0)

    async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> str:
        """
        2.4.1 通过message_key获取topic
        """
        # 通过message_key获取对应的topic
        # 返回值
        # topic: str
        request = MessageManager_pb2.GetTopicByMessageKeyRequest(messageKey=message_key, serviceID=component_id)
        response = await self.stub.GetTopicByMessageKey(request)
        return response.topic

    async def subscribe_topic(self, callback, message_key):
        """
        2.4.2 话题订阅
        """
        request = MessageManager_pb2.SubscribeTopicRequest(messageKey=message_key)
        subscribe_topic_response_stream = self.stub.SubscribeTopic(request)
        async for response in subscribe_topic_response_stream:
            # print(response)
            await callback.run(response.response)
            await asyncio.sleep(0)

    async def send_message(self, message_key, value):
        # message_key=None, value=None
        """
        2.4.3 消息发送
        """

        # 发送消息
        # 守护进程向消息中间件写入内容
        # 输入参数：
        # - message_key: 指定messageKey
        # - value: 准备的事件内容，二进制流
        # 返回参数：Boolean
        async def send_messages(message_key, message):
            yield MessageManager_pb2.SendMessageRequest(messageKey=message_key, value=message)

        # 调用gRPC流式方法
        response = self.stub.SendMessage(send_messages(message_key, value))
        return response

    async def send_unary_message(self, message_key, message_model):

        request = MessageManager_pb2.SendResultRequest(messageKey=message_key, value=message_model)
        response = await self.stub.SendResult(request)
        if response:
            return StatusEnum.SUCCESS

    async def unsubscribe_source(self, message_key: str):
        """取消订阅"""
        # 返回值："取消订阅成功通知"：str类型
        request = MessageManager_pb2.UnsubscribeTopicRequest(request=message_key, messageKey=message_key)
        unsubscribe_source_result = self.stub.UnsubscribeTopic(request)
        if unsubscribe_source_result:
            return StatusEnum.SUCCESS

    async def cancel_add_listener_on_bind_message(self) -> StatusEnum:
        request = MessageManager_pb2.CancelAddListenerOnBindMessageRequest(request="request")
        cancel_add_listener_on_bind_message_result = self.stub.CancelAddListenerOnBindMessage(request)
        if cancel_add_listener_on_bind_message_result:
            return StatusEnum.SUCCESS

    async def startup(self, component_startup_configuration):
        self.__grpc_connector_forwarder.set_grpc_connector_address(component_startup_configuration.server_address,
                                                                   component_startup_configuration.server_port)
        self.__grpc_connector_forwarder.connect()
        self.stub = MessageManager_pb2_grpc.MessageManagerServiceStub(
            self.__grpc_connector_forwarder.initial_stub())  # 替换为你的服务的 Stub 类
        self.component_pattern = component_startup_configuration.component_pattern.value
