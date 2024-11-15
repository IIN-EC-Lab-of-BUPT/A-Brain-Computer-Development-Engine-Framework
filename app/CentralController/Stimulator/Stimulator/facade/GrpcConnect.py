from typing import Union
import grpc
from injector import inject
from Stimulator.facade.interface.TriggerSystemInterface import GrpcConnectInterface


class GrpcConnector(GrpcConnectInterface):
    @inject
    def __init__(self):
        self.__config_dict = None
        self.__rpc_listen_address = None
        self.channel = None
        self.stub = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__config_dict = config_dict
        self.__rpc_listen_address = config_dict.get('external_trigger_address')

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        self.__config_dict = config_dict
        self.__rpc_listen_address = config_dict.get('external_trigger_address')

    async def open(self):
        channel_options = [
            ('grpc.max_receive_message_length', 1089600010),  # 设置最大接收消息大小
        ]
        self.channel = grpc.aio.insecure_channel(self.__rpc_listen_address, options=channel_options)
        # channel = grpc.insecure_channel('localhost:50051')

    async def shutdown(self):
        if self.channel is not None:
            await self.channel.close()

    def initial_stub(self):
        return self.channel


