import logging
from typing import Union

from injector import inject

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface, \
    UpdateConfigOperatorInterface
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import DataMessageModel
from Common.protobuf.CommonMessage_pb2 import DataMessage as DataMessage_pb2
from Task.facade.interface.ConnectorOperatorInterface import ConnectorSubscribeDataOperatorInterface, \
    ConnectorUpdateConfigOperatorInterface
from Task.facade.interface.SystemConnectorInterface import SystemConnectorInterface


class SystemConnector(SystemConnectorInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkApplicationInterface):
        self.__logger = logging.getLogger("taskLogger")
        self.__component_framework: ComponentFrameworkApplicationInterface = component_framework
        self.__common_message_converter = CommonMessageConverter()
        return

    async def subscribe_source(self, source_label: str,
                               operator: ConnectorSubscribeDataOperatorInterface) -> None:
        self.__logger.debug("SystemConnector.subscribe_source被调用")

        class ReceiveMessageOperator(ReceiveMessageOperatorInterface):
            async def receive_message(self, data: bytes) -> None:
                data_message = DataMessage_pb2()
                data_message.ParseFromString(data)
                package_name = data_message.WhichOneof('package')
                if package_name is not None:
                    data_message_model = CommonMessageConverter.protobuf_to_model(data_message)
                    await operator.run(data_message_model)

        await self.__component_framework.subscribe_message(source_label, ReceiveMessageOperator())

    async def unsubscribe_source(self, source_label: str):
        await self.__component_framework.unsubscribe_message(source_label)

    async def bind_message(self, message_key: str, topic: str = None) -> None:
        await self.__component_framework.bind_message(
            MessageBindingModel(
                message_key=message_key,
                topic=topic
            )
        )

    async def send_message(self, message_key: str, data_message_model: DataMessageModel) -> None:
        result_package = self.__common_message_converter.model_to_protobuf(data_message_model)
        await self.__component_framework.send_message(message_key, result_package.SerializeToString())
        self.__logger.debug(f"SystemConnector向{message_key}发送数据{result_package}")

    async def send_component_config(self, config_dict: dict[str, Union[str, dict]]):
        await self.__component_framework.update_component_info(config_dict)
        self.__logger.debug(f"SystemConnector发送{config_dict}配置信息")

    async def get_component_model(self) -> ComponentModel:
        return await self.__component_framework.get_component_model()

    async def subscribe_config_update(self, operator: ConnectorUpdateConfigOperatorInterface) -> None:
        self.__logger.debug("启动配置更新订阅")

        class UpdateConfigOperator(UpdateConfigOperatorInterface):
            async def on_update_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
                await operator.run(config_dict)

        await self.__component_framework.add_listener_on_update_component_info(UpdateConfigOperator())
