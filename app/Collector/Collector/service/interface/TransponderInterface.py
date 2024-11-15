from abc import abstractmethod

from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Collector.receiver.model.ReceiverTransferModel import ReceiverTransferModel
from Collector.service.interface.ServiceManagerInterface import ServiceManagerInterface


class ReceiverTransponderInterface(ServiceManagerInterface):
    @abstractmethod
    async def send_data(self, receiver_transfer_model: ReceiverTransferModel) -> None:
        pass


class InformationTransponderInterface(ReceiverTransponderInterface):
    """
    信息转发器接口
    """

    @abstractmethod
    async def receiver_external_trigger(self, external_trigger_model: ExternalTriggerModel) -> None:
        pass

    @abstractmethod
    async def start_data_sending(self):
        pass

    @abstractmethod
    async def stop_data_sending(self):
        pass

    @abstractmethod
    async def send_device_info(self):
        pass

    @abstractmethod
    async def send_impedance(self):
        pass
