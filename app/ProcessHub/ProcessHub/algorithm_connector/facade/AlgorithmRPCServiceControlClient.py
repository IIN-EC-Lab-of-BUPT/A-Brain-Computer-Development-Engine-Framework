import logging
from typing import Union

import yaml

from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmStatusMessageModel
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCServiceControlStub
from Common.protobuf.BaseDataClassMessage_pb2 import (
    StringMessage as StringMessage_pb2,
    EmptyMessage as EmptyMessage_pb2
)


class AlgorithmRPCServiceControlClient:

    def __init__(self):
        self.__algorithm_rpc_service_control_stub: AlgorithmRPCServiceControlStub = None
        self.__logger = logging.getLogger("processHubLogger")

    async def get_status(self) -> AlgorithmStatusMessageModel:
        algorithm_status_message_pb2 = await self.__algorithm_rpc_service_control_stub.getStatus(EmptyMessage_pb2())
        return AlgorithmRPCMessageConverter.protobuf_to_model(algorithm_status_message_pb2)

    async def send_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
        self.__logger.info("AlgorithmRPCServiceControlClient send config")
        await self.__algorithm_rpc_service_control_stub.sendConfig(
            StringMessage_pb2(
                data=yaml.safe_dump(config_dict)
            )
        )

    async def get_config(self) -> dict[str, Union[str, dict]]:
        """
        :return: config dict
        """
        message = await self.__algorithm_rpc_service_control_stub.getConfig(EmptyMessage_pb2())
        config_dict = yaml.safe_load(message.data)
        self.__logger.info(f"AlgorithmRPCServiceControlClient get_config:{config_dict}")
        return config_dict

    async def shutdown(self) -> bool:
        self.__logger.info("AlgorithmRPCServiceControlClient shutdown")
        return (await self.__algorithm_rpc_service_control_stub.shutdown(EmptyMessage_pb2())).data

    def set_algorithm_rpc_service_control_stub(
            self, algorithm_rpc_service_control_stub: AlgorithmRPCServiceControlStub) -> None:
        self.__algorithm_rpc_service_control_stub = algorithm_rpc_service_control_stub
