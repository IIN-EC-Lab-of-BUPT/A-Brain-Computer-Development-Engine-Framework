import logging
from typing import Union

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import UpdateConfigOperatorInterface
from Collector.control.interface.ControllerInterface import RPCControllerInterface, ExternalTriggerControllerInterface, \
    CommandControllerInterface
from Collector.service.interface.ConfigManagerInterface import ConfigManagerInterface
from Collector.service.interface.BusinessManagerInterface import BusinessManagerInterface
from Collector.service.interface.ReceiverManagerInterface import ReceiverManagerInterface
from Collector.service.interface.DataSenderManagerInterface import DataSenderManagerInterface


class ConfigManager(ConfigManagerInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface,
                 business_manager: BusinessManagerInterface,
                 data_sender_manager: DataSenderManagerInterface,
                 receiver_manager: ReceiverManagerInterface,
                 rpc_controller: RPCControllerInterface,
                 external_trigger_controller: ExternalTriggerControllerInterface,
                 command_controller: CommandControllerInterface):
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__data_sender_manager: DataSenderManagerInterface = data_sender_manager
        self.__receiver_manager: ReceiverManagerInterface = receiver_manager
        self.__rpc_controller: RPCControllerInterface = rpc_controller
        self.__external_trigger_controller: ExternalTriggerControllerInterface = external_trigger_controller
        self.__command_controller: CommandControllerInterface = command_controller
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        # 已经在ApplicationImplement中初始化完了
        return None

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        await self.__business_manager.update(config_dict)
        await self.__data_sender_manager.update(config_dict)
        await self.__receiver_manager.update(config_dict)
        await self.__rpc_controller.update(config_dict)
        await self.__external_trigger_controller.update(config_dict)
        await self.__command_controller.update(config_dict)

    async def startup(self) -> None:

        class UpdateConfigOperator(UpdateConfigOperatorInterface):
            def __init__(self, config_manager: ConfigManagerInterface):
                self.__config_manager = config_manager

            async def update_config(self, update_config_dict: dict[str, Union[str, dict]]) -> None:
                await self.__config_manager.update(update_config_dict)

        await self.__component_framework.add_listener_on_update_component_info(UpdateConfigOperator(self))

    async def shutdown(self) -> None:
        await self.__component_framework.cancel_listener_on_update_component_info()
