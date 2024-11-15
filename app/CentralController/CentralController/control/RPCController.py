import logging
from typing import Union

from injector import inject

from CentralController.api.proto.CentralManagementControlService_pb2_grpc import \
    add_CentralManagementControlServiceServicer_to_server
from CentralController.common.utils.EventManager import EventManager
from CentralController.control.CentralManagementControlServer import CentralManagementControlServer
from CentralController.control.GrpcServer import GrpcServer
from CentralController.control.interface.ControllerInterface import RPCControllerInterface
from CentralController.service.interface.ComponentMonitorInterface import ComponentMonitorInterface
from CentralController.service.interface.ProcessManagerInterface import ProcessManagerApplicationInterface
from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface


class RPCController(RPCControllerInterface):

    @inject
    def __init__(self,
                 event_manager: EventManager,
                 component_monitor: ComponentMonitorInterface,
                 process_manager: ProcessManagerApplicationInterface,
                 service_coordinator: ServiceCoordinatorInterface):

        self.__event_manager = event_manager
        self.__component_monitor = component_monitor
        self.__process_manager = process_manager
        self.__service_coordinator = service_coordinator
        self.__logger = logging.getLogger('centralControllerLogger')

        self.__central_management_control_server: CentralManagementControlServer = None
        self.__rpc_server: GrpcServer = None
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__rpc_server = GrpcServer()
        self.__rpc_server.initial(config_dict)
        self.__central_management_control_server = CentralManagementControlServer(
            event_manager=self.__event_manager,
            component_monitor=self.__component_monitor,
            process_manager=self.__process_manager,
            service_coordinator=self.__service_coordinator
        )
        self.__rpc_server.add_servicer_to_server(self.__central_management_control_server,
                                                 add_CentralManagementControlServiceServicer_to_server)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__rpc_server.update(config_dict)

    async def startup(self):
        await self.__rpc_server.startup()
        self.__logger.info("RPCController已启动")

    async def shutdown(self):
        await self.__rpc_server.shutdown()
        self.__logger.info("RPCController已关闭")
