import asyncio
from injector import inject
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.MessageManagerInterface import MessageManagerInterface
from componentframework.api.model.MessageModel import MessageModel
from componentframework.service.MessageManagerService import MessageManagerService
from componentframework.service.serviceInterface.ServiceOperatorInterface import (
    SubscribeTopicCallbackServiceInterface,
    AddListenerOnBindMessageCallbackServiceInterface)


class MessageManagerInterfaceImpl(MessageManagerInterface):

    @inject
    def __init__(self, message_forwarder: MessageManagerService):
        # 初始化操作，可以在这里进行一些初始化设置
        self.cancel_add_listener_on_bind_message_result = None
        self.bind_message_result = None
        self.get_topic_by_message_key_result = None
        self.unsubscribe_source_result = None
        self.generate_report_result = None
        self.__message_forwarder = message_forwarder

    async def bind_message(self, message_model: MessageModel):
        """
        2.4.1 话题创建
        """
        # service_id:str, message_key: str, topic: str
        # 绑定指定服务的指定话题，如果话题不存在则创建，订阅与发送消息前都需要先绑定消息
        # 守护进程或中央控制器填入具体topic，也可写入明确的topic
        # - service_id: 指定服务ID，该参数可为空，表示创建本服务事件
        # - message_key: 指定messageKey
        # - topic: 指定topic，该参数默认为空，表示由中控填写指定topic
        # 返回参数：事件结构体，包含service_id:str、message_key:str、topic:str

        self.bind_message_result = await self.__message_forwarder.bind_message(message_model)
        return self.bind_message_result

    async def add_listener_on_bind_message(self, callback) -> None:
        """
        2.4.2 话题绑定监听
        """

        # callback包含输入参数
        # service_id, message_key, topic
        # callback
        # 无需返回
        class AddListenerOnBindMessageCallbackOperator(AddListenerOnBindMessageCallbackServiceInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                final_result = await self.__operator.run(result)
                return final_result

        operator = AddListenerOnBindMessageCallbackOperator()
        asyncio.create_task(self.__message_forwarder.add_listener_on_bind_message(operator))

    async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> str:
        """
        2.4.1 通过message_key获取topic
        """
        # 通过message_key获取对应的topic
        # 返回值
        # topic: str
        self.get_topic_by_message_key_result = await self.__message_forwarder.get_topic_by_message_key(message_key
                                                                                                       , component_id)
        return self.get_topic_by_message_key_result

    async def subscribe_topic(self, callback, message_key):
        """
        2.4.2 话题订阅
        """

        # 直接订阅指定服务的指定话题，如果message_key未绑定，则抛出未绑定异常
        # - message_key: 指定messageKey
        # - callback: 触发回调时的调用方法输入参数message: bytes
        class SubscribeTopicCallbackOperator(SubscribeTopicCallbackServiceInterface):
            def __init__(self):
                super().__init__()
                self.__operator = callback

            async def run(self, result):
                await self.__operator.run(result)

        operator = SubscribeTopicCallbackOperator()
        asyncio.create_task(self.__message_forwarder.subscribe_topic(operator, message_key))

    async def send_message(self, message_key, value):
        """
        2.4.3 消息发送
        """
        # 发送消息
        # 守护进程向消息中间件写入内容
        # 输入参数：
        # - message_key: 指定messageKey
        # - value: 准备的事件内容，二进制流
        # 返回参数：Boolean
        # asyncio.create_task(self.__message_forwarder.send_message(message_key, value))
        await self.__message_forwarder.send_message(message_key, value)

    async def send_unary_message(self, message_key, message):
        self.generate_report_result = await self.__message_forwarder.send_unary_message(message_key, message)
        return self.generate_report_result

    async def unsubscribe_source(self, message_key: str):
        """取消订阅"""
        # 返回值："取消订阅成功通知"：枚举类型
        self.unsubscribe_source_result = await self.__message_forwarder.unsubscribe_source(message_key)
        return self.unsubscribe_source_result

    async def cancel_add_listener_on_bind_message(self) -> StatusEnum:
        self.cancel_add_listener_on_bind_message_result = \
            await self.__message_forwarder.cancel_add_listener_on_bind_message()
        return self.cancel_add_listener_on_bind_message_result

    async def startup(self, component_startup_configuration):
        await self.__message_forwarder.startup(component_startup_configuration)
