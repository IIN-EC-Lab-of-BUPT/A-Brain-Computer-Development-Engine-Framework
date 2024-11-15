from abc import ABC, abstractmethod
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnRequestComponentStopCallbackInterface


class ConnectManagerInterface(ABC):

    @abstractmethod
    async def shutdown(self) -> StatusEnum:
        """关闭连接"""
        # 返回值："关闭连接成功通知"：枚举类型
        pass

    @abstractmethod
    async def add_listener_on_request_component_stop(self,
                                                     callback: AddListenerOnRequestComponentStopCallbackInterface) \
            -> None:
        """
        2.6.2 监听请求组件停止
        """
        # 组件注销监听
        # callback包含输入参数
        # request : str
        # callback 无需返回
        pass

    @abstractmethod
    async def cancel_add_listener_on_request_component_stop(self) -> StatusEnum:
        """
        2.6.3 取消监听请求组件停止
        """
        pass
    @abstractmethod
    async def startup(self, component_startup_configuration):
        pass