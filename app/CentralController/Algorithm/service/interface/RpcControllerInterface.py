from abc import ABC, abstractmethod
from typing import Union

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel


class RpcControllerInterface(ABC):
    """
    与算法端连接服务控制接口，用于控制服务启动和关闭，通过Control层代码实现
    """

    @abstractmethod
    async def initial_system(self, config_dict: dict[str, Union[str, dict]]) -> None:
        # 配置初始化时所调用的方法
        pass

    @abstractmethod
    async def startup(self):
        """
        服务启动
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """
        服务关闭
        """
        pass

    @abstractmethod
    def delete(self):
        """
        服务删除
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        断开连接
        """
        pass

    @abstractmethod
    async def report(self, algorithm_report_message: AlgorithmReportMessageModel):
        pass
