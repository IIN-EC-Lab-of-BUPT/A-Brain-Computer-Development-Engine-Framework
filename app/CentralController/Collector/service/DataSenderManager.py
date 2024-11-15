import importlib
import logging
import os
import sys
from typing import Union
from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Collector.datasender.interface.DataSenderInterface import DataSenderInterface
from Collector.service.interface.DataSenderManagerInterface import DataSenderManagerInterface


class DataSenderManager(DataSenderManagerInterface):
    # 预处理管理器
    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__component_framework: ComponentFrameworkInterface = component_framework
        self.__current_data_sender: DataSenderInterface = None

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

    def get_data_sender(self) -> DataSenderInterface:
        return self.__current_data_sender

    async def startup(self) -> None:
        sub_dictionary = self.__config_dict.get('data_sender', dict())
        class_file = sub_dictionary.get('data_sender_class_file', None)
        class_name = sub_dictionary.get('data_sender_class_name', None)
        instance: DataSenderInterface = self.__create_instance(class_file, class_name)
        instance.set_component_framework(self.__component_framework)
        await instance.initial(self.__config_dict)
        self.__current_data_sender = instance

    async def shutdown(self) -> None:
        self.__current_data_sender = None

    @staticmethod
    def __create_instance(class_file: str, class_name: str) -> DataSenderInterface:
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
