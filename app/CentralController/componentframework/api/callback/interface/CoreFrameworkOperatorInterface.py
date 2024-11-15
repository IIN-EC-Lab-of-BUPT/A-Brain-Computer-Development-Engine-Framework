from abc import ABC, abstractmethod
from typing import Union

from componentframework.api.model.MessageModel import ComponentModel, MessageModel
from componentframework.api.model.MessageOperateModel import AddListenerOnBindMessageModel, \
    AddListenerOnRegisterComponentModel, AddListenerOnUpdateComponentInfoComponentModel, \
    AddListenerOnUnregisterComponentModel, AddListenerOnUpdateComponentStateModel


class AddListenerOnGlobalConfigCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: dict[str, Union[str, dict]]) -> None:
        pass


class AddListenerOnBindMessageCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnBindMessageModel) -> MessageModel:
        pass


class SubscribeTopicCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: bytes) -> None:
        pass


class AddListenerOnRegisterComponentCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnRegisterComponentModel) -> ComponentModel:
        pass


class AddListenerOnUpdateComponentInfoCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentInfoComponentModel) -> None:
        pass


class AddListenerOnUnregisterComponentCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUnregisterComponentModel) -> None:
        pass


class AddListenerOnRequestComponentStopCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: str) -> None:
        pass


class AddListenerOnUpdateComponentStateCallbackInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentStateModel) -> None:
        pass
