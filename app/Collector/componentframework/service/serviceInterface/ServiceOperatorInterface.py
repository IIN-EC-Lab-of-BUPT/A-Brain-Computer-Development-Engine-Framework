from abc import ABC, abstractmethod
from typing import Union
from componentframework.api.model.MessageOperateModel import AddListenerOnUnregisterComponentModel, \
    AddListenerOnUpdateComponentInfoComponentModel, AddListenerOnRegisterComponentModel, AddListenerOnBindMessageModel, \
    AddListenerOnUpdateComponentStateModel


class AddListenerOnGlobalConfigCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: dict[str, Union[str, dict]]) -> None:
        pass


class AddListenerOnBindMessageCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnBindMessageModel) -> None:
        pass


class SubscribeTopicCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: bytes) -> None:
        pass


class AddListenerOnRegisterComponentCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnRegisterComponentModel) -> None:
        pass


class AddListenerOnUpdateComponentInfoCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentInfoComponentModel) -> None:
        pass


class AddListenerOnUnregisterComponentCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUnregisterComponentModel) -> None:
        pass


class AddListenerOnRequestComponentStopCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: str) -> None:
        pass


class AddListenerOnUpdateComponentStateCallbackServiceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentStateModel) -> None:
        pass
