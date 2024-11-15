import asyncio
import logging
import os
import socket
from typing import Union

import aiofiles
import numpy as np
import yaml

from ApplicationFramework.api.interface.ComponentFrameworkOperatorInterface import ReceiveMessageOperatorInterface
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Collector.receiver.interface.ReceiverInterface import EEGReceiverInterface
from Collector.receiver.model.ReceiverTransferModel import DeviceTransferModel, TransferDataTypeEnum, \
    ReceiverTransferModel, InformationTransferModel, EventTransferModel, DataTransferModel
from Collector.receiver.virtual_receiver.api.converter.VirtualReceiverCustomControlMessageConverter import \
    VirtualReceiverCustomControlMessageConverter
from Collector.receiver.virtual_receiver.api.message.VirtualReceiverMessageKeyEnum import (
    VirtualReceiverMessageKeyEnum)
from Collector.receiver.virtual_receiver.api.model.VirtualReceiverCustomControlModel import \
    VirtualReceiverCustomControlModel
from Collector.receiver.virtual_receiver.exception.VirtualReceiverException import VirtualReceiverFileNotFoundException
from Collector.receiver.virtual_receiver.model.DataFileModel import DataFileModel
from Collector.receiver.virtual_receiver.api.proto.VirtualReceiverCustomControl_pb2 import (
    VirtualReceiverCustomControlMessage as VirtualReceiverCustomControlMessage_pb2)


