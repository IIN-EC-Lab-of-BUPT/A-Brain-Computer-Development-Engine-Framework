from abc import ABC, abstractmethod
from typing import Union

from CentralController.common.model import GroupInformationModel


class ProcessManagerApplicationInterface(ABC):
    """
    流程控制器应用接口
    """

    @abstractmethod
    async def prepare_system(self):
        pass

    @abstractmethod
    async def start_group(self, group_information_model: GroupInformationModel):
        pass

    @abstractmethod
    async def reset_group(self, group_information_model: GroupInformationModel):
        pass

    @abstractmethod
    async def close_system(self):
        pass


class ProcessManagerInterface(ProcessManagerApplicationInterface):
    """
    流程控制器接口
    """
    @abstractmethod
    async def initial(self):
        pass

    async def startup(self):
        pass

    async def shutdown(self):
        pass

