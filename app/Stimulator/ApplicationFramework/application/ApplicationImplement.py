import asyncio
import logging
import logging.config
import os
import uuid
from typing import Union

import yaml

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from ApplicationFramework.application.interface.ApplicationInterface import ApplicationInterface
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkApplicationInterface
from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface, \
    UpdateConfigOperatorInterface


class ApplicationImplement(ApplicationInterface):

    def __init__(self):
        super().__init__()
        self.__component_model: ComponentModel = None
        self.__component_info: dict[str, Union[str, dict]] = None
        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__finish_event: asyncio.Event = asyncio.Event()    # 允许应用退出标识

    def initial(self) -> None:
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
        # 设置停止事件
        self.__finish_event.clear()

    async def run(self) -> None:
        component_framework: ComponentFrameworkApplicationInterface = \
            self._context_manager.get_instance(ComponentFrameworkApplicationInterface)

        # 测试消息绑定及订阅
        class ReceiveMessageCallback(ReceiveMessageOperatorInterface):
            async def receive_message(self, data: bytes) -> None:
                print(str(data))

        source_dict = self.__config_dict.get("sources", list())
        for source_name in source_dict:
            await component_framework.bind_message(
                MessageBindingModel(
                    message_key=source_name,
                    topic=source_dict.get(source_name)
                )
            )
            await component_framework.subscribe_message(source_name, ReceiveMessageCallback())

        # 测试消息发送
        await component_framework.bind_message(
            MessageBindingModel(
                message_key='send_message_key',
                topic='send_message_topic'
            )
        )
        await component_framework.send_message("test_message_key", b"test_message")

        # 测试配置更新订阅
        class UpdateConfigCallback(UpdateConfigOperatorInterface):
            async def on_update_config(self, config_dict: dict[str, Union[str, dict]]) -> None:
                print(config_dict)

        await component_framework.add_listener_on_update_component_info(UpdateConfigCallback())
        # 测试组件配置拉取
        print(component_framework.get_component_model())
        # 测试组件配置更新
        await component_framework.update_component_info({"test_key": "test_value"})
        # 测试全局配置订阅
        await component_framework.add_listener_on_update_global_config(UpdateConfigCallback())
        # 测试全局配置拉取
        print(component_framework.get_global_config())
        # 测试全局配置更新
        await component_framework.update_global_config({"test_key": "test_value"})

        # 等待允许应用退出指令
        await self.__finish_event.wait()

    async def exit(self) -> None:
        # 允许应用退出
        self.__finish_event.set()

    def get_component_model(self) -> ComponentModel:
        return self.__component_model
