import logging
from enum import Enum
from urllib.parse import urljoin

import requests
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from CentralController.facade.interface.SubsystemConnectorInterface import ProcessorConnectorInterface
from Task.api.converter.TaskControlMessageConverter import TaskControlMessageConverter
from Task.api.message.MessageKeyEnum import MessageKeyEnum
from Task.api.model.TaskControlModel import TaskControlModel, ApplicationExitControlModel


class ProcessorConnectorCommandEnum(Enum):
    START_PROCESSOR_CONTAINER = "start_processor_container"
    STOP_PROCESSOR_CONTAINER = "stop_processor_container"


class ProcessorConnector(ProcessorConnectorInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):

        self.__challenge_id: int = None
        self.__processor_container_control_address: str = ''
        self.__start_processor_command: str = ''
        self.__stop_processor_command: str = ''
        self.__logger = logging.getLogger('centralControllerLogger')
        self.__component_framework = component_framework

    async def initial(self):
        pass

    async def startup(self):
        component_model = await self.__component_framework.get_component_model()
        config_dict = component_model.component_info
        if 'container_control_config' in config_dict:
            container_control_config_dict = config_dict.get('container_control_config', dict())
            self.__start_processor_command = container_control_config_dict.get(
                ProcessorConnectorCommandEnum.START_PROCESSOR_CONTAINER.value, '')
            self.__stop_processor_command = container_control_config_dict.get(
                ProcessorConnectorCommandEnum.STOP_PROCESSOR_CONTAINER.value, '')
            self.__processor_container_control_address = container_control_config_dict.get(
                'processor_container_control_address', '')
            self.__challenge_id = container_control_config_dict.get(
                'challenge_id', 0)

    async def shutdown(self):
        pass

    async def application_exit(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = TaskControlModel(
            package=ApplicationExitControlModel()
        )
        proto = TaskControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def start_processor_container(self):
        start_url = urljoin(
            f"http://{self.__processor_container_control_address}", self.__start_processor_command)
        values = {'paradigmId': self.__challenge_id}
        response = requests.post(start_url, data=values)
        self.__logger.info(f"发送start_processor_container请求，收到响应:{start_url} : {response.status_code} {response.text}")

    async def stop_processor_container(self):
        stop_url = urljoin(
            f"http://{self.__processor_container_control_address}", self.__stop_processor_command)
        values = {'paradigmId': self.__challenge_id}
        response = requests.post(stop_url, data=values)
        self.__logger.info(
            f"发送stop_processor_container请求，收到响应:{stop_url} : {response.status_code} {response.text}")
