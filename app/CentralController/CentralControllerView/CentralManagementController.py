import logging
from typing import Union

from CentralController.api.converter.CentralManagementControlServiceMessageConverter import \
    CentralManagementControlServiceMessageConverter
from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusModel
from CentralController.api.model.GroupModel import GroupModel
from CentralController.api.proto.CentralManagementControlService_pb2_grpc import CentralManagementControlServiceStub
from CentralControllerView.CentralManagementInterface import CentralManagementInterface
from CentralControllerView.GrpcClient import GrpcClient
from google.protobuf.empty_pb2 import Empty


class CentralManagementController(CentralManagementInterface):

    def __init__(self):
        self.__service_address: str = None
        self.__central_management_control_service_stub: CentralManagementControlServiceStub = None
        self.__rpc_client: GrpcClient = None
        self.__logger = logging.getLogger("centralControllerLogger")

    def initial(self, config_dict: dict[str, Union[str, dict]]):
        ui_config_dict = config_dict.get('ui_config', dict())
        rpc_port = ui_config_dict.get('rpc_port', 7963)
        self.__service_address = f"localhost:{rpc_port}"

    def startup(self):
        self.__rpc_client = GrpcClient(self.__service_address)

        # 先启动连接
        self.__rpc_client.startup()

        # 再绑定并注入服务
        self.__central_management_control_service_stub = (
            self.__rpc_client.get_stub_instance(CentralManagementControlServiceStub))

    def shutdown(self):
        # 关闭RPC连接
        self.__rpc_client.shutdown()

    def prepare_system(self):
        self.__central_management_control_service_stub.prepare_system(Empty())

    def start_group(self, group_model: GroupModel):
        group_message = CentralManagementControlServiceMessageConverter.model_to_protobuf(group_model)
        self.__central_management_control_service_stub.start_group(group_message)

    def reset_group(self, group_model: GroupModel):
        group_message = CentralManagementControlServiceMessageConverter.model_to_protobuf(group_model)
        self.__central_management_control_service_stub.reset_group(group_message)

    def close_system(self):
        self.__central_management_control_service_stub.close_system(Empty())

    def get_components_status_list(self) -> list[ComponentGroupStatusModel]:
        component_group_status_list_message = (self.__central_management_control_service_stub
                                               .get_components_status_list(Empty()))
        component_group_status_list_model = CentralManagementControlServiceMessageConverter.protobuf_to_model(
            component_group_status_list_message)
        return component_group_status_list_model.component_group_status_list

    def get_groups_model_list(self) -> list[GroupModel]:
        group_list_message = self.__central_management_control_service_stub.get_groups_model_list()
        group_list_model = CentralManagementControlServiceMessageConverter.protobuf_to_model(group_list_message)
        return group_list_model.group_list

    def __enter__(self):
        self.startup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
