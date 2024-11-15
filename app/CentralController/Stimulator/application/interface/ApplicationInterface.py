from abc import abstractmethod, ABC
from typing import Union

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.common.utils.ContextManager import ContextManager


class ApplicationInterface(ABC):

    def __init__(self):
        self._context_manager: ContextManager = None
        self._component_id: str = None  # 注入的组件ID

    @abstractmethod
    async def initial(self) -> None:
        # 初始化应用组件
        pass

    @abstractmethod
    async def run(self) -> None:
        pass

    @abstractmethod
    async def exit(self) -> None:
        # 退出应用组件,该函数被调用后，应用应自动退出
        pass

    @abstractmethod
    def get_component_model(self) -> ComponentModel:
        # 返回组件信息，用于中控识别组件及配置记录，初始化initial()后被调用
        pass

    def set_context_manager(self, context_manager: ContextManager) -> None:
        self._context_manager = context_manager

