from typing import Union

import yaml
from google.protobuf.message import Message

from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusModel, ComponentGroupStatusListModel
from CentralController.api.model.GroupModel import GroupModel, GroupListModel
from CentralController.api.proto.CentralManagementControlService_pb2 import (
    GroupMessage as GroupMessage_pb2,
    GroupListMessage as GroupListMessage_pb2,
    ComponentGroupStatusMessage as ComponentGroupStatusMessage_pb2,
    ComponentGroupStatusListMessage as ComponentGroupStatusListMessage_pb2
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class CentralManagementControlServiceMessageConverter:

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            GroupMessage_pb2: cls.__group_message_to_model,
            GroupListMessage_pb2: cls.__group_list_message_to_model,
            ComponentGroupStatusMessage_pb2: cls.__component_group_status_message_to_model,
            ComponentGroupStatusListMessage_pb2: cls.__component_group_status_list_message_to_model
        }
        cls.__model_class_for_convert_func_dict = {
            GroupModel: cls.__group_model_to_package_pb,
            GroupListModel: cls.__group_list_model_to_package_pb,
            ComponentGroupStatusModel: cls.__component_group_status_model_to_package_pb,
            ComponentGroupStatusListModel: cls.__component_group_status_list_model_to_package_pb
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        GroupModel,
        GroupListModel,
        ComponentGroupStatusModel,
        ComponentGroupStatusListModel
    ]:
        return cls.__package_name_for_convert_func_dict[type(pb_message)](pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[
        GroupModel,
        GroupListModel,
        ComponentGroupStatusModel,
        ComponentGroupStatusListModel
    ]) -> Message:
        return cls.__model_class_for_convert_func_dict[type(model)](model)

    @classmethod
    def __group_message_to_model(cls, proto_msg: GroupMessage_pb2) -> GroupModel:
        return GroupModel(
            group_id=proto_msg.groupId,
            group_info=yaml.safe_load(proto_msg.groupInfo)
        )

    @classmethod
    def __group_list_message_to_model(cls, proto_msg: GroupListMessage_pb2) -> GroupListModel:
        return GroupListModel(
            group_list=[cls.__group_message_to_model(group_message) for group_message in proto_msg.groupList]
        )

    @classmethod
    def __component_group_status_message_to_model(cls, proto_msg: ComponentGroupStatusMessage_pb2) \
            -> ComponentGroupStatusModel:
        return ComponentGroupStatusModel(
            component_id=proto_msg.componentId,
            component_type=proto_msg.componentType,
            component_info=yaml.safe_load(proto_msg.componentInfo),
            component_group_id=proto_msg.componentGroupId,
            component_status=proto_msg.componentStatus,
        )

    @classmethod
    def __component_group_status_list_message_to_model(
            cls, proto_msg: ComponentGroupStatusListMessage_pb2) -> ComponentGroupStatusListModel:
        return ComponentGroupStatusListModel(
            component_group_status_list=[cls.__component_group_status_message_to_model(component_group_status)
                                         for component_group_status in proto_msg.componentGroupStatusList]
        )

    # 模型转换消息

    @classmethod
    def __group_model_to_package_pb(cls, group_model: GroupModel) -> GroupMessage_pb2:
        return GroupMessage_pb2(
            groupId=group_model.group_id,
            groupInfo=yaml.safe_dump(group_model.group_info)
        )

    @classmethod
    def __group_list_model_to_package_pb(cls, group_list_model: GroupListModel) -> GroupListMessage_pb2:
        return GroupListMessage_pb2(
            groupList=[cls.__group_model_to_package_pb(group_model) for group_model in group_list_model.group_list]
        )

    @classmethod
    def __component_group_status_model_to_package_pb(cls, component_group_status_model: ComponentGroupStatusModel) \
            -> ComponentGroupStatusMessage_pb2:
        return ComponentGroupStatusMessage_pb2(
            componentId=component_group_status_model.component_id,
            componentType=component_group_status_model.component_type,
            componentInfo=yaml.safe_dump(component_group_status_model.component_info),
            componentGroupId=component_group_status_model.component_group_id,
            componentStatus=component_group_status_model.component_status
        )

    @classmethod
    def __component_group_status_list_model_to_package_pb(
            cls, component_group_status_list_model: ComponentGroupStatusListModel) \
            -> ComponentGroupStatusListMessage_pb2:
        return ComponentGroupStatusListMessage_pb2(
            componentGroupStatusList=[cls.__component_group_status_model_to_package_pb(component_group_status_model)
                                      for component_group_status_model in
                                      component_group_status_list_model.component_group_status_list]
        )
