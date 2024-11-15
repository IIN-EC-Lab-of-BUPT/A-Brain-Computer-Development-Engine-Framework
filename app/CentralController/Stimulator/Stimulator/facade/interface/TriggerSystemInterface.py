from abc import ABC, abstractmethod
from typing import Union
from Stimulator.facade.model.ExternalTriggerModel import ExternalTriggerModel


class TriggerSystemInterface(ABC):
    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass


class TriggerSendInterface(TriggerSystemInterface):

    @abstractmethod
    async def send(self, event):
        pass


class ExternalTriggerSendInterface(TriggerSystemInterface):
    @abstractmethod
    async def send(self, event: ExternalTriggerModel):
        pass


class GrpcConnectInterface(TriggerSystemInterface):
    @abstractmethod
    def initial_stub(self):
        pass
