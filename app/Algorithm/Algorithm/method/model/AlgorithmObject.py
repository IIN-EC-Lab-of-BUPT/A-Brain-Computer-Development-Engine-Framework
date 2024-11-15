from dataclasses import dataclass
from typing import Union, List

from numpy import ndarray


@dataclass
class AlgorithmContinuousDataObject:
    # 数据对象
    start_position: int = None  # 数据包内数据的起始位置
    data: ndarray = None    # 数据内容，每行表示一个导联，最后一行通道为trigger通道
    subject_id: str = None  # 当前数据包的subject_id
    finish_flag: bool = None    # 数据结束标志位，当该标志位为true时，表示该数据源所有数据已经发送完毕


@dataclass
class AlgorithmDeviceObject:
    data_type: str = None   # 数据类型，目前可支持 UNKNOWN,EEG,EYETRACKING,MEG,MRI,ECOG,SPIKE,EMG,ECG,NIRS
    channel_number: int = None  # 当前数据包的通道数
    sample_rate: float = None   # 采样率
    channel_label: List[str] = None  # 通道标签
    other_information: dict = None  # 其他配置信息


@dataclass
class AlgorithmResultObject:
    # 可支持字符串和二进制数据，如果为二进制数据，则可传输图片等数据，需在接收端或赛题端进行解码
    result: Union[None, bool, str, bytes, list[float], list[int], list[str]] = None

