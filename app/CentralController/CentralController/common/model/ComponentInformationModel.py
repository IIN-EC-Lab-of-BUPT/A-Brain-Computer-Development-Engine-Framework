from dataclasses import dataclass

from CentralController.api.model.ComponentGroupModel import ComponentGroupModel


@dataclass
class ComponentInformationModel(ComponentGroupModel):
    """
    组件模型
    """
    # component_id: str = None
    # component_type: str = None
    # component_info: dict[str, Union[str, dict]] = None  # 如果type为PROCESSOR，component_info中包含team_name和algorithm_number
    # component_group_id: str = None
    message_key_topic_dict: dict[str, str] = None


