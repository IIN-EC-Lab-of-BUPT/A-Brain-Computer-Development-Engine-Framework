from typing import Union

from google.protobuf.message import Message

from Collector.receiver.virtual_receiver.api.proto.VirtualReceiverCustomControl_pb2 import (
    VirtualReceiverCustomControlMessage as VirtualReceiverCustomControlMessage_pb2,
)

from Collector.receiver.virtual_receiver.api.model.VirtualReceiverCustomControlModel import \
    VirtualReceiverCustomControlModel
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import InformationPackageModel


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class VirtualReceiverCustomControlMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            VirtualReceiverCustomControlMessage_pb2: cls.__virtual_receiver_custom_control_message_to_model,
        }

        cls.__model_class_for_convert_func_dict = {
            VirtualReceiverCustomControlModel: cls.__virtual_receiver_custom_control_model_to_message_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        VirtualReceiverCustomControlModel,
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[VirtualReceiverCustomControlMessage_pb2]
                          ) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __virtual_receiver_custom_control_message_to_model(
            cls, virtual_receiver_custom_control_message: VirtualReceiverCustomControlMessage_pb2) -> (
            VirtualReceiverCustomControlModel):
        return VirtualReceiverCustomControlModel(
            package=CommonMessageConverter.protobuf_to_model(
                virtual_receiver_custom_control_message.virtualReceiverStartSendingPointMessage)
            if virtual_receiver_custom_control_message.WhichOneof(
                'package') == "virtualReceiverStartSendingPointMessage" else
            None
        )

    """
    model到package转换函数
    """
    @classmethod
    def __virtual_receiver_custom_control_model_to_message_pb(
            cls,
            virtual_receiver_custom_control_model: VirtualReceiverCustomControlModel
    ) -> VirtualReceiverCustomControlMessage_pb2:
        package = virtual_receiver_custom_control_model.package
        if isinstance(package, InformationPackageModel):
            return VirtualReceiverCustomControlMessage_pb2(
                virtualReceiverStartSendingPointMessage=CommonMessageConverter.model_to_protobuf(
                    virtual_receiver_custom_control_model.package)
            )
