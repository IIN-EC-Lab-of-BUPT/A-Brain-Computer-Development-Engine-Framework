from abc import ABC, abstractmethod
from typing import Union

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from Common.model.CommonMessageModel import DataMessageModel
from Task.facade.interface.ConnectorOperatorInterface import ConnectorUpdateConfigOperatorInterface, \
    ConnectorSubscribeDataOperatorInterface


class SystemConnectorInterface(ABC):

    @abstractmethod
    async def bind_message(self, message_key: str, topic: str = None) -> None:
        pass

    @abstractmethod
    async def subscribe_source(self, source_label: str,
                               operator: ConnectorSubscribeDataOperatorInterface) -> None:
        pass

    @abstractmethod
    async def unsubscribe_source(self, source_label: str):
        pass

    @abstractmethod
    async def send_message(self, message_key: str, data_message_model: DataMessageModel) -> None:
        pass

    @abstractmethod
    async def send_component_config(self, config_dict: dict[str, Union[str, dict]]):
        pass

    @abstractmethod
    # 获取与自己相关的全部配置信息
    async def get_component_model(self) -> ComponentModel:
        pass

    @abstractmethod
    async def subscribe_config_update(self, operator: ConnectorUpdateConfigOperatorInterface) -> None:
        pass
