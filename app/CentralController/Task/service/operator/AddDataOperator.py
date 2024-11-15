import time

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel
from Common.model.CommonMessageModel import DataMessageModel
from Task.facade.interface.ConnectorOperatorInterface import ConnectorSubscribeDataOperatorInterface
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface


class AddDataOperator(ConnectorSubscribeDataOperatorInterface):

    def __init__(self, source_label: str, message_forwarder: MessageForwardApplicationInterface):
        self.__source_label = source_label
        self.__message_forwarder: MessageForwardApplicationInterface = message_forwarder

    async def run(self, received_model: DataMessageModel) -> None:
        # 补充信息并调用MessageForwarder中方法并将数据传输出去
        await self.__message_forwarder.receive_message(
            AlgorithmDataMessageModel(
                source_label=self.__source_label,
                timestamp=time.time(),
                package=received_model.package
            )
        )

