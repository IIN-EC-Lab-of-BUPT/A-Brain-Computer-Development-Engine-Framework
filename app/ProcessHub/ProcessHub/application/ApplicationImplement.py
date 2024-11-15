import asyncio
import importlib
import logging
import logging.config
import os
import sys
import uuid

import yaml
from injector import Provider, Injector, T

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ProcessHub.algorithm_connector.AlgorithmConnectorFactoryManager import AlgorithmConnectorFactoryManager
from ProcessHub.algorithm_connector.interface.AlgorithmConnectorFactoryInterface import \
    AlgorithmConnectorFactoryManagerInterface, AlgorithmConnectorFactoryInterface
from ProcessHub.common.utils.EventManager import EventManager
from ProcessHub.common.enum.ProcessHubEventEnum import ProcessHubEventEnum
from ProcessHub.control.CommandController import CommandController
from ProcessHub.control.interface.ControllerInterface import CommandControllerInterface

from ProcessHub.algorithm_connector.facade.AlgorithmRPCDataConnectClient import AlgorithmRPCDataConnectClient
from ProcessHub.algorithm_connector.facade.AlgorithmRPCServiceControlClient import AlgorithmRPCServiceControlClient

from ProcessHub.orchestrator.interface.OrchestratorInterface import OrchestratorInterface


class ApplicationImplement(ApplicationInterface):

    def __init__(self):
        super().__init__()
        # 无初始配置信息
        self.__finish_event: asyncio.Event = asyncio.Event()
        self.__orchestrator: OrchestratorInterface = None
        self.__component_model: ComponentModel = None
        self.__orchestrator_class_name: str = None
        self.__orchestrator_class_file: str = None

        self.__injector: Injector = None
        self.__logger = logging.getLogger("processHubLogger")

    async def initial(self) -> None:
        # 加载日志配置文件
        current_file_path = os.path.abspath(__file__)
        log_config_file_directory_path = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), 'config')
        log_config_file_path = os.path.join(log_config_file_directory_path, 'LoggingConfig.yml')
        with open(log_config_file_path, 'r', encoding='utf-8') as logging_file:
            logging_config = yaml.safe_load(logging_file)

        # 应用配置到logging模块
        logging.config.dictConfig(logging_config)

        class AlgorithmConnectorFactoryManagerProvider(Provider):
            instance: AlgorithmConnectorFactoryManager = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = AlgorithmConnectorFactoryManager(
                        injector.get(AlgorithmRPCDataConnectClient),
                        injector.get(AlgorithmRPCServiceControlClient)
                    )
                return cls.instance

        self._context_manager.bind_class(clazz=EventManager, to_target=EventManager)

        self._context_manager.bind_class(clazz=AlgorithmRPCDataConnectClient, to_target=AlgorithmRPCDataConnectClient)
        self._context_manager.bind_class(clazz=AlgorithmRPCServiceControlClient,
                                         to_target=AlgorithmRPCServiceControlClient)
        self._context_manager.bind_class(clazz=AlgorithmConnectorFactoryInterface,
                                         to_target=AlgorithmConnectorFactoryManagerProvider())
        self._context_manager.bind_class(clazz=AlgorithmConnectorFactoryManagerInterface,
                                         to_target=AlgorithmConnectorFactoryManagerProvider())

        self._context_manager.bind_class(clazz=CommandControllerInterface, to_target=CommandController)

        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        application_config_file_name = 'ApplicationImplement.yml'
        application_config_path = os.path.join(directory_path, application_config_file_name)

        with open(application_config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        # 生成组件信息
        component_dict = config_dict.get("component", dict())
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

        orchestrator_dict = config_dict.get('orchestrator', dict())
        self.__orchestrator_class_file = orchestrator_dict.get('orchestrator_class_file', "")
        self.__orchestrator_class_name = orchestrator_dict.get('orchestrator_class_name', "")

        algorithm_connector_factory_manager = self._context_manager.get_instance(
            AlgorithmConnectorFactoryManagerInterface)
        await algorithm_connector_factory_manager.initial()
        command_controller = self._context_manager.get_instance(CommandControllerInterface)
        await command_controller.initial()

    async def run(self) -> None:
        algorithm_connector_factory_manager = self._context_manager.get_instance(
            AlgorithmConnectorFactoryManagerInterface)
        await algorithm_connector_factory_manager.startup()
        command_controller = self._context_manager.get_instance(CommandControllerInterface)
        await command_controller.startup()


        # 绑定应用结束事件处理方法
        event_manager: EventManager = self._context_manager.get_instance(EventManager)
        event_manager.subscribe(event_name=ProcessHubEventEnum.APPLICATION_EXIT.value,
                                callback=self.__on_application_exit)
        # 加载编排器对象
        self.__orchestrator = self.__load_orchestrator(
            orchestrator_class_file=self.__orchestrator_class_file,
            orchestrator_class_name=self.__orchestrator_class_name
        )
        # 注入组件框架和算法连接器工厂
        self.__orchestrator.set_component_framework(self._context_manager.get_instance(ComponentFrameworkInterface))
        self.__orchestrator.set_algorithm_connector_factory(algorithm_connector_factory_manager)
        await self.__orchestrator.initial()
        await self.__orchestrator.startup()
        await self.__finish_event.wait()

    async def exit(self) -> None:
        self.__logger.info("收到Application exit请求")
        event_manager: EventManager = self._context_manager.get_instance(EventManager)
        # 唤醒退出事件
        await event_manager.notify(event_name=ProcessHubEventEnum.APPLICATION_EXIT.value)

    def get_component_model(self) -> ComponentModel:
        return self.__component_model

    async def __on_application_exit(self):
        self.__logger.info("收到Application exit事件")
        await self.__orchestrator.shutdown()
        command_controller: CommandControllerInterface = self._context_manager.get_instance(CommandControllerInterface)
        await command_controller.shutdown()
        algorithm_connector_factory_manager: AlgorithmConnectorFactoryManagerInterface = (
            self._context_manager.get_instance(AlgorithmConnectorFactoryManagerInterface))
        await algorithm_connector_factory_manager.shutdown()
        self.__finish_event.set()

    def __load_orchestrator(self, orchestrator_class_file: str, orchestrator_class_name: str) -> OrchestratorInterface:
        self.__logger.debug('加载编排器: ' + orchestrator_class_file + ':' + orchestrator_class_name)
        workspace_path = os.getcwd()
        absolute_orchestrator_class_file = os.path.join(workspace_path, orchestrator_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_orchestrator_class_file))[0]
        # 获取赛题模块所在的目录
        module_dir = os.path.dirname(absolute_orchestrator_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        orchestrator_class = getattr(module, orchestrator_class_name)
        instance = orchestrator_class()
        return instance
