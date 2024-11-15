from abc import abstractmethod

from Collector.service.interface.DataSenderManagerInterface import DataSenderManagerInterface
from Collector.service.interface.ReceiverManagerInterface import ReceiverManagerInterface
from Collector.service.interface.TransponderInterface import InformationTransponderInterface


class BusinessManagerInterface(InformationTransponderInterface):
    """
    业务管理器接口
    """

    @abstractmethod
    def set_receiver_manager(self, receiver_manager: ReceiverManagerInterface):
        pass

    @abstractmethod
    def set_data_sender_manager(self, data_sender_manager: DataSenderManagerInterface):
        pass

