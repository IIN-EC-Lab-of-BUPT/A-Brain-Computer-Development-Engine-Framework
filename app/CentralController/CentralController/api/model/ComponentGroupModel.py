from dataclasses import dataclass

from ApplicationFramework.api.model.ComponentModel import ComponentModel


@dataclass
class ComponentGroupModel(ComponentModel):
    """
    组件所属组模型
    """
    # component_id: str = None
    # component_type: str = None
    # component_info: dict[str, Union[str, dict]] = None  # 如果type为PROCESSOR，component_info中包含team_name和algorithm_number,ip
    component_group_id: str = None


@dataclass
class ComponentGroupStatusModel(ComponentGroupModel):
    """
    组件状态模型
    """
    # component_id: str = None
    # component_type: str = None
    # component_info: dict[str, Union[str, dict]] = None  # 如果type为PROCESSOR，component_info中包含team_name和algorithm_number,ip
    # component_group_id: str = None
    component_status: str = None


@dataclass
class ComponentGroupStatusListModel:
    component_group_status_list: list[ComponentGroupStatusModel] = None
