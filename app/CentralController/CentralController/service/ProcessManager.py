import asyncio
import logging
from random import random
from typing import Union

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from CentralController.common.model import GroupInformationModel
from CentralController.facade.interface.SubsystemConnectorInterface import CollectorConnectorInterface, \
    ProcessorConnectorInterface, StimulatorConnectorInterface, DataStorageConnectorInterface, DatabaseConnectorInterface
from CentralController.service.interface.ProcessManagerInterface import ProcessManagerInterface
from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface


class ProcessManager(ProcessManagerInterface):

    @inject
    def __init__(self,
                 component_framework: ComponentFrameworkInterface,
                 service_coordinator: ServiceCoordinatorInterface,
                 collector_connector: CollectorConnectorInterface,
                 processor_connector: ProcessorConnectorInterface,
                 stimulator_connector: StimulatorConnectorInterface,
                 data_storage_connector: DataStorageConnectorInterface,
                 database_connector: DatabaseConnectorInterface,
                 ):
        self.__service_coordinator: ServiceCoordinatorInterface = service_coordinator
        self.__collector_connector: CollectorConnectorInterface = collector_connector
        self.__processor_connector: ProcessorConnectorInterface = processor_connector
        self.__stimulator_connector: StimulatorConnectorInterface = stimulator_connector
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__data_storage_connector: DataStorageConnectorInterface = data_storage_connector
        self.__database_connector: DatabaseConnectorInterface = database_connector

        self.__logger = logging.getLogger('centralControllerLogger')

    async def initial(self):
        pass

    async def startup(self):
        # 更新配置信息，并绑定所需消息
        central_controller_component_model = await self.__component_framework.get_component_model()
        component_info = central_controller_component_model.component_info
        message_dict = component_info.get('message', dict())
        for message_key in message_dict:
            await self.__component_framework.bind_message(MessageBindingModel(message_key=message_key))

    async def shutdown(self):
        pass

    async def prepare_system(self):
        # 启动处理容器
        # await self.__processor_connector.start_processor_container()

        # 启动数据存储
        registered_component_dict = self.__service_coordinator.get_registered_component_information_model_dict()
        # data_storage_component_list = [
        #     registered_component_dict[component_id]
        #     for component_id in registered_component_dict
        #     if registered_component_dict[component_id].component_type == 'DATASTORAGE'
        # ]
        database_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_type == 'DATABASE'
        ]

        for database_component in database_component_list:
            await self.__database_connector.start_receive(database_component.component_id)
        # await asyncio.sleep(5)
        #
        # for data_storage_component in data_storage_component_list:
        #     await self.__data_storage_connector.start_receive(data_storage_component.component_id)
        # await asyncio.sleep(1)

    async def start_group(self, group_information_model: GroupInformationModel):
        registered_component_dict = self.__service_coordinator.get_registered_component_information_model_dict()
        collector_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_group_id == group_information_model.group_id
               and registered_component_dict[component_id].component_type == 'COLLECTOR'
        ]
        stimulator_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_group_id == group_information_model.group_id
               and registered_component_dict[component_id].component_type == 'STIMULATOR'
        ]
        # 启动数据采集
        # 发送采集设备信息
        for collector_component in collector_component_list:
            await self.__collector_connector.send_device_info(collector_component.component_id)
        self.__logger.info(f"{group_information_model.group_id}采集设备信息发送")
        await asyncio.sleep(1)
        # 采集设备数据发送
        for collector_component in collector_component_list:
            await self.__collector_connector.start_data_sending(collector_component.component_id)
        self.__logger.info(f"启动{group_information_model.group_id}采集设备数据发送")
        await asyncio.sleep(1)
        # 启动范式刺激
        random_seed = random()
        for stimulator_component in stimulator_component_list:
            await self.__stimulator_connector.send_random_number_seeds(random_seed, stimulator_component.component_id)
        self.__logger.info(f"{group_information_model.group_id}发送随机数种子: {random_seed}")
        await asyncio.sleep(1)

        for stimulator_component in stimulator_component_list:
            await self.__stimulator_connector.start_stimulation(stimulator_component.component_id)
        self.__logger.info(f"{group_information_model.group_id}启动刺激组件")
        await asyncio.sleep(1)

    async def reset_group(self, group_information_model: GroupInformationModel):
        # 重置系统至就绪状态
        registered_component_dict = self.__service_coordinator.get_registered_component_information_model_dict()
        collector_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_group_id == group_information_model.group_id
               and registered_component_dict[component_id].component_type == 'COLLECTOR'
        ]
        stimulator_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_group_id == group_information_model.group_id
               and registered_component_dict[component_id].component_type == 'STIMULATOR'
        ]
        # 停止范式刺激
        for stimulator_component in stimulator_component_list:
            await self.__stimulator_connector.stop_stimulation(stimulator_component.component_id)
        self.__logger.info(f"{group_information_model.group_id}停止刺激组件")
        await asyncio.sleep(1)
        # 停止数据采集
        for collector_component in collector_component_list:
            await self.__collector_connector.stop_data_sending(collector_component.component_id)
        self.__logger.info(f"停止{group_information_model.group_id}采集设备数据发送")
        await asyncio.sleep(1)

    async def close_system(self):
        registered_component_dict = self.__service_coordinator.get_registered_component_information_model_dict()
        # 彻底关闭系统
        for component_id in registered_component_dict:
            match registered_component_dict[component_id].component_type:
                case 'COLLECTOR':
                    await self.__collector_connector.application_exit(component_id)
                    self.__logger.info(f"关闭{component_id}采集组件")
                case 'PROCESSOR':
                    await self.__processor_connector.application_exit(component_id)
                    self.__logger.info(f"关闭{component_id}处理组件")
                case 'STIMULATOR':
                    await self.__stimulator_connector.application_exit(component_id)
                    self.__logger.info(f"关闭{component_id}刺激组件")

        await asyncio.sleep(5)
        # 关闭处理容器
        await self.__processor_connector.stop_processor_container()

        # 其他节点关闭后再停止结果存储，最后停止数据存储
        data_storage_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_type == 'DATASTORAGE'
        ]
        database_component_list = [
            registered_component_dict[component_id]
            for component_id in registered_component_dict
            if registered_component_dict[component_id].component_type == 'DATABASE'
        ]
        for data_storage_component in data_storage_component_list:
            await self.__data_storage_connector.stop_receive(data_storage_component.component_id)
        await asyncio.sleep(1)
        for database_component in database_component_list:
            await self.__database_connector.stop_receive(database_component.component_id)
        await asyncio.sleep(1)
        for data_storage_component in data_storage_component_list:
            await self.__data_storage_connector.application_exit(data_storage_component.component_id)
        await asyncio.sleep(1)
        for database_component in database_component_list:
            await self.__database_connector.application_exit(database_component.component_id)
