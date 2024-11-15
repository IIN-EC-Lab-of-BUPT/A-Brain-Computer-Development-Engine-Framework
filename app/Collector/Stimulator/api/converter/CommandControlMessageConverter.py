from typing import Union
from google.protobuf.message import Message
from Stimulator.api.model.CommandControlModel import StartStimulationControlModel, StopStimulationControlModel, \
    StimulationControlModel, QuitStimulationControlModel
from Stimulator.api.protobuf.out.CommandControl_pb2 import (
    StartStimulationControlMessage as StartStimulationControlMessage_pb2,
    StopStimulationControlMessage as StopStimulationControlMessage_pb2,
    QuitStimulationControlMessage as QuitStimulationControlMessage_pb2,
    StimulationControlMessage as StimulationControlMessage_pb2
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class StimulationSystemCommandControlMessageConverter:
    __model_class_for_convert_func_dict: dict
    __package_name_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            StartStimulationControlMessage_pb2: cls.__start_stimulation_control_message_to_model,
            StopStimulationControlMessage_pb2: cls.__stop_stimulation_control_message_to_model,
            QuitStimulationControlMessage_pb2: cls.__quit_stimulation_control_message_to_model
        }
        cls.__model_class_for_convert_func_dict = {
            StartStimulationControlModel: cls.__start_stimulation_control_model_to_package_pb,
            StopStimulationControlModel: cls.__stop_stimulation_control_model_to_package_pb,
            QuitStimulationControlModel: cls.__quit_stimulation_control_model_to_package_pb
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: StimulationControlMessage_pb2) -> Union[
        StartStimulationControlModel,
        StopStimulationControlModel
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: StimulationControlModel) -> StimulationControlMessage_pb2:
        convert_func = cls.__model_class_for_convert_func_dict[type(model.package)]
        return convert_func(model)

    @classmethod
    def __start_stimulation_control_message_to_model(
            cls,
            start_data_sending_control_message: StartStimulationControlMessage_pb2) -> StartStimulationControlModel:
        return StartStimulationControlModel()

    @classmethod
    def __stop_stimulation_control_message_to_model(
            cls, stop_data_sending_control_message: StopStimulationControlMessage_pb2) -> StopStimulationControlModel:
        return StopStimulationControlModel()

    @classmethod
    def __quit_stimulation_control_message_to_model(
            cls, quit_data_sending_control_message: QuitStimulationControlMessage_pb2) -> StopStimulationControlModel:
        return StopStimulationControlModel()

    @classmethod
    def __start_stimulation_control_model_to_package_pb(
            cls, start_data_sending_control_model: StartStimulationControlModel) -> StartStimulationControlMessage_pb2:
        # return StimulationControlMessage_pb2(devicePackage=StartStimulationControlMessage_pb2())
        start_proto = StimulationControlMessage_pb2()
        start_proto.start_stimulation_control_message.CopyFrom(StartStimulationControlMessage_pb2())
        return start_proto

    @classmethod
    def __stop_stimulation_control_model_to_package_pb(
            cls, stop_data_sending_control_model: StopStimulationControlModel) -> StopStimulationControlMessage_pb2:
        stop_proto = StimulationControlMessage_pb2()
        stop_proto.stop_stimulation_control_message.CopyFrom(StopStimulationControlMessage_pb2())
        return stop_proto

    @classmethod
    def __quit_stimulation_control_model_to_package_pb(
            cls, quit_data_sending_control_model: QuitStimulationControlModel) -> QuitStimulationControlMessage_pb2:
        quit_proto = StimulationControlMessage_pb2()
        quit_proto.quit_stimulation_control_message.CopyFrom(QuitStimulationControlMessage_pb2())
        return quit_proto
