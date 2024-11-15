from abc import ABC

from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusModel


class ComponentMonitorInterface(ABC):
    """
    组件监视器接口
    """
    async def get_components_status_list(self) -> list[ComponentGroupStatusModel]:
        """
        获取所有组件状态,包括组件信息，关联关系及状态
        :return:
        """
        pass
