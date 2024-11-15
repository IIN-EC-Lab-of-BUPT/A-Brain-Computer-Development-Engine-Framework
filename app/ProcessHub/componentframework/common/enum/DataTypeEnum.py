from enum import Enum


class DataTypeEnum(Enum):
    # 数据类型定义
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

