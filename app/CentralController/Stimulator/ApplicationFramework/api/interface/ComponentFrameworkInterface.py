from abc import ABC, abstractmethod
from typing import Union

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface, \
    RegisterComponentOperatorInterface, UnRegisterComponentOperatorInterface, UpdateConfigOperatorInterface, \
    RequestApplicationExitOperatorInterface, BindMessageOperatorInterface, UpdateComponentStatusOperatorInterface
from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from ApplicationFramework.api.model.ComponentModel import ComponentModel


class ComponentFrameworkApplicationInterface(ABC):

    @abstractmethod
    async def get_global_config(self) -> dict[str, Union[str, dict]]:
        pass

    @abstractmethod
    async def update_global_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    @abstractmethod
    async def add_listener_on_update_global_config(self, operator: UpdateConfigOperatorInterface) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_update_global_config(self) -> None:
        pass

    @abstractmethod
    async def bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
        """
        绑定消息message_key 与 对应topic，使用message_key收发消息前务必先绑定消息
        :param message_binding_model:
            message_key: 消息key
            topic: 消息topic
            component_id: 组件id
        :return: 
        MessageBindingModel: 绑定完毕的绑定信息
        """
        pass

    @abstractmethod
    async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> str:
        pass

    @abstractmethod
    async def subscribe_message(self, message_key: str, operator: ReceiveMessageOperatorInterface) -> None:
        pass

    @abstractmethod
    async def unsubscribe_message(self, message_key: str) -> None:
        pass

    @abstractmethod
    async def send_message(self, message_key: str, message: bytes) -> None:
        pass

    @abstractmethod
    async def register_component(self, component_model: ComponentModel) -> ComponentModel:
        pass

    @abstractmethod
    async def unregister_component(self) -> None:
        pass

    @abstractmethod
    async def get_component_model(self, component_id: str = None) -> ComponentModel:
        pass

    @abstractmethod
    async def update_component_info(self, component_info: dict, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def add_listener_on_update_component_info(
            self, operator: UpdateConfigOperatorInterface, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_update_component_info(self, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def update_component_status(self, component_status: ComponentStatusEnum, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def get_component_status(self, component_id: str = None) -> ComponentStatusEnum:
        pass

    @abstractmethod
    async def add_listener_on_update_component_status(
            self, operator: UpdateComponentStatusOperatorInterface, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_update_component_status(self, component_id: str = None) -> None:
        pass

    @abstractmethod
    async def add_listener_on_request_application_exit(self, operator: RequestApplicationExitOperatorInterface) -> None:
        pass

    @abstractmethod
    async def initial(self) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    @abstractmethod
    def set_component_startup_configuration(
            self,
            daemon_address: str,
            daemon_port: int) -> None:
        pass


class ComponentFrameworkInterface(ComponentFrameworkApplicationInterface):

    @abstractmethod
    async def add_listener_on_bind_message(self, operator: BindMessageOperatorInterface) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_bind_message(self) -> None:
        pass

    @abstractmethod
    async def add_listener_on_register_component(self, operator: RegisterComponentOperatorInterface) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_register_component(self) -> None:
        pass

    @abstractmethod
    async def add_listener_on_unregister_component(self, operator: UnRegisterComponentOperatorInterface) -> None:
        pass

    @abstractmethod
    async def cancel_listener_on_unregister_component(self) -> None:
        pass

    @abstractmethod
    async def get_all_component_id(self) -> list[str]:
        pass
