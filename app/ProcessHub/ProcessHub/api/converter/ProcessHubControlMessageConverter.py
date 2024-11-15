from typing import Union

from google.protobuf.message import Message

from ProcessHub.api.model.ProcessHubControlModel import ApplicationExitControlModel, ProcessHubControlModel
from ProcessHub.api.protobuf.ProcessHubControl_pb2 import (
    ApplicationExitControlMessage as ApplicationExitControlMessage_pb2,
    ProcessHubControlMessage as ProcessHubControlMessage_pb2,
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class ProcessHubControlMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            ApplicationExitControlMessage_pb2: cls.__application_exit_control_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            ApplicationExitControlModel: cls.__application_exit_control_model_to_message_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        ApplicationExitControlModel,
        ProcessHubControlModel,
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[
        ApplicationExitControlModel,
        ProcessHubControlModel,
    ]
                          ) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __application_exit_control_message_to_model(
            cls, application_exit_control_message: ApplicationExitControlMessage_pb2) -> ApplicationExitControlModel:
        return ApplicationExitControlModel()

    @classmethod
    def __task_control_message_to_model(
            cls, collector_control_message: ProcessHubControlMessage_pb2) -> ProcessHubControlModel:
        package_name = collector_control_message.WhichOneof('package')
        return ProcessHubControlModel(
            package=cls.__application_exit_control_message_to_model(
                collector_control_message.applicationExitControlMessage)
            if package_name == "applicationExitControlMessage"
            else None
        )

    @classmethod
    def __application_exit_control_model_to_message_pb(cls, application_exit_control_model: ApplicationExitControlModel) \
            -> ApplicationExitControlMessage_pb2:
        return ApplicationExitControlMessage_pb2()

    @classmethod
    def __task_control_model_to_message_pb(cls, task_control_model: ProcessHubControlModel) \
            -> ProcessHubControlMessage_pb2:
        package = task_control_model.package
        if isinstance(package, ApplicationExitControlModel):
            return ProcessHubControlMessage_pb2(
                applicationExitControlMessage=cls.__application_exit_control_model_to_message_pb(
                    task_control_model.package)
            )

