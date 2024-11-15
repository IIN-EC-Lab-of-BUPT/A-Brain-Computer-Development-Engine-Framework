from abc import ABC, abstractmethod

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from CentralController.common.model.ComponentInformationModel import ComponentInformationModel
from CentralController.common.model.GroupInformationModel import GroupInformationModel


class ServiceCoordinatorInterface(ABC):
    """
    服务协调器接口
    负责各个组件之间消息协调
    """

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
    async def on_register_component(self, component_model: ComponentModel) -> ComponentModel:
        pass

    @abstractmethod
    async def on_unregister_component(self, component_model: ComponentModel) -> None:
        pass

    @abstractmethod
    async def on_bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
        pass

    @abstractmethod
    def get_registered_component_information_model_dict(self) -> dict[str, ComponentInformationModel]:
        pass

    @abstractmethod
    def get_static_group_information_model_dict(self) -> dict[str, GroupInformationModel]:
        pass
