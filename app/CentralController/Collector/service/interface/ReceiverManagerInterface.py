from abc import abstractmethod

from Collector.receiver.interface.ReceiverInterface import ReceiverInterface
from Collector.service.interface.ServiceManagerInterface import ServiceManagerInterface


class ReceiverManagerInterface(ServiceManagerInterface):
    """
    接收器管理器接口
    """

    @abstractmethod
    def get_receiver(self) -> ReceiverInterface:
        pass
