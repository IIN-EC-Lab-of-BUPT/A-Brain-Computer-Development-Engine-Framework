import logging
from injector import inject

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ProcessHub.api.converter.ProcessHubControlMessageConverter import ProcessHubControlMessageConverter
from ProcessHub.api.message.MessageKeyEnum import MessageKeyEnum
from ProcessHub.api.model.ProcessHubControlModel import ApplicationExitControlModel
from ProcessHub.common.enum.ProcessHubEventEnum import ProcessHubEventEnum
from ProcessHub.common.utils.EventManager import EventManager
from ProcessHub.control.interface.ControllerInterface import CommandControllerInterface
from ProcessHub.api.protobuf.ProcessHubControl_pb2 import ProcessHubControlMessage as ProcessHubControlMessage_pb2


class CommandController(CommandControllerInterface):

    @inject
    def __init__(self, event_manager: EventManager,
                 component_framework: ComponentFrameworkInterface,):

        self.__event_manager: EventManager = event_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("processHubLogger")
        self.__command_control_topic: str = None

    async def initial(self, command_control_topic: str = None):
        self.__command_control_topic = command_control_topic

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
                self.__logger = logging.getLogger("processHubLogger")

            async def __application_exit_control_func(self):
                await self.__event_manager.notify(ProcessHubEventEnum.APPLICATION_EXIT.value)

            async def receive_message(self, data: bytes) -> None:
                task_control_model = ProcessHubControlMessageConverter.protobuf_to_model(
                    ProcessHubControlMessage_pb2.FromString(data)
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


