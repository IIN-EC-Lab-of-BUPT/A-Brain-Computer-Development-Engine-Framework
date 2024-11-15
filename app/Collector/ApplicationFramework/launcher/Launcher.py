import asyncio
import importlib
import os
import sys
from typing import Union
import logging
import logging.config
import yaml
from injector import Provider, Injector, T

from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ApplicationFramework.common.utils.ContextManager import ContextManager
from ApplicationFramework.facade.ComponentFrameworkImplement import ComponentFrameworkImplement
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface, \
    ComponentFrameworkInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import \
    RequestApplicationExitOperatorInterface


class Launcher:
    def __init__(self):
        self.__context_manager: ContextManager = ContextManager()
        self.__component_framework: ComponentFrameworkApplicationInterface = None
        self.__application: ApplicationInterface = None
        self.__component_id: str = None
        self.__root_path: str = None
        self.__logger: logging.Logger = None

        self.__daemon_address: str = None
        self.__daemon_port: int = None

        self.__application_task: asyncio.Task = None

    async def initial(self):
        # 根目录为当前文件路径上级目录的上级目录
        self.__root_path = os.path.dirname(os.path.dirname(__file__))
        logging_config_file_path = os.path.join(self.__root_path, 'config', 'LoggingConfig.yml')
        with open(logging_config_file_path, 'r', encoding='utf-8') as logging_file:
            logging_config = yaml.safe_load(logging_file)
        # 应用配置到logging模块
        logging.config.dictConfig(logging_config)
        self.__logger = logging.getLogger('componentLogger')
        # 创建component_framework并封装context
        self.__create_context_manager()
        self.__component_framework = self.__context_manager.get_instance(ComponentFrameworkApplicationInterface)
        # 写入配置信息
        self.__component_framework.set_component_startup_configuration(
            daemon_address=self.__daemon_address,
            daemon_port=self.__daemon_port,
        )
        # 初始化组件框架
        await self.__component_framework.initial()
        # 初始化application
        # 获取当前脚本所在的目录
        launcher_config_file_path = os.path.join(self.__root_path, 'config', 'LauncherConfig.yml')
        with open(launcher_config_file_path, 'r', encoding='utf-8') as f:
            launcher_config_dict: dict = yaml.safe_load(f)
        # 构建当前应用实例
        self.__application = self.__load_application(launcher_config_dict)
        self.__application.set_context_manager(self.__context_manager)
        # 初始化应用实例
        await self.__application.initial()

    async def startup(self):
        # 启动组件框架
        await self.__component_framework.startup()

        # 创建应用退出回调监听
        class RequestApplicationExitOperator(RequestApplicationExitOperatorInterface):
            def __init__(self, application: ApplicationInterface):
                self.__application = application
                self.__logger = logging.getLogger('componentLogger')

            async def on_request_application_exit(self) -> None:
                try:
                    await self.__application.exit()
                except Exception as e:
                    self.__logger.exception(f"组件关闭发生异常:{e}")

        await self.__component_framework.add_listener_on_request_application_exit(
            RequestApplicationExitOperator(self.__application))

        # 注册组件
        component_model = self.__application.get_component_model()
        try:
            await self.__component_framework.register_component(component_model)
            # 启动application,直到应用运行结束
            self.__application_task = asyncio.create_task(self.__application.run())
            await self.__application_task
        except Exception as e:
            self.__logger.exception(f"组件注册运行发生异常:{e}")

    async def shutdown(self):
        # application自行关闭
        try:
            # 注销组件
            await self.__component_framework.unregister_component()
        except Exception as e:
            self.__logger.exception(f"组件注销发生异常:{e}")
        finally:
            # 关闭组件框架
            await self.__component_framework.shutdown()

    async def __aenter__(self):
        await self.initial()
        await self.startup()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()

    def configure(self, ip: str, port: int):
        self.__daemon_address = ip
        self.__daemon_port = port

    @staticmethod
    def __load_application(initial_config_dict: dict[str, Union[str, dict]]) -> ApplicationInterface:
        workspace_path = os.getcwd()
        application_dict = initial_config_dict['application']
        application_class_file = application_dict['application_class_file']
        application_class_name = application_dict['application_class_name']
        absolute_application_class_file = os.path.join(workspace_path, application_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_application_class_file))[0]
        # 获取模块所在的目录
        module_dir = os.path.dirname(absolute_application_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        application_class = getattr(module, application_class_name)
        application_obj = application_class()
        return application_obj

    def __create_context_manager(self):

        class ComponentFrameworkProvider(Provider):
            instance: ComponentFrameworkImplement = None

            @classmethod
            def get(cls, injector: Injector) -> T:
                if cls.instance is None:
                    cls.instance = ComponentFrameworkImplement()
                return cls.instance

        self.__context_manager.bind_class(ComponentFrameworkApplicationInterface, ComponentFrameworkProvider())
        self.__context_manager.bind_class(ComponentFrameworkInterface, ComponentFrameworkProvider())
