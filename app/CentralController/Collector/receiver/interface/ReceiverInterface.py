from abc import ABC, abstractmethod
from typing import Union

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Collector.service.interface.TransponderInterface import ReceiverTransponderInterface


class ReceiverInterface(ABC):

    def __init__(self):
        self._component_framework: ComponentFrameworkInterface = None
        self._receiver_transponder: ReceiverTransponderInterface = None

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def start_data_sending(self) -> None:
        pass

    @abstractmethod
    async def stop_data_sending(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    @abstractmethod
    async def send_device_info(self) -> None:
        pass

    def set_receiver_transponder(self, receiver_transponder: ReceiverTransponderInterface) -> None:
        self._receiver_transponder = receiver_transponder

    def set_component_framework(self, component_framework: ComponentFrameworkInterface) -> None:
        self._component_framework = component_framework


class EEGReceiverInterface(ReceiverInterface):

    @abstractmethod
    async def send_impedance(self) -> None:
        pass
