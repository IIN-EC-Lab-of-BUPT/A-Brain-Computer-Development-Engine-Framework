from dataclasses import dataclass


@dataclass
class BaseDataClassModel:
    """
    AlgorithmRPC通用数据包定义
    """
    data: any = None


@dataclass
# 布尔消息类型
class BooleanMessageModel(BaseDataClassModel):
    data: bool = None


@dataclass
# 字符串消息类型
class StringMessageModel(BaseDataClassModel):
    data: str = None


@dataclass
# 二进制消息类型
class BinaryMessageModel(BaseDataClassModel):
    data: bytes = None


@dataclass
class FloatListMessageModel(BaseDataClassModel):
    data: list[float] = None


@dataclass
class IntListMessageModel(BaseDataClassModel):
    data: list[int] = None


@dataclass
class StringListMessageModel(BaseDataClassModel):
    data: list[str] = None
