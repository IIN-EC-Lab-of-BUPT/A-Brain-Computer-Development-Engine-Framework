from abc import ABC, abstractmethod
from typing import Union

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Common.model.CommonMessageModel import DataMessageModel


class DataSenderInterface(ABC):

    def __init__(self):
        self._component_framework: ComponentFrameworkInterface = None

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    @abstractmethod
    async def start_data_sending(self):
        pass

    @abstractmethod
    async def stop_data_sending(self):
        pass

    @abstractmethod
    async def send_data(self, data_message_model: DataMessageModel) -> None:
        pass

    @abstractmethod
    async def receiver_external_trigger(self, external_trigger_model: ExternalTriggerModel) -> None:
        pass

    def set_component_framework(self, component_framework: ComponentFrameworkInterface) -> None:
        self._component_framework = component_framework
