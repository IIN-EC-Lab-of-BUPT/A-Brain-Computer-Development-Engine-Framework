import logging
from typing import Union

from injector import inject

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from Collector.api.converter.ExternalTriggerMessageConverter import ExternalTriggerMessageConverter
from Collector.api.message.MessageKeyEnum import MessageKeyEnum
from Collector.control.interface.ControllerInterface import ExternalTriggerControllerInterface
from Collector.api.protobuf.ExternalTriggerService_pb2 import ExternalTriggerMessage as ExternalTriggerMessage_pb2
from Collector.service.interface.TransponderInterface import InformationTransponderInterface


class ExternalTriggerController(ExternalTriggerControllerInterface):

    @inject
    def __init__(self,
                 information_transponder: InformationTransponderInterface,
                 component_framework: ComponentFrameworkInterface):
        self.__information_transponder: InformationTransponderInterface = information_transponder
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("collectorLogger")
        self.__external_trigger_topic: str = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        external_trigger_message_key = MessageKeyEnum.EXTERNAL_TRIGGER.value
        self.__external_trigger_topic = message_key_topic_dict.get(external_trigger_message_key, None)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        external_trigger_message_key = MessageKeyEnum.EXTERNAL_TRIGGER.value
        self.__external_trigger_topic = message_key_topic_dict.get(external_trigger_message_key, None)

    async def startup(self):
        await self.__component_framework.bind_message(
            MessageBindingModel(
                message_key=MessageKeyEnum.EXTERNAL_TRIGGER.value,
                topic=self.__external_trigger_topic
            )
        )

        class ReceiveExternalTriggerMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self, information_transponder: InformationTransponderInterface):
                self.__information_transponder: InformationTransponderInterface = information_transponder
                self.__logger = logging.getLogger("collectorLogger")

            async def receive_message(self, data: bytes) -> None:
                external_trigger_model = ExternalTriggerMessageConverter.protobuf_to_model(
                    ExternalTriggerMessage_pb2.ParseFromString(data))
                self.__logger.debug(f"Receive external trigger message {external_trigger_model}")
                await self.__information_transponder.receiver_external_trigger(external_trigger_model)

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.EXTERNAL_TRIGGER.value, ReceiveExternalTriggerMessageOperator(self.__information_transponder))

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.EXTERNAL_TRIGGER.value)
