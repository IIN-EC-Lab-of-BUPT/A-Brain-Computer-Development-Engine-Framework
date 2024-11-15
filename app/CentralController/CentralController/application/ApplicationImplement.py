import asyncio
import logging
import logging.config
import multiprocessing
import os
import uuid
from typing import Union

import yaml
from injector import Provider, Injector, T

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import BindMessageOperatorInterface, \
    RegisterComponentOperatorInterface, UnRegisterComponentOperatorInterface
from CentralController.api.exception.CentralControllerException import CentralControllerException
from CentralController.common.enum.CentralControllerEventEnum import CentralControllerEventEnum
from CentralController.common.utils.EventManager import EventManager
from CentralController.control.RPCController import RPCController
from CentralController.control.interface.ControllerInterface import RPCControllerInterface
from CentralController.facade.CollectorConnector import CollectorConnector
from CentralController.facade.DataStorageConnector import DataStorageConnector
from CentralController.facade.DatabaseConnector import DatabaseConnector
from CentralController.facade.ProcessorConnector import ProcessorConnector
from CentralController.facade.StimulatorConnector import StimulatorConnector
from CentralController.facade.interface.SubsystemConnectorInterface import CollectorConnectorInterface, \
    ProcessorConnectorInterface, StimulatorConnectorInterface, DataStorageConnectorInterface, DatabaseConnectorInterface
from CentralController.service.ComponentMonitor import ComponentMonitor
from CentralController.service.ProcessManager import ProcessManager
from CentralController.service.ServiceCoordinator import ServiceCoordinator
from CentralController.service.interface.ComponentMonitorInterface import ComponentMonitorInterface
from CentralController.service.interface.ProcessManagerInterface import ProcessManagerApplicationInterface, \
    ProcessManagerInterface
from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface
from CentralControllerView import ViewMain
from componentframework.api.Enum.ComponentStatusEnum import ComponentStatusEnum


