import asyncio
import importlib
import logging
import os
import sys
import time
import traceback
from typing import Union

from injector import inject

from Algorithm.common.enum.AlgorithmEventEnum import AlgorithmEventEnum
from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.common.utils.EventManager import EventManager
from Algorithm.method.interface.AlgorithmInterface import AlgorithmInterface
from Algorithm.method.interface.ProxyInterface import ProxyInterface
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.service.interface.ServiceManagerInterface import MethodManagerInterface
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel
from Common.model.CommonMessageModel import ExceptionPackageModel


class MethodManager(MethodManagerInterface):

    @inject
    def __init__(self, method_proxy: ProxyInterface, event_manager: EventManager):
        self.__method_proxy: ProxyInterface = method_proxy
        self.__rpc_controller: RpcControllerInterface = None
        self.__event_manager: EventManager = event_manager
        self.__logger = logging.getLogger("algorithmLogger")
        self.__method_instance: AlgorithmInterface = None
        self.__method_task: asyncio.tasks = None
        # 服务状态
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

    async def initial_system(self, config_dict: dict[str, Union[str, dict]] = None):
        if self.__service_status is not ServiceStatusEnum.STOPPED:
            return
        # 设置服务初始化状态
        self.__service_status = ServiceStatusEnum.INITIALIZING
        self.__method_instance = self.__load_algorithm_instance(config_dict)

        # 设置服务就绪状态
        self.__service_status = ServiceStatusEnum.READY

    async def startup(self) -> None:
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.STARTING

        self.__method_task = asyncio.create_task(self.__run_algorithm_method())
        self.__logger.info("算法已启动")

        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self) -> None:
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        if self.__method_task is not None and not self.__method_task.done():
            self.__logger.info("等待算法结束")
            # 设置算法结束标志，并等待算法停止
            self.__method_instance.set_end_flag(True)
            await self.__method_task
        self.__service_status = ServiceStatusEnum.READY

    def __load_algorithm_instance(self, method_config_dict: dict[str, Union[str, dict]]) -> AlgorithmInterface:
        # 辅助读取算法信息并生成实例
        method_class_file = method_config_dict['method_class_file']
        method_class_name = method_config_dict['method_class_name']
        workspace_path = os.getcwd()
        absolute_strategy_class_file = os.path.join(workspace_path, method_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_strategy_class_file))[0]
        # 获取模块所在的目录
        module_dir = os.path.dirname(absolute_strategy_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        method_class = getattr(module, method_class_name)
        instance = method_class()
        instance.set_proxy(self.__method_proxy)
        return instance

    async def __run_algorithm_method(self):
        try:
            await self.__method_instance.run()
        except Exception:
            self.__logger.exception("算法执行发生异常")
            exc_type, exc_value, exception_traceback = sys.exc_info()
            # 发送算法异常信息
            await self.__rpc_controller.report(
                AlgorithmReportMessageModel(
                    timestamp=time.time(),
                    package=ExceptionPackageModel(
                        exception_type=str(exc_type),
                        # 截断异常信息，保留20个字符，防止通过异常信息传输结果参数
                        exception_message=str(exc_value) if len(str(exc_value)) <= 20 else str(exc_value)[:20],
                        exception_stack_trace=traceback.format_tb(exception_traceback)
                    )
                )
            )
        finally:
            self.__logger.info("算法执行结束")
            # 发出算法结束事件,以异步方式执行，不用等待到事件处理结束
            asyncio.create_task(self.__event_manager.notify(AlgorithmEventEnum.METHOD_FINISHED.value))

    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        self.__rpc_controller = rpc_controller
