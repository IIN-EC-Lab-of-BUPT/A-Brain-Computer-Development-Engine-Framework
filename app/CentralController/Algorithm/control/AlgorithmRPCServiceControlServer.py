import asyncio
import logging
import yaml
from injector import inject
from Algorithm.service.interface.ServiceManagerInterface import ConfigManagerInterface, CoreControllerInterface
from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmStatusMessageModel, AlgorithmStatusEnum
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCServiceControlServicer
from Common.protobuf.BaseDataClassMessage_pb2 import StringMessage, EmptyMessage, BooleanMessage
from Algorithm.api.proto.AlgorithmRPCService_pb2 import AlgorithmStatusMessage


class AlgorithmRPCServiceControlServer(AlgorithmRPCServiceControlServicer):

    @inject
    def __init__(self, config_manager: ConfigManagerInterface, core_controller: CoreControllerInterface):
        self.__config_manager: ConfigManagerInterface = config_manager
        self.__core_controller: CoreControllerInterface = core_controller
        self.__logger = logging.getLogger("algorithmLogger")

    async def getStatus(self, request: EmptyMessage, context) -> AlgorithmStatusMessage:
        service_status = AlgorithmStatusEnum[self.__core_controller.get_service_status().name]
        algorithm_status_model = AlgorithmStatusMessageModel(status=service_status)
        return AlgorithmRPCMessageConverter.model_to_protobuf(algorithm_status_model)

    async def sendConfig(self, request: StringMessage, context) -> EmptyMessage:
        config_str = request.data
        config_dict = yaml.safe_load(config_str)
        self.__logger.info(f"接收到配置信息{config_dict}")
        await self.__config_manager.receive_config(config_dict)
        return EmptyMessage()

    async def getConfig(self, request: EmptyMessage, context) -> StringMessage:
        config_dict = await self.__config_manager.get_config()
        self.__logger.info(f"发送配置信息{config_dict}")
        config_str = yaml.dump(config_dict)
        return StringMessage(data=config_str)

    async def shutdown(self, request: EmptyMessage, context) -> BooleanMessage:
        self.__logger.info(f"收到算法服务关闭请求")
        asyncio.create_task(self.__core_controller.exit())
        return BooleanMessage(data=True)
