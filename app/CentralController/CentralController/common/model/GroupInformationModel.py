from dataclasses import dataclass
from CentralController.api.model.GroupModel import GroupModel


@dataclass
class GroupInformationModel(GroupModel):
    #     group_id: str = None
    #     group_info: dict[str, Union[str, dict]] = None
    message_key_topic_dict: dict[str, str] = None
