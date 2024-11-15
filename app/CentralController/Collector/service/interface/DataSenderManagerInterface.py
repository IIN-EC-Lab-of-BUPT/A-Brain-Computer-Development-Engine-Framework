from abc import abstractmethod

from Collector.datasender.interface.DataSenderInterface import DataSenderInterface
from Collector.service.interface.ServiceManagerInterface import ServiceManagerInterface


class DataSenderManagerInterface(ServiceManagerInterface):
    """
    预处理管理器接口
    """

    @abstractmethod
    def get_data_sender(self) -> DataSenderInterface:
        pass
