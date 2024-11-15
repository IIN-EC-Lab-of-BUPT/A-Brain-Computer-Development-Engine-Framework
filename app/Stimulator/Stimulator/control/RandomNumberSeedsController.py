import asyncio
import logging
from typing import Union, Optional
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Stimulator.api.converter.RandomNumberSeedsMessageConverter import RandomNumberSeedsMessageConverter
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel
from Stimulator.api.protobuf.out.RandomNumberSeeds_pb2 import RandomNumberSeedsMessage as RandomNumberSeeds_pb2
from Stimulator.control.interface.ControllerInterface import RandomNumberSeedsControllerInterface
from Stimulator.service.interface.ServiceManagerInterface import BusinessManagerInterface


class RandomNumberSeedsController(RandomNumberSeedsControllerInterface):

    @inject
    def __init__(self,
                 business_manager: BusinessManagerInterface,
                 component_framework: ComponentFrameworkInterface):
        self.message_key_topic_dict = None
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("stimulatorLogger")
        self.__random_number_seeds_control_topic: Optional[str] = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        self.message_key_topic_dict = config_dict.get("message", dict[str, str]())
        random_number_seeds_control_message_key = MessageKeyEnum.RANDOM_NUMBER_SEEDS.value
        self.__random_number_seeds_control_topic = self.message_key_topic_dict.get(
            random_number_seeds_control_message_key, None)
        self.__logger.debug("RandomNumberSeedsController初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.message_key_topic_dict = config_dict.get("message", dict[str, str]())
        random_number_seeds_control_message_key = MessageKeyEnum.RANDOM_NUMBER_SEEDS.value
        self.__random_number_seeds_control_topic = self.message_key_topic_dict.get(
            random_number_seeds_control_message_key, None)

    async def startup(self):
        message_binding_model = MessageBindingModel(message_key=MessageKeyEnum.RANDOM_NUMBER_SEEDS.value,
                                                    topic=self.__random_number_seeds_control_topic)
        await self.__component_framework.bind_message(message_binding_model)

        class ReceiveFeedbackControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self, business_manager: BusinessManagerInterface):
                self.__business_manager: BusinessManagerInterface = business_manager
                self.__logger = logging.getLogger("stimulatorLogger")

            async def receive_message(self, data: bytes) -> None:
                message = RandomNumberSeeds_pb2()
                message.ParseFromString(data)
                random_number_seeds_model = RandomNumberSeedsMessageConverter.protobuf_to_model(message)
                self.__logger.info(f"收到random_number_seeds: {random_number_seeds_model}")
                await self.__business_manager.set_random_number_seeds(random_number_seeds_model)

        await self.__component_framework.subscribe_message(
            MessageKeyEnum.RANDOM_NUMBER_SEEDS.value, ReceiveFeedbackControlMessageOperator(self.__business_manager))
        await asyncio.sleep(0.1)
        self.__logger.debug("RandomNumberSeedsController启动完成")
        # await self.__business_manager.set_random_number_seeds(RandomNumberSeedsModel(seeds=0.5914468765258789))

    async def shutdown(self):
        await self.__component_framework.unsubscribe_message(MessageKeyEnum.RANDOM_NUMBER_SEEDS.value)
