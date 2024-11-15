import asyncio
import logging
import time
from typing import Union

import numpy

from Collector.api.message.MessageKeyEnum import MessageKeyEnum
from Collector.api.model.ExternalTriggerModel import ExternalTriggerModel
from Collector.datasender.interface.DataSenderInterface import DataSenderInterface
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import (DataMessageModel, DataPackageModel, EventPackageModel, DevicePackageModel,
                                             ImpedancePackageModel, InformationPackageModel)


class TimingDataSender(DataSenderInterface):
    """
    计时数据发送器
    数据包发送时先记录当前数据点数和时间，当到达指定时间后才发送数据包
    """

    def __init__(self):
        super().__init__()
        self.__cached_external_trigger_list: list[ExternalTriggerModel] = list[ExternalTriggerModel]()
        self.__start_data_sending_time: float = 0.0
        self.__sample_rate: float = 0.0
        self.__channel_number: int = 0
        self.__sending_flag: bool = False
        self.__logger = logging.getLogger("collectorLogger")

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        # 清理缓存内容
        self.__cached_external_trigger_list.clear()

    async def start_data_sending(self):
        if self.__sending_flag:
            return
        else:
            self.__sending_flag = True
            # 计算起始时间
            self.__start_data_sending_time = time.perf_counter()

    async def stop_data_sending(self):
        self.__sending_flag = False

    async def send_data(self, data_message_model: DataMessageModel) -> None:
        # 如果不属于预定义的类型则不发送
        if not isinstance(data_message_model.package,
                          Union[
                              DevicePackageModel,
                              EventPackageModel,
                              DataPackageModel,
                              ImpedancePackageModel,
                              InformationPackageModel,
                          ]):
            return
        # 如果不是运行状态则不发送事件类型数据包合数据类型数据包
        if isinstance(data_message_model.package, Union[DataPackageModel, EventPackageModel]) and not self.__sending_flag:
            return

        # 检查是否有缓存的external_trigger，如果有，则打包该trigger，并按照list顺序以当前数据data_position的位置依次+1并发送
        # 如果包内数据对应位置已有trigger，则会在算法端覆盖
        match data_message_model.package:
            case DevicePackageModel():
                await self.__device_package_func(data_message_model)
            case DataPackageModel():
                await self.__data_package_func(data_message_model)
            case _:
                await self.__default_func(data_message_model)

    async def receiver_external_trigger(self, external_trigger_model: ExternalTriggerModel) -> None:
        # 收到外部trigger，缓存入list，待下一次数据发送时发出
        self.__cached_external_trigger_list.append(external_trigger_model)

    async def __device_package_func(self, data_message_model: DataMessageModel):
        device_package_model: DevicePackageModel = data_message_model.package
        self.__sample_rate = device_package_model.sample_rate
        self.__channel_number = device_package_model.channel_number
        await self._component_framework.send_message(
            MessageKeyEnum.SEND_DATA.value,
            CommonMessageConverter.model_to_protobuf(data_message_model).SerializeToString()
        )

    async def __data_package_func(self, data_message_model: DataMessageModel):
        current_time = time.perf_counter()
        data_package_model: DataPackageModel = data_message_model.package
        # 判断数据类型并转换
        if isinstance(data_package_model.data, list):
            if len(data_package_model.data) > 0:
                first_data = data_package_model.data[0]
                if isinstance(first_data, float):
                    data_package_model.data = numpy.ndarray(data_package_model.data, dtype=numpy.float32)
                elif isinstance(first_data, int):
                    data_package_model.data = numpy.ndarray(data_package_model.data, dtype=numpy.int32)
        elif isinstance(data_package_model.data, numpy.ndarray):
            if data_package_model.data.dtype == numpy.float64:
                data_package_model.data = data_package_model.data.astype(numpy.float32)
            elif data_package_model.data.dtype == numpy.int64:
                data_package_model.data = data_package_model.data.astype(numpy.int32)

        this_data_position = data_package_model.data_position
        data_message_class = type(data_package_model.data)
        this_data_end_point = this_data_position + (len(data_package_model.data) / self.__channel_number) - 1 \
            if data_message_class in [list, numpy.ndarray] else this_data_position

        # 计算所需等待时间
        wait_time = (this_data_end_point / self.__sample_rate)-(current_time - self.__start_data_sending_time)
        self.__logger.debug(f"当前距离发送开始时间:{current_time - self.__start_data_sending_time},"
                            f"数据包末尾时间{this_data_end_point / self.__sample_rate},"
                            f"所需等待时间:{wait_time}")
        # 如果当前时间已经比数据时间延后，则立刻返送，反之根据数据点数等待指定时间
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        for external_trigger_index, external_trigger in enumerate(self.__cached_external_trigger_list):
            event_package_model = EventPackageModel(
                event_position=[this_data_position + external_trigger_index],
                event_data=[external_trigger.trigger]
            )
            await self._component_framework.send_message(
                MessageKeyEnum.SEND_DATA.value,
                CommonMessageConverter.model_to_protobuf(event_package_model).SerializeToString()
            )
        # 清理缓存
        self.__cached_external_trigger_list.clear()
        await self._component_framework.send_message(
            MessageKeyEnum.SEND_DATA.value,
            CommonMessageConverter.model_to_protobuf(data_message_model).SerializeToString()
        )
        self.__logger.debug(f"发送数据包，当前距离发送开始时间:{time.perf_counter() - self.__start_data_sending_time}")

    async def __default_func(self, data_message_model: DataMessageModel):
        await self._component_framework.send_message(
            MessageKeyEnum.SEND_DATA.value,
            CommonMessageConverter.model_to_protobuf(data_message_model).SerializeToString()
        )
