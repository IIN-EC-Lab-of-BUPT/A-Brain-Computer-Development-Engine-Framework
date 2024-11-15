from abc import ABC, abstractmethod
from typing import Union
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel
from Task.facade.interface.ReceiveAlgorithmReportMessageOperatorInterface import \
    ReceiveAlgorithmReportMessageOperatorInterface


class RpcControllerApplicationInterface(ABC):
    """
    RPC控制器应用接口，
    """

    @abstractmethod
    def set_receive_report_operator(self, receive_report_operator: ReceiveAlgorithmReportMessageOperatorInterface):
        pass

    @abstractmethod
    async def send_data(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        pass

    async def send_config(self, config_dict: dict[str, Union[str, dict]]):
        """
        向算法端发送配置信息
        :parameter: dict中包含一个主键：
        'challenge_to_algorithm_config':
            challeng_config.yaml中对应字段的配置信息或者更新后配置信息。
            仅在启动时调用一次
        """
        pass

    @abstractmethod
    async def get_config(self) -> dict[str, Union[str, dict]]:
        """
        递归拉取算法端配置信息
        :return: 返回dict中包含一个主键：
        'sources':
            source_label_1:
                None
            source_label_2:
                None
            ……

        """
        pass


class RpcControllerManagementInterface(RpcControllerApplicationInterface):
    """
    RPC控制器管理接口
    """

    @abstractmethod
    def get_algorithm_address(self) -> str:
        pass

    @abstractmethod
    def get_max_connection_timeout(self) -> float:
        """
        获取最大连接超时时间
        :return:
        """
        pass

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]]):
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, Union[str, dict]]):
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
    async def shutdown_and_close_algorithm_system(self) -> None:
        # 服务关闭且远程关闭算法系统
        pass
