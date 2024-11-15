import logging
from typing import Union
from injector import inject
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import UpdateConfigOperatorInterface
from Stimulator.control.interface.ControllerInterface import CommandControllerInterface, \
    FeedbackControllerInterface, RandomNumberSeedsControllerInterface
from Stimulator.facade.interface.TriggerSystemInterface import TriggerSendInterface, \
    ExternalTriggerSendInterface, GrpcConnectInterface
from Stimulator.service.interface.ServiceManagerInterface import ConfigManagerInterface, \
    BusinessManagerInterface, ParadigmManagerInterface, TriggerManagerInterface


class ConfigManager(ConfigManagerInterface):
    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface,
                 business_manager: BusinessManagerInterface,
                 paradigm_manager: ParadigmManagerInterface,
                 trigger_manager: TriggerManagerInterface,
                 command_controller: CommandControllerInterface,
                 feedback_controller: FeedbackControllerInterface,
                 random_number_seeds_controller: RandomNumberSeedsControllerInterface):
        self.__config_dict: dict = None
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__paradigm_manager: ParadigmManagerInterface = paradigm_manager
        self.__trigger_manager: TriggerManagerInterface = trigger_manager
        self.__command_controller: CommandControllerInterface = command_controller
        self.__feedback_controller: FeedbackControllerInterface = feedback_controller
        self.__random_number_seeds_controller: RandomNumberSeedsControllerInterface = random_number_seeds_controller
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__logger = logging.getLogger("stimulatorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        # 已经在ApplicationImplement中初始化完了
        self.__config_dict = config_dict
        self.__logger.debug("ConfigManager初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        await self.__business_manager.update(config_dict)
        await self.__paradigm_manager.update(config_dict)
        await self.__trigger_manager.update(config_dict)
        await self.__command_controller.update(config_dict)
        await self.__feedback_controller.update(config_dict)
        await self.__random_number_seeds_controller.update(config_dict)

    async def startup(self) -> None:
        class UpdateConfigOperator(UpdateConfigOperatorInterface):
            def __init__(self, config_manager: ConfigManagerInterface):
                self.__config_manager = config_manager

            async def update_config(self, update_config_dict: dict[str, Union[str, dict]]) -> None:
                await self.__config_manager.update(update_config_dict)
        await self.__component_framework.add_listener_on_update_component_info(operator=UpdateConfigOperator(self))
        self.__logger.debug("ConfigManager启动已完成")

    async def shutdown(self) -> None:
        await self.__component_framework.cancel_listener_on_update_component_info()
