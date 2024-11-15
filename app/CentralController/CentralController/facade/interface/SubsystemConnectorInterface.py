from abc import ABC, abstractmethod
from typing import Union


class SubsystemConnectorInterface(ABC):
    @abstractmethod
    async def application_exit(self, component_id: str):
        pass


class CollectorConnectorInterface(SubsystemConnectorInterface):

    @abstractmethod
    async def start_data_sending(self, component_id: str):
        pass

    @abstractmethod
    async def stop_data_sending(self, component_id: str):
        pass

    @abstractmethod
    async def send_device_info(self, component_id: str):
        pass

    @abstractmethod
    async def send_impedance(self, component_id: str):
        pass


class StimulatorConnectorInterface(SubsystemConnectorInterface):

    @abstractmethod
    async def start_stimulation(self, component_id: str):
        pass

    @abstractmethod
    async def stop_stimulation(self, component_id: str):
        pass

    @abstractmethod
    async def send_random_number_seeds(self, random_number_seeds: float, component_id: str):
        pass


class ProcessorConnectorInterface(SubsystemConnectorInterface, ABC):
    @abstractmethod
    async def initial(self):
        pass

    @abstractmethod
    async def startup(self):
        pass

    @abstractmethod
    async def shutdown(self):
        pass

    @abstractmethod
    async def start_processor_container(self):
        pass

    @abstractmethod
    async def stop_processor_container(self):
        pass


class DataStorageConnectorInterface(SubsystemConnectorInterface):
    @abstractmethod
    async def start_receive(self, component_id: str):
        pass

    @abstractmethod
    async def stop_receive(self, component_id: str):
        pass


class DatabaseConnectorInterface(SubsystemConnectorInterface):
    @abstractmethod
    async def start_receive(self, component_id: str):
        pass

    @abstractmethod
    async def stop_receive(self, component_id: str):
        pass

