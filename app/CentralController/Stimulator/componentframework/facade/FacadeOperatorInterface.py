from abc import ABC, abstractmethod
from typing import Union
from componentframework.api.model.MessageOperateModel import AddListenerOnUnregisterComponentModel, \
    AddListenerOnUpdateComponentInfoComponentModel, AddListenerOnRegisterComponentModel, AddListenerOnBindMessageModel, \
    AddListenerOnUpdateComponentStateModel


class AddListenerOnGlobalConfigCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: dict[str, Union[str, dict]]) -> None:
        pass


class AddListenerOnBindMessageCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnBindMessageModel) -> None:
        pass


class SubscribeTopicCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: bytes) -> None:
        pass


class AddListenerOnRegisterComponentCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnRegisterComponentModel) -> None:
        pass


class AddListenerOnUpdateComponentInfoCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentInfoComponentModel) -> None:
        pass


class AddListenerOnUnregisterComponentCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUnregisterComponentModel) -> None:
        pass


class AddListenerOnRequestComponentStopCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: str) -> None:
        pass


class AddListenerOnUpdateComponentStateCallbackFacadeInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, data: AddListenerOnUpdateComponentStateModel) -> None:
        pass
