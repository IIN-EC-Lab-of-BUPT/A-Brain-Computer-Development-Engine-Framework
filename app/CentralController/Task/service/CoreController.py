import asyncio
import logging
from typing import Union
from injector import inject

from ApplicationFramework.common.utils.ContextManager import ContextManager
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from Common.model.CommonMessageModel import ControlPackageModel, DataMessageModel
from Task.api.exception.TaskException import TaskException
from Task.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Task.common.model.SourceModel import SourceModel
from Task.control.interface.ControllerInterface import CommandControllerInterface
from Task.facade.interface.SystemConnectorInterface import SystemConnectorInterface
from Task.facade.interface.RpcControllerInterface import RpcControllerManagementInterface
from Task.service.excepiton.TaskServiceException import TaskServiceStatusException
from Task.service.interface.ServiceManagerInterface import CoreControllerInterface, ChallengeManagerInterface, \
    StrategyManagerInterface, MessageForwarderInterface


class CoreController(CoreControllerInterface):

    # 核心逻辑管理器,主要负责全部流程管理
    @inject
    def __init__(self, challenge_manager: ChallengeManagerInterface,
                 strategy_manager: StrategyManagerInterface,
                 message_forwarder: MessageForwarderInterface,
                 system_connector: SystemConnectorInterface,
                 rpc_controller: RpcControllerManagementInterface,
                 command_controller: CommandControllerInterface,
                 context_manager: ContextManager
                 ):
        self.__challenge_manager: ChallengeManagerInterface = challenge_manager
        self.__strategy_manager: StrategyManagerInterface = strategy_manager
        self.__message_forwarder: MessageForwarderInterface = message_forwarder
        self.__systemConnector: SystemConnectorInterface = system_connector
        self.__rpc_controller: RpcControllerManagementInterface = rpc_controller
        self.__command_controller: CommandControllerInterface = command_controller
        self.__context_manager: ContextManager = context_manager
        self.__component_framework: ComponentFrameworkApplicationInterface = \
            self.__context_manager.get_instance(ComponentFrameworkApplicationInterface)

        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

        # 阻塞标记，用于阻塞主线程
        self.__finish_async_event = asyncio.Event()
        self.__logger = logging.getLogger("taskLogger")

    def get_service_status(self) -> ServiceStatusEnum:
        return self.__service_status

    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if self.__service_status not in [ServiceStatusEnum.STOPPED, ServiceStatusEnum.ERROR]:
            raise TaskServiceStatusException(f"CoreController初始化异常，"
                                             f"当前状态为{self.__service_status.name}，需要状态为STOPPED或ERROR")
        self.__service_status = ServiceStatusEnum.INITIALIZING

        try:
            self.__logger.info("CoreController初始化")
            # 拉取注册中心更新配置信息
            component_model = await self.__systemConnector.get_component_model()
            component_info = component_model.component_info
            config_dict.update(component_info)
            # 初始化所有管理器配置信息
            # 初始化配置信息
            await self.__rpc_controller.initial(config_dict)
            await self.__command_controller.initial(config_dict)
            await self.__message_forwarder.initial(config_dict)
            await self.__strategy_manager.initial(config_dict)
            await self.__challenge_manager.initial(config_dict)

            self.__service_status = ServiceStatusEnum.READY
        except TaskException as e:
            self.__logger.error(f"CoreController初始化失败，错误信息为{e}")
            self.__service_status = ServiceStatusEnum.ERROR
        return

    async def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        self.__logger.info("CoreController更新配置")
        try:
            await self.__rpc_controller.update(config_dict)
            await self.__command_controller.update(config_dict)
            await self.__message_forwarder.update(config_dict)
            await self.__strategy_manager.update(config_dict)
            await self.__challenge_manager.update(config_dict)
        except TaskException as e:
            self.__logger.error(f"CoreController初始化失败，错误信息为{e}")
            self.__service_status = ServiceStatusEnum.ERROR
        return

    async def startup(self):
        if self.__service_status is not ServiceStatusEnum.READY:
            raise TaskServiceStatusException(f"CoreController启动失败，当前状态为{self.__service_status.name}，需要状态为READY")
        self.__service_status = ServiceStatusEnum.STARTING
        self.__logger.info("CoreController流程启动")

        try:
            await self.__challenge_manager.startup()
            await self.__strategy_manager.startup()

            current_challenge = self.__challenge_manager.get_current_challenge()
            current_strategy = self.__strategy_manager.get_current_strategy()
            await current_strategy.set_challenge(current_challenge)
            self.__message_forwarder.set_current_strategy(current_strategy)

            # 算法启动流程
            # 先启动RPC连接，然后发送初始化配置信息，然后拉取算法端配置信息，并推送给数据转发节点订阅数据源。
            # 所有配置更新仅允许算法启动前执行一次，算法运行过程中不更新任何配置内容
            # 能连接成功就意味着算法端已经启动，算法已经初始化完毕，达到就绪状态
            await self.__rpc_controller.startup()
            await self.__command_controller.startup()

            # 向算法端发送赛题的配置信息
            to_algorithm_config = await current_challenge.get_to_algorithm_config()
            await self.__rpc_controller.send_config(to_algorithm_config)

            # 准备启动数据转发
            # 设定所需订阅数据源
            self.__message_forwarder.set_subscribe_source(await current_challenge.get_source_list())
            # 设定所需转发数据源
            algorithm_config_dict = await self.__rpc_controller.get_config()
            transfer_sources_dict = algorithm_config_dict.get('sources', {})
            self.__message_forwarder.set_transfer_source(
                [SourceModel(source_label=source_label) for source_label in transfer_sources_dict]
            )
            # 启动数据转发器连接
            await self.__message_forwarder.startup()
            self.__service_status = ServiceStatusEnum.RUNNING
            # 向注册中心发送状态
            await self.__component_framework.update_component_status(ComponentStatusEnum.RUNNING)
            self.__logger.info("CoreController流程启动完成")

            # 阻塞直到收到停止指令
            await self.__finish_async_event.wait()

        except TaskException as e:
            self.__logger.error(f"CoreController流程启动失败，错误信息为{e}")
            self.__service_status = ServiceStatusEnum.ERROR
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def shutdown(self):
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            raise TaskServiceStatusException(f"CoreController流程停止失败，当前状态为{self.__service_status.name}，需要状态为RUNNING")
        self.__service_status = ServiceStatusEnum.STOPPING
        self.__logger.info("CoreController流程停止开始")
        try:
            await self.__message_forwarder.send_report(
                DataMessageModel(
                    package=ControlPackageModel(end_flag=True)))
            await self.__message_forwarder.shutdown()
            await self.__command_controller.shutdown()
            # 断开RPC数据连接
            await self.__rpc_controller.shutdown()

            # 关闭各种服务
            await self.__strategy_manager.shutdown()
            await self.__challenge_manager.shutdown()

            # 向注册中心发送状态
            await self.__component_framework.update_component_status(ComponentStatusEnum.STOP)
            # 解除阻塞
            self.__finish_async_event.set()
            self.__service_status = ServiceStatusEnum.STOPPED
            self.__logger.info("CoreController流程停止已完成")
        except TaskException as e:
            self.__logger.error(f"CoreController流程停止失败，错误信息为{e}")
            self.__service_status = ServiceStatusEnum.ERROR
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def shutdown_and_close_algorithm_system(self):
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            raise TaskServiceStatusException(f"CoreController流程停止失败，当前状态为{self.__service_status.name}，需要状态为RUNNING")
        self.__service_status = ServiceStatusEnum.STOPPING
        self.__logger.info("CoreController流程停止开始，并且关闭算法系统")
        try:
            await self.__message_forwarder.send_report(
                DataMessageModel(
                    package=ControlPackageModel(end_flag=True)))
            await self.__message_forwarder.shutdown()
            await self.__command_controller.shutdown()
            # 断开RPC数据连接
            await self.__rpc_controller.shutdown_and_close_algorithm_system()
            # 向注册中心发送状态
            await self.__component_framework.update_component_status(ComponentStatusEnum.STOP)
            # 解除阻塞
            self.__finish_async_event.set()
            self.__service_status = ServiceStatusEnum.STOPPED
            self.__logger.info("CoreController流程停止已完成")
        except TaskException as e:
            self.__logger.error(f"CoreController流程停止失败，错误信息为{e}")
            self.__service_status = ServiceStatusEnum.ERROR
