from dataclasses import dataclass
from typing import Union


@dataclass
# 任务数据类
class MessageModel(object):
    component_id: str = None
    message_key: str = None
    topic: str = None


@dataclass
# 任务数据类
class ComponentModel(object):
    component_id: str = None
    component_type: str = None
    component_info: dict[str, Union[str, dict]] = None
