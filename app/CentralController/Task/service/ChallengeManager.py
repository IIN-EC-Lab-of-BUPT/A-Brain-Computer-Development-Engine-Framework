import importlib
import logging
import os
import sys
from typing import Union

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from Task.challenge.interface.ChallengeInterface import ChallengeInterface
from Task.service.interface.ServiceManagerInterface import ChallengeManagerInterface


class ChallengeManager(ChallengeManagerInterface):

    # 赛题任务管理器，管理所有赛题任务
    # 通过注解实现单例模式，可通过ChallengeManager()直接获取单一实例
    @inject
    def __init__(self, component_framework: ComponentFrameworkApplicationInterface):
        self.__component_framework = component_framework
        # 创建当前赛题字典
        self.__challenge_class_name: str = None
        self.__challenge_class_file: str = None
        self.__current_challenge: ChallengeInterface = None
        self.__logger = logging.getLogger("taskLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        challenges_dict = config_dict.get('challenge', None)
        if challenges_dict is None:
            return
        self.__challenge_class_file = challenges_dict.get('challenge_class_file', "")
        self.__challenge_class_name = challenges_dict.get('challenge_class_name', "")

    async def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if self.__current_challenge is not None:
            await self.__current_challenge.update(config_dict)
        challenges_dict = config_dict.get('challenge', None)
        if challenges_dict is None:
            return
        self.__challenge_class_file = challenges_dict.get('challenge_class_file', self.__challenge_class_file)
        self.__challenge_class_name = challenges_dict.get('challenge_class_name', self.__challenge_class_name)

    async def startup(self) -> None:
        self.__current_challenge = self.__load_challenge(self.__challenge_class_file, self.__challenge_class_name)
        #todo
        # self.__current_challenge.set_component_framework(self.__component_framework)
        await self.__current_challenge.initial()
        await self.__current_challenge.startup()

    async def shutdown(self) -> None:
        await self.__current_challenge.shutdown()
        self.__current_challenge = None

    def __load_challenge(self, challenge_class_file: str, challenge_class_name: str) -> ChallengeInterface:
        self.__logger.debug('加载赛题: ' + challenge_class_file + ':' + challenge_class_name)
        workspace_path = os.getcwd()
        absolute_challenge_class_file = os.path.join(workspace_path, challenge_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_challenge_class_file))[0]
        # 获取赛题模块所在的目录
        module_dir = os.path.dirname(absolute_challenge_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        challenge_class = getattr(module, challenge_class_name)
        instance = challenge_class()
        return instance

    def get_current_challenge(self) -> ChallengeInterface:
        return self.__current_challenge
