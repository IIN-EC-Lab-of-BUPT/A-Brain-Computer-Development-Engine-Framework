import asyncio
import os
import uuid
from typing import Union, Optional
import yaml
import logging
import logging.config
from ApplicationFramework.api.model.ComponentEnum import ComponentStatusEnum
from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ApplicationFramework.common.utils.ContextManager import ContextManager
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Stimulator.Paradigm.interface.ProxyInterface import ProxyInterface
from Stimulator.Paradigm.ssvep.config.ssvep_config import SSVEPConfig
from Stimulator.api.exception.StimulationSystemException import StimulationSystemException
from Stimulator.application.ui import register_subject
from Stimulator.control.CommandController import CommandController
from Stimulator.control.FeedbackConntroller import FeedbackController
from Stimulator.control.RandomNumberSeedsController import RandomNumberSeedsController
from Stimulator.control.interface.ControllerInterface import CommandControllerInterface, \
    FeedbackControllerInterface, RandomNumberSeedsControllerInterface
from Stimulator.facade.GrpcConnect import GrpcConnector
from Stimulator.facade.interface.TriggerSystemInterface import GrpcConnectInterface
from Stimulator.service.BusinessManager import BusinessManager
from Stimulator.service.ConfigManager import ConfigManager
from Stimulator.service.ParadigmManager import ParadigmManager
from Stimulator.service.TriggerManager import TriggerManager
from Stimulator.service.interface.ServiceManagerInterface import BusinessManagerInterface, \
    ConfigManagerInterface, ParadigmManagerInterface, TriggerManagerInterface


