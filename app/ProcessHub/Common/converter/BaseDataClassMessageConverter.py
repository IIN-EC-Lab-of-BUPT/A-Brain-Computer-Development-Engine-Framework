from typing import Union

from google.protobuf.message import Message
from Common.model.BaseDataClassModel import BooleanMessageModel, StringMessageModel, BinaryMessageModel, \
    FloatListMessageModel, IntListMessageModel, StringListMessageModel, BaseDataClassModel
from Common.protobuf.BaseDataClassMessage_pb2 import (
    BooleanMessage as BooleanMessage_pb2,
    StringMessage as StringMessage_pb2,
    BinaryMessage as BinaryMessage_pb2,
    FloatListMessage as FloatListMessage_pb2,
    DoubleListMessage as DoubleListMessage_pb2,
    Int32ListMessage as Int32ListMessage_pb2,
    Int64ListMessage as Int64ListMessage_pb2,
    StringListMessage as StringListMessage_pb2,
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class BaseDataClassMessageConverter:

    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            BooleanMessage_pb2: cls.__boolean_message_to_model,
            StringMessage_pb2: cls.__string_message_to_model,
            BinaryMessage_pb2: cls.__binary_message_to_model,
            FloatListMessage_pb2: cls.__float_list_message_to_model,
            DoubleListMessage_pb2: cls.__float_list_message_to_model,
            Int32ListMessage_pb2: cls.__int_list_message_to_model,
            Int64ListMessage_pb2: cls.__int_list_message_to_model,
            StringListMessage_pb2: cls.__string_list_message_to_model
        }
        cls.__model_class_for_convert_func_dict = {
            BooleanMessageModel: cls.__boolean_model_to_package_pb,
            StringMessageModel: cls.__string_model_to_package_pb,
            BinaryMessageModel: cls.__binary_model_to_package_pb,
            FloatListMessageModel: cls.__float_list_model_to_package_pb,
            IntListMessageModel: cls.__int_list_model_to_package_pb,
            StringListMessageModel: cls.__string_list_model_to_package_pb
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        BooleanMessageModel,
        StringMessageModel,
        BinaryMessageModel,
        FloatListMessageModel,
        IntListMessageModel,
        StringListMessageModel
    ]:
        return cls.__package_name_for_convert_func_dict[type(pb_message)](pb_message)

    @classmethod
    def model_to_protobuf(cls, model: BaseDataClassModel, precision: int = None) -> Message:
        return cls.__model_class_for_convert_func_dict[type(model)](model, precision)

    @classmethod
    def __boolean_message_to_model(cls, boolean_message: BooleanMessage_pb2) -> BooleanMessageModel:
        return BooleanMessageModel(data=boolean_message.data)

    @classmethod
    def __string_message_to_model(cls, string_message: StringMessage_pb2) -> StringMessageModel:
        return StringMessageModel(data=string_message.data)

    @classmethod
    def __binary_message_to_model(cls, binary_message: BinaryMessage_pb2) -> BinaryMessageModel:
        return BinaryMessageModel(data=binary_message.data)

    @classmethod
    def __float_list_message_to_model(cls, float_list_message: FloatListMessage_pb2) -> FloatListMessageModel:
        return FloatListMessageModel(data=list(float_list_message.data))

    @classmethod
    def __int_list_message_to_model(cls, int_list_message: Int32ListMessage_pb2) -> IntListMessageModel:
        return IntListMessageModel(data=list(int_list_message.data))

    @classmethod
    def __string_list_message_to_model(cls, string_list_message: StringListMessage_pb2) -> StringListMessageModel:
        return StringListMessageModel(data=list(string_list_message.data))

    @classmethod
    def __boolean_model_to_package_pb(cls, boolean_model: BooleanMessageModel, precision: int = None) -> BooleanMessage_pb2:
        return BooleanMessage_pb2(data=boolean_model.data)

    @classmethod
    def __string_model_to_package_pb(cls, string_model: StringMessageModel, precision: int = None) -> StringMessage_pb2:
        return StringMessage_pb2(data=string_model.data)

    @classmethod
    def __binary_model_to_package_pb(cls, binary_model: BinaryMessageModel, precision: int = None) -> BinaryMessage_pb2:
        return BinaryMessage_pb2(data=binary_model.data)

    @classmethod
    def __float_list_model_to_package_pb(cls, float_list_model: FloatListMessageModel,
                                         precision: int = None) -> FloatListMessage_pb2:
        if precision == 64:
            return DoubleListMessage_pb2(data=float_list_model.data)
        else:
            return FloatListMessage_pb2(data=float_list_model.data)

    @classmethod
    def __int_list_model_to_package_pb(cls, int_list_model: IntListMessageModel, precision: int = None) -> Int32ListMessage_pb2:
        if precision == 32:
            return Int32ListMessage_pb2(data=int_list_model.data)
        else:
            return Int64ListMessage_pb2(data=int_list_model.data)

    @classmethod
    def __string_list_model_to_package_pb(cls, string_list_model: StringListMessageModel,
                                          precision: int = None) -> StringListMessage_pb2:
        return StringListMessage_pb2(data=string_list_model.data)
