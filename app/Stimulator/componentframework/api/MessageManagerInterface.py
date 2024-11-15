from abc import ABC, abstractmethod
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    SubscribeTopicCallbackInterface, \
    AddListenerOnBindMessageCallbackInterface
from componentframework.api.model.MessageModel import MessageModel


class MessageManagerInterface(ABC):
    @abstractmethod
    async def bind_message(self, message_model: MessageModel) -> MessageModel:
        """
        2.4.1 话题绑定
        """
        # 创建指定服务的指定话题
        # 守护进程或中央控制器填入具体topic，也可写入明确的topic
        # 输入参数：
        # - message_key: 指定messageKey,不为空
        # - topic: 指定topic，该参数可为空，表示由中控填写指定topic
        # 返回参数：事件结构体，包含service_id:str、message_key:str、topic:str
        pass

    @abstractmethod
    async def add_listener_on_bind_message(self, callback: AddListenerOnBindMessageCallbackInterface) -> MessageModel:
        """
        2.4.2 话题绑定监听
        """
        # callback包含输入参数
        # service_id, message_key, topic
        # callback
        # 无需返回
        pass

    @abstractmethod
    async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> str:
        """
        2.4.1 通过message_key获取topic
        """
        # 通过message_key获取对应的topic
        # 返回值
        # topic: str
        pass

    @abstractmethod
    async def subscribe_topic(self, callback: SubscribeTopicCallbackInterface, message_key: str) -> None:
        """
        2.4.2 话题订阅
        """
        # 直接订阅指定服务的指定话题，如果message_key未绑定，则抛出未绑定异常
        # - message_key: 指定messageKey
        # - callback: 触发回调时的调用方法输入参数message: bytes
        pass

    @abstractmethod
    async def send_message(self, message_key: str, value: bytes) -> None:
        """
        2.4.3 消息发送
        """
        # 发送消息
        # 守护进程向消息中间件写入内容
        # 输入参数：
        # - message_key: 指定messageKey
        # - value: 准备的事件内容
        pass

    @abstractmethod
    async def send_unary_message(self, message_key: str, message: bytes) -> None:
        """
        结果汇报
        """
        # 发送结果
        # 守护进程向消息中间件写入内容
        # 输入参数：
        # - message_key: 指定messageKey
        # - message: 准备的结果内容
        pass

    @abstractmethod
    async def unsubscribe_source(self, message_key: str) -> StatusEnum:
        """取消订阅"""
        # 返回值：StatusEnum枚举类型
        pass

    @abstractmethod
    async def cancel_add_listener_on_bind_message(self) -> StatusEnum:
        """
        2.4.8 取消话题绑定监听
        """
        pass

    @abstractmethod
    async def startup(self, component_startup_configuration):
        pass
