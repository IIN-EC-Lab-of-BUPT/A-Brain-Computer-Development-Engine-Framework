import logging
import os
from typing import Union

import yaml
from injector import inject

from ApplicationFramework.api.model.ComponentModel import ComponentModel
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from CentralController.common.model.ComponentInformationModel import ComponentInformationModel
from CentralController.common.model.GroupInformationModel import GroupInformationModel

from CentralController.service.interface.ServiceCoordinatorInterface import ServiceCoordinatorInterface


class ServiceCoordinator(ServiceCoordinatorInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        """
        初始化服务协调器
        :param component_framework: 组件框架
        """

        self.__component_framework: ComponentFrameworkInterface = component_framework
        # 预先定义的组件消息配置列表
        self.__static_component_information_model_dict: dict[str, ComponentInformationModel] = {}
        # 预先定义的组件组消息配置列表
        self.__static_group_information_model_dict: dict[str, GroupInformationModel] = {}

        # 运行中配置信息
        # 组件字典
        self.__registered_component_information_model_dict: dict[str, ComponentInformationModel] = {}

        self.__logger = logging.getLogger('centralControllerLogger')

    async def initial(self):
        root_path = os.path.dirname(os.path.dirname(__file__))
        central_controller_config_file_path = os.path.join(root_path, 'config', 'CentralControllerConfig.yml')
        # 加载静态组件配置
        with open(central_controller_config_file_path, 'r', encoding='utf-8') as central_controller_config_file:
            central_controller_config_dict = yaml.safe_load(central_controller_config_file)

        central_controller_config_static_groups_dict = central_controller_config_dict.get('groups', dict())

        # 装载组配置
        for group_id in central_controller_config_static_groups_dict:
            static_group_information_model = GroupInformationModel(
                group_id=group_id,
                group_info=central_controller_config_static_groups_dict[group_id].get('group_info', dict()),
                message_key_topic_dict=central_controller_config_static_groups_dict[group_id].get(
                    'message_key_topic_dict', dict())
            )
            self.__static_group_information_model_dict[group_id] = static_group_information_model

        # 装载组件配置
        central_controller_config_static_components_dict = central_controller_config_dict.get('components', dict())
        for component_id in central_controller_config_static_components_dict:
            self.__static_component_information_model_dict[component_id] = ComponentInformationModel(
                component_id=component_id,
                component_type=central_controller_config_static_components_dict[component_id].get('component_type',
                                                                                                  None),
                component_group_id=central_controller_config_static_components_dict[component_id].get(
                    'component_group_id', None),
                component_info=central_controller_config_static_components_dict[component_id].get('component_info',
                                                                                                  dict()),
                message_key_topic_dict=central_controller_config_static_components_dict[component_id].get(
                    'message_key_topic_dict', dict())
            )

    async def startup(self) -> None:
        registered_component_id_list = await self.__component_framework.get_all_component_id()
        for component_id in registered_component_id_list:
            registered_component_model = await self.__component_framework.get_component_model(component_id)
            component_model = ComponentInformationModel(
                component_id=component_id,
                component_type=registered_component_model.component_type,
                component_info=registered_component_model.component_info
                if registered_component_model.component_info is not None else dict[str, Union[str, dict]](),
                message_key_topic_dict=dict[str, str]())
            self.__registered_component_information_model_dict[component_id] = component_model
            # 根据component_id判断是否在静态组件中
            if component_id in self.__static_component_information_model_dict:
                static_component_information_model = self.__static_component_information_model_dict[component_id]
                component_model.component_group_id = static_component_information_model.component_group_id \
                    if static_component_information_model.component_group_id is not None \
                    else component_model.component_group_id
                component_model.message_key_topic_dict.update(static_component_information_model.message_key_topic_dict)
                # 更新组件配置
                # component_model.component_info.update(static_component_information_model.component_info)
                if static_component_information_model.component_info is not None:
                    component_model.component_info.update(static_component_information_model.component_info)
                await self.__component_framework.update_component_info(component_model.component_info, component_id)

    async def shutdown(self) -> None:
        self.__registered_component_information_model_dict.clear()

    async def on_register_component(self, component_model: ComponentModel) -> ComponentModel:
        component_id = component_model.component_id
        component_type = component_model.component_type
        component_info = component_model.component_info

        # 先判断component_id是否已经在组件组中
        if component_id in self.__registered_component_information_model_dict:
            return self.__registered_component_information_model_dict.get(component_id, component_model)
        else:
            component_information_model = ComponentInformationModel(
                component_id=component_id,
                component_type=component_type,
                component_info=component_info if component_info is not None else dict[str, Union[str, dict]](),
                message_key_topic_dict=dict[str, str]())
            self.__registered_component_information_model_dict[component_id] = component_information_model

        # 根据component_id判断是否在静态组件中
        if component_id in self.__static_component_information_model_dict:
            static_component_information_model = self.__static_component_information_model_dict[component_id]
            component_information_model.component_group_id = static_component_information_model.component_group_id \
                if static_component_information_model.component_group_id is not None \
                else component_information_model.component_group_id
            component_information_model.message_key_topic_dict.update(
                static_component_information_model.message_key_topic_dict)
            # 更新组件配置
            # component_information_model.component_info.update(static_component_information_model.component_info)
            # component_model.component_info.update(component_information_model.component_info)
            if static_component_information_model.component_info is not None:
                component_information_model.component_info.update(static_component_information_model.component_info)
            if component_model.component_info is None:
                component_model.component_info = dict[str, Union[str, dict]]()
            component_model.component_info.update(component_information_model.component_info)

        self.__logger.info(f"{component_id}组件注册成功")
        self.__logger.debug(f"{component_model}")
        return component_model

    async def on_unregister_component(self, component_model: ComponentModel) -> None:
        self.__registered_component_information_model_dict.pop(component_model.component_id, None)
        self.__logger.info(f"{component_model.component_id}组件注销成功")

    async def on_bind_message(self, message_binding_model: MessageBindingModel) -> MessageBindingModel:
        component_id = message_binding_model.component_id
        message_key = message_binding_model.message_key
        topic = message_binding_model.topic
        if component_id in self.__registered_component_information_model_dict:
            new_topic = self.__registered_component_information_model_dict[component_id].message_key_topic_dict.get(
                message_key, topic)
        else:
            new_topic = topic
        new_message_binding_model = MessageBindingModel(
            component_id=component_id,
            message_key=message_key,
            topic=new_topic
        )
        self.__logger.info(f"绑定消息成功:{new_message_binding_model}")
        return new_message_binding_model

    def get_registered_component_information_model_dict(self) -> dict[str, ComponentInformationModel]:
        return self.__registered_component_information_model_dict

    def get_static_group_information_model_dict(self) -> dict[str, GroupInformationModel]:
        return self.__static_group_information_model_dict
