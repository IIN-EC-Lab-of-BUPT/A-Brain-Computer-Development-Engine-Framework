from google.protobuf.message import Message

from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Collector.api.protobuf.ExternalTriggerService_pb2 import ExternalTriggerMessage as ExternalTriggerMessage_pb2


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class ExternalTriggerMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            ExternalTriggerMessage_pb2: cls.__external_trigger_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            ExternalTriggerModel: cls.__external_trigger_model_to_message_pb
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> ExternalTriggerModel:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: ExternalTriggerModel) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __external_trigger_message_to_model(
            cls,
            external_trigger_message: ExternalTriggerMessage_pb2) -> ExternalTriggerModel:
        return ExternalTriggerModel(
            timestamp=external_trigger_message.timestamp,
            trigger=external_trigger_message.trigger
        )

    """
    model到package转换函数
    """

    @classmethod
    def __external_trigger_model_to_message_pb(cls, external_trigger_model: ExternalTriggerModel) \
            -> ExternalTriggerMessage_pb2:
        return ExternalTriggerMessage_pb2(
            timestamp=external_trigger_model.timestamp,
            trigger=external_trigger_model.trigger
        )
