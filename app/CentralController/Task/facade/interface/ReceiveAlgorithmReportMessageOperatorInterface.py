from abc import ABC, abstractmethod

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel


class ReceiveAlgorithmReportMessageOperatorInterface(ABC):

    @abstractmethod
    async def receive_report(self, algorithm_report_message: AlgorithmReportMessageModel) -> None:
        """
        接收到算法报告消息后的处理函数
        :param algorithm_report_message: 接收到的算法报告消息
        :return:
        """
        pass
