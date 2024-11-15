import importlib
import logging
import os
import sys
from typing import Union
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from Task.common.utils.EventManager import EventManager
from Task.facade.interface.RpcControllerInterface import RpcControllerManagementInterface
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface
from Task.service.interface.ServiceManagerInterface import StrategyManagerInterface, CoreControllerInterface
from Task.strategies.interface.StrategyInterface import StrategyInterface


class StrategyManager(StrategyManagerInterface):

    # 策略管理器
    # 通过注解实现单例模式，可通过ChallengeManager()直接获取单一实例
    @inject
    def __init__(self,
                 message_forwarder: MessageForwardApplicationInterface,
                 rpc_controller: RpcControllerManagementInterface,
                 event_manager: EventManager,
                 component_framework: ComponentFrameworkApplicationInterface
                 ):
        self.__strategy_class_name: str = None
        self.__strategy_class_file: str = None
        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__current_strategy: StrategyInterface = None
        self.__strategy_dict = dict[str, StrategyInterface]()
        self.__message_forwarder: MessageForwardApplicationInterface = message_forwarder
        self.__core_controller: CoreControllerInterface = None
        self.__rpc_controller: RpcControllerManagementInterface = rpc_controller
        self.__event_manager: EventManager = event_manager
        self.__component_framework: ComponentFrameworkApplicationInterface = component_framework
        self.__logger = logging.getLogger("taskLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        self.__config_dict = config_dict
        strategy_dict = config_dict.get('strategy', None)
        if strategy_dict is None:
            return
        self.__strategy_class_file = strategy_dict.get('strategy_class_file', "")
        self.__strategy_class_name = strategy_dict.get('strategy_class_name', "")
        self.__config_dict = config_dict

    async def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        self.__config_dict = config_dict
        if self.__current_strategy is not None:
            await self.__current_strategy.update(config_dict)
        strategy_dict = config_dict.get('strategy', None)
        if strategy_dict is None:
            return
        self.__strategy_class_file = strategy_dict.get('strategy_class_file', self.__strategy_class_file)
        self.__strategy_class_name = strategy_dict.get('strategy_class_name', self.__strategy_class_name)

    async def startup(self) -> None:
        self.__current_strategy = self.__load_strategy(self.__strategy_class_file, self.__strategy_class_name)
        self.__current_strategy.set_message_forwarder(self.__message_forwarder)
        self.__current_strategy.set_core_controller(self.__core_controller)
        self.__current_strategy.set_rpc_controller(self.__rpc_controller)
        self.__current_strategy.set_event_manager(self.__event_manager)
        self.__current_strategy.set_component_framework(self.__component_framework)
        await self.__current_strategy.initial(self.__config_dict)
        await self.__current_strategy.startup()

    async def shutdown(self) -> None:
        await self.__current_strategy.shutdown()
        self.__current_strategy = None

    @staticmethod
    def __load_strategy(strategy_class_file: str, strategy_class_name: str) -> StrategyInterface:
        # 辅助读取策略信息并生成实例
        workspace_path = os.getcwd()
        absolute_strategy_class_file = os.path.join(workspace_path, strategy_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_strategy_class_file))[0]
        # 获取模块所在的目录
        module_dir = os.path.dirname(absolute_strategy_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        strategy_class = getattr(module, strategy_class_name)
        instance = strategy_class()
        return instance

    def get_current_strategy(self) -> StrategyInterface:
        return self.__current_strategy

    def set_core_controller(self, core_controller: CoreControllerInterface):
        self.__core_controller = core_controller
