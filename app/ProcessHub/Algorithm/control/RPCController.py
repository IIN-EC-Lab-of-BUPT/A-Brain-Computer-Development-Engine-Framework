import logging
from typing import Union

from injector import inject

from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.control.AlgorithmRPCDataConnectServer import AlgorithmRPCDataConnectServer
from Algorithm.control.GrpcServer import GrpcServer
from Algorithm.control.operator.ReceiveDataOperator import ReceiveMessageOperator
from Algorithm.service.interface.DataForwarderInterface import DataForwarderInterface
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import (
    AlgorithmRPCServiceControlServicer,
    add_AlgorithmRPCDataConnectServicer_to_server,
    add_AlgorithmRPCServiceControlServicer_to_server
)


class RPCController(RpcControllerInterface):

    @inject
    def __init__(self,
                 algorithm_rpc_data_connect_server: AlgorithmRPCDataConnectServer,
                 algorithm_rpc_service_control_server: AlgorithmRPCServiceControlServicer,
                 data_forwarder: DataForwarderInterface):
        self.__algorithm_rpc_data_connect_server = algorithm_rpc_data_connect_server
        self.__algorithm_rpc_service_control_server = algorithm_rpc_service_control_server
        self.__data_forwarder: DataForwarderInterface = data_forwarder
        self.__rpc_server: GrpcServer = None
        self.__logger = logging.getLogger("algorithmLogger")
        self.__report_converter = AlgorithmRPCMessageConverter()
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

    async def report(self, algorithm_report_message: AlgorithmReportMessageModel):
        await self.__algorithm_rpc_data_connect_server.send_report(
            self.__report_converter.model_to_protobuf(algorithm_report_message))

    async def initial_system(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if self.__service_status is not ServiceStatusEnum.STOPPED:
            return
        # 设置服务初始化状态
        self.__service_status = ServiceStatusEnum.INITIALIZING
        self.__rpc_server = GrpcServer()
        self.__rpc_server.initial(config_dict)
        self.__rpc_server.add_servicer_to_server(self.__algorithm_rpc_data_connect_server,
                                                 add_AlgorithmRPCDataConnectServicer_to_server)
        self.__rpc_server.add_servicer_to_server(self.__algorithm_rpc_service_control_server,
                                                 add_AlgorithmRPCServiceControlServicer_to_server)
        # 插入数据接收operator
        self.__algorithm_rpc_data_connect_server.add_receive_data_operator(
            ReceiveMessageOperator(self.__data_forwarder))

        # 设置服务就绪状态
        self.__service_status = ServiceStatusEnum.READY

    async def startup(self):
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.STARTING
        await self.__rpc_server.startup()
        self.__logger.info("RPCController已启动")
        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self):
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        await self.__algorithm_rpc_data_connect_server.disconnect()
        await self.__rpc_server.shutdown()
        self.__logger.info("RPCController已关闭")
        self.__service_status = ServiceStatusEnum.READY

    async def disconnect(self):
        await self.__algorithm_rpc_data_connect_server.disconnect()

    def delete(self):
        self.__rpc_server.delete()
