import asyncio
import logging.config
import os
import yaml
from injector import Binder, Injector, singleton, Module
from Algorithm.common.utils.EventManager import EventManager
from Algorithm.control.AlgorithmRPCDataConnectServer import AlgorithmRPCDataConnectServer
from Algorithm.control.AlgorithmRPCServiceControlServer import AlgorithmRPCServiceControlServer
from Algorithm.control.RPCController import RPCController
from Algorithm.method.interface.ProxyInterface import ProxyInterface
from Algorithm.service.BusinessManager import BusinessManager
from Algorithm.service.ConfigManager import ConfigManager
from Algorithm.service.CoreController import CoreController
from Algorithm.service.MethodManager import MethodManager
from Algorithm.service.interface.DataForwarderInterface import DataForwarderInterface
from Algorithm.service.interface.RpcControllerInterface import RpcControllerInterface
from Algorithm.service.interface.ServiceManagerInterface import BusinessManagerInterface, MethodManagerInterface, \
    CoreControllerInterface, ConfigManagerInterface
from Algorithm.api.proto.AlgorithmRPCService_pb2_grpc import AlgorithmRPCDataConnectServicer, \
    AlgorithmRPCServiceControlServicer


class CommonLayerModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(EventManager, to=EventManager, scope=singleton)


class ControlLayerModule(Module):

    def configure(self, binder: Binder) -> None:
        binder.bind(AlgorithmRPCDataConnectServicer, to=AlgorithmRPCDataConnectServer, scope=singleton)
        binder.bind(AlgorithmRPCServiceControlServicer, to=AlgorithmRPCServiceControlServer, scope=singleton)
        binder.bind(RpcControllerInterface, to=RPCController, scope=singleton)


class ServiceLayerModule(Module):

    def configure(self, binder: Binder) -> None:
        business_manager = BusinessManager()
        binder.bind(BusinessManagerInterface, to=business_manager, scope=singleton)
        binder.bind(ProxyInterface, to=business_manager, scope=singleton)
        binder.bind(DataForwarderInterface, to=business_manager, scope=singleton)
        binder.bind(MethodManagerInterface, to=MethodManager, scope=singleton)
        binder.bind(ConfigManagerInterface, to=ConfigManager, scope=singleton)
        binder.bind(CoreControllerInterface, to=CoreController, scope=singleton)


async def startup():
    # 加载配置文件
    algorithm_config_file_path = os.path.join(os.getcwd(), 'Algorithm', 'config', 'AlgorithmConfig.yml')
    logging_config_file_path = os.path.join(os.getcwd(), 'Algorithm', 'config', 'LoggingConfig.yml')
    with open(logging_config_file_path, 'r', encoding='utf-8') as logging_file:
        logging_config = yaml.safe_load(logging_file)

    # 应用配置到logging模块
    logging.config.dictConfig(logging_config)

    # 创建子Injector，指定父Injector
    injector = Injector(
        ControlLayerModule,
        parent=Injector(
            ServiceLayerModule,
            parent=Injector(CommonLayerModule)
        )
    )
    # 外部延迟注入
    rpc_controller = injector.get(RpcControllerInterface)
    core_controller = injector.get(CoreControllerInterface)
    core_controller.set_rpc_controller(rpc_controller)
    business_manager = injector.get(BusinessManagerInterface)
    business_manager.set_rpc_controller(rpc_controller)
    method_manager = injector.get(MethodManagerInterface)
    method_manager.set_rpc_controller(rpc_controller)
    config_manager = injector.get(ConfigManagerInterface)
    config_manager.set_rpc_controller(rpc_controller)
    config_manager.set_config_file_path(algorithm_config_file_path)
    await core_controller.initial_system()


if __name__ == '__main__':
    asyncio.run(startup())
