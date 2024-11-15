from abc import ABC, abstractmethod
from typing import Union

from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusModel
from CentralController.api.model.GroupModel import GroupModel


class CentralManagementViewControllerInterface(ABC):
    @abstractmethod
    def prepare_system(self):
        pass

    @abstractmethod
    def start_group(self, group_model: GroupModel):
        pass

    @abstractmethod
    def reset_group(self, group_model: GroupModel):
        pass

    @abstractmethod
    def close_system(self):
        pass

    @abstractmethod
    def get_components_status_list(self) -> list[ComponentGroupStatusModel]:
        pass

    @abstractmethod
    def get_groups_model_list(self) -> list[GroupModel]:
        pass


class CentralManagementInterface(CentralManagementViewControllerInterface):

    @abstractmethod
    def initial(self, config_dict: dict[str, Union[str, dict]]):
        pass

    @abstractmethod
    def startup(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

