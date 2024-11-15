import logging
from typing import Union

from injector import inject

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from Common.model.CommonMessageModel import DataMessageModel
from Task.api.message.MessageKeyEnum import MessageKeyEnum
from Task.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Task.common.model.SourceModel import SourceModel
from Task.facade.interface.SystemConnectorInterface import SystemConnectorInterface
from Task.facade.interface.RpcControllerInterface import RpcControllerApplicationInterface
from Task.service.interface.ServiceManagerInterface import MessageForwarderInterface
from Task.service.operator.AddDataOperator import AddDataOperator
from Task.service.operator.ReceiveAlgorithmReportMessageOperator import ReceiveAlgorithmReportMessageOperator
from Task.strategies.interface.StrategyInterface import StrategyInterface


class MessageForwarder(MessageForwarderInterface):
    @inject
    def __init__(self,
                 system_connector: SystemConnectorInterface,
                 rpc_controller: RpcControllerApplicationInterface):
        self.__system_connector: SystemConnectorInterface = system_connector
        self.__rpc_controller: RpcControllerApplicationInterface = rpc_controller
        self.__report_message_key: str = None
        self.__report_message_topic: str = None
        self.__source_dict = dict[str, SourceModel]()  # 保存当前源信息
        self.__transfer_source_dict = dict[str, SourceModel]()  # 需要往算法端转发的源信息
        self.__current_strategy: StrategyInterface = None  # 当前策略

        # 产生接收结果报告处理器
        self.__rpc_controller.set_receive_report_operator(ReceiveAlgorithmReportMessageOperator(self))

        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED
        self.__logger = logging.getLogger("taskLogger")

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        self.__logger.debug(f"{algorithm_data_message_model.source_label}收到消息"
                            f"{type(algorithm_data_message_model.package)}")
        preprocessed_message_model = await self.__current_strategy.receive_message(algorithm_data_message_model)
        if preprocessed_message_model.source_label in self.__transfer_source_dict \
                and preprocessed_message_model is not None:
            await self.__rpc_controller.send_data(preprocessed_message_model)
            self.__logger.debug(f"{algorithm_data_message_model.source_label}转发消息"
                                f"{type(preprocessed_message_model.package)}")

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        self.__logger.debug(f"收到报告{type(algorithm_report_message_model)}")
        await self.__current_strategy.receive_report(algorithm_report_message_model)

    async def send_report(self, data_message_model: DataMessageModel):
        await self.__system_connector.send_message(self.__report_message_key, data_message_model)

    async def initial(self, config_dict: dict[str, any]) -> None:
        if self.__service_status not in [ServiceStatusEnum.STOPPED, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.INITIALIZING
        # 初始化配置信息
        if 'message' in config_dict:
            message_dict = config_dict.get('message', dict())
            self.__report_message_key = MessageKeyEnum.REPORT.value
            self.__report_message_topic = message_dict.get(self.__report_message_key, None)
        self.__service_status = ServiceStatusEnum.READY

    async def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if 'message' in config_dict:
            message_dict = config_dict.get('message', dict())
            self.__report_message_key = MessageKeyEnum.REPORT.value
            self.__report_message_topic = message_dict.get(self.__report_message_key, self.__report_message_topic)

    async def startup(self) -> None:
        if self.__service_status is not ServiceStatusEnum.READY:
            return
        self.__service_status = ServiceStatusEnum.STARTING
        await self.__system_connector.bind_message(self.__report_message_key, self.__report_message_topic)
        await self.__subscribe_source()
        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self) -> None:
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING

        for source_label in self.__source_dict:
            await self.__system_connector.unsubscribe_source(source_label)

        self.__service_status = ServiceStatusEnum.READY

    def set_subscribe_source(self, source_list: list[SourceModel]):
        self.__source_dict = {source_model.source_label: source_model for source_model in source_list}

    def set_transfer_source(self, source_list: list[SourceModel]):
        self.__transfer_source_dict = {source_model.source_label: source_model for source_model in source_list}
        self.__logger.debug(f"设置向算法端转发数据源{self.__transfer_source_dict}")

    def set_current_strategy(self, strategy: StrategyInterface):
        self.__current_strategy = strategy

    async def __subscribe_source(self):
        self.__logger.info(f"\n订阅数据源{self.__source_dict:}")
        for source_label in self.__source_dict:
            source_model = self.__source_dict[source_label]
            operator = AddDataOperator(source_label, self)
            await self.__system_connector.bind_message(source_model.source_label, source_model.source_topic)
            await self.__system_connector.subscribe_source(source_model.source_label, operator)
            self.__source_dict[source_model.source_label] = source_model
