from dataclasses import dataclass
from typing import Union


@dataclass
class ComponentModel:
    """
    组件模型
    """
    component_id: str = None
    component_type: str = None
    component_info: dict[str, Union[str, dict]] = None
    