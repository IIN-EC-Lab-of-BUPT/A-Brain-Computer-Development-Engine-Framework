import asyncio
import logging

from CentralController.api.converter.CentralManagementControlServiceMessageConverter import \
    CentralManagementControlServiceMessageConverter
from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusListModel
from CentralController.api.model.GroupModel import GroupListModel
from CentralController.api.proto.CentralManagementControlService_pb2_grpc import CentralManagementControlServiceServicer
from CentralController.common.enum.CentralControllerEventEnum import CentralControllerEventEnum
from CentralController.common.utils.EventManager import EventManager
from CentralController.service.interface.ComponentMonitorInterface import ComponentMonitorInterface
from CentralController.service.interface.ProcessManagerInterface import ProcessManagerApplicationInterface
from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface
from google.protobuf.empty_pb2 import Empty
from CentralController.api.proto.CentralManagementControlService_pb2 import (
    GroupMessage, GroupListMessage, ComponentGroupStatusMessage, ComponentGroupStatusListMessage
)


class CentralManagementControlServer(CentralManagementControlServiceServicer):

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

    async def prepare_system(self, request: Empty, context):
        self.__logger.info('收到系统准备请求')
        await self.__process_manager.prepare_system()
        return Empty()

    async def start_group(self, request: GroupMessage, context):
        group_model = CentralManagementControlServiceMessageConverter.protobuf_to_model(request)
        self.__logger.info(f"收到系统{group_model.group_id}组启动请求")
        await self.__process_manager.start_group(group_model)
        return Empty()

    async def reset_group(self, request: GroupMessage, context):
        group_model = CentralManagementControlServiceMessageConverter.protobuf_to_model(request)
        self.__logger.info(f"收到系统{group_model.group_id}组重置请求")
        await self.__process_manager.reset_group(group_model)
        return Empty()

    async def close_system(self, request: Empty, context):
        self.__logger.info("收到系统关闭请求")
        await self.__process_manager.close_system()
        # 抛出程序退出事件
        asyncio.create_task(self.__delay_shutdown(1.0))
        return Empty()

    async def get_components_status_list(self, request: Empty, context):
        self.__logger.debug("收到获取组件状态请求")
        component_group_status_list = await self.__component_monitor.get_components_status_list()
        return CentralManagementControlServiceMessageConverter.model_to_protobuf(
            ComponentGroupStatusListModel(
                component_group_status_list=component_group_status_list
            )
        )

    async def get_groups_model_list(self, request: Empty, context):
        self.__logger.debug("收到获取group请求")
        group_dict = self.__service_coordinator.get_static_group_information_model_dict()
        group_model_list = [group_information_model for _, group_information_model in group_dict.items()]
        return CentralManagementControlServiceMessageConverter.model_to_protobuf(
            GroupListModel(group_list=group_model_list)
        )

    async def __delay_shutdown(self, delay_time: float):
        await asyncio.sleep(delay_time)
        await self.__event_manager.notify(CentralControllerEventEnum.APPLICATION_EXIT.value)