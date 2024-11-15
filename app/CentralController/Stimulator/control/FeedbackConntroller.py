import asyncio
import logging
from typing import Union, Optional
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Common.converter.CommonMessageConverter import CommonMessageConverter
# from Common.model.BaseDataClassModel import IntListMessageModel
# from Common.model.CommonMessageModel import ResultPackageModel, BaseDataMessageClassEnum, ReportSourceInformationModel
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum
from Common.protobuf.CommonMessage_pb2 import DataMessage as DataMessage_2
from Stimulator.control.interface.ControllerInterface import FeedbackControllerInterface
from Stimulator.service.interface.ServiceManagerInterface import BusinessManagerInterface


class FeedbackController(FeedbackControllerInterface):

    @inject
    def __init__(self,
                 business_manager: BusinessManagerInterface,
                 component_framework: ComponentFrameworkInterface):
        self.message_key_topic_dict = None
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("stimulatorLogger")
        self.__command_control_topic: Optional[str] = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        self.message_key_topic_dict = config_dict.get("message", dict[str, str]())
        feedback_control_message_key = MessageKeyEnum.FEEDBACK_CONTROL.value
        self.__command_control_topic = self.message_key_topic_dict.get(feedback_control_message_key, None)
        self.__logger.debug("FeedbackController初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.message_key_topic_dict = config_dict.get("message", dict[str, str]())
        feedback_control_message_key = MessageKeyEnum.FEEDBACK_CONTROL.value
        self.__command_control_topic = self.message_key_topic_dict.get(feedback_control_message_key, None)

    async def startup(self):
        feedback_control_model = MessageBindingModel(message_key=MessageKeyEnum.FEEDBACK_CONTROL.value,
                                                    topic=self.__command_control_topic)
        await self.__component_framework.bind_message(feedback_control_model)

        class ReceiveFeedbackControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self, business_manager: BusinessManagerInterface):
                self.__business_manager: BusinessManagerInterface = business_manager
                self.__logger = logging.getLogger("stimulatorLogger")

            async def receive_message(self, data: bytes) -> None:
                message = DataMessage_2()
                message.ParseFromString(data)
                DataMessageModel = CommonMessageConverter.protobuf_to_model(message)
                self.__logger.info(f"收到反馈信息: {DataMessageModel}")
                await self.__business_manager.set_feedback_control_message(DataMessageModel.package)

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.FEEDBACK_CONTROL.value, ReceiveFeedbackControlMessageOperator(self.__business_manager))
        self.__logger.debug("FeedbackController启动完成")
        # result = ResultPackageModel(result=IntListMessageModel(data=[4]),
        #                             result_message_class=BaseDataMessageClassEnum.INT32LIST,
        #                             report_source_information=[
        #                                 ReportSourceInformationModel(source_label="None", position=1.32)])
        # await self.__business_manager.set_feedback_control_message(result)
        # await asyncio.sleep(1)

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.FEEDBACK_CONTROL.value)
