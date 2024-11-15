import logging

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel
from Task.facade.interface.ReceiveAlgorithmReportMessageOperatorInterface import \
    ReceiveAlgorithmReportMessageOperatorInterface
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface


class ReceiveAlgorithmReportMessageOperator(ReceiveAlgorithmReportMessageOperatorInterface):

    def __init__(self, message_forwarder: MessageForwardApplicationInterface):
        self.__message_forwarder: MessageForwardApplicationInterface = message_forwarder
        self.__logger = logging.getLogger("taskLogger")

    async def receive_report(self, algorithm_report_message: AlgorithmReportMessageModel) -> None:
        await self.__message_forwarder.receive_report(algorithm_report_message)
