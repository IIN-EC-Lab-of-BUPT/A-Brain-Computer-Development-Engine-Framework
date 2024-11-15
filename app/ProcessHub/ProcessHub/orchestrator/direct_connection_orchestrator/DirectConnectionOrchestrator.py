import importlib
import os
import socket
import logging
import sys
import time
from typing import Union

import yaml

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import DataMessageModel
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorInterface import AlgorithmConnectorInterface, \
    ReceiveAlgorithmReportMessageOperatorInterface
from ProcessHub.api.exception.ProcessHubException import ProcessHubException
from ProcessHub.bci_competition_task.interface.BCICompetitionTaskInterface import BCICompetitionTaskInterface
from ProcessHub.algorithm_connector.model.AlgorithmConnectModel import AlgorithmConnectModel
from ProcessHub.orchestrator.interface.OrchestratorInterface import OrchestratorInterface
from Common.protobuf.CommonMessage_pb2 import DataMessage as DataMessage_pb2
from ProcessHub.orchestrator.model.ReportDestinationModel import ReportDestinationModel
from ProcessHub.orchestrator.model.SourceModel import SourceModel


class DirectConnectionOrchestrator(OrchestratorInterface):

    def __init__(self):
        super().__init__()
        # self._component_framework: ComponentFrameworkInterface
        # self._algorithm_connector_factory: AlgorithmConnectorFactoryManagerInterface
        # 只需要一个算法连接器，如果需要多个可以列为list
        self.__source_list: list[SourceModel] = list[SourceModel]()
        self.__report_destination_list: list[ReportDestinationModel] = list[ReportDestinationModel]()
        self.__algorithm_connector: AlgorithmConnectorInterface = None
        self.__logger = logging.getLogger("processHubLogger")

    async def initial(self):
        config_path = os.path.join(os.path.dirname(__file__), 'DirectConnectionOrchestratorConfig.yml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict: dict = yaml.safe_load(f)

        # 加载source配置信息
        source_dict = config_dict.get('sources', dict[str, str]())
        for source_label, source_topic in source_dict.items():
            self.__source_list.append(SourceModel(source_label, source_topic))

        # 结果报告配置信息
        report_key_topic_dict = config_dict.get('report_key_topic_dict', dict())
        for report_key, report_topic in report_key_topic_dict.items():
            self.__report_destination_list.append(ReportDestinationModel(report_key, report_topic))

        algorithm_connect_dict = config_dict.get('algorithm_connection', dict())
        algorithm_connector_model = AlgorithmConnectModel(
            address=algorithm_connect_dict.get('address', ""),
            max_time_out=algorithm_connect_dict.get('max_time_out', 0)
        )

        self.__algorithm_connector = await self._algorithm_connector_factory.get_algorithm_connector(
            algorithm_connector_model)

    async def startup(self):
        self.__logger.info("ProcessHub Orchestrator流程开始启动")
        try:


            # 获取数据源并预定转发
            class ReceiveDataOperator(ReceiveMessageOperatorInterface):

                def __init__(self, source_label: str, algorithm_connector: AlgorithmConnectorInterface):
                    self.__source_label = source_label
                    self.__algorithm_connector = algorithm_connector

                async def receive_message(self, data: bytes) -> None:
                    # 转换类型，补充信息并直接转发
                    data_message = DataMessage_pb2()
                    data_message.ParseFromString(data)
                    data_message_model = CommonMessageConverter.protobuf_to_model(data_message)
                    algorithm_data_message_model = AlgorithmDataMessageModel(
                        source_label=self.__source_label,
                        timestamp=time.time(),
                        package=data_message_model.package)

                    await self.__algorithm_connector.send_data(algorithm_data_message_model)

            for source_model in self.__source_list:
                await self._component_framework.bind_message(
                    MessageBindingModel(message_key=source_model.source_label, topic=source_model.source_topic))
                await self._component_framework.subscribe_message(
                    source_model.source_label,
                    ReceiveDataOperator(source_model.source_label, self.__algorithm_connector)
                )

            # 获取结果并转发结果
            class ReceiveAlgorithmReportMessageOperator(ReceiveAlgorithmReportMessageOperatorInterface):
                def __init__(self, component_framework: ComponentFrameworkInterface,
                             report_destination_list: list[ReportDestinationModel]):
                    self.__component_framework: ComponentFrameworkInterface = component_framework
                    self.__report_destination_list: list[ReportDestinationModel] = report_destination_list

                async def receive_report(self, algorithm_report_message: AlgorithmReportMessageModel) -> None:
                    report_message_model = CommonMessageConverter.model_to_protobuf(
                        DataMessageModel(package=algorithm_report_message.package))

                    for inner_report_destination_model in self.__report_destination_list:
                        await self.__component_framework.send_message(
                            inner_report_destination_model.report_key,
                            report_message_model.SerializeToString())

            for report_destination_model in self.__report_destination_list:
                await self._component_framework.bind_message(
                    MessageBindingModel(message_key=report_destination_model.report_key,
                                        topic=report_destination_model.report_topic))

            self.__algorithm_connector.set_receive_report_operator(
                ReceiveAlgorithmReportMessageOperator(self._component_framework, self.__report_destination_list))
            # 启动算法连接器
            await self.__algorithm_connector.startup()

            await self._component_framework.update_component_status(ComponentStatusEnum.RUNNING)
            self.__logger.info("ProcessHub Orchestrator流程启动完成")
        except ProcessHubException  as e:
            self.__logger.error(f"ProcessHub Orchestrator流程启动失败，错误信息为{e}")
            await self._component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def shutdown(self):
        try:
            # 取消数据订阅
            for source_model in self.__source_list:
                await self._component_framework.unsubscribe_message(source_model.source_label)

            await self.__algorithm_connector.shutdown()
            # 向注册中心发送状态
            await self._component_framework.update_component_status(ComponentStatusEnum.STOP)
        except ProcessHubException  as e:
            self.__logger.error(f"ProcessHub Orchestrator流程停止失败，错误信息为{e}")
            await self._component_framework.update_component_status(ComponentStatusEnum.ERROR)
