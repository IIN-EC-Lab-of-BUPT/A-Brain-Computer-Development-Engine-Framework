from injector import inject

from ProcessHub.algorithm_connector.AlgorithmConnector import AlgorithmConnector
from ProcessHub.algorithm_connector.facade.AlgorithmRPCDataConnectClient import AlgorithmRPCDataConnectClient
from ProcessHub.algorithm_connector.facade.AlgorithmRPCServiceControlClient import AlgorithmRPCServiceControlClient
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorInterface import AlgorithmConnectorInterface
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorFactoryInterface import (
    AlgorithmConnectorFactoryManagerInterface)
from ProcessHub.algorithm_connector.model.AlgorithmConnectModel import AlgorithmConnectModel


class AlgorithmConnectorFactoryManager(AlgorithmConnectorFactoryManagerInterface):

    @inject
    def __init__(self,
                 algorithm_rpc_data_connect_client: AlgorithmRPCDataConnectClient,
                 algorithm_rpc_service_control_client: AlgorithmRPCServiceControlClient):
        self.__algorithm_rpc_data_connect_client = algorithm_rpc_data_connect_client
        self.__algorithm_rpc_service_control_client = algorithm_rpc_service_control_client

    async def get_algorithm_connector(self, algorithm_connect_model: AlgorithmConnectModel) -> (
            AlgorithmConnectorInterface):
        algorithm_connector = AlgorithmConnector(
            algorithm_rpc_data_connect_client=self.__algorithm_rpc_data_connect_client,
            algorithm_rpc_service_control_client=self.__algorithm_rpc_service_control_client)
        await algorithm_connector.initial(algorithm_connect_model)
        return algorithm_connector

    async def initial(self):
        pass

    async def startup(self):
        pass

    async def shutdown(self):
        pass
