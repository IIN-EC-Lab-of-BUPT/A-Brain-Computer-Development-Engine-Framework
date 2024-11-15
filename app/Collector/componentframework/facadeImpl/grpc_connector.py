import grpc
from injector import inject


class GrpcConnector(object):
    @inject
    def __init__(self, server_address: str, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.channel = None
        self.stub = None
        self.address_port = '{}:{}'.format(server_address, server_port)

    def connect(self):
        channel_options = [
            ('grpc.max_receive_message_length', 1089600010),  # 设置最大接收消息大小
        ]
        self.channel = grpc.aio.insecure_channel(self.address_port, options=channel_options)
        # channel = grpc.insecure_channel('localhost:50051')

    async def disconnect(self):
        if self.channel is not None:
            await self.channel.close()

    def initial_stub(self):
        return self.channel

    def set_grpc_connector_address(self, server_address: str, server_port: int):
        self.server_address = server_address
        self.server_port = server_port
        self.address_port = '{}:{}'.format(server_address, server_port)
