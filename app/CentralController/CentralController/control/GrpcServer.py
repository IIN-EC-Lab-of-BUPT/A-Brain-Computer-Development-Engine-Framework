import logging
from typing import Union

import grpc
from injector import inject


class GrpcServer:

    @inject
    def __init__(self):
        self.__rpc_address: str = None
        self.__server: grpc.aio.Server = None
        self.__logger = logging.getLogger("centralControllerLogger")
        self.__servicer_dict = dict[object, callable]()
        self.__channel_options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]

    def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if config_dict is None:
            return
        ui_config = config_dict.get('ui_config', None)
        self.__rpc_address = ui_config.get('rpc_address', None)

    def update(self, config_dict: dict[str, Union[str, dict]]) -> None:
        if config_dict is None:
            return
        ui_config = config_dict.get('ui_config', None)
        self.__rpc_address = ui_config.get('rpc_address', None)

    def add_servicer_to_server(self, servicer, add_servicer_func: callable):
        self.__servicer_dict[servicer] = add_servicer_func

    async def startup(self):
        if self.__rpc_address is None:
            return
        self.__logger.info("Starting GRPC Server")
        self.__server = grpc.aio.server(options=self.__channel_options)
        for servicer, add_servicer_func in self.__servicer_dict.items():
            add_servicer_func(servicer, self.__server)
            self.__logger.debug(f"GRPC Server add servicer {servicer}")
        listen_addr = self.__rpc_address
        self.__server.add_insecure_port(listen_addr)
        await self.__server.start()
        self.__logger.info(f"GRPC Server listening on {listen_addr}")
        self.__logger.info("GRPC Server started")

    async def shutdown(self):
        if self.__server is None:
            return
        self.__logger.info("准备停止GRPC Server")
        await self.__server.stop(1)
        self.__logger.info("GRPC Server 已停止")

    def delete(self):
        self.__server = None
