from abc import ABC, abstractmethod

from injector import inject, Injector

from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.model.ComponentStartupConfigurationModel import ComponentStartupConfigurationModel


class ConnectManagerFacade(ABC):
    @inject
    def __init__(self):
        pass

    @abstractmethod
    def shutdown(self):
        """关闭连接"""
        # 返回值："关闭连接成功通知"：str类型
        pass
