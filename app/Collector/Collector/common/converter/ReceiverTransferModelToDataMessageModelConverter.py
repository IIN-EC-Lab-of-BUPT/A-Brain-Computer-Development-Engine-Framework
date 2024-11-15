from typing import Union

from Collector.receiver.model.ReceiverTransferModel import ReceiverTransferModel, TransferDataTypeEnum, \
    DeviceTransferModel, EventTransferModel, DataTransferModel, ImpedanceTransferModel, InformationTransferModel
from Common.model.CommonMessageModel import DataMessageModel, DevicePackageModel, EventPackageModel, DataPackageModel, \
    ImpedancePackageModel, InformationPackageModel, DataTypeEnum


class ReceiverTransferModelToDataMessageModelConverter:

    @classmethod
    def convert(cls, transfer_model: Union[
        TransferDataTypeEnum,
        DeviceTransferModel,
        EventTransferModel,
        DataTransferModel,
        ImpedanceTransferModel,
        InformationTransferModel,
        ReceiverTransferModel,
    ]
                ) -> Union[
        DataTypeEnum,
        DevicePackageModel,
        EventPackageModel,
        DataPackageModel,
        ImpedancePackageModel,
        InformationPackageModel,
        DataMessageModel
    ]:
        if isinstance(transfer_model, ReceiverTransferModel):
            return DataMessageModel(
                package=ReceiverTransferModelToDataMessageModelConverter.convert(transfer_model.package)
            )
        elif isinstance(transfer_model, DeviceTransferModel):
            return cls._convert_device(transfer_model)

        elif isinstance(transfer_model, EventTransferModel):
            return cls._convert_event(transfer_model)

        elif isinstance(transfer_model, DataTransferModel):
            return cls._convert_data(transfer_model)

        elif isinstance(transfer_model, ImpedanceTransferModel):
            return cls._convert_impedance(transfer_model)

        elif isinstance(transfer_model, InformationTransferModel):
            return cls._convert_information(transfer_model)
        elif isinstance(transfer_model, TransferDataTypeEnum):
            return cls._convert_data_type_enum(transfer_model)
        else:
            raise ValueError("Unsupported package type.")

    @classmethod
    def _convert_device(cls, device_transfer_model: DeviceTransferModel) -> DevicePackageModel:
        return DevicePackageModel(
            data_type=cls._convert_data_type_enum(device_transfer_model.data_type),
            channel_number=device_transfer_model.channel_number,
            sample_rate=device_transfer_model.sample_rate,
            channel_label=device_transfer_model.channel_label,
            other_information=device_transfer_model.other_information
        )

    @classmethod
    def _convert_event(cls, event_transfer_model: EventTransferModel) -> EventPackageModel:
        return EventPackageModel(
            event_position=event_transfer_model.event_position,
            event_data=event_transfer_model.event_data
        )

    @classmethod
    def _convert_data(cls, data_transfer_model: DataTransferModel) -> DataPackageModel:
        return DataPackageModel(
            data_position=data_transfer_model.data_position,
            data=data_transfer_model.data
        )

    @classmethod
    def _convert_impedance(cls, impedance_transfer_model: ImpedanceTransferModel) -> ImpedancePackageModel:
        return ImpedancePackageModel(
            channel_impedance=impedance_transfer_model.channel_impedance
        )

    @classmethod
    def _convert_information(cls, information_transfer_model: InformationTransferModel) -> InformationPackageModel:
        return InformationPackageModel(
            subject_id=information_transfer_model.subject_id,
            block_id=information_transfer_model.block_id
        )

    @classmethod
    def _convert_data_type_enum(cls, transfer_data_type: TransferDataTypeEnum) -> DataTypeEnum:
        data_type_map = {
            TransferDataTypeEnum.UNKNOWN: DataTypeEnum.UNKNOWN,
            TransferDataTypeEnum.EEG: DataTypeEnum.EEG,
            TransferDataTypeEnum.EYETRACKING: DataTypeEnum.EYETRACKING,
            TransferDataTypeEnum.MEG: DataTypeEnum.MEG,
            TransferDataTypeEnum.MRI: DataTypeEnum.MRI,
            TransferDataTypeEnum.ECOG: DataTypeEnum.ECOG,
            TransferDataTypeEnum.SPIKE: DataTypeEnum.SPIKE,
            TransferDataTypeEnum.EMG: DataTypeEnum.EMG,
            TransferDataTypeEnum.ECG: DataTypeEnum.ECG,
            TransferDataTypeEnum.NIRS: DataTypeEnum.NIRS,
        }
        return data_type_map.get(transfer_data_type, DataTypeEnum.UNKNOWN)
