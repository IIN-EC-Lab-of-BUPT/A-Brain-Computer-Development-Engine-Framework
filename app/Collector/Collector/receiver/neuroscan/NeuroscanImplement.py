import asyncio
import logging
import os
import socket
import time
from typing import Union, Dict
import matplotlib.pyplot as plt

import numpy as np
import yaml

from Collector.receiver.exception.ReceiverException import ReceiverConnectionException
from Collector.receiver.interface.NeuroscanEEGInterface import NeuroScanEEGInterface
from Collector.receiver.interface.ReceiverInterface import ReceiverInterface
from Collector.receiver.model.NeuroscanMessage import NeuroScanMessage, ChannelInfoOffsets
from Collector.receiver.model.ReceiverTransferModel import DeviceTransferModel, TransferDataTypeEnum, \
    ReceiverTransferModel, EventTransferModel, DataTransferModel


class NeuroscanImplement(ReceiverInterface):
    def __init__(self):
        super().__init__()

        self.__info = None
        self.__data_byte_width = 4
        self.__downsampling_factor: int = 4  # 降采样因子，默认为1为不降采样。采用N抽1的方式降采样。
        self.__send_flag = None

        self.__device_transfer_model: DeviceTransferModel = None
        self.__logger = logging.getLogger("collectorLogger")
        self.__amplifier_reader: asyncio.StreamReader = None
        self.__amplifier_writer: asyncio.StreamWriter = None
        self.__amplifier_socket: socket = None
        self.__connect_address: str = None

        self.__amplifier_connect_flag = None
        self.__logger = logging.getLogger("collectorLogger")
        self.openflag = None
        # 接收数据包的长度
        self.n_chan = 0
        self.chanInfoLen = 0

        self.__read_data_task: asyncio.Task = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        receiver_config_file_name = 'NeuroScan.yml'
        receiver_config_path = os.path.join(directory_path, receiver_config_file_name)
        with open(receiver_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)

        connection_dict = self.__config_dict.get("connection", dict())
        self.__connect_address = connection_dict.get("connect_address", dict())
        self.__max_connection_timeout = connection_dict.get("max_connection_timeout", 0)

        send_config_dict = self.__config_dict.get("send_config", dict())
        self.__send_package_points = send_config_dict.get("send_package_points", 0)

        n_chan = self.__config_dict.get("device_info", dict())
        self.n_chan = n_chan.get("n_chan", 0)

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

        info = await self.__get_device_info()
        self.__config_dict['info'] = info

        channellabels = await self.__requestChannelInfo()
        self.__config_dict['channellabels'] = channellabels

        self.__device_transfer_model = DeviceTransferModel(
            data_type=TransferDataTypeEnum.EEG,
            channel_number=self.__info.get("eegChan", None) - 1,
            sample_rate=self.__info.get("sampleRate", None),
            channel_label=self.__info.get("channelLabels", []),
            other_information=self.__info.get("other_information", dict())
        )

        self.__read_data_task = asyncio.create_task(self.__read_data(self.__amplifier_reader))
        # 初始化启始点数位置
        self.__current_date_position = 0
        self.__logger.info(f"{self.__connect_address}放大器连接成功")

    async def __read_data(self, reader: asyncio.StreamReader):
        while True:
            try:
                sendStartStreaming = NeuroScanMessage().startStreaming()
                sendStartStreaming = sendStartStreaming.tobytes()

                self.__amplifier_writer.write(sendStartStreaming)
                message, data = await self.__clientProcess()

                if (self.__info['eegChan'] != self.n_chan + 1):
                    self.__logger.error(f"通道数不匹配: self.n_chan={self.n_chan}, eegChan={self.__info['eegChan']}")
                    raise Exception("通道数不匹配")

                if (message['code'] == 2):  # 接收到数据包
                    t = 'data'
                    # self.__logger.info("接收到数据包")
                    if data.any():
                        if self.__send_flag:
                            data_list = self.__processPacket(data)
                            for data in data_list:
                                await self._receiver_transponder.send_data(data)
                                self.__logger.info("发送处理数据完毕")
                        else:
                            self.__logger.info("未发送数据")
                    else:
                        pass

                if (message['code'] == 3):  # 接收事件
                    t = 'event'
                    self.__logger.info("接收到事件")

                if (message['code'] == 4):  # 接收阻抗
                    t = 'impedance'
                    self.__logger.info("接收到阻抗")

            except Exception as e:
                print("错误类型：", e)

    def __processPacket(self, data) -> list[ReceiverTransferModel]:
        if self.__info['datasize'] == 2:
            data = data.view(np.int16)
        elif self.__info['datasize'] == 4:
            data = data.view(np.single)

        # 重塑二维矩阵，并上下翻转，使得数据按照时间先后顺序排列
        numSamples = int(len(data) / self.__info['eegChan'])
        data_array = data.reshape(numSamples, self.__info['eegChan'])
        data_array = data_array.T

        # 去除基线
        data_array = data_array - np.repeat(np.median(data_array, axis=-1, keepdims=True), numSamples, axis=1)
        # self.__logger.info(f"重塑二维矩阵: {data_array}")


        # 判断是否需要降采样
        if self.__downsampling_factor is not None and self.__downsampling_factor != 1:
            data_array = self.__downsample(data_array, self.__downsampling_factor)

        new_data_array = np.delete(data_array, -1, axis=0)  # 删除trigger通道，并将其单独存储
        trigger_array = data_array[-1, :]
        receiver_transfer_model_list = list[ReceiverTransferModel]()
        event_position_array = np.where(trigger_array != 0)[0]
        for event_position in event_position_array:
            event_data = trigger_array[event_position]

            # -----------------------------------------------------------------------------------------------
            # 如果trigger发送和接收不一致，可能是并口线序问题，在这里进行线序修正 如果不需要线序修正，注释掉此方法即可
            # binary_str = format(int(event_data), '08b')
            # # 按照交换规则重新排列位
            # swapped_str = str((int(binary_str[0])) or (int(binary_str[7]))) + binary_str[7] + binary_str[6] + \
            #               binary_str[5] + binary_str[4] + binary_str[3] + binary_str[2] + binary_str[1]
            # # 将二进制字符串转换回整数
            # swapped_value = int(swapped_str, 2)
            # event_data = swapped_value
            # 线序修正结束
            # -----------------------------------------------------------------------------------------------

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

        self.__current_date_position = self.__current_date_position + numSamples / self.__downsampling_factor
        return receiver_transfer_model_list

    async def __get_device_info(self):
        self.openflag = True
        while self.__amplifier_connect_flag:
            sendBasicInfo = NeuroScanMessage().getBasicInfo()
            # 发送header信息
            sendBasicInfo = sendBasicInfo.tobytes()
            self.__amplifier_writer.write(sendBasicInfo)

            # 接收消息（包括消息头和消息体）
            message, data = await self.__clientProcess()

            size = np.uint8(data[0:4]).copy().view(dtype=np.uint32)
            eegChan = np.uint8(data[4:8]).copy().view(np.uint32)
            sampleRate = np.uint8(data[8:12]).copy().view(np.uint32)
            datasize = np.uint8(data[12:16]).copy().view(np.uint32)
            if (eegChan > 100000):
                continue
            elif (len(eegChan) == 0 and len(datasize) == 0):
                eegChan = 1
                size = 24
                sampleRate = 1000
                datasize = [4]
            else:
                self.openflag = False

            self.__logger.info(
                f"requestINFO: size={size}, eegChan={eegChan}, sampleRate={sampleRate}, datasize={datasize}")
            # 从消息体中获取Info
            info = {
                'size': size,
                'eegChan': int(eegChan),
                'sampleRate': float(sampleRate[0]),
                'datasize': datasize[0]
            }

            self.__info = info
            return self

    async def __requestChannelInfo(self):
        # Offsets in CURRY struct( in bytes)
        offset_channelId = ChannelInfoOffsets.offset_channelId
        offset_chanLabel = ChannelInfoOffsets.offset_chanLabel
        offset_chanType = ChannelInfoOffsets.offset_chanType
        offset_deviceType = ChannelInfoOffsets.offset_deviceType
        offset_eegGroup = ChannelInfoOffsets.offset_eegGroup
        offset_posX = ChannelInfoOffsets.offset_posX
        offset_posY = ChannelInfoOffsets.offset_posY
        offset_posZ = ChannelInfoOffsets.offset_posZ
        offset_posStatus = ChannelInfoOffsets.offset_posStatus
        offset_bipolarRef = ChannelInfoOffsets.offset_bipolarRef
        offset_addScale = ChannelInfoOffsets.offset_addScale
        offset_isDropDown = ChannelInfoOffsets.offset_isDropDown
        offset_isNoFilter = ChannelInfoOffsets.offset_isNoFilter

        chanInfoLen = ChannelInfoOffsets.get_chan_info_len()
        self.chanInfoLen = chanInfoLen

        sendchannelInfo = NeuroScanMessage().getChannelInfo()
        sendchannelInfo = sendchannelInfo.tobytes()

        self.__amplifier_writer.write(sendchannelInfo)

        message, data = await self.__clientProcess()
        numChannels = self.__info['eegChan']
        channelLabels = []
        for i in range(numChannels):
            j = chanInfoLen * i
            chanLabel = data[j + offset_chanLabel - 1: j + offset_chanType - 1]
            chanLabel = chanLabel[:16]
            chanLabel = [chr(code) for code in chanLabel if code != 0]
            chanLabel = ''.join(chanLabel)
            channelLabels.append(chanLabel)

        self.__info['channelLabels'] = channelLabels
        self.__logger.info(f"channelLabels:{channelLabels}")
        return self

    async def __clientProcess(self):
        headSize = 20
        head = await self.__amplifier_reader.readexactly(headSize)
        head = np.frombuffer(head, dtype=np.uint8)
        message = self.__parseHeader(head)
        if message["packetSize"] == 0:
            self.__logger.error(f"包的大小为0")
        # 根据消息头中的长度接收消息体
        data = await self.__amplifier_reader.readexactly(message['packetSize'])
        data = np.frombuffer(data, dtype=np.uint8)
        return message, data

    def __parseHeader(self, head):
        # parsing head
        # 颠倒矩阵顺序
        code = np.flip(head[4:6]).copy().view(dtype=np.uint16)
        request = np.flip(head[6:8]).copy().view(np.uint16)
        startSample = np.flip(head[8:12]).copy().view(np.uint32)
        packetSize = np.flip(head[12:16]).copy().view(np.uint32)

        message = {
            'code': code,
            'request': request,
            'startSample': startSample[0],
            'packetSize': packetSize[0]
        }

        return message

    async def start_data_sending(self) -> None:
        self.__send_flag = True

    async def stop_data_sending(self) -> None:
        self.__send_flag = False

    async def send_device_info(self) -> None:
        await self._receiver_transponder.send_data(ReceiverTransferModel(package=self.__device_transfer_model))
        self.__logger.info("发送设备信息")

    async def send_impedance(self) -> None:
        pass

    async def shutdown(self) -> None:
        self.__amplifier_connect_flag = False
        await self.__read_data_task
        self.__amplifier_writer.close()
        await self.__amplifier_writer.wait_closed()

    def __downsample(self, data_array: np.ndarray, downsampling_factor: int) -> np.ndarray:
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
