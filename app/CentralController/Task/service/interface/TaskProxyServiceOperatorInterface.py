from abc import ABC, abstractmethod

from injector import inject


class TaskProxyServiceOperatorInterface(ABC):
    # 数据转发器处理接口，由MessageForwarder通过该接口回调control层方法，实现代码隔离

    @inject
    @abstractmethod
    def __init__(self, task_proxy_controller):
        pass

    @abstractmethod
    async def transfer(self, model):
        pass

    @abstractmethod
    def stop_transfer(self):
        # 停止转发
        pass
