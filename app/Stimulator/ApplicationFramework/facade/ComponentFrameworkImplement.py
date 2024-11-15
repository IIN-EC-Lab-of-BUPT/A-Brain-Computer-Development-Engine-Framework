from typing import Union

from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.common.utils.ContextManager import ContextManager
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface, \
    RegisterComponentOperatorInterface, UnRegisterComponentOperatorInterface, UpdateConfigOperatorInterface, \
    RequestApplicationExitOperatorInterface, BindMessageOperatorInterface, UpdateComponentStatusOperatorInterface

from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from ApplicationFramework.api.model.ComponentModel import ComponentModel
from componentframework.api.ComponentManagerInterface import ComponentManagerInterface
from componentframework.api.ConfigManagerInterface import ConfigManagerInterface
from componentframework.api.ConnectManagerInterface import ConnectManagerInterface
from componentframework.api.MessageManagerInterface import MessageManagerInterface
from componentframework.api.callback.interface.CoreFrameworkOperatorInterface import \
    AddListenerOnGlobalConfigCallbackInterface, SubscribeTopicCallbackInterface, \
    AddListenerOnUpdateComponentInfoCallbackInterface, AddListenerOnRegisterComponentCallbackInterface, \
    AddListenerOnUnregisterComponentCallbackInterface, AddListenerOnRequestComponentStopCallbackInterface, \
    AddListenerOnBindMessageCallbackInterface, AddListenerOnUpdateComponentStateCallbackInterface
from componentframework.api.impl.ComponentFrameworkManager import ComponentFrameworkManager
from componentframework.api.interface.ComponentFrameworkManagerinterface import ComponentFrameworkManagerInterface
from componentframework.api.model.ComponentStartupConfigurationModel import ComponentStartupConfigurationModel, \
    ComponentPatternEnum
from componentframework.api.model.MessageModel import MessageModel
from componentframework.api.model.MessageOperateModel import AddListenerOnUpdateComponentInfoComponentModel, \
    AddListenerOnRegisterComponentModel, AddListenerOnUnregisterComponentModel, AddListenerOnBindMessageModel, \
    AddListenerOnUpdateComponentStateModel
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum as ComponentFrameworkComponentStatusEnum
from componentframework.api.model.MessageModel import ComponentModel as ComponentModel_CCM


