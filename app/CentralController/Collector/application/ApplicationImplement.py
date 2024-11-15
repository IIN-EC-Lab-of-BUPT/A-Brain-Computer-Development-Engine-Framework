import asyncio
import logging
import logging.config
import os
import uuid
from typing import Union

import yaml
from injector import Provider, Injector, T

from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from ApplicationFramework.api.model.ComponentModel import ComponentModel
from Collector.api.exception.CollectorException import CollectorException
from Collector.common.enum.CollectorEventEnum import CollectorEventEnum
from Collector.common.utils.EventManager import EventManager
from Collector.control.CommandController import CommandController
from Collector.control.ExternalTriggerController import ExternalTriggerController
from Collector.control.RPCController import RPCController
from Collector.control.interface.ControllerInterface import CommandControllerInterface, \
    ExternalTriggerControllerInterface, RPCControllerInterface
from Collector.service.BusinessManager import BusinessManager
from Collector.service.ConfigManager import ConfigManager
from Collector.service.DataSenderManager import DataSenderManager
from Collector.service.ReceiverManager import ReceiverManager
from Collector.service.interface.ConfigManagerInterface import ConfigManagerInterface
from Collector.service.interface.BusinessManagerInterface import BusinessManagerInterface
from Collector.service.interface.TransponderInterface import ReceiverTransponderInterface, \
    InformationTransponderInterface
from Collector.service.interface.ReceiverManagerInterface import ReceiverManagerInterface
from Collector.service.interface.DataSenderManagerInterface import DataSenderManagerInterface


class ApplicationImplement(ApplicationInterface):

    def __init__(self):
        super().__init__()

        self.__component_model: ComponentModel = None
        self.__business_manager: BusinessManagerInterface = None
        self.__config_manager: ConfigManagerInterface = None
        self.__data_sender_manager: DataSenderManagerInterface = None
        self.__receiver_manager: ReceiverManagerInterface = None
        self.__rpc_controller: RPCControllerInterface = None
        self.__external_trigger_controller: ExternalTriggerControllerInterface = None
        self.__command_controller: CommandControllerInterface = None
        self.__component_framework: ComponentFrameworkInterface = None
        self.__event_manager: EventManager = None

        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__finish_event: asyncio.Event = asyncio.Event()
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self) -> None:
        # 加载日志配置文件
        current_file_path = os.path.abspath(__file__)
        log_config_file_directory_path = os.path.join(os.path.dirname(os.path.dirname(current_file_path)),  'config')
        log_config_file_path = os.path.join(log_config_file_directory_path, 'LoggingConfig.yml')
        with open(log_config_file_path, 'r', encoding='utf-8') as logging_file:
            logging_config = yaml.safe_load(logging_file)

        # 应用配置到logging模块
        logging.config.dictConfig(logging_config)

        # 应用初始化
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

        # 应用上下文封装
        class BusinessManagerProvider(Provider):
            instance: BusinessManager = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = BusinessManager(injector.get(ComponentFrameworkInterface))
                return cls.instance

        self._context_manager.bind_class(clazz=EventManager, to_target=EventManager)
        self._context_manager.bind_class(clazz=ReceiverTransponderInterface, to_target=BusinessManagerProvider())
        self._context_manager.bind_class(clazz=InformationTransponderInterface, to_target=BusinessManagerProvider())
        self._context_manager.bind_class(clazz=BusinessManagerInterface, to_target=BusinessManagerProvider())
        self._context_manager.bind_class(clazz=DataSenderManagerInterface, to_target=DataSenderManager)
        self._context_manager.bind_class(clazz=ReceiverManagerInterface, to_target=ReceiverManager)

        self._context_manager.bind_class(clazz=CommandControllerInterface, to_target=CommandController)
        self._context_manager.bind_class(clazz=ExternalTriggerControllerInterface, to_target=ExternalTriggerController)
        self._context_manager.bind_class(clazz=RPCControllerInterface, to_target=RPCController)

        self._context_manager.bind_class(clazz=ConfigManagerInterface, to_target=ConfigManager)

        # 获取各个服务组件实例
        self.__event_manager: EventManager = self._context_manager.get_instance(EventManager)
        self.__component_framework: ComponentFrameworkInterface = self._context_manager.get_instance(
            ComponentFrameworkInterface)
        self.__business_manager: BusinessManagerInterface = self._context_manager.get_instance(BusinessManagerInterface)
        self.__config_manager: ConfigManagerInterface = self._context_manager.get_instance(ConfigManagerInterface)
        self.__data_sender_manager: DataSenderManagerInterface = self._context_manager.get_instance(
            DataSenderManagerInterface)
        self.__receiver_manager: ReceiverManagerInterface = self._context_manager.get_instance(ReceiverManagerInterface)
        self.__rpc_controller: RPCControllerInterface = self._context_manager.get_instance(RPCControllerInterface)
        self.__external_trigger_controller: ExternalTriggerControllerInterface = self._context_manager.get_instance(
            ExternalTriggerControllerInterface)
        self.__command_controller: CommandControllerInterface = self._context_manager.get_instance(
            CommandControllerInterface)

        # 补充构建服务组件
        self.__business_manager.set_receiver_manager(self.__receiver_manager)
        self.__business_manager.set_data_sender_manager(self.__data_sender_manager)

        # 初始化各个服务组件
        await self.__business_manager.initial(self.__component_model.component_info)
        await self.__config_manager.initial(self.__component_model.component_info)
        await self.__data_sender_manager.initial(self.__component_model.component_info)
        await self.__receiver_manager.initial(self.__component_model.component_info)

        await self.__rpc_controller.initial(self.__component_model.component_info)
        await self.__external_trigger_controller.initial(self.__component_model.component_info)
        await self.__command_controller.initial(self.__component_model.component_info)

        # 注册应用退出响应事件
        self.__event_manager.subscribe(event_name=CollectorEventEnum.APPLICATION_EXIT.value, callback=self.exit)

        # 设置停止事件
        self.__finish_event.clear()

    async def run(self) -> None:
        # 启动各个服务组件
        try:
            await self.__data_sender_manager.startup()
            await self.__receiver_manager.startup()
            await self.__business_manager.startup()
            # 启动控制组件
            await self.__rpc_controller.startup()
            await self.__external_trigger_controller.startup()
            await self.__command_controller.startup()

            await self.__component_framework.update_component_status(ComponentStatusEnum.RUNNING)
            await self.__finish_event.wait()
        except CollectorException as e:
            self.__logger.exception(e)
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def exit(self) -> None:
        self.__logger.info("收到Application exit请求")
        try:
            await self.__command_controller.shutdown()
            await self.__external_trigger_controller.shutdown()
            await self.__rpc_controller.shutdown()

            await self.__business_manager.shutdown()
            await self.__data_sender_manager.shutdown()
            await self.__receiver_manager.shutdown()
            await self.__component_framework.update_component_status(ComponentStatusEnum.STOP)
        except CollectorException as e:
            self.__logger.exception(e)
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

        # 允许程序结束执行
        self.__finish_event.set()

    def get_component_model(self) -> ComponentModel:
        return self.__component_model
