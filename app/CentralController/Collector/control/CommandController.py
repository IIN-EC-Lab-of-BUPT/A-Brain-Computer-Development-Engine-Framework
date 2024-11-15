import logging
from typing import Union

from injector import inject

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from Collector.api.converter.CollectorControlMessageConverter import CollectorControlMessageConverter
from Collector.api.message.MessageKeyEnum import MessageKeyEnum
from Collector.api.model.CollectorControlModel import StartDataSendingControlModel, StopDataSendingControlModel, \
    SendDeviceInfoControlModel, SendImpedanceControlModel, ApplicationExitControlModel
from Collector.common.enum.CollectorEventEnum import CollectorEventEnum
from Collector.common.utils.EventManager import EventManager
from Collector.control.interface.ControllerInterface import CommandControllerInterface
from Collector.service.exception.BusinessCollectorException import BusinessCollectorException
from Collector.service.interface.BusinessManagerInterface import BusinessManagerInterface
from Collector.api.protobuf.CollectorControl_pb2 import CollectorControlMessage as CollectorControlMessage_pb2


class CommandController(CommandControllerInterface):

    @inject
    def __init__(self,
                 business_manager: BusinessManagerInterface,
                 component_framework: ComponentFrameworkInterface,
                 event_manager: EventManager):
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__event_manager: EventManager = event_manager
        self.__logger = logging.getLogger("collectorLogger")
        self.__command_control_topic: str = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        command_control_message_key = MessageKeyEnum.COMMAND_CONTROL.value
        self.__command_control_topic = message_key_topic_dict.get(command_control_message_key, None)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        command_control_message_key = MessageKeyEnum.COMMAND_CONTROL.value
        self.__command_control_topic = message_key_topic_dict.get(command_control_message_key, None)

    async def startup(self):
        await self.__component_framework.bind_message(
            MessageBindingModel(
                message_key=MessageKeyEnum.COMMAND_CONTROL.value,
                topic=self.__command_control_topic
            )
        )

        class ReceiveCommandControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self,
                         event_manager: EventManager,
                         business_manager: BusinessManagerInterface):
                self.__logger = logging.getLogger("collectorLogger")
                self.__business_manager: BusinessManagerInterface = business_manager
                self.__event_manager: EventManager = event_manager

            async def __application_exit_control_func(self):
                self.__logger.info("收到Application exit请求")
                await self.__event_manager.notify(CollectorEventEnum.APPLICATION_EXIT.value)

            async def receive_message(self, data: bytes) -> None:
                collector_control_model = CollectorControlMessageConverter.protobuf_to_model(
                    CollectorControlMessage_pb2.FromString(data)
                )
                self.__logger.info(f"收到命令控制消息: {collector_control_model}")
                try:
                    if isinstance(collector_control_model.package, StartDataSendingControlModel):
                        await self.__business_manager.start_data_sending()
                    elif isinstance(collector_control_model.package, StopDataSendingControlModel):
                        await self.__business_manager.stop_data_sending()
                    elif isinstance(collector_control_model.package, SendDeviceInfoControlModel):
                        await self.__business_manager.send_device_info()
                    elif isinstance(collector_control_model.package, SendImpedanceControlModel):
                        await self.__business_manager.send_impedance()
                    elif isinstance(collector_control_model.package, ApplicationExitControlModel):
                        await self.__application_exit_control_func()
                except BusinessCollectorException as e:
                    self.__logger.error(e)

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.COMMAND_CONTROL.value,
            ReceiveCommandControlMessageOperator(
                event_manager=self.__event_manager,
                business_manager=self.__business_manager)
        )

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.COMMAND_CONTROL.value)