class ApplicationImplement(ApplicationInterface):
    def __init__(self):
        super().__init__()
        self.__component_model = None
        self._context_manager: ContextManager = ContextManager()
        self.__random_number_seeds_controller: Optional[RandomNumberSeedsControllerInterface] = None
        self.__business_manager: Optional[BusinessManagerInterface] = None
        self.__config_manager: Optional[ConfigManagerInterface] = None
        self.__paradigm_manager: Optional[ParadigmManagerInterface] = None
        self.__trigger_manager: Optional[TriggerManagerInterface] = None
        self.__command_controller: Optional[CommandControllerInterface] = None
        self.__feedback_controller: Optional[FeedbackControllerInterface] = None
        self.__component_framework: Optional[ComponentFrameworkInterface] = None

        self.__component_info: Optional[dict[str, Union[str, dict]]] = None
        self.__config_dict: Optional[dict[str, Union[str, dict]]] = None
        self.__finish_event: asyncio.Event = asyncio.Event()
        self.__logger = logging.getLogger("stimulatorLogger")

    async def initial(self) -> None:
        # 加载日志配置文件
        current_file_path = os.path.abspath(__file__)
        log_config_file_directory_path = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), 'config')
        log_config_file_path = os.path.join(log_config_file_directory_path, 'LoggingConfig.yml')
        with open(log_config_file_path, 'r', encoding='utf-8') as logging_file:
            logging_config = yaml.safe_load(logging_file)

        # 应用配置到logging模块
        logging.config.dictConfig(logging_config)
        self.__logger.info("系统开始初始化")
        # 应用初始化
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        application_config_file_name = 'ApplicationImplement.yml'
        application_config_path = os.path.join(directory_path, application_config_file_name)
        with open(application_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)
        self.__component_info = self.__config_dict.get("component_info", dict())
        # 组件ID遵循如下规则：
        # 1.如果在配置文件中写入，则优先使用配置文件定义的ID
        # 2.如果配置文件中未写入，则检查环境变量中COMPONENT_ID字段，如果存在则使用环境变量中定义的ID
        # 3.如果环境变量中未找到COMPONENT_ID字段，则根据component_type字段自动生成component_type+随机uuid作为component_id
        component_type = self.__component_info.get('component_type', "")
        component_id = self.__component_info.get('component_id') \
            if self.__component_info.get('component_id', None) is not None else \
            (
                os.environ.get('COMPONENT_ID') if os.environ.get('COMPONENT_ID', None) is not None else
                component_type + '_' + str(uuid.uuid4())
            )
        self.__component_model = ComponentModel(
            component_id=component_id,
            component_type=component_type,
            component_info=self.__component_info
        )
        self.__component_info['component_id'] = component_id
        # 应用上下文封装
        self._context_manager.bind_class(clazz=GrpcConnectInterface, to_target=GrpcConnector)
        self._context_manager.bind_class(clazz=BusinessManagerInterface, to_target=BusinessManager)
        self._context_manager.bind_class(clazz=ProxyInterface, to_target=BusinessManager)
        self._context_manager.bind_class(clazz=ParadigmManagerInterface, to_target=ParadigmManager)
        self._context_manager.bind_class(clazz=TriggerManagerInterface, to_target=TriggerManager)

        self._context_manager.bind_class(clazz=CommandControllerInterface, to_target=CommandController)
        self._context_manager.bind_class(clazz=FeedbackControllerInterface, to_target=FeedbackController)
        self._context_manager.bind_class(clazz=RandomNumberSeedsControllerInterface,
                                         to_target=RandomNumberSeedsController)
        self._context_manager.bind_class(clazz=ConfigManagerInterface, to_target=ConfigManager)
        # 获取各个服务组件实例
        self.__component_framework: ComponentFrameworkInterface = self._context_manager.get_instance(
            ComponentFrameworkInterface)
        self.__business_manager: BusinessManagerInterface = self._context_manager.get_instance(BusinessManagerInterface)
        self.__config_manager: ConfigManagerInterface = self._context_manager.get_instance(ConfigManagerInterface)
        self.__paradigm_manager: ParadigmManagerInterface = self._context_manager.get_instance(ParadigmManagerInterface)
        self.__trigger_manager: TriggerManagerInterface = self._context_manager.get_instance(TriggerManagerInterface)
        self.__command_controller: CommandControllerInterface = self._context_manager.get_instance(
            CommandControllerInterface)
        self.__feedback_controller: FeedbackControllerInterface = self._context_manager.get_instance(
            FeedbackControllerInterface)
        self.__random_number_seeds_controller: RandomNumberSeedsControllerInterface = \
            (self._context_manager.get_instance(RandomNumberSeedsControllerInterface))

        # 补充构建服务组件
        self.__business_manager.set_paradigm_manager(self.__paradigm_manager)
        self.__business_manager.set_trigger_manager(self.__trigger_manager)

        # 初始化各个服务组件
        await self.__business_manager.initial(self.__component_info)
        await self.__config_manager.initial(self.__component_info)
        await self.__paradigm_manager.initial(self.__component_info)
        await self.__trigger_manager.initial(self.__component_info)

        await self.__command_controller.initial(self.__component_info)
        await self.__feedback_controller.initial(self.__component_info)
        await self.__random_number_seeds_controller.initial(self.__component_info)

        # 设置停止事件
        self.__finish_event.clear()
        self.__logger.info("系统初始化完成")

    async def run(self) -> None:
        try:
            self.__logger.info("系统开始启动")
            subject_id = register_subject()
            component_model = await self.__component_framework.get_component_model()
            self.__component_info = component_model.component_info
            self.__component_info['subject_id'] = subject_id
            self.__component_info['trigger_target'] = SSVEPConfig.TRIGGER_TARGET
            self.__component_info['stim_target'] = SSVEPConfig.STIM_TARGET
            self.__component_info['block_number'] = SSVEPConfig.BLOCK_NUMBER
            self.__component_info['trial_number'] = SSVEPConfig.TRIAL_NUMBER
            await self.__component_framework.update_component_info(self.__component_info,
                                                                   self.__component_model.component_id)
            await asyncio.gather(self.__config_manager.update(self.__component_info))
            # 启动各个服务组件
            await asyncio.gather(self.__paradigm_manager.startup(), self.__trigger_manager.startup())
            await self.__business_manager.startup()
            await self.__config_manager.startup()

            # 启动控制组件
            await asyncio.gather(self.__random_number_seeds_controller.startup())
            await self.__feedback_controller.startup()
            await self.__command_controller.startup()

            await self.__component_framework.update_component_status(ComponentStatusEnum.RUNNING)
            self.__logger.info("系统启动完成")
            await self.__finish_event.wait()

        except StimulationSystemException as e:
            self.__logger.exception(e)
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

    async def exit(self) -> None:
        self.__logger.info("收到Application exit请求")
        try:
            await self.__random_number_seeds_controller.shutdown()
            await self.__feedback_controller.shutdown()
            await self.__command_controller.shutdown()

            await self.__business_manager.shutdown()
            await self.__paradigm_manager.shutdown()
            await self.__trigger_manager.shutdown()
            await self.__config_manager.shutdown()

            await self.__component_framework.update_component_status(ComponentStatusEnum.STOP)
            self.__finish_event.set()

        except StimulationSystemException as e:
            self.__logger.exception(e)
            await self.__component_framework.update_component_status(ComponentStatusEnum.ERROR)

    def get_component_model(self) -> ComponentModel:
        return self.__component_model
