from typing import Union

import numpy
import yaml
from google.protobuf.message import Message
from google.protobuf.empty_pb2 import Empty as Empyt_pb2

from Common.converter.BaseDataClassMessageConverter import BaseDataClassMessageConverter
from Common.model.CommonMessageModel import BaseCommonMessageModel, DevicePackageModel, DataTypeEnum, \
    EventPackageModel, DataPackageModel, ImpedancePackageModel, InformationPackageModel, ControlPackageModel, \
    DataMessageModel, ReportSourceInformationModel, ResultPackageModel, ScorePackageModel, \
    ExceptionPackageModel
from Common.protobuf.CommonMessage_pb2 import (
    DataType as DataType_pb2,
    DevicePackage as DevicePackage_pb2,
    EventPackage as EventPackage_pb2,
    DataPackage as DataPackage_pb2,
    ImpedancePackage as ImpedancePackage_pb2,
    InformationPackage as InformationPackage_pb2,
    ControlPackage as ControlPackage_pb2,
    DataMessage as DataMessage_pb2,
    ReportSourceInformation as ReportSourceInformation_pb2,
    ResultPackage as ResultPackage_pb2,
    ScorePackage as ScorePackage_pb2,
    ExceptionPackage as ExceptionPackage_pb2,
)
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
class CommonMessageConverter:
    __package_name_for_convert_func_dict: dict
    __model_class_for_convert_func_dict: dict
    __base_data_class_message_converter: BaseDataClassMessageConverter

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            DevicePackage_pb2: cls.__device_package_to_model,
            EventPackage_pb2: cls.__event_package_to_model,
            DataPackage_pb2: cls.__data_package_to_model,
            ImpedancePackage_pb2: cls.__impedance_package_to_model,
            InformationPackage_pb2: cls.__information_package_to_model,
            ControlPackage_pb2: cls.__control_package_to_model,
            DataMessage_pb2: cls.__data_message_package_to_model,
            ReportSourceInformation_pb2: cls.__report_source_information_package_to_model,
            ResultPackage_pb2: cls.__result_package_to_model,
            ScorePackage_pb2: cls.__score_package_to_model,
            ExceptionPackage_pb2: cls.__exception_package_to_model,
        }
        cls.__model_class_for_convert_func_dict = {
            DevicePackageModel: cls.__device_model_to_package_pb,
            EventPackageModel: cls.__event_model_to_package_pb,
            DataPackageModel: cls.__data_model_to_package_pb,
            ImpedancePackageModel: cls.__impedance_model_to_package_pb,
            InformationPackageModel: cls.__information_model_to_package_pb,
            ControlPackageModel: cls.__control_model_to_package_pb,
            DataMessageModel: cls.__data_message_model_to_package_pb,
            ReportSourceInformationModel: cls.__report_source_information_model_to_package_pb,
            ResultPackageModel: cls.__result_model_to_package_pb,
            ScorePackageModel: cls.__score_model_to_package_pb,
            ExceptionPackageModel: cls.__exception_model_to_package_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> Union[
        DevicePackageModel,
        EventPackageModel,
        DataPackageModel,
        ImpedancePackageModel,
        InformationPackageModel,
        ControlPackageModel,
        DataMessageModel,
        ReportSourceInformationModel,
        ResultPackageModel,
        ScorePackageModel,
        ExceptionPackageModel
    ]:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: BaseCommonMessageModel) -> Message:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    # DevicePackage 转换函数
    def __device_package_to_model(cls, device_package: DevicePackage_pb2) -> DevicePackageModel:

        return DevicePackageModel(
            data_type=DataTypeEnum[DataType_pb2.Name(device_package.dataType)],
            channel_number=device_package.channelNumber,
            sample_rate=device_package.sampleRate,
            channel_label=list(device_package.channelLabel),
            other_information=yaml.safe_load(device_package.otherInformation)
            if device_package.otherInformation is not None else None)

    @classmethod
    # EventPackage 转换函数
    def __event_package_to_model(cls, event_package: EventPackage_pb2) -> EventPackageModel:
        return EventPackageModel(
            event_position=list(event_package.eventPosition),
            event_data=list(event_package.eventData)
        )

    @classmethod
    # DataPackage 转换函数
    def __data_package_to_model(cls, data_package: DataPackage_pb2) -> DataPackageModel:
        data_name = data_package.WhichOneof('data')
        match data_name:
            case "booleanMessage":
                data = getattr(data_package, data_name).data
            case "stringMessage":
                data = getattr(data_package, data_name).data
            case "binaryMessage":
                data = getattr(data_package, data_name).data
            case "floatListMessage":
                data = numpy.array(getattr(data_package, data_name).data, dtype=numpy.float32)
            case "doubleListMessage":
                data = list(getattr(data_package, data_name).data)
            case "int32ListMessage":
                data = numpy.array(getattr(data_package, data_name).data, dtype=numpy.int32)
            case "int64ListMessage":
                data = list(getattr(data_package, data_name).data)
            case "stringListMessage":
                data = list(getattr(data_package, data_name).data)
            case "emptyMessage":
                data = None
            case _:
                raise TypeError(f"Unknown data_package.data type {data_name}")
        return DataPackageModel(
            data_position=data_package.dataPosition,
            data=data
        )

    @classmethod
    # ImpedancePacket 转换函数
    def __impedance_package_to_model(cls, impedance_package: ImpedancePackage_pb2) -> ImpedancePackageModel:
        return ImpedancePackageModel(
            channel_impedance=list(impedance_package.channelImpedance)
        )

    @classmethod
    # InformationPackage 转换函数
    def __information_package_to_model(cls, information_package: InformationPackage_pb2) -> InformationPackageModel:
        return InformationPackageModel(
            subject_id=information_package.subjectId,
            block_id=information_package.blockId
        )

    @classmethod
    def __control_package_to_model(cls, control_package: ControlPackage_pb2) -> ControlPackageModel:
        return ControlPackageModel(
            end_flag=control_package.endFlag
        )

    @classmethod
    def __data_message_package_to_model(cls, data_message: DataMessage_pb2) -> DataMessageModel:
        package_name = data_message.WhichOneof('package')
        return DataMessageModel(
            package=CommonMessageConverter.__device_package_to_model(data_message.devicePackage)
            if package_name == "devicePackage" else
            CommonMessageConverter.__event_package_to_model(data_message.eventPackage)
            if package_name == "eventPackage" else
            CommonMessageConverter.__data_package_to_model(data_message.dataPackage)
            if package_name == "dataPackage" else
            CommonMessageConverter.__impedance_package_to_model(data_message.impedancePackage)
            if package_name == "impedancePackage" else
            CommonMessageConverter.__information_package_to_model(data_message.informationPackage)
            if package_name == "informationPackage" else
            CommonMessageConverter.__control_package_to_model(data_message.controlPackage)
            if package_name == "controlPackage" else
            CommonMessageConverter.__result_package_to_model(data_message.resultPackage)
            if package_name == "resultPackage" else
            CommonMessageConverter.__score_package_to_model(data_message.scorePackage)
            if package_name == "scorePackage" else
            CommonMessageConverter.__exception_package_to_model(data_message.exceptionPackage)
            if package_name == "exceptionPackage" else None
        )

    @classmethod
    def __report_source_information_package_to_model(
            cls, report_source_information_package: ReportSourceInformation_pb2) -> ReportSourceInformationModel:
        return ReportSourceInformationModel(
            source_label=report_source_information_package.sourceLabel,
            position=report_source_information_package.position
        )

    @classmethod
    def __result_package_to_model(cls, result_package: ResultPackage_pb2) -> ResultPackageModel:
        result_name = result_package.WhichOneof('result')
        match result_name:
            case "booleanMessage":
                result = getattr(result_package, result_name).data
            case "stringMessage":
                result = getattr(result_package, result_name).data
            case "binaryMessage":
                result = getattr(result_package, result_name).data
            case "floatListMessage":
                result = numpy.array(getattr(result_package, result_name).data, dtype=numpy.float32)
            case "doubleListMessage":
                result = list(getattr(result_package, result_name).data)
            case "int32ListMessage":
                result = numpy.array(getattr(result_package, result_name).data, dtype=numpy.int32)
            case "int64ListMessage":
                result = list(getattr(result_package, result_name).data)
            case "stringListMessage":
                result = list(getattr(result_package, result_name).data)
            case "emptyMessage":
                result = None
            case _:
                raise TypeError(f"Unknown result_package.result type {result_name}")
        return ResultPackageModel(
            result=result,
            report_source_information=[
                CommonMessageConverter.__report_source_information_package_to_model(report_source_info)
                for report_source_info in result_package.reportSourceInformation]
        )

    @classmethod
    def __score_package_to_model(cls, score_package: ScorePackage_pb2) -> ScorePackageModel:
        return ScorePackageModel(
            show_text=score_package.showText,
            score=score_package.score,
            trial_time=score_package.trialTime,
            trial_id=score_package.trialId,
            block_id=score_package.blockId,
            subject_id=score_package.subjectId
        )

    @classmethod
    def __exception_package_to_model(cls, exception_package: ExceptionPackage_pb2) -> ExceptionPackageModel:
        return ExceptionPackageModel(
            exception_type=exception_package.exceptionType,
            exception_message=exception_package.exceptionMessage,
            exception_stack_trace=exception_package.exceptionStackTrace
        )

    """
    model到package转换函数
    """

    @classmethod
    def __device_model_to_package_pb(cls, device_package_model: DevicePackageModel) -> DevicePackage_pb2:
        return DevicePackage_pb2(
            dataType=DataType_pb2.Value(device_package_model.data_type.name),
            # dataMessageClass=BaseDataMessageClass_pb2.Value(device_package_model.data_message_class.name),
            channelNumber=device_package_model.channel_number,
            sampleRate=device_package_model.sample_rate,
            channelLabel=list(device_package_model.channel_label),
            otherInformation=yaml.safe_dump(device_package_model.other_information)
            if device_package_model.other_information is not None else None
        )

    @classmethod
    def __event_model_to_package_pb(cls, event_model: EventPackageModel) -> EventPackage_pb2:
        return EventPackage_pb2(
            eventPosition=list(event_model.event_position),
            eventData=list(event_model.event_data)
        )

    @classmethod
    def __data_model_to_package_pb(cls, data_model: DataPackageModel) -> DataPackage_pb2:
        match data_model.data:
            case numpy.ndarray():
                dtype = data_model.data.dtype

                match dtype:
                    case numpy.dtypes.Float32DType():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            floatListMessage=FloatListMessage_pb2(data=list(data_model.data))
                        )
                    case numpy.dtypes.Float64DType():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            doubleListMessage=DoubleListMessage_pb2(data=list(data_model.data))
                        )
                    case numpy.dtypes.Int32DType():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            int32ListMessage=Int32ListMessage_pb2(data=list(data_model.data))
                        )
                    case numpy.dtypes.Int64DType():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            int64ListMessage=Int64ListMessage_pb2(data=list(data_model.data))
                        )
                    case _:
                        raise TypeError(f"Unsupported data type: {dtype}")

            case bool():
                data_package = DataPackage_pb2(
                    dataPosition=data_model.data_position,
                    booleanMessage=BooleanMessage_pb2(data=data_model.data)
                )
            case str():
                data_package = DataPackage_pb2(
                    dataPosition=data_model.data_position,
                    stringMessage=StringMessage_pb2(data=data_model.data)
                )
            case bytes():
                data_package = DataPackage_pb2(
                    dataPosition=data_model.data_position,
                    binaryMessage=BinaryMessage_pb2(data=data_model.data)
                )
            case list():
                if len(data_model.data) == 0:
                    raise ValueError(f"list data is empty, please check the data number")

                inner_data = data_model.data[0]
                match inner_data:
                    case str():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            stringListMessage=StringListMessage_pb2(data=list(data_model.data))
                        )
                    case float():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            floatListMessage=FloatListMessage_pb2(data=list(data_model.data))
                        )
                    case int():
                        data_package = DataPackage_pb2(
                            dataPosition=data_model.data_position,
                            int64ListMessage=Int64ListMessage_pb2(data=list(data_model.data))
                        )
                    case _:
                        raise TypeError(f"Unsupported data type: {type(inner_data)}")
            case None:
                data_package = DataPackage_pb2(
                    dataPosition=data_model.data_position,
                    emptyMessage=Empyt_pb2()
                )

            case _:
                raise TypeError(f"data_model.data type error {type(data_model.data)}")

        return data_package

    @classmethod
    def __impedance_model_to_package_pb(cls, impedance_model: ImpedancePackageModel) -> ImpedancePackage_pb2:
        return ImpedancePackage_pb2(
            channelImpedance=list(impedance_model.channel_impedance)
        )

    @classmethod
    def __information_model_to_package_pb(cls, information_model: InformationPackageModel) -> InformationPackage_pb2:
        return InformationPackage_pb2(
            subjectId=information_model.subject_id,
            blockId=information_model.block_id
        )

    @classmethod
    def __control_model_to_package_pb(cls, control_model: ControlPackageModel) -> ControlPackage_pb2:
        return ControlPackage_pb2(
            endFlag=control_model.end_flag
        )

    @classmethod
    def __data_message_model_to_package_pb(cls, data_message_model: DataMessageModel) -> DataMessage_pb2:
        package = data_message_model.package
        if isinstance(package, DevicePackageModel):
            return DataMessage_pb2(
                devicePackage=CommonMessageConverter.__device_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, EventPackageModel):
            return DataMessage_pb2(
                eventPackage=CommonMessageConverter.__event_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, DataPackageModel):
            return DataMessage_pb2(
                dataPackage=CommonMessageConverter.__data_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, ImpedancePackageModel):
            return DataMessage_pb2(
                impedancePackage=CommonMessageConverter.__impedance_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, InformationPackageModel):
            return DataMessage_pb2(
                informationPackage=CommonMessageConverter.__information_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, ControlPackageModel):
            return DataMessage_pb2(
                controlPackage=CommonMessageConverter.__control_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, ResultPackageModel):
            return DataMessage_pb2(
                resultPackage=CommonMessageConverter.__result_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, ScorePackageModel):
            return DataMessage_pb2(
                scorePackage=CommonMessageConverter.__score_model_to_package_pb(data_message_model.package)
            )
        elif isinstance(package, ExceptionPackageModel):
            return DataMessage_pb2(
                exceptionPackage=CommonMessageConverter.__exception_model_to_package_pb(data_message_model.package)
            )

    @classmethod
    def __report_source_information_model_to_package_pb(cls, report_source_information: ReportSourceInformationModel) \
            -> ReportSourceInformation_pb2:
        return ReportSourceInformation_pb2(
            sourceLabel=report_source_information.source_label,
            position=report_source_information.position
        )

    @classmethod
    def __result_model_to_package_pb(cls, result_model: ResultPackageModel) -> ResultPackage_pb2:
        report_source_information = [
            CommonMessageConverter.__report_source_information_model_to_package_pb(report_source_info)
            for report_source_info in result_model.report_source_information]
        match result_model.result:
            case numpy.ndarray():
                dtype = result_model.result.dtype
                match dtype:
                    case numpy.dtypes.Float32DType():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            floatListMessage=FloatListMessage_pb2(data=list(result_model.result))
                        )
                    case numpy.dtypes.Float64DType():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            doubleListMessage=DoubleListMessage_pb2(data=list(result_model.result))
                        )
                    case numpy.dtypes.Int32DType():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            int32ListMessage=Int32ListMessage_pb2(data=list(result_model.result))
                        )
                    case numpy.dtypes.Int64DType():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            int64ListMessage=Int64ListMessage_pb2(data=list(result_model.result))
                        )
                    case _:
                        raise TypeError(f"Unsupported result type: {dtype}")
            case bool():
                result_package = ResultPackage_pb2(
                    reportSourceInformation=report_source_information,
                    booleanMessage=BooleanMessage_pb2(data=result_model.result)
                )
            case str():
                result_package = ResultPackage_pb2(
                    reportSourceInformation=report_source_information,
                    stringMessage=StringMessage_pb2(data=result_model.result)
                )
            case bytes():
                result_package = ResultPackage_pb2(
                    reportSourceInformation=report_source_information,
                    binaryMessage=BinaryMessage_pb2(data=result_model.result)
                )
            case list():
                if len(result_model.result) == 0:
                    raise ValueError(f"list result is empty, please check the result number")

                inner_data = result_model.result[0]
                match inner_data:
                    case str():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            stringListMessage=StringListMessage_pb2(data=list(result_model.result))
                        )
                    case float():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            floatListMessage=FloatListMessage_pb2(data=list(result_model.result))
                        )
                    case int():
                        result_package = ResultPackage_pb2(
                            reportSourceInformation=report_source_information,
                            int64ListMessage=Int64ListMessage_pb2(data=list(result_model.result))
                        )
                    case _:
                        raise TypeError(f"Unsupported result type: {type(inner_data)}")
            case None:
                result_package = ResultPackage_pb2(
                    reportSourceInformation=report_source_information,
                    emptyMessage=Empyt_pb2()
                )
            case _:
                raise TypeError(f"result_model.result type error {type(result_model.result)}")
        return result_package

    @classmethod
    def __score_model_to_package_pb(cls, score_package: ScorePackageModel) -> ScorePackage_pb2:
        return ScorePackage_pb2(
            showText=score_package.show_text,
            score=score_package.score,
            trialTime=score_package.trial_time,
            trialId=score_package.trial_id,
            blockId=score_package.block_id,
            subjectId=score_package.subject_id
        )

    @classmethod
    def __exception_model_to_package_pb(cls, exception_model: ExceptionPackageModel) -> ExceptionPackage_pb2:
        return ExceptionPackage_pb2(
            exceptionType=exception_model.exception_type,
            exceptionMessage=exception_model.exception_message,
            exceptionStackTrace=exception_model.exception_stack_trace
        )
