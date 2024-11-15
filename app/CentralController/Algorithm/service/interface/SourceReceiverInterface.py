from abc import ABC, abstractmethod
from typing import Union

from Algorithm.method.interface.SourceReceiverReaderInterface import SourceReceiverReaderInterface
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel


class SourceReceiverInterface(SourceReceiverReaderInterface, ABC):
    """
    源接收器接口
    """

    @abstractmethod
    def get_used_data_position(self) -> int:
        """
        获取已使用的数据位置
        :return: 已使用的数据位置
        """
        pass

    @abstractmethod
    async def set_message_model(self, message_model: AlgorithmDataMessageModel):
        """
        设置算法数据消息模型
        :param message_model: 算法数据消息模型
        :return:
        """
        pass

    @abstractmethod
    def set_source_label(self, source_label: str):
        """
        设置源标签
        :param source_label: 源标签
        :return:
        """
        pass

    @abstractmethod
    def set_configuration(self, configuration: dict[str, Union[str, dict]]):
        """
        设置配置信息
        :param configuration: 配置信息
        :return:
        """
        pass

