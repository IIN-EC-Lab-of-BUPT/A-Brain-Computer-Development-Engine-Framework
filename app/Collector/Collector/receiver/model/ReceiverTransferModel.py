from dataclasses import dataclass, field
from enum import Enum
from typing import Union

import numpy


class TransferDataTypeEnum(Enum):
    UNKNOWN = 'unknown'
    EEG = 'eeg'
    EYETRACKING = 'eyetracking'
    MEG = 'meg'
    MRI = 'mri'
    ECOG = 'ecog'
    SPIKE = 'spike'
    EMG = 'emg'
    ECG = 'ecg'
    NIRS = 'nirs'


@dataclass
class DeviceTransferModel:
    data_type: TransferDataTypeEnum = None
    channel_number: int = None
    sample_rate: float = None
    channel_label: list[str] = field(default_factory=list)
    other_information: dict[str, Union[str, dict]] = None


@dataclass
class EventTransferModel:
    event_position: list[float] = field(default_factory=list)
    event_data: list[str] = field(default_factory=list)


@dataclass
class DataTransferModel:
    data_position: float = None
    data: Union[
        bool,
        str,
        bytes,
        list[float],
        list[int],
        list[str],
        numpy.ndarray,
    ] = None


@dataclass
class ImpedanceTransferModel:
    channel_impedance: list[float] = None


@dataclass
class InformationTransferModel:
    subject_id: str = None
    block_id: str = None


@dataclass
class ReceiverTransferModel:
    package: Union[
        DeviceTransferModel,
        EventTransferModel,
        DataTransferModel,
        ImpedanceTransferModel,
        InformationTransferModel,
    ] = None