class ApplicationImplement(ApplicationInterface):

    def __init__(self):
        super().__init__()
        self.__finish_event: asyncio.Event = asyncio.Event()
        self.__logger = logging.getLogger("centralControllerLogger")
        self.__component_model: ComponentModel = None
        self.__config_dict: dict[str, Union[str, dict]] = None

        # self._component_id: str = None  可以调用通过接口注入的组件ID

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

        class ProcessManagerProvider(Provider):
            instance: ProcessManager = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = ProcessManager(
                        injector.get(ComponentFrameworkInterface),
                        injector.get(ServiceCoordinatorInterface),
                        injector.get(CollectorConnectorInterface),
                        injector.get(ProcessorConnectorInterface),
                        injector.get(StimulatorConnectorInterface),
                        injector.get(DataStorageConnectorInterface),
                        injector.get(DatabaseConnectorInterface),
                    )
                return cls.instance

        self._context_manager.bind_class(clazz=EventManager, to_target=EventManager)
        self._context_manager.bind_class(CollectorConnectorInterface, to_target=CollectorConnector)
        self._context_manager.bind_class(ProcessorConnectorInterface, to_target=ProcessorConnector)
        self._context_manager.bind_class(StimulatorConnectorInterface, to_target=StimulatorConnector)
        self._context_manager.bind_class(DataStorageConnectorInterface, to_target=DataStorageConnector)
        self._context_manager.bind_class(DatabaseConnectorInterface, to_target=DatabaseConnector)

        self._context_manager.bind_class(ServiceCoordinatorInterface, to_target=ServiceCoordinator)
        self._context_manager.bind_class(ProcessManagerApplicationInterface, to_target=ProcessManagerProvider())
        self._context_manager.bind_class(ProcessManagerInterface, to_target=ProcessManagerProvider())
        self._context_manager.bind_class(ComponentMonitorInterface, to_target=ComponentMonitor)

        self._context_manager.bind_class(RPCControllerInterface, to_target=RPCController)

        event_manager: EventManager = self._context_manager.get_instance(EventManager)
        # 应用上下文封装
        service_coordinator: ServiceCoordinatorInterface = \
            self._context_manager.get_instance(ServiceCoordinatorInterface)
        process_manager: ProcessManagerInterface = \
            self._context_manager.get_instance(ProcessManagerApplicationInterface)
        rpc_controller: RPCControllerInterface = \
            self._context_manager.get_instance(RPCControllerInterface)
        processor_connector: ProcessorConnectorInterface \
            = self._context_manager.get_instance(ProcessorConnectorInterface)

        await processor_connector.initial()
        await service_coordinator.initial()
        await process_manager.initial()
        await rpc_controller.initial(self.__component_model.component_info)
        # 设置停止事件
        self.__finish_event.clear()

        # 注册应用退出响应事件
        event_manager.subscribe(event_name=CentralControllerEventEnum.APPLICATION_EXIT.value, callback=self.exit)

    async def run(self) -> None:

        component_framework: ComponentFrameworkInterface = \
            self._context_manager.get_instance(ComponentFrameworkInterface)

        process_manager: ProcessManagerInterface = \
            self._context_manager.get_instance(ProcessManagerInterface)

        service_coordinator: ServiceCoordinatorInterface = \
            self._context_manager.get_instance(ServiceCoordinatorInterface)

        rpc_controller: RPCControllerInterface = \
            self._context_manager.get_instance(RPCControllerInterface)

        processor_connector: ProcessorConnectorInterface \
            = self._context_manager.get_instance(ProcessorConnectorInterface)

        # 指令绑定
        class BindMessageOperator(BindMessageOperatorInterface):
            def __init__(self):
                self.__logger = logging.getLogger('centralControllerLogger')

            async def on_bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
                self.__logger.debug(f"收到消息绑定请求，来自"
                                    f"{message_binding_model.component_id}组件的{message_binding_model.message_key}消息")
                return await service_coordinator.on_bind_message(message_binding_model)

        class RegisterComponentOperator(RegisterComponentOperatorInterface):
            def __init__(self):
                self.__logger = logging.getLogger('centralControllerLogger')

            async def on_register_component(self, component_model: ComponentModel) -> ComponentModel:
                self.__logger.debug(f"收到组件注册请求，{component_model.component_id}组件注册")
                return await service_coordinator.on_register_component(component_model)

        class UnRegisterComponentOperator(UnRegisterComponentOperatorInterface):
            def __init__(self):
                self.__logger = logging.getLogger('centralControllerLogger')

            async def on_unregister_component(self, component_model: ComponentModel) -> None:
                self.__logger.debug(f"收到组件注销请求，{component_model.component_id}组件注销")
                await service_coordinator.on_unregister_component(component_model)

        try:

            await component_framework.add_listener_on_bind_message(BindMessageOperator())
            await component_framework.add_listener_on_register_component(RegisterComponentOperator())
            await component_framework.add_listener_on_unregister_component(UnRegisterComponentOperator())

            # 启动服务协调器
            await service_coordinator.startup()

            # 启动处理容器连接器
            await processor_connector.startup()

            # 启动流程管理器
            await process_manager.startup()

            # 启动控制管理器
            await rpc_controller.startup()
            print("系统启动就绪，请开启界面连接模块")
            ui_config = self.__component_model.component_info.get('ui_config', dict())
            ui_auto_start_flag = ui_config.get('auto_start', False)
            if ui_auto_start_flag:
                ui_process = multiprocessing.Process(target=ViewMain.main)
                ui_process.start()

            await component_framework.update_component_status(ComponentStatusEnum.RUNNING)
            await self.__finish_event.wait()

        except CentralControllerException as e:
            self.__logger.exception(e)
            await component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def exit(self) -> None:
        self.__logger.info("收到Application exit请求")
        component_framework: ComponentFrameworkInterface = \
            self._context_manager.get_instance(ComponentFrameworkInterface)
        rpc_controller: RPCControllerInterface = \
            self._context_manager.get_instance(RPCControllerInterface)

        try:
            await component_framework.cancel_listener_on_bind_message()
            await component_framework.cancel_listener_on_register_component()
            await component_framework.cancel_listener_on_unregister_component()

            service_coordinator: ServiceCoordinatorInterface = \
                self._context_manager.get_instance(ServiceCoordinatorInterface)

            # 关闭服务协调器
            await service_coordinator.shutdown()

            # 关闭rpc控制器
            await rpc_controller.shutdown()
            await component_framework.update_component_status(ComponentStatusEnum.STOP)

        except CentralControllerException as e:
            self.__logger.exception(e)
            await component_framework.update_component_status(ComponentStatusEnum.ERROR)
        # 允许程序结束执行
        self.__finish_event.set()

    def get_component_model(self) -> ComponentModel:
        return self.__component_model
