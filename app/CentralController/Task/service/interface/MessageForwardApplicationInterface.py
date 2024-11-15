from abc import ABC, abstractmethod

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from Common.model.CommonMessageModel import DataMessageModel


class MessageForwardApplicationInterface(ABC):
    @abstractmethod
    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        pass

    @abstractmethod
    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        pass

    @abstractmethod
    async def send_report(self, data_message_model: DataMessageModel):
        pass
