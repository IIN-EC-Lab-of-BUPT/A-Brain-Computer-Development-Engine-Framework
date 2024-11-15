from Algorithm.service.interface.DataForwarderInterface import DataForwarderInterface
from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.proto.AlgorithmRPCService_pb2 import AlgorithmDataMessage


class ReceiveMessageOperator:

    def __init__(self, data_forwarder: DataForwarderInterface):
        self.__data_forwarder = data_forwarder
        self.__data_convert = AlgorithmRPCMessageConverter()

    async def receive_message(self, algorithm_data_message: AlgorithmDataMessage):
        await self.__data_forwarder.forward_data(self.__data_convert.protobuf_to_model(algorithm_data_message))