class ComponentFrameworkImplement(ComponentFrameworkInterface):

    def __init__(self):
        self.__component_framework_manager: ComponentFrameworkManagerInterface = None
        self.__component_manager: ComponentManagerInterface = None
        self.__message_component: MessageManagerInterface = None
        self.__connector_manager: ConnectManagerInterface = None
        self.__config_manager: ConfigManagerInterface = None
        self.__context_manager: ContextManager = ContextManager()
        self.__daemon_address: str = None
        self.__daemon_port: int = None

    async def get_global_config(self) -> dict[str, Union[str, dict]]:
        return await self.__config_manager.get_global_config()

    async def update_global_config(self, config_dict: dict[str, Union[str, dict]]):
        return await self.__config_manager.update_global_config(config_dict)

    async def add_listener_on_update_global_config(self, operator: UpdateConfigOperatorInterface):
        class AddListenerOnGlobalConfigCallback(AddListenerOnGlobalConfigCallbackInterface):
            async def run(self, data: dict[str, Union[str, dict]]) -> None:
                await operator.on_update_config(data)

        await self.__config_manager.add_listener_on_global_config(AddListenerOnGlobalConfigCallback())

    async def cancel_listener_on_update_global_config(self) -> None:
        await self.__config_manager.cancel_add_listener_on_global_config()

    async def bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
        new_message_model = await self.__message_component.bind_message(
            MessageModel(
                component_id=message_binding_model.component_id,
                message_key=message_binding_model.message_key,
                topic=message_binding_model.topic,
            )
        )
        return MessageBindingModel(
            component_id=new_message_model.component_id,
            message_key=new_message_model.message_key,
            topic=new_message_model.topic,
        )

    async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> str:
        return await self.__message_component.get_topic_by_message_key(message_key, component_id)

    async def subscribe_message(self, message_key: str, operator: ReceiveMessageOperatorInterface) -> None:
        class SubscribeTopicCallbackImpl(SubscribeTopicCallbackInterface):

            async def run(self, data: bytes) -> None:
                await operator.receive_message(data)

        await self.__message_component.subscribe_topic(SubscribeTopicCallbackImpl(), message_key)

    async def unsubscribe_message(self, message_key: str):
        await self.__message_component.unsubscribe_source(message_key)

    async def send_message(self, message_key: str, message: bytes) -> None:
        await self.__message_component.send_message(message_key, message)

    async def register_component(self, component_model: ComponentModel) -> ComponentModel:
        registered_component: ComponentModel_CCM = await self.__component_manager.component_register(
            ComponentModel_CCM(
                component_type=component_model.component_type,
                component_info=component_model.component_info,
                component_id=component_model.component_id
            )
        )
        return ComponentModel(component_id=registered_component.component_id,
                              component_type=registered_component.component_type,
                              component_info=registered_component.component_info)

    async def unregister_component(self) -> None:
        await self.__component_manager.unregister_component()

    async def get_component_model(self, component_id: str = None) -> ComponentModel:
        component_info_model = await self.__component_manager.get_component_info(component_id)
        return ComponentModel(component_id=component_info_model.component_id,
                              component_type=component_info_model.component_type,
                              component_info=component_info_model.component_info)

    async def update_component_info(self, component_info: dict, component_id: str = None) -> None:
        await self.__component_manager.update_component_info(component_info, component_id)

    async def add_listener_on_update_component_info(
            self, operator: UpdateConfigOperatorInterface, component_id: str = None) -> None:
        class AddListenerOnUpdateComponentInfoCallbackImpl(AddListenerOnUpdateComponentInfoCallbackInterface):
            async def run(self, data: AddListenerOnUpdateComponentInfoComponentModel) -> None:
                await operator.on_update_config(data.component_info)

        await self.__component_manager.add_listener_on_update_component_info(
            AddListenerOnUpdateComponentInfoCallbackImpl(), component_id)

    async def cancel_listener_on_update_component_info(self, component_id: str = None) -> None:
        await self.__component_manager.cancel_add_listener_on_update_component_info(component_id)

    async def update_component_status(self, component_status: ComponentStatusEnum, component_id: str = None) -> None:
        component_framework_component_status = next(
            (target_enum for target_enum in ComponentFrameworkComponentStatusEnum
             if target_enum.value == component_status.value), None)
        await self.__component_manager.update_component_state(component_framework_component_status, component_id)

    async def get_component_status(self, component_id: str = None) -> ComponentStatusEnum:
        component_framework_component_status: ComponentFrameworkComponentStatusEnum = \
            await self.__component_manager.get_component_state(component_id)
        component_status = next(
            (target_enum for target_enum in ComponentStatusEnum
             if target_enum.value == component_framework_component_status.value), None)
        return component_status

    async def add_listener_on_update_component_status(self, operator: UpdateComponentStatusOperatorInterface,
                                                      component_id: str = None) -> None:
        class AddListenerOnUpdateComponentStateCallbackImpl(AddListenerOnUpdateComponentStateCallbackInterface):

            async def run(self, data: AddListenerOnUpdateComponentStateModel) -> None:
                component_state: ComponentFrameworkComponentStatusEnum = data.component_state
                await operator.on_update_component_status(data.component_id, component_state.name)

        await self.__component_manager.add_listener_on_update_component_state(
            AddListenerOnUpdateComponentStateCallbackImpl(), component_id)

    async def cancel_listener_on_update_component_status(self, component_id: str = None) -> None:
        await self.__component_manager.cancel_add_listener_on_update_component_state(component_id)

    async def add_listener_on_bind_message(self, operator: BindMessageOperatorInterface) -> None:
        class AddListenerOnBindMessageCallbackImpl(AddListenerOnBindMessageCallbackInterface):
            async def run(self, data: AddListenerOnBindMessageModel) -> AddListenerOnBindMessageModel:
                message_binding_model: MessageBindingModel = await operator.on_bind_message(
                    MessageBindingModel(
                        component_id=data.component_id,
                        message_key=data.message_key,
                        topic=data.topic
                    )
                )
                return AddListenerOnBindMessageModel(
                    component_id=message_binding_model.component_id,
                    message_key=message_binding_model.message_key,
                    topic=message_binding_model.topic
                )

        await self.__message_component.add_listener_on_bind_message(AddListenerOnBindMessageCallbackImpl())

    async def cancel_listener_on_bind_message(self) -> None:
        await self.__message_component.cancel_add_listener_on_bind_message()

    async def add_listener_on_register_component(self, operator: RegisterComponentOperatorInterface) -> None:
        class AddListenerOnRegisterComponentCallbackImpl(AddListenerOnRegisterComponentCallbackInterface):
            async def run(self, data: AddListenerOnRegisterComponentModel) -> AddListenerOnRegisterComponentModel:
                component_model = await operator.on_register_component(
                    ComponentModel(
                        component_id=data.component_id,
                        component_type=data.component_type,
                        component_info=data.component_info
                    )
                )
                return AddListenerOnRegisterComponentModel(
                    component_id=component_model.component_id,
                    component_type=component_model.component_type,
                    component_info=component_model.component_info
                )

        await self.__component_manager.add_listener_on_register_component(AddListenerOnRegisterComponentCallbackImpl())

    async def cancel_listener_on_register_component(self) -> None:
        await self.__component_manager.cancel_add_listener_on_register_component()

    async def add_listener_on_unregister_component(self, operator: UnRegisterComponentOperatorInterface) -> None:
        class AddListenerOnUnregisterComponentCallbackImpl(AddListenerOnUnregisterComponentCallbackInterface):
            async def run(self, data: AddListenerOnUnregisterComponentModel) -> None:
                await operator.on_unregister_component(
                    ComponentModel(
                        component_id=data.component_id,
                        component_type=data.component_type,
                        component_info=data.component_info
                    )
                )

        await self.__component_manager.add_listener_on_unregister_component(
            AddListenerOnUnregisterComponentCallbackImpl())

    async def cancel_listener_on_unregister_component(self) -> None:
        await self.__component_manager.cancel_add_listener_on_unregister_component()

    def set_component_startup_configuration(
            self,
            daemon_address: str,
            daemon_port: int) -> None:
        self.__daemon_address = daemon_address
        self.__daemon_port = daemon_port

    async def get_all_component_id(self) -> list[str]:
        return await self.__component_manager.get_all_component()

    async def add_listener_on_request_application_exit(self, operator: RequestApplicationExitOperatorInterface) -> None:
        class AddListenerOnRequestComponentStopCallback(AddListenerOnRequestComponentStopCallbackInterface):
            async def run(self, data: str) -> None:
                await operator.on_request_application_exit()

        await self.__connector_manager.add_listener_on_request_component_stop(
            AddListenerOnRequestComponentStopCallback())

    async def initial(self) -> None:
        self.__component_framework_manager = ComponentFrameworkManager()
        self.__component_framework_manager.initial()
        self.__component_manager = self.__component_framework_manager.get_component_manager()
        self.__message_component = self.__component_framework_manager.get_message_manager()
        self.__connector_manager = self.__component_framework_manager.get_connect_manager()
        self.__config_manager = self.__component_framework_manager.get_config_manager()
        self.__context_manager.bind_class(ComponentManagerInterface, self.__component_manager)
        self.__context_manager.bind_class(MessageManagerInterface, self.__message_component)
        self.__context_manager.bind_class(ConfigManagerInterface, self.__config_manager)
        self.__context_manager.bind_class(ConnectManagerInterface, self.__connector_manager)
        self.__context_manager.bind_class(ComponentFrameworkManagerInterface, self.__component_framework_manager)

    async def startup(self) -> None:
        component_startup_configuration_model = ComponentStartupConfigurationModel(
            server_address=self.__daemon_address,
            server_port=self.__daemon_port
        )
        await self.__component_framework_manager.startup(component_startup_configuration_model)

    async def shutdown(self) -> None:
        await self.__connector_manager.shutdown()
