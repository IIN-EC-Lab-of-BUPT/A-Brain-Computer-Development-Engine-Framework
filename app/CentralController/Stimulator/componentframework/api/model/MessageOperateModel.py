from dataclasses import dataclass
from typing import Union
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum


@dataclass
# 任务数据类
class AddListenerOnBindMessageModel(object):
    component_id: str = None
    message_key: str = None
    topic: str = None


@dataclass
# 任务数据类
class AddListenerOnRegisterComponentModel(object):
    component_type: str = None
    component_id: str = None
    component_info: dict[str, Union[str, dict]] = None


@dataclass
# 任务数据类
class AddListenerOnUpdateComponentInfoComponentModel(object):
    component_id: str = None
    component_info: dict[str, Union[str, dict]] = None


@dataclass
# 任务数据类
class AddListenerOnUnregisterComponentModel(object):
    component_id: str = None
    component_type: str = None
    component_info: dict[str, Union[str, dict]] = None


@dataclass
# 任务数据类
class AddListenerOnUpdateComponentStateModel(object):
    component_id: str = None
    component_state: ComponentStatusEnum = None
