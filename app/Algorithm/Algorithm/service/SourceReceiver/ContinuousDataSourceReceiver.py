import asyncio
import bisect
import logging
import math
from asyncio import Queue
from collections import deque
from dataclasses import dataclass
from typing import Union

import numpy as np

from Algorithm.method.model.AlgorithmObject import AlgorithmContinuousDataObject, AlgorithmDeviceObject
from Algorithm.service.exception.AlgorithmSourceException import AlgorithmSourceReceiverIsTurnedOffException
from Algorithm.service.interface.SourceReceiverInterface import SourceReceiverInterface
from Common.converter.BaseDataClassMessageConverter import BaseDataClassMessageConverter
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmDataMessageModel
from Common.model.CommonMessageModel import DevicePackageModel, EventPackageModel, DataPackageModel, \
    ImpedancePackageModel, ControlPackageModel, InformationPackageModel


@dataclass
class SingleEvent:
    event_position: int = None
    event_data: float = None

    def __lt__(self, other):
        # 比较两个SingleEvent对象的position属性
        return self.event_position < other.event_position

    def __le__(self, other):
        # 比较两个SingleEvent对象的position属性
        return self.event_position <= other.event_position


class ContinuousDataSourceReceiver(SourceReceiverInterface):

    def __init__(self):
        # 配置信息
        self.__source_label: str = ""
        # 设置多少个点一个数据包,如果为0，则不进行分块
        self.__chunk_size: int = 0
        self.__algorithm_device_object: AlgorithmDeviceObject = AlgorithmDeviceObject()
        self.__data_queue = Queue[AlgorithmContinuousDataObject]()  # 异步队列用于保存和读取数据
        self.__data_deque = deque[AlgorithmContinuousDataObject]()  # 配合异步队列用于检索和修改内部对象,用于做索引，降低计算开销
        self.__event_list = list[SingleEvent]()

        self.__base_data_class_message_converter = BaseDataClassMessageConverter()

        # 临时变量
        self.__device_information_write_event = asyncio.Event()
        self.__current_add_data_subject_id = None
        self.__current_add_data_block_id = None
        self.__current_data_cache = deque()
        # 缓存数据记录位置
        self.__current_data_cache_position = 0

        # 读取数据记录位
        self.__used_data_position = 0

        self.__model_class_for_operate_func_dict = {
            ControlPackageModel: self.__control_model_process,
            DevicePackageModel: self.__device_model_process,
            EventPackageModel: self.__event_model_process,
            DataPackageModel: self.__data_model_process,
            ImpedancePackageModel: self.__impedance_model_process,
            InformationPackageModel: self.__information_model_process,
        }

        self.__finish_flag = False

        self.__logger = logging.getLogger("algorithmLogger")

    def get_source_label(self) -> str:
        return self.__source_label

    def get_used_data_position(self) -> int:
        return self.__used_data_position

    async def get_data(self) -> AlgorithmContinuousDataObject:
        await asyncio.sleep(0)  # 允许协程切换
        if self.__finish_flag:
            raise AlgorithmSourceReceiverIsTurnedOffException("数据源已关闭")
        # 获取数据,同时弹出__data_queue和__data_deque的元素
        # 使用asyncio.queue做异步阻塞
        algorithm_data_object = await self.__data_queue.get()
        # 顺便弹出__data_deque的元素
        self.__data_deque.popleft()
        # self.__logger.debug(
        #     f"获取数据，data queue size{self.__data_queue.qsize()} data deque size {len(self.__data_deque)}")

        # 记录使用数据位置
        if algorithm_data_object.data is not None and algorithm_data_object.start_position is not None:
            self.__used_data_position = algorithm_data_object.start_position + algorithm_data_object.data.shape[1]

        # 如果获取到终止标记位，则标记源数据读取结束，下次再读取则抛出异常
        self.__finish_flag = algorithm_data_object.finish_flag
        return algorithm_data_object

    async def get_device(self) -> AlgorithmDeviceObject:
        await self.__device_information_write_event.wait()
        self.__logger.debug(f"获取设备信息{self.__algorithm_device_object}")
        return self.__algorithm_device_object

    async def set_message_model(self, message_model: AlgorithmDataMessageModel):
        package = message_model.package
        func = self.__model_class_for_operate_func_dict[type(package)]
        # self.__logger.debug(f"收到消息内容{type(package).__name__}")
        if asyncio.iscoroutinefunction(func):
            return await func(package)
        else:
            return func(package)

    def set_source_label(self, source_label: str):
        self.__source_label = source_label

    def set_configuration(self, configuration: dict[str, Union[str, dict]]):
        self.__chunk_size = configuration['chunk_size'] \
            if configuration is not None and 'chunk_size' in configuration else 0

    async def __control_model_process(self, control_model: ControlPackageModel):
        # 装入终止标记位
        if control_model.end_flag:
            # 判断数据缓冲区是否还有数据,如果有，则生成AlgorithmDataObject
            if len(self.__current_data_cache) > 0:
                # 获取数据
                new_data_list = [self.__current_data_cache.popleft() for _ in range(len(self.__current_data_cache))]
                # 生成 AlgorithmDataObject
                algorithm_data_object = self.__create_algorithm_data_object(new_data_list,
                                                                            self.__current_data_cache_position)
                await self.__data_queue.put(algorithm_data_object)
                self.__data_deque.append(algorithm_data_object)
                self.__current_data_cache_position += algorithm_data_object.data.shape[1]
            # 发送终止标记位
            finish_algorithm_data_object = AlgorithmContinuousDataObject(data=None,
                                                                         subject_id=None,
                                                                         finish_flag=control_model.end_flag)
            await self.__data_queue.put(finish_algorithm_data_object)
            self.__data_deque.append(finish_algorithm_data_object)
        return

    async def __data_model_process(self, data_model: DataPackageModel):
        # 获取数据，数据内容已转换为基础数据格式，可能为np.ndarray或者list()
        new_data = data_model.data
        if isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        self.__current_data_cache.extend(new_data)  # 新数据装入缓存队列
        channel_number = self.__algorithm_device_object.channel_number
        if self.__chunk_size == 0 or self.__chunk_size is None:
            package_length = len(new_data)
        else:
            package_length = self.__chunk_size * channel_number
        # 循环判断缓存队列是否达到一个数据包
        while len(self.__current_data_cache) >= package_length:
            new_data_list = [self.__current_data_cache.popleft() for _ in range(package_length)]
            # 生成 AlgorithmDataObject
            algorithm_data_object = self.__create_algorithm_data_object(new_data_list,
                                                                        self.__current_data_cache_position)
            # 插入用于保存数据的异步队列
            await self.__data_queue.put(algorithm_data_object)
            # 同时插入用于检索和修改内部对象
            self.__data_deque.append(algorithm_data_object)
            # 需要注意有可能有数据包不满的情况（如终止过一次）
            self.__current_data_cache_position = self.__current_data_cache_position + algorithm_data_object.data.shape[
                1]

    def __device_model_process(self, device_model: DevicePackageModel):

        # 实时更新设备信息
        self.__algorithm_device_object = AlgorithmDeviceObject(
            data_type=device_model.data_type.name,
            channel_number=device_model.channel_number,
            sample_rate=device_model.sample_rate,
            channel_label=device_model.channel_label,
            other_information=device_model.other_information,
        )
        self.__device_information_write_event.set()

    def __event_model_process(self, event_model: EventPackageModel):
        # 判断event_model.position是否在已有data_queue中，如果是则修改对应的AlgorithmDataObject，如果不是则加入__event_list。如果事件position已经小于第一个数据包，则丢弃
        # 将event_model中的event分解为多个SingleEvent
        single_event_list = [
            SingleEvent(event_position=int(event_model.event_position[i]), event_data=float(event_model.event_data[i]))
            for i in range(len(event_model.event_position))]

        for single_event in single_event_list:
            bisect.insort_left(self.__event_list, single_event)

        if len(self.__data_deque) == 0:
            return

        for single_event_index in range(len(self.__event_list) - 1, -1, -1):

            if self.__event_list[single_event_index].event_position \
                    > self.__data_deque[-1].start_position + self.__data_deque[-1].data.shape[1]:
                # 如果event的位置大于最后一个数据包中所有元素的位置，则跳过
                continue

            elif self.__event_list[single_event_index].event_position < self.__data_deque[0].start_position:
                # 如果event的位置小于第一个数据包中所有元素的位置，则删除之前所有事件记录，并退出（因为数据包已经被使用了）
                self.__event_list[:] = self.__event_list[single_event_index + 1:]
                return
            else:
                # 遍历数据包中的所有元素，找到第一个小于等于event的位置，且包内数据结尾大于等于event位置的包，然后插入event
                for data_index in range(len(self.__data_deque) - 1, -1, -1):
                    if self.__data_deque[data_index].start_position \
                            <= self.__event_list[single_event_index].event_position \
                            < self.__data_deque[data_index].start_position + \
                            self.__data_deque[data_index].data.shape[1]:
                        self.__insert_event_to_algorithm_data_object(
                            self.__data_deque[data_index],
                            self.__event_list[single_event_index])
                        self.__event_list.pop(single_event_index)
                        break

    def __impedance_model_process(self, impedance_model: ImpedancePackageModel):
        # 阻抗信息暂不处理
        return

    def __information_model_process(self, information_model: InformationPackageModel):
        self.__current_add_data_subject_id = information_model.subject_id
        self.__current_add_data_block_id = information_model.block_id

    def __create_algorithm_data_object(self, new_data_list: list[float], start_position: int) \
            -> AlgorithmContinuousDataObject:
        # 创建 AlgorithmDataObject
        channel_number = self.__algorithm_device_object.channel_number
        sample_number = len(new_data_list) / channel_number
        if not (isinstance(sample_number, int)
                or (math.floor(sample_number) == sample_number and not math.isnan(sample_number))):
            raise Exception("sample_number is not a integer")
        sample_number = int(sample_number)
        data = np.array(new_data_list)
        # 数据传入时是按照先通道再采样点，所以需要重塑
        data = data.reshape(sample_number, channel_number)
        data = data.T
        zero_row = np.zeros((1, data.shape[1]))  # 创建一个与重塑后 data 列数相同的全 0 行
        padded_data = np.concatenate((data, zero_row), axis=0)  # 将全 0 行添加到 data 的末尾，用于记录event

        # 判断是否有事件在当前数据包中
        event_index = len(self.__event_list) - 1
        while event_index >= 0 and self.__event_list[event_index].event_position >= start_position:
            # 如果当前事件的position大于等于start_position且小于start_position+data.shape[1]，则插入并从event_list中删除它
            if start_position <= self.__event_list[event_index].event_position < start_position + data.shape[1]:
                # 计算对应的event位置，并插入数据
                relative_position = self.__event_list[event_index].event_position - start_position
                padded_data[channel_number, relative_position] = self.__event_list[event_index].event_data
                # 从列表中删除指定位置的事件
                del self.__event_list[event_index]

            event_index = event_index - 1

        return AlgorithmContinuousDataObject(
            start_position=start_position,
            data=padded_data,
            subject_id=self.__current_add_data_subject_id,
            finish_flag=False)

    def __insert_event_to_algorithm_data_object(
            self, algorithm_data_object: AlgorithmContinuousDataObject, single_event: SingleEvent) \
            -> AlgorithmContinuousDataObject:
        # 计算相对位置
        relative_position = single_event.event_position - algorithm_data_object.start_position
        if relative_position < 0 or relative_position >= algorithm_data_object.data.shape[1]:
            raise ValueError("event_position is out of range")
        else:
            algorithm_data_object.data[self.__algorithm_device_object.channel_number, relative_position] = \
                single_event.event_data
        return algorithm_data_object
