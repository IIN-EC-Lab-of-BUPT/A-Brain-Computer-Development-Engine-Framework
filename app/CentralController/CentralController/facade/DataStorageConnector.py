import logging

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from CentralController.facade.interface.SubsystemConnectorInterface import DataStorageConnectorInterface
from EEGDataPersistence.api.python.converter.EEGPersistenceControlMessageConverter import \
    EEGPersistenceControlMessageConverter
from EEGDataPersistence.api.python.message.MessageKeyEnum import MessageKeyEnum
from EEGDataPersistence.api.python.model.EEGPersistenceControlModel import EEGPersistenceControlModel, \
    StartReceiveEEGControlModel, StopReceiveEEGControlModel, EEGPersistenceExitControlModel


class DataStorageConnector(DataStorageConnectorInterface):
    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__logger = logging.getLogger('centralControllerLogger')
        self.__component_framework = component_framework

    async def start_receive(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = EEGPersistenceControlModel(
            package=StartReceiveEEGControlModel()
        )
        proto = EEGPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def stop_receive(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = EEGPersistenceControlModel(
            package=StopReceiveEEGControlModel()
        )
        proto = EEGPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def application_exit(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = EEGPersistenceControlModel(
            package=EEGPersistenceExitControlModel()
        )
        proto = EEGPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())
