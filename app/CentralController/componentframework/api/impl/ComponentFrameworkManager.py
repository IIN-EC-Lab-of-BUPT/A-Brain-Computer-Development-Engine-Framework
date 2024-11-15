from componentframework.common.decorators.singleton import singleton as singleton1
from componentframework.control.ComponentManagerInterfaceImpl import ComponentManagerInterfaceImpl
from componentframework.control.ConfigManagerInterfaceImpl import ConfigManagerInterfaceImpl
from componentframework.control.ConnectManagerInterfaceImpl import ConnectManagerInterfaceImpl
from componentframework.control.MessageManagerInterfaceImpl import MessageManagerInterfaceImpl
from componentframework.facadeImpl.ComponentManagerFacadeImpl import ComponentManagerFacadeImpl
from componentframework.facadeImpl.ConfigManagerGrpcFacadeImpl import ConfigManagerGrpcFacadeImpl
from componentframework.facadeImpl.ConnectManagerFacadeImpl import ConnectManagerFacadeImpl
from componentframework.facadeImpl.MessageManagerGrpcFacadeImpl import MessageManagerGrpcFacadeImpl
from componentframework.facadeImpl.grpc_connector import GrpcConnector
from componentframework.api.interface.ComponentFrameworkManagerinterface import ComponentFrameworkManagerInterface
from componentframework.api.ComponentManagerInterface import ComponentManagerInterface
from componentframework.api.ConfigManagerInterface import ConfigManagerInterface
from componentframework.api.ConnectManagerInterface import ConnectManagerInterface
from componentframework.api.Enum.StatusEnum import StatusEnum
from componentframework.api.MessageManagerInterface import MessageManagerInterface
from componentframework.api.model.ComponentStartupConfigurationModel import ComponentStartupConfigurationModel, \
    ComponentPatternEnum
from componentframework.service.ComponentManagerService import ComponentManagerService
from componentframework.service.ConfigManagerService import ConfigManagerService
from componentframework.service.ConnectManagerService import ConnectManagerService
from componentframework.service.MessageManagerService import MessageManagerService
from injector import Binder, Injector, singleton


@singleton1
class ComponentFrameworkManager(ComponentFrameworkManagerInterface):
    context: Injector = None

    def __init__(self):
        # self.context = Injector(self.component_framework_manager_initial)
        super().__init__()
        self.connect_manager = None
        self.component_manager = None
        self.message_manager = None
        self.config_manager = None
        self.component_framework_manager_injector = None
        self.grpc_connect_implementation = None

    # @staticmethod
    def __component_framework_manager_initial(self, binder: Binder):
        """创建config_manager, event_manager, message_manager, service_manager, component_manager实体对象，并注入组件框架"""

        # 创建grpc_connect对象
        self.grpc_connect_implementation = GrpcConnector('localhost', 9000)  # server_address
        # self.grpc_connect_implementation.connect()
        # 配置注入
        binder.bind(ConfigManagerService, scope=singleton)
        binder.bind(ConfigManagerGrpcFacadeImpl, scope=singleton)
        binder.bind(MessageManagerService, scope=singleton)
        binder.bind(MessageManagerGrpcFacadeImpl, scope=singleton)
        binder.bind(ComponentManagerService, scope=singleton)
        binder.bind(ComponentManagerFacadeImpl, scope=singleton)
        binder.bind(ConnectManagerService, scope=singleton)
        binder.bind(ConnectManagerFacadeImpl, scope=singleton)
        binder.bind(GrpcConnector, to=self.grpc_connect_implementation, scope=singleton)
        binder.bind(ConfigManagerInterface, to=ConfigManagerInterfaceImpl, scope=singleton)
        binder.bind(MessageManagerInterface, to=MessageManagerInterfaceImpl, scope=singleton)
        binder.bind(ComponentManagerInterface, to=ComponentManagerInterfaceImpl, scope=singleton)
        binder.bind(ConnectManagerInterface, to=ConnectManagerInterfaceImpl, scope=singleton)

    def initial(self) -> None:
        """初始化"""
        # # 加载配置文件
        # logging_config_file_path = os.path.join(os.getcwd(),  'config', 'LoggingConfig.yml')
        # with open(logging_config_file_path, 'r', encoding='utf-8') as logging_file:
        #     logging_config = yaml.safe_load(logging_file)
        #
        # # 应用配置到logging模块
        # logging.config.dictConfig(logging_config)
        self.component_framework_manager_injector = Injector(self.__component_framework_manager_initial)
        self.config_manager = self.component_framework_manager_injector.get(ConfigManagerInterface)
        self.message_manager = self.component_framework_manager_injector.get(MessageManagerInterface)
        self.component_manager = self.component_framework_manager_injector.get(ComponentManagerInterface)
        self.connect_manager = self.component_framework_manager_injector.get(ConnectManagerInterface)
        # self.context = self.component_framework_manager.context
        # return self.component_framework_manager_injector

    async def startup(self, component_startup_configuration: ComponentStartupConfigurationModel) -> StatusEnum:
        """启动"""
        component_startup_configuration = ComponentStartupConfigurationModel(server_address='localhost',
                                                                             server_port=9000,
                                                                             component_pattern=ComponentPatternEnum.CLUSTER_CENTRAL_CONTROL)
        # component_startup_configuration = ComponentStartupConfigurationModel(server_address='localhost',
        #                                                                      server_port=9000,
        #                                                                      component_pattern=ComponentPatternEnum.CLUSTER_NON_CENTRAL_CONTROL)
        # 返回值："启动成功通知"：枚举类型
        # self.grpc_connect_implementation = GrpcConnector(ComponentStartupConfigurationModel.server_address,
        #                                                  ComponentStartupConfigurationModel.server_port)
        # self.component_framework_manager_injector = Injector(self.__component_framework_manager_initial)
        # self.grpc_connect_implementation.set_grpc_connector_address(component_startup_configuration.server_address,
        #                                                             component_startup_configuration.server_port)
        # self.grpc_connect_implementation.connect()
        # self.component_framework_manager_injector.get(ConfigManagerGrpcFacadeImpl).get_stub()
        # self.component_framework_manager_injector.get(MessageManagerGrpcFacadeImpl).get_stub()
        # self.component_framework_manager_injector.get(ComponentManagerFacadeImpl).get_stub()
        # self.component_framework_manager_injector.get(ConnectManagerFacadeImpl).get_stub()
        await self.config_manager.startup(component_startup_configuration)
        await self.message_manager.startup(component_startup_configuration)
        await self.component_manager.startup(component_startup_configuration)
        await self.connect_manager.startup(component_startup_configuration)
        return StatusEnum.SUCCESS

    def get_config_manager(self) -> ConfigManagerInterface:
        return self.config_manager

    def get_message_manager(self) -> MessageManagerInterface:
        return self.message_manager

    def get_component_manager(self) -> ComponentManagerInterface:
        return self.component_manager

    def get_connect_manager(self) -> ConnectManagerInterface:
        return self.connect_manager
