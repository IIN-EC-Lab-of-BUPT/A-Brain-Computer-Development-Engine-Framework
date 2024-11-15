from abc import ABC
from typing import Union

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel


class ReceiveMessageOperatorInterface(ABC):

    async def receive_message(self, data: bytes) -> None:
        pass


class BindMessageOperatorInterface(ABC):
    async def on_bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
        pass


class RegisterComponentOperatorInterface(ABC):

    async def on_register_component(self, component_model: ComponentModel) -> ComponentModel:
        pass


class UnRegisterComponentOperatorInterface(ABC):

    async def on_unregister_component(self, component_model: ComponentModel) -> None:
        pass


class UpdateConfigOperatorInterface(ABC):

    async def on_update_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass


class UpdateComponentStatusOperatorInterface(ABC):
    async def on_update_component_status(self, component_id: str, component_status: str) -> None:
        pass


class RequestApplicationExitOperatorInterface(ABC):
    async def on_request_application_exit(self) -> None:
        pass
