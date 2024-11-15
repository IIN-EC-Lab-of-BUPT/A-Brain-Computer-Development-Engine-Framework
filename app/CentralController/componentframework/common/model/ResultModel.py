from dataclasses import dataclass
from typing import List, Union


@dataclass
class SourcePosition:
    source_label: str = None  # 标记数据源ID，多数据源时用于区分来自不同数据源的响应
    position: int = None  # 报告时读取对应源的位置


@dataclass
# 任务数据类
class ResultModel:
    result: str = None  # 反馈结果
    source_position: List[SourcePosition] = None  # 结果反馈时不同源数据位置
    trial_time: float = None
    end_flag: bool = False
    timestamp: float = None  # 报告时间戳
    score: float = None  # 当前试次成绩
    trialId: str = None  # 当前试次ID
    blockId: str = None  # 当前blockID
    subjectId: str = None  # 当前被试ID
