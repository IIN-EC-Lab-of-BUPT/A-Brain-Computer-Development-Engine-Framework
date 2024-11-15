import importlib
import logging
import os
import sys
from typing import Union, Optional
from injector import inject
from Stimulator.facade.interface.TriggerSystemInterface import TriggerSystemInterface
from Stimulator.service.interface.ServiceManagerInterface import TriggerManagerInterface


class TriggerManager(TriggerManagerInterface):
    """
    ReceiverManager
    """

    @inject
    def __init__(self):
        self.__current_trigger: Optional[TriggerSystemInterface] = None
        self.__config_dict: Optional[dict[str, Union[str, dict]]] = dict[str, Union[str, dict]]()
        self.__logger = logging.getLogger("stimulatorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            self.__config_dict = config_dict
        else:
            self.__config_dict.update(config_dict)
        self.__logger.debug("TriggerManager初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)
        if self.__current_trigger is not None:
            await self.__current_trigger.update(self.__config_dict)

    def get_trigger_sender(self) -> TriggerSystemInterface:
        return self.__current_trigger

    async def startup(self) -> None:
        sub_dictionary = self.__config_dict.get('trigger_sender', dict())
        class_file = sub_dictionary.get('trigger_sender_class_file', None)
        class_name = sub_dictionary.get('trigger_sender_class_name', None)
        self.__logger.debug(f"当前选择的trigger send mode为:{class_name}")
        instance = self.__create_instance(class_file, class_name)
        self.__current_trigger = instance
        self.__logger.debug("TriggerManager启动完成")

    async def shutdown(self) -> None:
        self.__current_trigger = None

    @staticmethod
    def __create_instance(class_file: str, class_name: str) -> TriggerSystemInterface:
        # 辅助读取策略信息并生成实例
        workspace_path = os.getcwd()
        parent_dir = os.path.dirname(workspace_path)
        new_dir_path = os.path.join(parent_dir, "Stimulator")
        absolute_class_file = os.path.join(new_dir_path, class_file)
        module_name = os.path.splitext(os.path.basename(absolute_class_file))[0]
        # 获取模块所在的目录
        module_dir = os.path.dirname(absolute_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        target_class = getattr(module, class_name)
        instance = target_class()
        return instance
