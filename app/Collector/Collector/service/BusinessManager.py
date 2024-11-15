import logging
from enum import Enum
from typing import Union

from injector import inject

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Collector.common.converter.ReceiverTransferModelToDataMessageModelConverter import \
    ReceiverTransferModelToDataMessageModelConverter
from Collector.datasender.interface.DataSenderInterface import DataSenderInterface
from Collector.receiver.interface.ReceiverInterface import ReceiverInterface, EEGReceiverInterface
from Collector.api.exception.CollectorException import ReceiverNotSupportCommandException
from Collector.api.message.MessageKeyEnum import MessageKeyEnum
from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Collector.receiver.model.ReceiverTransferModel import ReceiverTransferModel
from Collector.service.exception.BusinessCollectorException import BusinessStatusesNotSuitableException
from Collector.service.interface.BusinessManagerInterface import BusinessManagerInterface
from Collector.service.interface.ReceiverManagerInterface import ReceiverManagerInterface
from Collector.service.interface.DataSenderManagerInterface import DataSenderManagerInterface


class BusinessStatusEnum(Enum):
    READY = 'READY'
    DATASENDING = 'DATASENDING'
    STOPPED = 'STOPPED'


class BusinessManager(BusinessManagerInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__receiver_manager: ReceiverManagerInterface = None
        self.__data_sender_manager: DataSenderManagerInterface = None
        self.__component_framework: ComponentFrameworkInterface = component_framework

        self.__send_data_topic: str = None
        self.__logger = logging.getLogger("collectorLogger")
        self.__business_status: BusinessStatusEnum = BusinessStatusEnum.STOPPED
        self.__current_data_sender: DataSenderInterface = None
        self.__current_receiver: ReceiverInterface = None

    async def receiver_external_trigger(self, external_trigger_model: ExternalTriggerModel) -> None:
        await self.__current_data_sender.receiver_external_trigger(external_trigger_model)

    async def send_data(self, receiver_transfer_model: ReceiverTransferModel) -> None:
        await self.__current_data_sender.send_data(
            # 转换放大器接收数据类型为通用数据类型DataMessageModel
            ReceiverTransferModelToDataMessageModelConverter.convert(receiver_transfer_model)
            )

    async def start_data_sending(self):
        if self.__business_status != BusinessStatusEnum.READY:
            raise BusinessStatusesNotSuitableException(
                f"Business status is not {BusinessStatusEnum.READY}, now is {self.__business_status}")
        self.__business_status = BusinessStatusEnum.DATASENDING
        await self.__current_data_sender.start_data_sending()
        await self.__current_receiver.start_data_sending()

    async def stop_data_sending(self):
        if self.__business_status != BusinessStatusEnum.DATASENDING:
            raise BusinessStatusesNotSuitableException(
                f"Business status is not {BusinessStatusEnum.DATASENDING}, now is {self.__business_status}")
        await self.__current_receiver.stop_data_sending()
        await self.__current_data_sender.stop_data_sending()
        self.__business_status = BusinessStatusEnum.READY

    async def send_device_info(self):
        await self.__current_receiver.send_device_info()

    async def send_impedance(self):
        if isinstance(self.__current_receiver, EEGReceiverInterface):
            await self.__current_receiver.send_impedance()
        else:
            raise ReceiverNotSupportCommandException("Receiver does not support send impedance command")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        send_data_message_key = MessageKeyEnum.SEND_DATA.value
        self.__send_data_topic = message_key_topic_dict.get(send_data_message_key, None)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        message_key_topic_dict = config_dict.get("message", dict[str, str]())
        send_data_message_key = MessageKeyEnum.SEND_DATA.value
        self.__send_data_topic = message_key_topic_dict.get(send_data_message_key, None)

    async def startup(self) -> None:
        self.__current_data_sender = self.__data_sender_manager.get_data_sender()
        self.__current_receiver = self.__receiver_manager.get_receiver()
        # 绑定所需消息
        await self.__component_framework.bind_message(
            MessageBindingModel(
                message_key=MessageKeyEnum.SEND_DATA.value,
                topic=self.__send_data_topic
            )
        )

        # 启动指定预处理和指定接收器
        await self.__current_data_sender.startup()
        await self.__current_receiver.startup()
        self.__business_status = BusinessStatusEnum.READY

    async def shutdown(self) -> None:
        # 停止指定预处理和指定接收器
        await self.__current_receiver.shutdown()
        await self.__current_data_sender.shutdown()
        self.__business_status = BusinessStatusEnum.STOPPED

    def set_receiver_manager(self, receiver_manager: ReceiverManagerInterface):
        self.__receiver_manager = receiver_manager

    def set_data_sender_manager(self, data_sender_manager: DataSenderManagerInterface):
        self.__data_sender_manager = data_sender_manager
