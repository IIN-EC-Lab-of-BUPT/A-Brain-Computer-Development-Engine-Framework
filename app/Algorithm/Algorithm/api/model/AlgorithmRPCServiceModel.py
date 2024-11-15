from dataclasses import dataclass
from enum import Enum
from typing import Union

from Common.model.CommonMessageModel import DevicePackageModel, EventPackageModel, DataPackageModel, \
    ImpedancePackageModel, \
    InformationPackageModel, ControlPackageModel, ResultPackageModel, ExceptionPackageModel


class BaseAlgorithmRPCMessageModel:
    """
    AlgorithmRPC通用数据包定义
    """
    pass


# 数据消息类型
@dataclass
class AlgorithmDataMessageModel(BaseAlgorithmRPCMessageModel):
    source_label: str = None
    timestamp: float = None
    package: Union[
        DevicePackageModel,
        EventPackageModel,
        DataPackageModel,
        ImpedancePackageModel,
        InformationPackageModel,
        ControlPackageModel,
    ] = None


# 报告消息
@dataclass
class AlgorithmReportMessageModel(BaseAlgorithmRPCMessageModel):
    """
    算法报告消息
    """
    timestamp: float = None
    package: Union[
        ResultPackageModel,
        ControlPackageModel,
        ExceptionPackageModel
    ] = None


@dataclass
class AlgorithmStatusEnum(Enum):
    INITIALIZING = 0  # 初始化过程状态
    READY = 1  # 就绪状态
    STARTING = 2  # 启动过程状态
    RUNNING = 3  # 运行状态
    STOPPING = 4  # 停止过程状态
    STOPPED = 5  # 停止状态
    ERROR = 6  # 错误状态


@dataclass
class AlgorithmStatusMessageModel(BaseAlgorithmRPCMessageModel):
    """
    算法状态消息
    """
    status: AlgorithmStatusEnum = None