class VirtualReceiverImplement(EEGReceiverInterface):

    def __init__(self):
        super().__init__()

        # 已经包含 self._receiver_transponder
        # 已经包含 self._component_framework
        self.__virtual_receiver_command_control_topic: str = None
        self.__data_byte_width = 4  # 假设是数据是float32，每个浮点数占用4个字节
        self.__downsampling_factor: int = 1   # 降采样因子，默认为1为不降采样。采用N抽1的方式降采样。

        self.__amplifier_socket: socket = None
        self.__send_package_points: int = 0
        self.__device_transfer_model: DeviceTransferModel = None
        self.__config_dict: dict[str, Union[str, dict]] = None

        self.__logger = logging.getLogger("collectorLogger")
        # 数据发送文件缓存
        self.__data_files_model_list: list[DataFileModel] = list()

        # 记录应该从哪个data_file_model开始读取
        self.__current_data_file_model_index: int = 0

        # 单次读取并发送数据包字节长度
        self.__cache_bytes_number: int = 0
        self.__current_date_position = 0
        # 缓存被试者block信息
        self.__subject_block_dict: dict[str, int] = dict()

        self.__read_data_task: asyncio.Task = None

        self.__send_flag_event: asyncio.Event = asyncio.Event()

        self.__shutdown_flag: bool = False

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        receiver_config_file_name = 'VirtualReceiverConfig.yml'
        receiver_config_path = os.path.join(directory_path, receiver_config_file_name)
        with open(receiver_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)

        message_dict = self.__config_dict.get("message", dict())
        self.__virtual_receiver_command_control_topic = message_dict.get(
            VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value, None)

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
        data_files_dict = self.__config_dict.get("data_files", dict())
        self.__data_files_model_list = [
            DataFileModel(subject_id, file_path)
            for subject_id, file_paths in data_files_dict.items()
            for file_path in file_paths
        ]

        # 计算单次读取并发送数据包字节长度
        self.__cache_bytes_number = (
                self.__send_package_points *
                (self.__device_transfer_model.channel_number + 1) *
                self.__data_byte_width
        )

    async def startup(self) -> None:
        # 初始化点数记录
        self.__current_date_position = 0
        self.__shutdown_flag = False

        # 绑定虚拟接收器控制指令
        await self._component_framework.bind_message(
            MessageBindingModel(
                message_key=VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value,
                topic=self.__virtual_receiver_command_control_topic
            )
        )

        # 订阅管理message_key
        class ReceiveVirtualReceiverCustomControlMessageOperator(ReceiveMessageOperatorInterface):
            def __init__(self, virtual_receiver: VirtualReceiverImplement):
                self.__virtual_receiver: VirtualReceiverImplement = virtual_receiver

            async def receive_message(self, data: bytes) -> None:
                virtual_receiver_custom_control_model = VirtualReceiverCustomControlMessageConverter.protobuf_to_model(
                    VirtualReceiverCustomControlMessage_pb2.FromString(data)
                )
                await self.__virtual_receiver.custom_control(virtual_receiver_custom_control_model)

        await self._component_framework.subscribe_message(
            VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value,
            ReceiveVirtualReceiverCustomControlMessageOperator(virtual_receiver=self)
        )

        # 启动数据读取任务
        self.__read_data_task = asyncio.create_task(self.__read_data())

    async def start_data_sending(self) -> None:
        self.__send_flag_event.set()

    async def stop_data_sending(self) -> None:
        self.__send_flag_event.clear()

    async def send_device_info(self) -> None:
        await self._receiver_transponder.send_data(ReceiverTransferModel(package=self.__device_transfer_model))

    async def send_impedance(self) -> None:
        pass

    async def shutdown(self) -> None:
        # 取消订阅管理message_key
        await self._component_framework.unsubscribe_message(
            VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value)
        # 防止发送数据卡死，使之能够正常退出
        self.__send_flag_event.set()
        self.__shutdown_flag = True
        await self.__read_data_task

    async def custom_control(self, virtual_receiver_custom_control_model: VirtualReceiverCustomControlModel):
        # 目前只有information_package_model一种控制
        information_package_model = virtual_receiver_custom_control_model.package
        subject_id = information_package_model.subject_id
        block_id = int(information_package_model.block_id)
        block_index = 0
        index = 0
        for data_file_model in self.__data_files_model_list:
            if data_file_model.subject_id == subject_id:
                block_index = block_index + 1
                if block_index == block_id:
                    self.__current_data_file_model_index = index
            index = index + 1

    async def __read_data(self) -> None:
        # 等待数据发送事件置位
        await self.__send_flag_event.wait()
        workspace_path = os.getcwd()
        for data_file_model in self.__data_files_model_list[self.__current_data_file_model_index:]:
            # 如果收到关闭信号，则退出数据读取函数
            if self.__shutdown_flag:
                return
            subject_id = data_file_model.subject_id
            data_file_path = os.path.join(workspace_path, data_file_model.file_path)
            # 检查一下指定文件路径是否存在
            if not os.path.exists(data_file_path):
                try:
                    raise FileNotFoundError(f"{data_file_path} not found")
                except FileNotFoundError as e:
                    raise VirtualReceiverFileNotFoundException(f"{data_file_path} not found") from e
            self.__logger.info(f"开始读取{data_file_path}数据")
            file = await aiofiles.open(data_file_path, 'rb')
            try:
                # 新文件先发送人员信息
                self.__subject_block_dict[subject_id] = self.__subject_block_dict.get(subject_id, 0) + 1
                subject_block_information_message_model = ReceiverTransferModel(
                    package=InformationTransferModel(
                        subject_id=subject_id,
                        block_id=str(self.__subject_block_dict[subject_id])
                    )
                )
                await self._receiver_transponder.send_data(subject_block_information_message_model)
                while not self.__shutdown_flag:
                    await asyncio.sleep(0)  # 允许切换协程到其他任务
                    # 等待数据发送事件置位
                    await self.__send_flag_event.wait()
                    if self.__shutdown_flag:
                        break
                    data_bytes = await file.read(self.__cache_bytes_number)
                    if not data_bytes:
                        # 如果读取不到数据，表示文件读取完毕
                        break
                    # 处理数据
                    receiver_transfer_model_list = self.__preprocess_data(data_bytes)
                    for receiver_transfer_model in receiver_transfer_model_list:
                        await self._receiver_transponder.send_data(receiver_transfer_model)
            except Exception as e:
                self.__logger.exception(f"read data error: {e}")
            finally:
                await file.close()
                self.__logger.info(f"{data_file_path}数据读取完毕")

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
                        event_data=[str(int(event_data))]) # event务必先转换为整数再转换为字符串，否则无法识别
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
