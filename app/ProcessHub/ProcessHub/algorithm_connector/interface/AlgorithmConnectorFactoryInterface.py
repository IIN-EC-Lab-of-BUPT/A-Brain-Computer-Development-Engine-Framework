from abc import ABC, abstractmethod

from ProcessHub.algorithm_connector.interface.AlgorithmConnectorInterface import AlgorithmConnectorInterface
from ProcessHub.algorithm_connector.model.AlgorithmConnectModel import AlgorithmConnectModel


class AlgorithmConnectorFactoryInterface(ABC):

    @abstractmethod
    async def get_algorithm_connector(self, algorithm_connect_model: AlgorithmConnectModel) -> (
            AlgorithmConnectorInterface):
        pass


class AlgorithmConnectorFactoryManagerInterface(AlgorithmConnectorFactoryInterface):

    @abstractmethod
    async def initial(self):
        pass

    @abstractmethod
    async def startup(self):
        pass

    @abstractmethod
    async def shutdown(self):
        pass
