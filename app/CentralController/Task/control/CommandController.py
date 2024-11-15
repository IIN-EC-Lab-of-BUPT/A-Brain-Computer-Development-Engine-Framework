import logging
from typing import Union

from injector import inject

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from Task.api.converter.TaskControlMessageConverter import TaskControlMessageConverter
from Task.api.message.MessageKeyEnum import MessageKeyEnum
from Task.api.model.TaskControlModel import ApplicationExitControlModel
from Task.common.enum.TaskEventEnum import TaskEventEnum
from Task.common.utils.EventManager import EventManager
from Task.control.interface.ControllerInterface import CommandControllerInterface
from Task.api.protobuf.TaskControl_pb2 import TaskControlMessage as TaskControlMessage_pb2


class CommandController(CommandControllerInterface):

    @inject
    def __init__(self, event_manager: EventManager,
                 component_framework: ComponentFrameworkInterface,):

        self.__event_manager: EventManager = event_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("taskLogger")
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
                message_key= MessageKeyEnum.COMMAND_CONTROL.value,
                topic=self.__command_control_topic
            )
        )

        class ReceiveCommandControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self,  event_manager: EventManager):
                self.__event_manager: EventManager = event_manager
                self.__logger = logging.getLogger("taskLogger")

            async def __application_exit_control_func(self):
                await self.__event_manager.notify(TaskEventEnum.APPLICATION_EXIT.value)

            async def receive_message(self, data: bytes) -> None:
                task_control_model = TaskControlMessageConverter.protobuf_to_model(
                    TaskControlMessage_pb2.FromString(data)
                )
                self.__logger.info(f"收到任务控制消息: {task_control_model}")
                if isinstance(task_control_model.package, ApplicationExitControlModel):
                    await self.__application_exit_control_func()

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.COMMAND_CONTROL.value,
            ReceiveCommandControlMessageOperator(
                event_manager=self.__event_manager)
        )

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.COMMAND_CONTROL.value)


