from abc import ABC, abstractmethod

from Algorithm.method.model.AlgorithmObject import AlgorithmContinuousDataObject, AlgorithmDeviceObject


class SourceReceiverReaderInterface(ABC):
    """
    源接收器读取接口
    """

    @abstractmethod
    def get_source_label(self) -> str:
        """
        获取源标签
        :return:
        """
        pass

    @abstractmethod
    async def get_data(self) -> AlgorithmContinuousDataObject:
        """
        获取数据
        :return:
        """
        pass

    @abstractmethod
    async def get_device(self) -> AlgorithmDeviceObject:
        """
        获取设备信息
        :return:
        """
        pass
