import logging
from typing import Union

from injector import inject

from Collector.api.protobuf.ExternalTriggerService_pb2_grpc import add_ExternalTriggerServiceServicer_to_server
from Collector.control.ExternalTriggerServer import ExternalTriggerServer
from Collector.control.GrpcServer import GrpcServer
from Collector.control.interface.ControllerInterface import RPCControllerInterface
from Collector.service.interface.TransponderInterface import InformationTransponderInterface


class RPCController(RPCControllerInterface):

    @inject
    def __init__(self, information_transponder: InformationTransponderInterface):
        self.__information_transponder: InformationTransponderInterface = information_transponder
        self.__external_trigger_server: ExternalTriggerServer = None
        self.__rpc_server: GrpcServer = None
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__rpc_server = GrpcServer()
        self.__rpc_server.initial(config_dict)
        self.__external_trigger_server = ExternalTriggerServer(self.__information_transponder)
        self.__rpc_server.add_servicer_to_server(self.__external_trigger_server,
                                                 add_ExternalTriggerServiceServicer_to_server)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__rpc_server.update(config_dict)

    async def startup(self):
        await self.__rpc_server.startup()
        self.__logger.info("RPCController已启动")

    async def shutdown(self):
        await self.__rpc_server.shutdown()
        self.__logger.info("RPCController已关闭")
