import logging
import grpc


class GrpcClient:
    def __init__(self, service_address: str):
        self.__service_address = service_address  # 标准格式:'localhost:19981'
        self.__channel: grpc.Channel = None
        # 最大单次消息长度1GB
        self.__channel_options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]
        self.__logger = logging.getLogger("centralControllerLogger")

    def get_stub_instance(self, stub_class: type):
        if self.__channel is None:
            raise RuntimeError("Channel is not open.")
        return stub_class(self.__channel)

    def startup(self):
        self.__channel = grpc.insecure_channel(self.__service_address, options=self.__channel_options)
        self.__logger.info(f"gRPC channel created to {self.__service_address}")

    def shutdown(self):
        self.__channel.close()
        self.__logger.info("gRPC channel closed")

    def __enter__(self):
        self.startup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False
