import logging

from injector import inject

from Collector.api.converter.ExternalTriggerMessageConverter import ExternalTriggerMessageConverter
from Collector.api.protobuf.ExternalTriggerService_pb2_grpc import ExternalTriggerServiceServicer

from Collector.service.interface.TransponderInterface import InformationTransponderInterface
from google.protobuf.empty_pb2 import Empty


class ExternalTriggerServer(ExternalTriggerServiceServicer):

    @inject
    def __init__(self, information_transponder: InformationTransponderInterface):
        self.__information_transponder: InformationTransponderInterface = information_transponder
        self.__logger = logging.getLogger("collectorLogger")

    async def trigger(self, request, context):
        external_trigger_model = ExternalTriggerMessageConverter.protobuf_to_model(request)
        await self.__information_transponder.receiver_external_trigger(external_trigger_model)
        self.__logger.debug(f"received external trigger message {external_trigger_model}")
        return Empty()

    def connect(self, request: Empty, context):
        return Empty()
