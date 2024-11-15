import importlib
import logging
import os
import sys
from typing import Union
from injector import inject
from Stimulator.Paradigm.interface.ProxyInterface import ProxyInterface
from Stimulator.Paradigm.interface.paradigminterface import ParadigmInterface
from Stimulator.service.interface.ServiceManagerInterface import ParadigmManagerInterface


class ParadigmManager(ParadigmManagerInterface):
    # 预处理管理器
    @inject
    def __init__(self, method_proxy: ProxyInterface):
        self.__method_proxy: ProxyInterface = method_proxy
        self.__current_paradigm: ParadigmInterface = None
        self.__config_dict: dict[str, Union[str, dict]] = dict[str, Union[str, dict]]()
        self.__logger = logging.getLogger("stimulatorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            self.__config_dict = config_dict
        else:
            self.__config_dict.update(config_dict)
        self.__logger.debug("ParadigmManager初始化完成")

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            return
        self.__config_dict.update(config_dict)

    def get_paradigm(self) -> ParadigmInterface:
        return self.__current_paradigm

    async def startup(self) -> None:
        sub_dictionary = self.__config_dict.get('paradigm', dict())
        class_file = sub_dictionary.get('paradigm_class_file', None)
        class_name = sub_dictionary.get('paradigm_class_name', None)
        self.__logger.debug(f"当前选择的paradigm为:{class_name}")
        instance: ParadigmInterface = self.__create_instance(class_file, class_name)
        await instance.set_proxy(self.__method_proxy)
        self.__current_paradigm = instance
        self.__logger.debug("ParadigmManager启动完成")

    async def shutdown(self) -> None:
        self.__current_paradigm = None

    @staticmethod
    def __create_instance(class_file: str, class_name: str) -> ParadigmInterface:
        # 辅助读取策略信息并生成实例
        workspace_path = os.getcwd()
        parent_dir = os.path.dirname(workspace_path)
        new_dir_path = os.path.join(parent_dir,"Stimulator")
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
