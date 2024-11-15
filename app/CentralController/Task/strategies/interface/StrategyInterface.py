from abc import abstractmethod, ABC
from typing import Union

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from Task.common.utils.EventManager import EventManager
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, AlgorithmReportMessageModel
from Task.challenge.interface.ChallengeInterface import ChallengeInterface
from Task.facade.interface.RpcControllerInterface import RpcControllerManagementInterface
from Task.service.interface.MessageForwardApplicationInterface import MessageForwardApplicationInterface
from Task.service.interface.ServiceManagerInterface import CoreControllerInterface


class StrategyInterface(ABC):
    def __init__(self):
        # 必须有无参构造函数，通过update_config方法更新配置并处理
        self._name: str = None
        self._message_forwarder: MessageForwardApplicationInterface = None
        self._challenge: ChallengeInterface = None
        self._core_controller: CoreControllerInterface = None
        self._rpc_controller: RpcControllerManagementInterface = None
        self._event_manager: EventManager = None
        self._component_framework: ComponentFrameworkApplicationInterface = None
    @abstractmethod
    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) \
            -> Union[AlgorithmDataMessageModel, None]:
        # 需要针对algorithm_data_message_model中不同来源，不同类型的数据包(DevicePackageModel,EventPackageModel
        # DataPackageModel,ImpedancePackageModel，InformationPackageModel，ControlpackageModel)进行预处理
        pass

    @abstractmethod
    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        pass

    async def trigger_timeout_notification(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        pass

    @abstractmethod
    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        # 初始化配置信息
        pass

    @abstractmethod
    async def update(self, config_dict: dict[str, dict[str, Union[str, dict]]]) -> None:
        # 配置更新处理
        pass

    @abstractmethod
    async def startup(self) -> None:
        # 策略启动时调用
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        # 策略关闭时调用
        pass

    async def set_challenge(self, challenge: ChallengeInterface) -> None:
        # 设置当前策略所属的赛题
        self._challenge = challenge

    def set_message_forwarder(self, message_forwarder: MessageForwardApplicationInterface) -> None:
        # 设置消息转发器
        self._message_forwarder = message_forwarder

    def set_core_controller(self, core_controller: CoreControllerInterface) -> None:
        # 设置任务系统控制操作器
        self._core_controller = core_controller

    def set_rpc_controller(self, rpc_controller: RpcControllerManagementInterface) -> None:
        # 设置rpc控制器
        self._rpc_controller = rpc_controller

    def set_event_manager(self, event_manager: EventManager) -> None:
        # 设置事件管理器
        self._event_manager = event_manager

    def set_component_framework(self, component_framework: ComponentFrameworkApplicationInterface) -> None:
        # 设置组件框架
        self._component_framework = component_framework
