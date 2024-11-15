import asyncio
import logging
from typing import Union
from injector import inject

from Algorithm.common.enum.AlgorithmEventEnum import AlgorithmEventEnum
from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.common.utils.EventManager import EventManager
from Algorithm.service.exception.AlgorithmServiceException import AlgorithmServiceStatusException

from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.service.interface.ServiceManagerInterface import CoreControllerInterface, MethodManagerInterface, \
    BusinessManagerInterface, ConfigManagerInterface


class CoreController(CoreControllerInterface):

    @inject
    def __init__(self, config_manager: ConfigManagerInterface,
                 business_manager: BusinessManagerInterface,
                 method_manager: MethodManagerInterface,
                 event_manager: EventManager
                 ):
        self.__config_manager: ConfigManagerInterface = config_manager
        self.__business_manager: BusinessManagerInterface = business_manager
        self.__method_manager: MethodManagerInterface = method_manager
        self.__rpc_controller: RpcControllerInterface = None
        self.__event_manager: EventManager = event_manager
        self.__logger = logging.getLogger("algorithmLogger")
        # 设置系统退出停止事件
        self.__finish_async_event = asyncio.Event()
        # 服务状态
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

    async def initial_system(self, config_dict: dict[str, Union[str, dict]] = None):
        if self.__service_status is not ServiceStatusEnum.STOPPED:
            raise AlgorithmServiceStatusException(f"CoreController初始化异常，"
                                                  f"当前状态为{self.__service_status.name}，需要状态为STOPPED")
        # 设置服务初始化状态
        self.__service_status = ServiceStatusEnum.INITIALIZING
        self.__logger.info("core_manager初始化系统")
        # 先初始化配置管理器,由配置管理器初始化其他管理器
        await self.__config_manager.initial_system()

        # 启动RpcController.startup
        await self.__rpc_controller.startup()

        # 订阅数据接收开始事件,执行启动指令
        self.__event_manager.subscribe(AlgorithmEventEnum.RPC_DATA_INPUT_CONNECT_STARTED.value, self.startup)

        # 订阅算法结束事件,执行退出指令
        self.__event_manager.subscribe(AlgorithmEventEnum.METHOD_FINISHED.value, self.shutdown)

        # 订阅数据接收完成事件,执行退出指令
        self.__event_manager.subscribe(AlgorithmEventEnum.RPC_DATA_INPUT_CONNECT_FINISHED.value, self.shutdown)

        # 设置服务就绪状态
        self.__service_status = ServiceStatusEnum.READY

        # 阻塞直到收到停止指令,初始化以后可以多次startup/shutdown，直到收到exit指令
        await self.__finish_async_event.wait()

    async def startup(self) -> None:
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            self.__logger.info(f"CoreController已非就绪状态，无需再次启动，"
                               f"当前状态为{self.__service_status.name}，需要状态为READY或ERROR")
            return
        self.__service_status = ServiceStatusEnum.STARTING
        await self.__config_manager.startup()
        await self.__business_manager.startup()
        await self.__method_manager.startup()
        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self) -> None:
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            self.__logger.info(f"CoreController已经非运行状态，无需再次关闭，"
                               f"当前状态为{self.__service_status.name}")
            return
        self.__service_status = ServiceStatusEnum.STOPPING
        await self.__method_manager.shutdown()
        await self.__business_manager.shutdown()
        await self.__rpc_controller.disconnect()
        await self.__config_manager.shutdown()
        self.__service_status = ServiceStatusEnum.READY
        self.__logger.info(f"CoreController已经正常关闭"
                           f"当前状态为{self.__service_status.name}")

    async def exit(self):
        # 彻底关闭RpcController.shutdown
        try:
            await self.__rpc_controller.shutdown()
        except AlgorithmServiceStatusException as e:
            self.__logger.info(f"CoreController状态为{self.__service_status.name},已经非RUNNING")
        # 直接结束算法进程
        self.__finish_async_event.set()

        self.__logger.info("算法系统已经关闭")

    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        self.__rpc_controller = rpc_controller

    def get_service_status(self) -> ServiceStatusEnum:
        return self.__service_status
