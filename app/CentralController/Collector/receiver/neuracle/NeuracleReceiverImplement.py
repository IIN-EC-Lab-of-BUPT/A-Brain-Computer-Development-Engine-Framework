import asyncio
import logging
import os
import socket
import time
from typing import Union

import numpy as np
import yaml

from Collector.receiver.interface.ReceiverInterface import EEGReceiverInterface
from Collector.receiver.exception.ReceiverException import ReceiverConnectionException
from Collector.receiver.model.ReceiverTransferModel import DeviceTransferModel, TransferDataTypeEnum, \
    ReceiverTransferModel, EventTransferModel, DataTransferModel


class NeuracleReceiverImplement(EEGReceiverInterface):

    def __init__(self):
        super().__init__()

        # 已经包含 self._receiver_transponder

        self.__data_byte_width = 4  # 假设是数据是float32，每个浮点数占用4个字节
        self.__downsampling_factor: int = 1   # 降采样因子，默认为1为不降采样。采用N抽1的方式降采样。

        self.__amplifier_reader: asyncio.StreamReader = None
        self.__amplifier_writer: asyncio.StreamWriter = None
        self.__amplifier_socket: socket = None
        self.__connect_address: str = None
        self.__max_connection_timeout: float = 0
        self.__send_package_points: int = 0
        self.__device_transfer_model: DeviceTransferModel = None
        self.__config_dict: dict[str, Union[str, dict]] = None

        self.__logger = logging.getLogger("collectorLogger")

        self.__cache_bytes_number: int = 0
        self.__current_date_position = 0
        self.__read_data_task: asyncio.Task = None

        self.__send_flag: bool = False

        self.__amplifier_connect_flag: bool = False

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        receiver_config_file_name = 'NeuracleReceiverConfig.yml'
        receiver_config_path = os.path.join(directory_path, receiver_config_file_name)
        with open(receiver_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)

        connection_dict = self.__config_dict.get("connection", dict())
        self.__connect_address = connection_dict.get("connect_address", dict())
        self.__max_connection_timeout = connection_dict.get("max_connection_timeout", 0)

        send_config_dict = self.__config_dict.get("send_config", dict())
        self.__send_package_points = send_config_dict.get("send_package_points", 0)

        device_info_dict = self.__config_dict.get("device_info", dict())
        self.__device_transfer_model = DeviceTransferModel(
            data_type=TransferDataTypeEnum.EEG,
            channel_number=device_info_dict.get("channel_number", None),
            sample_rate=device_info_dict.get("sample_rate", None),
            channel_label=list(device_info_dict.get("channel_label", dict()).keys()),
            other_information=device_info_dict.get("other_information", dict())
        )

        # 计算单次接收数据包字节长度
        self.__cache_bytes_number = (
                self.__send_package_points *
                (self.__device_transfer_model.channel_number + 1) *
                self.__data_byte_width
        )

    async def startup(self) -> None:
        # 尝试建立socket连接
        host, port = self.__connect_address.split(':')
        self.__logger.info(f"启动{self.__connect_address}放大器连接，最长等待时间{self.__max_connection_timeout}秒...")
        start_time = time.time()
        while True:
            try:
                self.__amplifier_reader, self.__amplifier_writer = await asyncio.open_connection(host, port)
                break
            except (ConnectionRefusedError, TimeoutError, OSError) as e:
                if time.time() - start_time > self.__max_connection_timeout != 0:
                    raise ReceiverConnectionException(
                        f"{self.__connect_address}放大器连接超时，请检查放大器是否正常运行"
                    ) from e
                await asyncio.sleep(1)
        self.__amplifier_connect_flag = True
        self.__read_data_task = asyncio.create_task(self.__read_data(self.__amplifier_reader))
        # 初始化启始点数位置
        self.__current_date_position = 0
        self.__logger.info(f"{self.__connect_address}放大器连接成功")

    async def start_data_sending(self) -> None:
        self.__send_flag = True

    async def stop_data_sending(self) -> None:
        self.__send_flag = False

    async def send_device_info(self) -> None:
        await self._receiver_transponder.send_data(ReceiverTransferModel(package=self.__device_transfer_model))

    async def send_impedance(self) -> None:
        pass

    async def shutdown(self) -> None:
        self.__amplifier_connect_flag = False
        await self.__read_data_task
        self.__amplifier_writer.close()
        await self.__amplifier_writer.wait_closed()

    async def __read_data(self, reader: asyncio.StreamReader) -> None:
        while self.__amplifier_connect_flag:
            # 从socket中整段读取数据
            await asyncio.sleep(0)  # 允许切换协程到其他任务
            data_bytes = await reader.readexactly(self.__cache_bytes_number)
            if data_bytes:
                # 根据self.__send_flag的值决定是否发送数据
                if self.__send_flag:
                    # 处理数据
                    data_message_model_list = self.__preprocess_data(data_bytes)
                    for data_message_model in data_message_model_list:
                        await self._receiver_transponder.send_data(data_message_model)
                else:
                    # 如果没有收到start指令，则丢弃数据
                    pass
            else:
                # 如果没有数据，跳出循环
                break

    def __preprocess_data(self, data_bytes: bytes) -> list[ReceiverTransferModel]:
        data_array = np.frombuffer(data_bytes, dtype=np.float32)
        sample_number = len(data_array) // (self.__device_transfer_model.channel_number + 1)
        # 数据传入时是按照先通道再采样点，所以需要重塑
        data_array = data_array.reshape(sample_number, self.__device_transfer_model.channel_number + 1)
        data_array = data_array.T
        # 判断是否需要降采样
        if self.__downsampling_factor is not None and self.__downsampling_factor != 1:
            data_array = self.__downsample(data_array, self.__downsampling_factor)

        new_data_array = np.delete(data_array, -1, axis=0)
        trigger_array = data_array[-1, :]
        receiver_transfer_model_list = list[ReceiverTransferModel]()
        # 寻找Event位置，提取data_array最后一行元素并寻找非0元素
        event_position_array = np.where(trigger_array != 0)[0]
        for event_position in event_position_array:
            event_data = trigger_array[event_position]
            receiver_transfer_model_list.append(
                ReceiverTransferModel(
                    package=EventTransferModel(
                        event_position=[event_position + self.__current_date_position],
                        event_data=[str(int(event_data))])  # event务必先转换为整数再转换为字符串，否则无法识别
                )
            )
        transfer_data = new_data_array.T.reshape(-1)
        transfer_data = transfer_data.astype(np.float32)  # 建议输出为np.float32，否则输出时也会强制转换为float32
        receiver_transfer_model_list.append(
            ReceiverTransferModel(
                package=DataTransferModel(
                    data_position=self.__current_date_position,
                    data=transfer_data,
                )
            )
        )
        self.__current_date_position = self.__current_date_position + sample_number
        return receiver_transfer_model_list

    @staticmethod
    def __downsample(data_array: np.ndarray, downsampling_factor: int) -> np.ndarray:
        """
        对输入数据进行整体降采样，以直接抽取的方式进行，抽取trigger时保留第一位非0元素
        :param data_array: 输入数据，行表示导联，列表示样本点，最后一行为trigger通道
        :param downsampling_factor: 整数降采样因子
        :return:
        """
        new_data_array = np.delete(data_array, -1, axis=0)
        downsampled_data_array = new_data_array[:, ::downsampling_factor]
        downsampled_trigger_array = np.zeros([1, downsampled_data_array.shape[1]])
        trigger_array = data_array[-1, :]
        trigger_index = np.where(trigger_array != 0)[0]
        new_trigger_index = trigger_index // downsampling_factor
        for i in range(len(new_trigger_index) - 1, -1, -1):
            downsampled_trigger_array[0, new_trigger_index[i]] = trigger_array[trigger_index[i]]

        downsampled_total_array = np.concatenate((downsampled_data_array, downsampled_trigger_array), axis=0)
        return downsampled_total_array
