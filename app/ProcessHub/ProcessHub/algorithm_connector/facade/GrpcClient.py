import logging

from grpc import aio


class GrpcClient:
    def __init__(self, service_address: str):
        self.__service_address = service_address  # 标准格式:'localhost:19981'
        self.__channel: aio.Channel = None
        # 最大单次消息长度1GB
        self.__channel_options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]
        self.__logger = logging.getLogger("processHubLogger")

    def get_stub_instance(self, stub_class: type):
        if self.__channel is None:
            raise RuntimeError("Channel is not open.")
        return stub_class(self.__channel)

    async def startup(self):
        self.__channel = aio.insecure_channel(self.__service_address, options=self.__channel_options)
        self.__logger.info(f"gRPC channel created to {self.__service_address}")

    async def shutdown(self):
        await self.__channel.close()
        self.__logger.info("gRPC channel closed")

    async def __aenter__(self):
        await self.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
        return False
