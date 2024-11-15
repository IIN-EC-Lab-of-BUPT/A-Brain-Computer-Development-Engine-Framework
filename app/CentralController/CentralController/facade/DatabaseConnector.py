import logging

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from CentralController.facade.interface.SubsystemConnectorInterface import DatabaseConnectorInterface
from ResultPersistence.api.python.converter.ResultPersistenceControlMessageConverter import \
    ResultPersistenceControlMessageConverter
from ResultPersistence.api.python.message.MessageKeyEnum import MessageKeyEnum
from ResultPersistence.api.python.model.ResultPersistenceControlModel import ResultPersistenceControlModel, \
    StartReceiveResultControlModel, StopReceiveResultControlModel, ResultPersistenceExitControlModel


class DatabaseConnector(DatabaseConnectorInterface):
    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__logger = logging.getLogger('centralControllerLogger')
        self.__component_framework = component_framework

    async def start_receive(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = ResultPersistenceControlModel(
            package=StartReceiveResultControlModel()
        )
        proto = ResultPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def stop_receive(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = ResultPersistenceControlModel(
            package=StopReceiveResultControlModel()
        )
        proto = ResultPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def application_exit(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = ResultPersistenceControlModel(
            package=ResultPersistenceExitControlModel()
        )
        proto = ResultPersistenceControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())
