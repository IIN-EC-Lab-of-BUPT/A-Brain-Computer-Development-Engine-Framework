from abc import ABC, abstractmethod
from typing import Union

from Common.model.CommonMessageModel import DataMessageModel


class ConnectorOperatorInterface(ABC):

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass


class ConnectorSubscribeDataOperatorInterface(ConnectorOperatorInterface):

    @abstractmethod
    async def run(self, received_model: DataMessageModel):
        pass


class ConnectorUpdateConfigOperatorInterface(ConnectorOperatorInterface):

    @abstractmethod
    async def run(self, config_dict: dict[str, Union[str, dict]]):
        pass

