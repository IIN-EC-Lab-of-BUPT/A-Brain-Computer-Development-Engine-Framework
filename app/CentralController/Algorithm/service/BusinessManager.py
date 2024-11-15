import importlib
import logging
import os
import sys
import time
from typing import Union

from injector import inject

from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.method.interface.ProxyInterface import ProxyInterface
from Algorithm.method.model.AlgorithmObject import AlgorithmResultObject
from Algorithm.service.exception.AlgorithmSourceException import AlgorithmSourceReceiverNotFoundException
from Algorithm.service.exception.AlgorithmReportException import AlgorithmReportResultTypeIsNotSupportedException
from Algorithm.service.interface.DataForwarderInterface import DataForwarderInterface
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.service.interface.ServiceManagerInterface import BusinessManagerInterface
from Algorithm.service.interface.SourceReceiverInterface import SourceReceiverInterface
from Common.converter.BaseDataClassMessageConverter import BaseDataClassMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from Common.model.BaseDataClassModel import StringMessageModel, EmptyMessageModel, BinaryMessageModel, \
    IntListMessageModel, FloatListMessageModel, StringListMessageModel
from Common.model.CommonMessageModel import ResultPackageModel, ReportSourceInformationModel


class BusinessManager(ProxyInterface, DataForwarderInterface, BusinessManagerInterface):
    """
    业务模块
    数据收发结果报告等核心业务逻辑处理类
    """

    @inject
    def __init__(self):
        # 根据config_dict中的配置信息初始化数据源对象
        # 源接收器创建器
        self.__source_receiver_dict: dict[str, SourceReceiverInterface] \
            = dict[str, SourceReceiverInterface]()
        self.__rpc_controller: RpcControllerInterface = None
        self.__logger = logging.getLogger("algorithmLogger")

        # 服务状态
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

        # 源接收器工厂
        self.__source_receiver_factory_dict = dict[str, any]()
        # 源配置信息
        self.__source_config_dict = dict[str, Union[str, dict]]()

        self.__challenge_config_dict = dict[str, Union[str, dict]]()

        self.__base_data_class_message_converter = BaseDataClassMessageConverter()

    def get_source(self, source_label: str) -> SourceReceiverInterface:
        return self.__source_receiver_dict[source_label]

    async def forward_data(self, algorithm_data_message: AlgorithmDataMessageModel):
        # 模型解析器，根据不同的模型标签，转发到不同的源模块
        source_label = algorithm_data_message.source_label
        self.__logger.debug(f"forward data to source: {source_label}\ndata:{type(algorithm_data_message.package)}")
        if source_label in self.__source_receiver_dict:
            await self.__source_receiver_dict[source_label].set_message_model(algorithm_data_message)
        else:
            raise AlgorithmSourceReceiverNotFoundException(f"SourceReceiver: {source_label} is not exist")
        return

    async def report(self, algorithm_result_object: AlgorithmResultObject):
        # 接收算法结果，并且汇总各个源点数信息，并且报告
        algorithm_report_message_model = AlgorithmReportMessageModel(
            timestamp=time.time(),
            package=self.__convert_algorithm_result_object_to_result_package_model(algorithm_result_object)
        )
        await self.__rpc_controller.report(algorithm_report_message_model)
        return

    def get_challenge_config(self) -> dict[str, Union[str, dict]]:
        return self.__challenge_config_dict

    async def initial_system(self, config_dict: dict[str, Union[str, dict]] = None):
        if self.__service_status is not ServiceStatusEnum.STOPPED:
            return
        # 设置服务初始化状态
        self.__service_status = ServiceStatusEnum.INITIALIZING

        # 根据config_dict中的配置信息初始化数据源对象
        if 'source_receiver_handlers' in config_dict:
            # 加载数据源接收器配置
            source_receiver_config_dict = config_dict['source_receiver_handlers']
            self.__load_source_receiver_handles(source_receiver_config_dict)
            self.__logger.info(f"已经加载数据源处理器{source_receiver_config_dict}")
        if 'sources' in config_dict:
            self.__source_config_dict = config_dict['sources']
            self.__logger.info(f"已缓存源配置信息{self.__source_config_dict}")

        # 设置服务就绪状态
        self.__service_status = ServiceStatusEnum.READY

    async def receive_config(self, config_dict: dict[str, Union[str, dict]]):
        self.__challenge_config_dict.update(config_dict)

    async def get_config(self) -> dict[str, Union[str, dict]]:
        config_dict = dict[str, Union[str, dict]]()
        # config_dict['challenge_to_algorithm_config'] = self.__challenge_config_dict
        config_dict['sources'] = {key: None for key in self.__source_config_dict.keys()}
        return config_dict

    async def startup(self):
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.STARTING

        for source_label in self.__source_config_dict:
            source_receiver_dict = self.__source_config_dict[source_label]['source_receiver']
            handler_name = source_receiver_dict['handler']
            configuration_dict = source_receiver_dict['configuration']
            self.__source_receiver_dict[source_label] = self.__get_source_receiver_instance(
                source_label,
                handler_name,
                configuration_dict
            )
        self.__logger.info(f"已经初始化数据源接收器{self.__source_receiver_dict}")

        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self):
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        # 清理所有数据源接收器
        self.__source_config_dict.clear()
        self.__logger.info("业务管理器已关闭")
        self.__service_status = ServiceStatusEnum.READY

    def __load_source_receiver_handles(self, source_receiver_handlers_dict: dict[str, Union[str, dict]]):
        # 辅助读取源接收器配置信息
        workspace_path = os.getcwd()
        for source_receiver_name in source_receiver_handlers_dict:
            receiver_config_dict = source_receiver_handlers_dict[source_receiver_name]
            receiver_class_file = receiver_config_dict['receiver_class_file']
            receiver_class_name = receiver_config_dict['receiver_class_name']
            absolute_receiver_class_file = os.path.join(workspace_path, receiver_class_file)
            module_name = os.path.splitext(os.path.basename(absolute_receiver_class_file))[0]
            # 获取模块所在的目录
            module_dir = os.path.dirname(absolute_receiver_class_file)
            if module_dir not in sys.path:
                sys.path.append(module_dir)
            module = importlib.import_module(module_name)
            source_receiver_class = getattr(module, receiver_class_name)
            self.__source_receiver_factory_dict[source_receiver_name] = source_receiver_class

    def __get_source_receiver_instance(self,
                                       source_label: str,
                                       source_receiver_handler_name: str,
                                       configuration: dict[str, Union[str, dict]]) -> SourceReceiverInterface:
        source_receiver_class = self.__source_receiver_factory_dict[source_receiver_handler_name]
        source_receiver: SourceReceiverInterface = source_receiver_class()
        source_receiver.set_source_label(source_label)
        source_receiver.set_configuration(configuration)
        return source_receiver

    def __convert_algorithm_result_object_to_result_package_model(
            self, algorithm_result_object: AlgorithmResultObject) -> ResultPackageModel:
        result_data = algorithm_result_object.result
        if result_data is None:
            result_model = EmptyMessageModel()
        elif isinstance(result_data, bytes):
            result_model = BinaryMessageModel(data=result_data)
        elif isinstance(result_data, str):
            result_model = StringMessageModel(data=result_data)
        elif isinstance(result_data, list):
            if len(result_data) == 0:
                result_model = EmptyMessageModel()
            elif isinstance(result_data[0], int):
                result_model = IntListMessageModel(data=result_data)
            elif isinstance(result_data[0], float):
                result_model = FloatListMessageModel(data=result_data)
            elif isinstance(result_data[0], str):
                result_model = StringListMessageModel(data=result_data)
            else:
                raise AlgorithmReportResultTypeIsNotSupportedException(type(result_data).__name__)
        result_package_model = ResultPackageModel(
            result=result_model,
            result_message_class=None,  # 由转化方法自动填充
            report_source_information=[
                ReportSourceInformationModel(source_label=source_business_object.get_source_label(),
                                             position=source_business_object.get_used_data_position())
                for source_business_object in self.__source_receiver_dict.values()]
        )
        return result_package_model

    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        self.__rpc_controller = rpc_controller
