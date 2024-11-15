from dataclasses import dataclass
from typing import Union, List

from componentframework.common.enum.DataTypeEnum import DataTypeEnum


@dataclass
class BaseMessageModel:
    source_label: str = None
    timestamp: float = None


@dataclass
# 任务数据类
class DataModel(BaseMessageModel):
    data_position: int = None  # 数据启始位置
    data: Union[float, List[float]] = None  # 数据信息


@dataclass
class DeviceModel(BaseMessageModel):
    data_type: DataTypeEnum = None
    channel_number: int = None
    sample_rate: float = None
    channel_label: Union[str, List[str]] = None
    other_config_map: dict[str, str] = None  # 其他配置信息


@dataclass
class EventModel(BaseMessageModel):
    event_position: Union[int, List[int]] = None
    event_data: Union[int, List[int]] = None


@dataclass
class ImpedanceModel(BaseMessageModel):
    channel_impedance: Union[float, List[float]] = None


@dataclass
class InformationModel(BaseMessageModel):
    subject_id: str = None
    block_id: str = None


@dataclass
class ControlModel(BaseMessageModel):
    endFlag: bool = None
