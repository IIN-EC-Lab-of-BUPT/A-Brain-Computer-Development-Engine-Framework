from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.ComponentModel import ComponentModel
from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusModel
from CentralController.service.interface.ComponentMonitorInterface import ComponentMonitorInterface
from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface


class ComponentMonitor(ComponentMonitorInterface):

    @inject
    def __init__(self, service_coordinator: ServiceCoordinatorInterface,
                 component_framework: ComponentFrameworkInterface):
        self.__service_coordinator = service_coordinator
        self.__component_framework = component_framework

    async def get_components_status_list(self) -> list[ComponentGroupStatusModel]:
        """
        获取所有组件状态,包括组件信息，所属组及状态
        :return:
        """
        component_model_dict = self.__service_coordinator.get_registered_component_information_model_dict()
        component_info_status_model_list: list[ComponentGroupStatusModel] = []
        for component_model_id in component_model_dict:
            registered_component_information_model = component_model_dict[component_model_id]
            component_model: ComponentModel = \
                await self.__component_framework.get_component_model(component_model_id)
            component_status = await self.__component_framework.get_component_status(component_model_id)
            component_info_status_model = ComponentGroupStatusModel(
                component_id=component_model.component_id,
                component_type=component_model.component_type,
                component_info=component_model.component_info,
                component_group_id=registered_component_information_model.component_group_id,
                component_status=component_status.value
            )
            component_info_status_model_list.append(component_info_status_model)
        return component_info_status_model_list
