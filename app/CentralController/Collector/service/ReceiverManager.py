import importlib
import logging
import os
import sys
from typing import Union

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Collector.receiver.interface.ReceiverInterface import ReceiverInterface
from Collector.service.interface.BusinessManagerInterface import BusinessManagerInterface
from Collector.service.interface.ReceiverManagerInterface import ReceiverManagerInterface


class ReceiverManager(ReceiverManagerInterface):
    """
    ReceiverManager
    """
    @inject
    def __init__(self, business_manager: BusinessManagerInterface, component_framework: ComponentFrameworkInterface):
        self.__current_receiver: ReceiverInterface = None
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__config_dict: dict[str, Union[str, dict]] = dict[str, Union[str, dict]]()
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)

    def get_receiver(self) -> ReceiverInterface:
        return self.__current_receiver

    async def startup(self) -> None:
        sub_dictionary = self.__config_dict.get('receiver', dict())
        class_file = sub_dictionary.get('receiver_class_file', None)
        class_name = sub_dictionary.get('receiver_class_name', None)
        instance = self.__create_instance(class_file, class_name)
        instance.set_receiver_transponder(self.__business_manager)
        instance.set_component_framework(self.__component_framework)
        await instance.initial(self.__config_dict)
        self.__current_receiver = instance

    async def shutdown(self) -> None:
        self.__current_receiver = None

    @staticmethod
    def __create_instance(class_file: str, class_name: str) -> ReceiverInterface:
        # 辅助读取策略信息并生成实例
        workspace_path = os.getcwd()
        absolute_class_file = os.path.join(workspace_path, class_file)
        module_name = os.path.splitext(os.path.basename(absolute_class_file))[0]
        # 获取模块所在的目录
        module_dir = os.path.dirname(absolute_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        target_class = getattr(module, class_name)
        instance = target_class()
        return instance
