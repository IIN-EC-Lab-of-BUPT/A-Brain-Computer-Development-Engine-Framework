import logging

from injector import inject

from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface

from CentralController.facade.interface.SubsystemConnectorInterface import StimulatorConnectorInterface
from Stimulator.api.converter.CommandControlMessageConverter import StimulationSystemCommandControlMessageConverter
from Stimulator.api.converter.RandomNumberSeedsMessageConverter import RandomNumberSeedsMessageConverter
from Stimulator.api.message.MessageKeyEnum import MessageKeyEnum

from Stimulator.api.model.CommandControlModel import StimulationControlModel, StartStimulationControlModel, \
    StopStimulationControlModel, QuitStimulationControlModel
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel


class StimulatorConnector(StimulatorConnectorInterface):

    @inject
    def __init__(self, component_framework: ComponentFrameworkInterface):
        self.__logger = logging.getLogger('centralControllerLogger')
        self.__component_framework = component_framework

    async def start_stimulation(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = StimulationControlModel(
            package=StartStimulationControlModel()
        )
        proto = StimulationSystemCommandControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def stop_stimulation(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = StimulationControlModel(
            package=StopStimulationControlModel()
        )
        proto = StimulationSystemCommandControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def send_random_number_seeds(self, random_number_seeds: float, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.RANDOM_NUMBER_SEEDS.value}"
        send_model = RandomNumberSeedsModel(
            seeds=random_number_seeds
        )
        proto = RandomNumberSeedsMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())

    async def application_exit(self, component_id: str):
        message_key = f"{component_id}.{MessageKeyEnum.COMMAND_CONTROL.value}"
        send_model = StimulationControlModel(
            package=QuitStimulationControlModel()
        )
        proto = StimulationSystemCommandControlMessageConverter.model_to_protobuf(send_model)
        await self.__component_framework.send_message(message_key, proto.SerializeToString())
