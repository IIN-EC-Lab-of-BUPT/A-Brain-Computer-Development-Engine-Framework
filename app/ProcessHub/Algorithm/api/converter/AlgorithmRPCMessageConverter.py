from google.protobuf.message import Message

from Common.converter.CommonMessageConverter import CommonMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel, \
    AlgorithmReportMessageModel, BaseAlgorithmRPCMessageModel, AlgorithmStatusEnum, AlgorithmStatusMessageModel

from Common.model.CommonMessageModel import DevicePackageModel, EventPackageModel, \
    DataPackageModel, ImpedancePackageModel, InformationPackageModel, ControlPackageModel, ResultPackageModel, \
    ExceptionPackageModel
from Algorithm.api.proto.AlgorithmRPCService_pb2 import (
    AlgorithmDataMessage as AlgorithmDataMessage_pb2,
    AlgorithmReportMessage as AlgorithmReportMessage_pb2,
    AlgorithmStatusMessage as AlgorithmStatusMessage_pb2,
    AlgorithmStatusEnum as AlgorithmStatusEnum_pb2
)


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class AlgorithmRPCMessageConverter:

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            AlgorithmDataMessage_pb2: cls.__algorithm_data_message_to_model,
            AlgorithmReportMessage_pb2: cls.__algorithm_report_message_to_model,
            AlgorithmStatusMessage_pb2: cls.__algorithm_status_message_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            AlgorithmDataMessageModel: cls.__algorithm_data_model_to_package_pb,
            AlgorithmReportMessageModel: cls.__algorithm_report_model_to_package_pb,
            AlgorithmStatusMessageModel: cls.__algorithm_status_model_to_package_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> BaseAlgorithmRPCMessageModel:
        return cls.__package_name_for_convert_func_dict[type(pb_message)](pb_message)

    @classmethod
    def model_to_protobuf(cls, model: BaseAlgorithmRPCMessageModel) -> Message:
        return cls.__model_class_for_convert_func_dict[type(model)](model)

    @classmethod
    def __algorithm_data_message_to_model(cls,
                                          algorithm_data_message: AlgorithmDataMessage_pb2) -> AlgorithmDataMessageModel:
        package_name = algorithm_data_message.WhichOneof('package')
        return AlgorithmDataMessageModel(
            source_label=algorithm_data_message.sourceLabel,
            timestamp=algorithm_data_message.timestamp,
            package=CommonMessageConverter.protobuf_to_model(algorithm_data_message.devicePackage)
            if package_name == "devicePackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_data_message.eventPackage)
            if package_name == "eventPackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_data_message.dataPackage)
            if package_name == "dataPackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_data_message.impedancePackage)
            if package_name == "impedancePackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_data_message.informationPackage)
            if package_name == "informationPackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_data_message.controlPackage)
            if package_name == "controlPackage" else None
        )

    @classmethod
    def __algorithm_report_message_to_model(
            cls, algorithm_report_message: AlgorithmReportMessage_pb2) -> AlgorithmReportMessageModel:
        package_name = algorithm_report_message.WhichOneof('package')
        return AlgorithmReportMessageModel(
            timestamp=algorithm_report_message.timestamp,
            package=CommonMessageConverter.protobuf_to_model(algorithm_report_message.resultPackage)
            if package_name == "resultPackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_report_message.controlPackage)
            if package_name == "controlPackage" else
            CommonMessageConverter.protobuf_to_model(algorithm_report_message.exceptionPackage)
            if package_name == "exceptionPackage" else None
        )

    @classmethod
    def __algorithm_status_message_to_model(
            cls, algorithm_status_message: AlgorithmStatusMessage_pb2) -> AlgorithmStatusMessageModel:
        return AlgorithmStatusMessageModel(
            status=AlgorithmStatusEnum[AlgorithmStatusEnum_pb2.Name(algorithm_status_message.status)]
        )

    @classmethod
    def __algorithm_data_model_to_package_pb(
            cls, algorithm_data_message: AlgorithmDataMessageModel) -> AlgorithmDataMessage_pb2:
        algorithm_data_message_pb = AlgorithmDataMessage_pb2(
            sourceLabel=algorithm_data_message.source_label,
            timestamp=algorithm_data_message.timestamp)
        if isinstance(algorithm_data_message.package, DevicePackageModel):
            algorithm_data_message_pb.devicePackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        elif isinstance(algorithm_data_message.package, EventPackageModel):
            algorithm_data_message_pb.eventPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        elif isinstance(algorithm_data_message.package, DataPackageModel):
            algorithm_data_message_pb.dataPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        elif isinstance(algorithm_data_message.package, ImpedancePackageModel):
            algorithm_data_message_pb.impedancePackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        elif isinstance(algorithm_data_message.package, InformationPackageModel):
            algorithm_data_message_pb.informationPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        elif isinstance(algorithm_data_message.package, ControlPackageModel):
            algorithm_data_message_pb.controlPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_data_message.package))
        return algorithm_data_message_pb

    @classmethod
    def __algorithm_report_model_to_package_pb(
            cls, algorithm_report_message: AlgorithmReportMessageModel) -> AlgorithmReportMessage_pb2:
        algorithm_report_message_pb = AlgorithmReportMessage_pb2(timestamp=algorithm_report_message.timestamp)
        if isinstance(algorithm_report_message.package, ResultPackageModel):
            algorithm_report_message_pb.resultPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_report_message.package))
        elif isinstance(algorithm_report_message.package, ControlPackageModel):
            algorithm_report_message_pb.controlPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_report_message.package))
        elif isinstance(algorithm_report_message.package, ExceptionPackageModel):
            algorithm_report_message_pb.exceptionPackage.CopyFrom(
                CommonMessageConverter.model_to_protobuf(algorithm_report_message.package))
        return algorithm_report_message_pb

    @classmethod
    def __algorithm_status_model_to_package_pb(
            cls, algorithm_status_message: AlgorithmStatusMessageModel) -> AlgorithmStatusMessage_pb2:
        return AlgorithmStatusMessage_pb2(status=AlgorithmStatusEnum_pb2.Value(algorithm_status_message.status.name))
