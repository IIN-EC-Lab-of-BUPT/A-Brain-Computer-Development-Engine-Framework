from typing import Union

from google.protobuf.message import Message

from Collector.api.model.CollectorControlModel import StartDataSendingControlModel, StopDataSendingControlModel, \
    SendDeviceInfoControlModel, CollectorControlModel, SendImpedanceControlModel, \
    ApplicationExitControlModel
from Collector.api.protobuf.CollectorControl_pb2 import (
    StartDataSendingControlMessage as StartDataSendingControlMessage_pb2,
    StopDataSendingControlMessage as StopDataSendingControlMessage_pb2,
    SendDeviceInfoControlMessage as SendDeviceInfoControlMessage_pb2,
    SendImpedanceControlMessage as SendImpedanceControlMessage_pb2,
    CollectorControlMessage as CollectorControlMessage_pb2,
    ApplicationExitControlMessage as ApplicationExitControlMessage_pb2,
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class CollectorControlMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            ApplicationExitControlMessage_pb2: cls.__application_exit_control_message_to_model,
            StartDataSendingControlMessage_pb2: cls.__start_data_sending_control_message_to_model,
            StopDataSendingControlMessage_pb2: cls.__stop_data_sending_control_message_to_model,
            SendDeviceInfoControlMessage_pb2: cls.__send_device_info_control_message_to_model,
            CollectorControlMessage_pb2: cls.__collector_control_message_to_model,
            SendImpedanceControlMessage_pb2: cls.__send_impedance_control_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            ApplicationExitControlModel: cls.__application_exit_control_model_to_message_pb,
            StartDataSendingControlModel: cls.__start_data_sending_control_model_to_message_pb,
            StopDataSendingControlModel: cls.__stop_data_sending_control_model_to_message_pb,
            SendDeviceInfoControlModel: cls.__send_device_info_control_model_to_message_pb,
            SendImpedanceControlModel: cls.__send_impedance_control_model_to_message_pb,
            CollectorControlModel: cls.__collector_control_model_to_message_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        StartDataSendingControlModel,
        StopDataSendingControlModel,
        SendDeviceInfoControlModel,
        SendImpedanceControlModel,
        CollectorControlModel,
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: Union[
        StartDataSendingControlModel,
        StopDataSendingControlModel,
        SendDeviceInfoControlModel,
        CollectorControlModel]
                          ) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    # DevicePackage 转换函数
    def __start_data_sending_control_message_to_model(
            cls,
            start_data_sending_control_message: StartDataSendingControlMessage_pb2) -> StartDataSendingControlModel:
        return StartDataSendingControlModel()

    @classmethod
    def __stop_data_sending_control_message_to_model(
            cls, stop_data_sending_control_message: StopDataSendingControlMessage_pb2) -> StopDataSendingControlModel:
        return StopDataSendingControlModel()

    @classmethod
    def __send_device_info_control_message_to_model(
            cls, send_device_info_control_message: SendDeviceInfoControlMessage_pb2) -> SendDeviceInfoControlModel:
        return SendDeviceInfoControlModel()

    @classmethod
    def __send_impedance_control_message_to_model(
            cls, send_impedance_control_message: SendImpedanceControlMessage_pb2) -> SendImpedanceControlModel:
        return SendImpedanceControlModel()

    @classmethod
    def __application_exit_control_message_to_model(
            cls, application_exit_control_message: ApplicationExitControlMessage_pb2) -> ApplicationExitControlModel:
        return ApplicationExitControlModel()

    @classmethod
    def __collector_control_message_to_model(
            cls, collector_control_message: CollectorControlMessage_pb2) -> CollectorControlModel:
        package_name = collector_control_message.WhichOneof('package')
        return CollectorControlModel(
            package=cls.__start_data_sending_control_message_to_model(
                collector_control_message.startDataSendingControlMessage)
            if package_name == "startDataSendingControlMessage" else
            cls.__stop_data_sending_control_message_to_model(collector_control_message.stopDataSendingControlMessage)
            if package_name == "stopDataSendingControlMessage" else
            cls.__send_device_info_control_message_to_model(collector_control_message.sendDeviceInfoControlMessage)
            if package_name == "sendDeviceInfoControlMessage" else
            cls.__send_impedance_control_message_to_model(collector_control_message.sendImpedanceControlMessage)
            if package_name == "sendImpedanceControlMessage"
            else cls.__application_exit_control_message_to_model(
                collector_control_message.applicationExitControlMessage)
            if package_name == "applicationExitControlMessage"
            else None
        )

    """
    model到package转换函数
    """

    @classmethod
    def __start_data_sending_control_model_to_message_pb(cls,
                                                         start_data_sending_control_model: StartDataSendingControlModel) \
            -> StartDataSendingControlMessage_pb2:
        return StartDataSendingControlMessage_pb2()

    @classmethod
    def __stop_data_sending_control_model_to_message_pb(cls,
                                                        stop_data_sending_control_model: StopDataSendingControlModel) \
            -> StopDataSendingControlMessage_pb2:
        return StopDataSendingControlMessage_pb2()

    @classmethod
    def __send_device_info_control_model_to_message_pb(cls, send_device_info_control_model: SendDeviceInfoControlModel) \
            -> SendDeviceInfoControlMessage_pb2:
        return SendDeviceInfoControlMessage_pb2()

    @classmethod
    def __send_impedance_control_model_to_message_pb(cls, send_impedance_control_model: SendImpedanceControlModel) \
            -> SendImpedanceControlMessage_pb2:
        return SendImpedanceControlMessage_pb2()

    @classmethod
    def __application_exit_control_model_to_message_pb(cls, application_exit_control_model: ApplicationExitControlModel) \
            -> ApplicationExitControlMessage_pb2:
        return ApplicationExitControlMessage_pb2()

    @classmethod
    def __collector_control_model_to_message_pb(cls, collector_control_model: CollectorControlModel) \
            -> CollectorControlMessage_pb2:
        package = collector_control_model.package
        if isinstance(package, StartDataSendingControlModel):
            return CollectorControlMessage_pb2(
                startDataSendingControlMessage=cls.__start_data_sending_control_model_to_message_pb(
                    collector_control_model.package)
            )
        elif isinstance(package, StopDataSendingControlModel):
            return CollectorControlMessage_pb2(
                stopDataSendingControlMessage=cls.__stop_data_sending_control_model_to_message_pb(
                    collector_control_model.package)
            )
        elif isinstance(package, SendDeviceInfoControlModel):
            return CollectorControlMessage_pb2(
                sendDeviceInfoControlMessage=cls.__send_device_info_control_model_to_message_pb(
                    collector_control_model.package)
            )
        elif isinstance(package, SendImpedanceControlModel):
            return CollectorControlMessage_pb2(
                sendImpedanceControlMessage=cls.__send_impedance_control_model_to_message_pb(
                    collector_control_model.package)
            )
        elif isinstance(package, ApplicationExitControlModel):
            return CollectorControlMessage_pb2(
                applicationExitControlMessage=cls.__application_exit_control_model_to_message_pb(
                    collector_control_model.package)
            )

