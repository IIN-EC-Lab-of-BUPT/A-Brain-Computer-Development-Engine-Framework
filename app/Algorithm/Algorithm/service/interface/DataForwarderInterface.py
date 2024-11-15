from abc import ABC, abstractmethod

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel


class DataForwarderInterface(ABC):
    """
    数据转发器接口
    """
    @abstractmethod
    async def forward_data(self, algorithm_data_message: AlgorithmDataMessageModel):
        pass
