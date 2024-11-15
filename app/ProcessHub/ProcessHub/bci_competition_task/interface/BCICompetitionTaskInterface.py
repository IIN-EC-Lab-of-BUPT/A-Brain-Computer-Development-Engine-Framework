from abc import ABC, abstractmethod

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorInterface import AlgorithmConnectorInterface
from ProcessHub.orchestrator.model.SourceModel import SourceModel


class BCICompetitionTaskInterface(ABC):

    def __init__(self):
        self._algorithm_connector: AlgorithmConnectorInterface = None
        self._component_framework: ComponentFrameworkApplicationInterface = None

    @abstractmethod
    async def get_source_list(self) -> list[SourceModel]:
        pass
        # # 获取当前赛题的source配置信息
        # return self._source_list

    @abstractmethod
    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        pass

    @abstractmethod
    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        pass

    @abstractmethod
    async def initial(self):
        pass

    @abstractmethod
    async def startup(self):
        pass

    @abstractmethod
    async def shutdown(self):
        pass

    def set_component_framework(self, component_framework: ComponentFrameworkApplicationInterface):
        self._component_framework = component_framework

    def set_algorithm_connector(self, algorithm_connector: AlgorithmConnectorInterface):
        self._algorithm_connector = algorithm_connector
