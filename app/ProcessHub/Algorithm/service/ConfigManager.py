import logging
import os
from typing import Union

import yaml
from injector import inject

from Algorithm.common.enum.ServiceStatusEnum import ServiceStatusEnum
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.service.interface.ServiceManagerInterface import MethodManagerInterface, \
    BusinessManagerInterface, ConfigManagerInterface


class ConfigManager(ConfigManagerInterface):

    @inject
    def __init__(self,
                 method_manager: MethodManagerInterface,
                 business_manager: BusinessManagerInterface
                 ):
        self.__config_dict = dict[str, Union[str, dict]]()
        self.__config_file_path: str = None
        self.__logger = logging.getLogger("algorithmLogger")

        self.__rpc_controller: RpcControllerInterface = None
        self.__method_manager: MethodManagerInterface = method_manager
        self.__business_manager: BusinessManagerInterface = business_manager

        # 服务状态
        self.__service_status: ServiceStatusEnum = ServiceStatusEnum.STOPPED

    async def initial_system(self, config_dict: dict[str, Union[str, dict]] = None):
        """
        初始化配置信息
        :return:
        """
        if self.__service_status is not ServiceStatusEnum.STOPPED:
            return
        # 设置服务初始化状态
        self.__service_status = ServiceStatusEnum.INITIALIZING

        self.__logger.info("config_manager启动")
        workspace_path = os.getcwd()
        config_path = os.path.join(workspace_path, self.__config_file_path)
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            # 通知所有其他管理器进行配置初始化
            self.__logger.info(f"config_manager启动系统初始化{config_dict}")
            if 'connection' in config_dict:
                await self.__rpc_controller.initial_system(config_dict['connection'])
            # 检查是否有策略更新
            if 'method' in config_dict:
                await self.__method_manager.initial_system(config_dict['method'])

            business_config_dict = dict[str, Union[str, dict]]()
            if 'source_receiver_handlers' in config_dict:
                business_config_dict['source_receiver_handlers'] = config_dict['source_receiver_handlers']
            if 'sources' in config_dict:
                business_config_dict['sources'] = config_dict['sources']
            # 检查是否有配置更新
            await self.__business_manager.initial_system(business_config_dict)
        # 设置服务就绪状态
        self.__service_status = ServiceStatusEnum.READY

    async def receive_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
        await self.__business_manager.receive_config(config_dict)

    async def get_config(self) -> dict[str, Union[str, dict]]:
        return await self.__business_manager.get_config()

    async def startup(self) -> None:
        if self.__service_status not in [ServiceStatusEnum.READY, ServiceStatusEnum.ERROR]:
            return
        self.__service_status = ServiceStatusEnum.STARTING

        self.__service_status = ServiceStatusEnum.RUNNING

    async def shutdown(self) -> None:
        if self.__service_status is not ServiceStatusEnum.RUNNING:
            return
        self.__service_status = ServiceStatusEnum.STOPPING

        self.__service_status = ServiceStatusEnum.READY

    def set_config_file_path(self, config_file_path: str) -> None:
        self.__config_file_path = config_file_path

    def set_rpc_controller(self, rpc_controller: RpcControllerInterface) -> None:
        self.__rpc_controller = rpc_controller
