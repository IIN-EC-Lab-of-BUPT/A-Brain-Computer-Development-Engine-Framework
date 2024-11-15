from abc import ABC, abstractmethod

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorFactoryInterface import (
    AlgorithmConnectorFactoryInterface)


class OrchestratorInterface(ABC):
    """
    ProcessHub核心接口，负责数据读取，结果转发等操作
    """

    def __init__(self):
        self._component_framework: ComponentFrameworkInterface = None
        self._algorithm_connector_factory: AlgorithmConnectorFactoryInterface = None

    @abstractmethod
    async def initial(self):
        pass

    @abstractmethod
    async def startup(self):
        pass

    @abstractmethod
    async def shutdown(self):
        pass

    def set_component_framework(self, component_framework: ComponentFrameworkInterface):
        self._component_framework = component_framework

    def set_algorithm_connector_factory(self, algorithm_connector_factory: AlgorithmConnectorFactoryInterface):
        self._algorithm_connector_factory = algorithm_connector_factory
