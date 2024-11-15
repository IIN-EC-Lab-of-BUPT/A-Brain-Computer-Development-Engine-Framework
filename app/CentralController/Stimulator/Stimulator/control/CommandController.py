import asyncio
import logging
from typing import Union, Optional
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Stimulator.api.converter.CommandControlMessageConverter import (
    StimulationSystemCommandControlMessageConverter)
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum
from Stimulator.api.model.CommandControlModel import StartStimulationControlModel, StopStimulationControlModel, \
    QuitStimulationControlModel
from Stimulator.api.protobuf.out.CommandControl_pb2 import \
    StartStimulationControlMessage as StimulationControlMessage_pb2
from Stimulator.control.interface.ControllerInterface import CommandControllerInterface
from Stimulator.service.interface.ServiceManagerInterface import BusinessManagerInterface


# from Stimulator.test.sendcontrol import controller


class CommandController(CommandControllerInterface):

    @inject
    def __init__(self,
                 business_manager: BusinessManagerInterface,
                 component_framework: ComponentFrameworkInterface):
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("stimulatorLogger")
        self.__command_control_topic: Optional[str] = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        command_control_message_key = MessageKeyEnum.COMMAND_CONTROL.value
        self.__command_control_topic = message_key_topic_dict.get(command_control_message_key, None)
        self.__logger.debug("CommandController初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        command_control_message_key = MessageKeyEnum.COMMAND_CONTROL.value
        self.__command_control_topic = message_key_topic_dict.get(command_control_message_key, None)

    async def startup(self):
        message_binding_model = MessageBindingModel(message_key=MessageKeyEnum.COMMAND_CONTROL.value,
                                                    topic=self.__command_control_topic)
        await self.__component_framework.bind_message(message_binding_model)

        class ReceiveCommandControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self, business_manager: BusinessManagerInterface):
                self.__business_manager: BusinessManagerInterface = business_manager
                self.__logger = logging.getLogger("stimulatorLogger")

            async def receive_message(self, data) -> None:
                message = StimulationControlMessage_pb2()
                message.ParseFromString(data)
                StimulationControlModel = StimulationSystemCommandControlMessageConverter.protobuf_to_model(message)
                self.__logger.info(f"收到命令控制消息: {StimulationControlModel}")
                if isinstance(StimulationControlModel, StartStimulationControlModel):
                    await self.__business_manager.start_stimulation_system()
                elif isinstance(StimulationControlModel, StopStimulationControlModel):
                    await self.__business_manager.stop_stimulation_system()
                elif isinstance(StimulationControlModel, QuitStimulationControlModel):
                    await self.__business_manager.shutdown()

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.COMMAND_CONTROL.value, ReceiveCommandControlMessageOperator(self.__business_manager))
        await asyncio.sleep(0.1)
        self.__logger.debug("CommandController启动完成")
        # data = controller.start()
        # message = StimulationControlMessage_pb2()
        # message.ParseFromString(data)
        # StimulationControlModel = StimulationSystemCommandControlMessageConverter.protobuf_to_model(message)
        # if isinstance(StimulationControlModel, StartStimulationControlModel):
        #     await self.__business_manager.start_stimulation_system()
        # elif isinstance(StimulationControlModel, StopStimulationControlModel):
        #     await self.__business_manager.stop_stimulation_system()
        # elif isinstance(StimulationControlModel, QuitStimulationControlModel):
        #     await self.__business_manager.shutdown()

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.COMMAND_CONTROL.value)
