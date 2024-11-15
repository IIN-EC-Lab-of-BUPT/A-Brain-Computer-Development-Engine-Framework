import logging
import logging.config
import os
import socket
import uuid
from typing import Union

import yaml
from injector import Provider, Injector, T

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from Task.common.utils.EventManager import EventManager
from Task.common.enum.TaskEventEnum import TaskEventEnum
from Task.control.CommandController import CommandController
from Task.control.interface.ControllerInterface import CommandControllerInterface

from Task.facade.AlgorithmRPCDataConnectClient import AlgorithmRPCDataConnectClient
from Task.facade.AlgorithmRPCServiceControlClient import AlgorithmRPCServiceControlClient
from Task.facade.RPCController import RPCController
from Task.facade.SystemConnector import SystemConnector
from Task.facade.interface.RpcControllerInterface import RpcControllerApplicationInterface, \
    RpcControllerManagementInterface
from Task.facade.interface.SystemConnectorInterface import SystemConnectorInterface
from Task.service.ChallengeManager import ChallengeManager
from Task.service.CoreController import CoreController
from Task.service.MessageForwarder import MessageForwarder
from Task.service.StrategyManager import StrategyManager
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface
from Task.service.interface.ServiceManagerInterface import (ChallengeManagerInterface, CoreControllerInterface,
                                                            MessageForwarderInterface, StrategyManagerInterface)


class ApplicationImplement(ApplicationInterface):

    def __init__(self):
        super().__init__()
        # 无初始配置信息
        self.__component_model: ComponentModel = None
        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__component_info: dict[str, Union[str, dict]] = dict()
        self.__injector: Injector = None
        self.__logger = logging.getLogger("taskLogger")

    async def initial(self) -> None:
        # 加载日志配置文件
        current_file_path = os.path.abspath(__file__)
        log_config_file_directory_path = os.path.join(os.path.dirname(os.path.dirname(current_file_path)),  'config')
        log_config_file_path = os.path.join(log_config_file_directory_path, 'LoggingConfig.yml')
        with open(log_config_file_path, 'r', encoding='utf-8') as logging_file:
            logging_config = yaml.safe_load(logging_file)

        # 应用配置到logging模块
        logging.config.dictConfig(logging_config)

        class RPCControllerProvider(Provider):
            instance: RPCController = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = RPCController(
                        injector.get(AlgorithmRPCDataConnectClient),
                        injector.get(AlgorithmRPCServiceControlClient)
                    )
                return cls.instance

        class MessageForwarderProvider(Provider):
            instance: MessageForwarder = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = MessageForwarder(
                        injector.get(SystemConnectorInterface),
                        injector.get(RpcControllerApplicationInterface)
                    )
                return cls.instance

        self._context_manager.bind_class(clazz=EventManager, to_target=EventManager)

        self._context_manager.bind_class(clazz=AlgorithmRPCDataConnectClient, to_target=AlgorithmRPCDataConnectClient)
        self._context_manager.bind_class(clazz=AlgorithmRPCServiceControlClient,
                                         to_target=AlgorithmRPCServiceControlClient)
        self._context_manager.bind_class(clazz=RpcControllerApplicationInterface, to_target=RPCControllerProvider())
        self._context_manager.bind_class(clazz=RpcControllerManagementInterface, to_target=RPCControllerProvider())
        self._context_manager.bind_class(clazz=SystemConnectorInterface, to_target=SystemConnector)

        self._context_manager.bind_class(clazz=ChallengeManagerInterface, to_target=ChallengeManager)
        self._context_manager.bind_class(clazz=MessageForwardApplicationInterface, to_target=MessageForwarderProvider())
        self._context_manager.bind_class(clazz=MessageForwarderInterface, to_target=MessageForwarderProvider())
        self._context_manager.bind_class(clazz=StrategyManagerInterface, to_target=StrategyManager)
        self._context_manager.bind_class(clazz=CommandControllerInterface, to_target=CommandController)

        self._context_manager.bind_class(clazz=CoreControllerInterface, to_target=CoreController)

        # 外部延迟注入
        core_controller = self._context_manager.get_instance(CoreControllerInterface)
        strategy_manager = self._context_manager.get_instance(StrategyManagerInterface)
        strategy_manager.set_core_controller(core_controller)

        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        application_config_file_name = 'ApplicationImplement.yml'
        application_config_path = os.path.join(directory_path, application_config_file_name)

        with open(application_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)
        # 生成组件信息
        component_dict = self.__config_dict.get("component", dict())
        # 组件ID遵循如下规则：
        # 1.如果在配置文件中写入，则优先使用配置文件定义的ID
        # 2.如果配置文件中未写入，则检查环境变量中COMPONENT_ID字段，如果存在则使用环境变量中定义的ID
        # 3.如果环境变量中未找到COMPONENT_ID字段，则根据component_type字段自动生成component_type+随机uuid作为component_id
        component_type = component_dict.get('component_type', "")
        component_id = component_dict.get('component_id') \
            if component_dict.get('component_id', None) is not None else \
            (
                os.environ.get('COMPONENT_ID') if os.environ.get('COMPONENT_ID', None) is not None else
                component_type + '_' + str(uuid.uuid4())
            )
        self.__component_model = ComponentModel(
            component_id=component_id,
            component_type=component_type,
            component_info=component_dict.get('component_info', dict())
        )

        self.__component_model.component_info.update(component_dict.get("component_info", dict()))

        if self.__component_model.component_info.get('team_name', None) is None:
            self.__component_model.component_info['team_name'] = os.getenv('TEAM_NAME', None)
        if self.__component_model.component_info.get('algorithm_number', None) is None:
            self.__component_model.component_info['algorithm_number'] = os.getenv('ALGORITHM_NUMBER', None)

        # 获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.254.254.254', 1))
            ip_address = s.getsockname()[0]
        except Exception as e:
            ip_address = '127.0.0.1'
        finally:
            s.close()

        self.__component_model.component_info.update({'ip': ip_address})

    async def run(self) -> None:
        # 加载配置文件
        core_controller: CoreControllerInterface = self._context_manager.get_instance(CoreControllerInterface)
        await core_controller.initial(self.__component_info)
        await core_controller.startup()  # core_controller已经包含等待结束事件

    async def exit(self) -> None:
        self.__logger.info("收到Application exit请求")
        event_manager: EventManager = self._context_manager.get_instance(EventManager)
        # 唤醒退出事件
        await event_manager.notify(event_name=TaskEventEnum.APPLICATION_EXIT.value)

    def get_component_model(self) -> ComponentModel:
        return self.__component_model
