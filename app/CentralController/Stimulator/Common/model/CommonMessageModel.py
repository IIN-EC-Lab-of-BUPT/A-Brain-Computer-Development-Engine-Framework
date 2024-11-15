from dataclasses import dataclass, field
from enum import Enum
from typing import Union


class DataTypeEnum(Enum):
    UNKNOWN = 0
    EEG = 1
    EYETRACKING = 2
    MEG = 3
    MRI = 4
    ECOG = 5
    SPIKE = 6
    EMG = 7
    ECG = 8
    NIRS = 9


class BaseCommonMessageModel:
    """
    通用数据包定义
    """
    pass


@dataclass
class DevicePackageModel(BaseCommonMessageModel):
    data_type: DataTypeEnum = None
    channel_number: int = None
    sample_rate: float = None
    channel_label: list[str] = field(default_factory=list)
    other_information: dict[str, Union[str, dict]] = None


@dataclass
class EventPackageModel(BaseCommonMessageModel):
    event_position: list[float] = field(default_factory=list)
    event_data: list[str] = field(default_factory=list)


@dataclass
class DataPackageModel(BaseCommonMessageModel):
    data_position: float = None
    data: Union[
        list[float],
        list[int],
        list[str],
        bytes,
        str,
        bool,
    ] = None


@dataclass
class ImpedancePackageModel(BaseCommonMessageModel):
    channel_impedance: list[float] = field(default_factory=list)


@dataclass
class InformationPackageModel(BaseCommonMessageModel):
    subject_id: str = None
    block_id: str = None


@dataclass
class ControlPackageModel(BaseCommonMessageModel):
    end_flag: bool = None


@dataclass
class ReportSourceInformationModel(BaseCommonMessageModel):
    source_label: str = None
    position: float = None


@dataclass
class ResultPackageModel(BaseCommonMessageModel):
    result: Union[
        list[float],
        list[int],
        list[str],
        bytes,
        str,
        bool,
    ] = None
    report_source_information: list[ReportSourceInformationModel] = field(default_factory=list)


@dataclass
class ScorePackageModel(BaseCommonMessageModel):
    show_text: str = None
    score: float = None
    trial_time: float = None
    trial_id: str = None
    block_id: str = None
    subject_id: str = None


@dataclass
class ExceptionPackageModel(BaseCommonMessageModel):
    exception_type: str = None
    exception_message: str = None
    exception_stack_trace: list[str] = None


@dataclass
class DataMessageModel(BaseCommonMessageModel):
    package: Union[
        DevicePackageModel,
        EventPackageModel,
        DataPackageModel,
        ImpedancePackageModel,
        InformationPackageModel,
        ControlPackageModel,
        ResultPackageModel,
        ScorePackageModel,
        ExceptionPackageModel
    ] = None
