from typing import Union

from google.protobuf.message import Message
from EEGDataPersistence.api.protobuf.EEGPersistenceControl_pb2 import (
    StartReceiveEEGControlMessage as StartReceiveEEGControlMessage_pb2,
    StopReceiveEEGControlMessage as StopReceiveEEGControlMessage_pb2,
    EEGPersistenceExitControlMessage as EEGPersistenceExitControlMessage_pb2,
    EEGPersistenceControlMessage as EEGPersistenceControlMessage_pb2,
)
from EEGDataPersistence.api.python.model.EEGPersistenceControlModel import (
    EEGPersistenceExitControlModel,
    StartReceiveEEGControlModel,
    StopReceiveEEGControlModel,
    EEGPersistenceControlModel,
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class EEGPersistenceControlMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            EEGPersistenceExitControlMessage_pb2: cls.__eeg_persistence_exit_control_message_to_model,
            StartReceiveEEGControlMessage_pb2: cls.__start_receive_eeg_control_message_to_model,
            StopReceiveEEGControlMessage_pb2: cls.__stop_receive_eeg_control_message_to_model,
            EEGPersistenceControlMessage_pb2: cls.__eeg_persistence_control_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            EEGPersistenceExitControlModel: cls.__eeg_persistence_exit_control_model_to_message_pb,
            StartReceiveEEGControlModel: cls.__start_receive_eeg_control_model_to_message_pb,
            StopReceiveEEGControlModel: cls.__stop_receive_eeg_control_model_to_message_pb,
            EEGPersistenceControlModel: cls.__eeg_persistence_control_model_to_message_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        EEGPersistenceExitControlModel,
        StartReceiveEEGControlModel,
        StopReceiveEEGControlModel,
        EEGPersistenceControlModel,
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[
        EEGPersistenceExitControlModel,
        StartReceiveEEGControlModel,
        StopReceiveEEGControlModel,
        EEGPersistenceControlModel,]
                          ) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __eeg_persistence_exit_control_message_to_model(
            cls, eeg_persistence_control_message: EEGPersistenceControlMessage_pb2) -> EEGPersistenceExitControlModel:
        return EEGPersistenceExitControlModel()

    @classmethod
    def __start_receive_eeg_control_message_to_model(
            cls, start_receive_eeg_control_message: StartReceiveEEGControlMessage_pb2) -> StartReceiveEEGControlModel:
        return StartReceiveEEGControlModel()

    @classmethod
    def __stop_receive_eeg_control_message_to_model(
            cls, stop_receive_eeg_control_message: StopReceiveEEGControlMessage_pb2) -> StopReceiveEEGControlModel:
        return StopReceiveEEGControlModel()

    @classmethod
    def __eeg_persistence_control_message_to_model(
            cls, eeg_persistence_control_message: EEGPersistenceControlMessage_pb2) -> EEGPersistenceControlModel:
        package_name = eeg_persistence_control_message.WhichOneof('package')
        return EEGPersistenceControlModel(
            package=cls.__eeg_persistence_exit_control_message_to_model(
                eeg_persistence_control_message.startReceiveEEGControlMessage)
            if package_name == "startReceiveEEGControlMessage" else
            cls.__stop_receive_eeg_control_message_to_model(
                eeg_persistence_control_message.stopReceiveEEGControlMessage)
            if package_name == "stopReceiveEEGControlMessage" else
            cls.__eeg_persistence_control_message_to_model(
                eeg_persistence_control_message.eegPersistenceExitControlMessage)
            if package_name == "eegPersistenceExitControlMessage" else
            None
        )

    """
    model到package转换函数
    """

    @classmethod
    def __eeg_persistence_exit_control_model_to_message_pb(cls, eeg_persistence_exit_control_model: EEGPersistenceExitControlModel) \
            -> EEGPersistenceExitControlMessage_pb2:
        return EEGPersistenceExitControlMessage_pb2()

    @classmethod
    def __start_receive_eeg_control_model_to_message_pb(cls, start_receive_eeg_control_model: StartReceiveEEGControlModel) \
            -> StartReceiveEEGControlMessage_pb2:
        return StartReceiveEEGControlMessage_pb2()

    @classmethod
    def __stop_receive_eeg_control_model_to_message_pb(cls, stop_receive_eeg_control_model: StopReceiveEEGControlModel) \
            -> StopReceiveEEGControlMessage_pb2:
        return StopReceiveEEGControlMessage_pb2()

    @classmethod
    def __eeg_persistence_control_model_to_message_pb(cls, eeg_persistence_control_model: EEGPersistenceControlModel) \
            -> EEGPersistenceControlMessage_pb2:
        package = eeg_persistence_control_model.package
        if isinstance(package, EEGPersistenceExitControlModel):
            return EEGPersistenceControlMessage_pb2(
                eegPersistenceExitControlMessage=cls.__eeg_persistence_exit_control_model_to_message_pb(
                    eeg_persistence_control_model.package)
            )
        elif isinstance(package, StartReceiveEEGControlModel):
            return EEGPersistenceControlMessage_pb2(
                startReceiveEEGControlMessage=cls.__start_receive_eeg_control_model_to_message_pb(
                    eeg_persistence_control_model.package)
            )
        elif isinstance(package, StopReceiveEEGControlModel):
            return EEGPersistenceControlMessage_pb2(
                stopReceiveEEGControlMessage=cls.__stop_receive_eeg_control_model_to_message_pb(
                    eeg_persistence_control_model.package)
            )
