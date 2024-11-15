import asyncio
import logging
import time
from typing import Union

from grpc.aio import AioRpcError
from injector import inject

from Algorithm.api.converter.AlgorithmRPCMessageConverter import AlgorithmRPCMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCDataConnectStub, AlgorithmRPCServiceControlStub
from Task.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Task.facade.AlgorithmRPCDataConnectClient import AlgorithmRPCDataConnectClient
from Task.facade.AlgorithmRPCServiceControlClient import AlgorithmRPCServiceControlClient
from Task.facade.GrpcClient import GrpcClient
from Task.facade.excepiton.TaskRPCException import TaskRPCClientTimeoutException
from Task.facade.interface.ReceiveAlgorithmReportMessageOperatorInterface import \
    ReceiveAlgorithmReportMessageOperatorInterface
from Task.facade.interface.RpcControllerInterface import RpcControllerManagementInterface


class RPCController(RpcControllerManagementInterface):
    """
    RPC控制器
    被调用执行次序
    1、初始化实例__init__()
    2、注入接收结果处理器 set_receive_report_operator()
    3、注入算法断开事件处理器set_algorithm_disconnect_event_operator
    4、设置算法地址set_algorithm_address()
    5、启动startup()
    6、随时发送配置信息send_config()
    7、获取配置信息get_config():获取包括数据源的配置信息
    8、开始发送数据send_data()
    9、关闭shutdown()
    10、关闭远程算法系统remote_close_algorithm_system()：可选
    """

    @inject
    def __init__(self,
                 algorithm_rpc_data_connect_client: AlgorithmRPCDataConnectClient,
                 algorithm_rpc_service_control_client: AlgorithmRPCServiceControlClient):
        self.__algorithm_rpc_data_connect_client = algorithm_rpc_data_connect_client
        self.__algorithm_rpc_service_control_client = algorithm_rpc_service_control_client
        self.__rpc_client: GrpcClient = None
        self.__logger = logging.getLogger("taskLogger")
        self.__receive_report_operator: ReceiveAlgorithmReportMessageOperatorInterface = None
        self.__message_converter = AlgorithmRPCMessageConverter()
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.READY
        self.__algorithm_address: str = None
        self.__max_connection_timeout: float = None

    def set_receive_report_operator(self, receive_report_operator: ReceiveAlgorithmReportMessageOperatorInterface):
        self.__receive_report_operator = receive_report_operator

    async def send_data(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        await self.__algorithm_rpc_data_connect_client.send_data(
            self.__message_converter.model_to_protobuf(
                algorithm_data_message_model
            )
        )

    async def send_config(self, config_dict: dict[str, Union[str, dict]]):
        await self.__algorithm_rpc_service_control_client.send_config(config_dict)

    async def get_config(self) -> dict[str, Union[str, dict]]:
        """
        递归拉取算法端配置信息
        :return: 返回dict中包含二个主键：
        'sources':
            source_label_1:
                None
            source_label_2:
                None
            ……
        'challenge_to_algorithm_config':
            challeng_config.yaml中对应字段的配置信息
        """
        return await self.__algorithm_rpc_service_control_client.get_config()

    def get_algorithm_address(self) -> str:
        return self.__algorithm_address

    def get_max_connection_timeout(self) -> float:
        return self.__max_connection_timeout

    async def initial(self, config_dict: dict[str, Union[str, dict]]):
        rpc_config_dict = config_dict.get('algorithm_connection', None)
        if rpc_config_dict is None:
            self.__service_status = ServiceStatusEnum.ERROR
            return
        self.__algorithm_address = rpc_config_dict.get('address', None)
        if self.__algorithm_address is None:
            self.__service_status = ServiceStatusEnum.ERROR
            return
        self.__max_connection_timeout = rpc_config_dict.get('max_connection_timeout', 0)

    async def update(self, config_dict: dict[str, Union[str, dict]]):
        rpc_config_dict = config_dict.get('algorithm_connection', None)
        if rpc_config_dict is None:
            return
        self.__algorithm_address = rpc_config_dict.get('address', self.__algorithm_address)
        if self.__algorithm_address is None:
            return
        self.__max_connection_timeout = rpc_config_dict.get('max_connection_timeout', self.__max_connection_timeout)

    async def startup(self):
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.STARTING

        self.__rpc_client = GrpcClient(self.__algorithm_address)

        # 先启动连接
        await self.__rpc_client.startup()

        # 再绑定并注入服务
        self.__algorithm_rpc_service_control_client.set_algorithm_rpc_service_control_stub(
            self.__rpc_client.get_stub_instance(AlgorithmRPCServiceControlStub)
        )

        self.__algorithm_rpc_data_connect_client.set_algorithm_rpc_data_connect_stub(
            self.__rpc_client.get_stub_instance(AlgorithmRPCDataConnectStub)
        )
        # 注入接收报告处理器
        self.__algorithm_rpc_data_connect_client.add_receive_report_operator(self.__receive_report_operator)

        # 等待连接建立
        await self.__wait_for_connect()

        # 建立数据连接
        await self.__algorithm_rpc_data_connect_client.connect()

        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self):
        self.__logger.info(f"RPC控制器关闭，即将断开与{self.__algorithm_address}算法端服务器连接")
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        # 断开数据连接
        await self.__algorithm_rpc_data_connect_client.disconnect()
        # 关闭RPC连接
        await self.__rpc_client.shutdown()
        self.__service_status = ServiceStatusEnum.READY
        self.__logger.info(f"RPC控制器已关闭，已断开与{self.__algorithm_address}算法端服务器连接")

    async def shutdown_and_close_algorithm_system(self) -> None:
        self.__logger.info(f"向算法服务器{self.__algorithm_address}发送系统关闭请求")
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        # 发送算法系统关闭请求
        await self.__algorithm_rpc_service_control_client.shutdown()
        # 关闭RPC连接
        await self.__rpc_client.shutdown()
        self.__service_status = ServiceStatusEnum.READY
        self.__logger.info(f"RPC控制器已关闭，已关闭{self.__algorithm_address}算法端服务器")

    async def __wait_for_connect(self):
        self.__logger.info(f"启动{self.__algorithm_address}算法端连接，最长等待时间{self.__max_connection_timeout}秒...")
        start_time = time.time()
        while True:
            try:
                service_status = await self.__algorithm_rpc_service_control_client.get_status()
                break
            except AioRpcError as e:
                if time.time() - start_time > self.__max_connection_timeout:
                    raise TaskRPCClientTimeoutException(
                        f"{self.__algorithm_address}算法端连接超时，请检查算法端是否正常运行"
                    ) from e
                await asyncio.sleep(1)
        self.__logger.info(f"{self.__algorithm_address}算法端连接成功")
