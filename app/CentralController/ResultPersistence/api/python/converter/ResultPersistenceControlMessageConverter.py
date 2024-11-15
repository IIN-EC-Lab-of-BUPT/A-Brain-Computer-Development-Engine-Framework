from typing import Union

from google.protobuf.message import Message
from ResultPersistence.api.protobuf.ResultPersistenceControl_pb2 import (
    StartReceiveResultControlMessage as StartReceiveResultControlMessage_pb2,
    StopReceiveResultControlMessage as StopReceiveResultControlMessage_pb2,
    ResultPersistenceExitControlMessage as ResultPersistenceExitControlMessage_pb2,
    ResultPersistenceControlMessage as ResultPersistenceControlMessage_pb2,
)
from ResultPersistence.api.python.model.ResultPersistenceControlModel import (
    ResultPersistenceExitControlModel,
    StartReceiveResultControlModel,
    StopReceiveResultControlModel,
    ResultPersistenceControlModel,
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class ResultPersistenceControlMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            ResultPersistenceExitControlMessage_pb2: cls.__result_persistence_exit_control_message_to_model,
            StartReceiveResultControlMessage_pb2: cls.__start_receive_result_control_message_to_model,
            StopReceiveResultControlMessage_pb2: cls.__stop_receive_result_control_message_to_model,
            ResultPersistenceControlMessage_pb2: cls.__result_persistence_control_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            ResultPersistenceExitControlModel: cls.__result_persistence_exit_control_model_to_message_pb,
            StartReceiveResultControlModel: cls.__start_receive_result_control_model_to_message_pb,
            StopReceiveResultControlModel: cls.__stop_receive_result_control_model_to_message_pb,
            ResultPersistenceControlModel: cls.__result_persistence_control_model_to_message_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        ResultPersistenceExitControlModel,
        StartReceiveResultControlModel,
        StopReceiveResultControlModel,
        ResultPersistenceControlModel,
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[
        ResultPersistenceExitControlModel,
        StartReceiveResultControlModel,
        StopReceiveResultControlModel,
        ResultPersistenceControlModel,]
                          ) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __result_persistence_exit_control_message_to_model(
            cls, result_persistence_control_message: ResultPersistenceControlMessage_pb2) -> ResultPersistenceExitControlModel:
        return ResultPersistenceExitControlModel()

    @classmethod
    def __start_receive_result_control_message_to_model(
            cls, start_receive_result_control_message: StartReceiveResultControlMessage_pb2) -> StartReceiveResultControlModel:
        return StartReceiveResultControlModel()

    @classmethod
    def __stop_receive_result_control_message_to_model(
            cls, stop_receive_result_control_message: StopReceiveResultControlMessage_pb2) -> StopReceiveResultControlModel:
        return StopReceiveResultControlModel()

    @classmethod
    def __result_persistence_control_message_to_model(
            cls, result_persistence_control_message: ResultPersistenceControlMessage_pb2) -> ResultPersistenceControlModel:
        package_name = result_persistence_control_message.WhichOneof('package')
        return ResultPersistenceControlModel(
            package=cls.__result_persistence_exit_control_message_to_model(
                result_persistence_control_message.startReceiveResultControlMessage)
            if package_name == "startReceiveResultControlMessage" else
            cls.__stop_receive_result_control_message_to_model(
                result_persistence_control_message.stopReceiveResultControlMessage)
            if package_name == "stopReceiveResultControlMessage" else
            cls.__result_persistence_control_message_to_model(
                result_persistence_control_message.resultPersistenceExitControlMessage)
            if package_name == "resultPersistenceExitControlMessage" else
            None
        )

    """
    model到package转换函数
    """

    @classmethod
    def __result_persistence_exit_control_model_to_message_pb(cls, result_persistence_exit_control_model: ResultPersistenceExitControlModel) \
            -> ResultPersistenceExitControlMessage_pb2:
        return ResultPersistenceExitControlMessage_pb2()

    @classmethod
    def __start_receive_result_control_model_to_message_pb(cls, start_receive_result_control_model: StartReceiveResultControlModel) \
            -> StartReceiveResultControlMessage_pb2:
        return StartReceiveResultControlMessage_pb2()

    @classmethod
    def __stop_receive_result_control_model_to_message_pb(cls, stop_receive_result_control_model: StopReceiveResultControlModel) \
            -> StopReceiveResultControlMessage_pb2:
        return StopReceiveResultControlMessage_pb2()

    @classmethod
    def __result_persistence_control_model_to_message_pb(cls, result_persistence_control_model: ResultPersistenceControlModel) \
            -> ResultPersistenceControlMessage_pb2:
        package = result_persistence_control_model.package
        if isinstance(package, ResultPersistenceExitControlModel):
            return ResultPersistenceControlMessage_pb2(
                resultPersistenceExitControlMessage=cls.__result_persistence_exit_control_model_to_message_pb(
                    result_persistence_control_model.package)
            )
        elif isinstance(package, StartReceiveResultControlModel):
            return ResultPersistenceControlMessage_pb2(
                startReceiveResultControlMessage=cls.__start_receive_result_control_model_to_message_pb(
                    result_persistence_control_model.package)
            )
        elif isinstance(package, StopReceiveResultControlModel):
            return ResultPersistenceControlMessage_pb2(
                stopReceiveResultControlMessage=cls.__stop_receive_result_control_model_to_message_pb(
                    result_persistence_control_model.package)
            )
