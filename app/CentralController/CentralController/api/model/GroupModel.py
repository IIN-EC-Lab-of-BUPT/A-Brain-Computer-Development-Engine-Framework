from dataclasses import dataclass
from typing import Union


@dataclass
class GroupModel:
    group_id: str = None
    group_info: dict[str, Union[str, dict]] = None


@dataclass
class GroupListModel:
    group_list: list[GroupModel] = None
