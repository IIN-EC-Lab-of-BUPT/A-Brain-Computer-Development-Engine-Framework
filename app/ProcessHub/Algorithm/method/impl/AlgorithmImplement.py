import asyncio
from typing import Union

from Algorithm.method.interface.AlgorithmInterface import AlgorithmInterface
from Algorithm.method.impl.algorithm import FBCCA
from Algorithm.method.impl.algorithm import CCA

import numpy as np

from Algorithm.method.model.AlgorithmObject import AlgorithmResultObject
from datetime import datetime
import pickle


class AlgorithmImplement(AlgorithmInterface):

    def __init__(self, *args, **kwargs):
        # 继承父类，请务必保留
        super().__init__(*args, **kwargs)
        # 在此处初始化算法，请将预处理，io处理等操作放在此处
        '''
        内部已经初始化_proxy, 可通过self._proxy调用
        内部包含_end_flag标志位，当为True时，算法应自动退出,例如
        if self._end_flag:
            break
        '''
        self.__trial_start_trigger = [i for i in range(1, 41)]  # 根据赛题定义试次起始trigger
        self.__trial_end_trigger = 242  # 根据赛题定义试次终止trigger

        # 定义本算法参数
        self.__trial_duration = 3  # 定义所使用数据长度(s)

        # 定义赛题配置信息(必须在run()方法中才能够获取，初始化时)
        self.__challenge_config: dict[str, Union[str, dict]] = None

        freq_set = np.linspace(8, 15.8, 40)
        self.fbcca = FBCCA(frequency_set=freq_set)
        # self.fbcca = CCA(frequency_set=freq_set)
        self.i = 0

    async def run(self):
        try:
            # 是否停止标签
            data_finished_flag = False
            data_cache: np.ndarray = None  # 用于缓存数据
            data_cache_start_point = 0

            # 获取赛题相关配置信息(具体需参见赛题说明, 只能在run()方法中才能够获取）
            self.__challenge_config = self._proxy.get_challenge_config()

            # 读取数据源
            source_eeg = self._proxy.get_source('eeg_1')  # 如果存在多个源，可以依次读取
            source_eeg_device = await source_eeg.get_device()  # 获取数据源设备信息.采用异步模式，未获取则阻塞等待
            channel_number = source_eeg_device.channel_number
            # print(channel_number)# 获取数据源通道数
            sample_rate = source_eeg_device.sample_rate  # 获取数据源采样率

            trial_point = int(self.__trial_duration * sample_rate)  # 一个试次中所需要用到的数据点数

            # 循环读取数据,退出条件为 1、获取到数据结束标志 或者 2、外部停止标志为True （根据赛题要求设定退出条件）
            while not data_finished_flag and not self._end_flag:
                algorithm_data_object = await source_eeg.get_data()  # 读取数据务必使用await标签
                data_finished_flag = algorithm_data_object.finish_flag
                new_data = algorithm_data_object.data  # 获取新数据
                if new_data is None:
                    continue
                if data_cache is None:
                    data_cache = new_data
                else:
                    data_cache = np.concatenate((data_cache, new_data), axis=1)
                # print(data_cache)
                current_data_position = algorithm_data_object.start_position + new_data.shape[1]  # 实际上是当前所有获取的总点数
                search_point = max(0, current_data_position - trial_point)  # 需要截取trial_point的数据，从满足条件的位置向前倒查试次起始trigger
                # 检索最后一个通道从第一个点到搜索点的所有数据
                search_trigger_data = data_cache[channel_number, :search_point - data_cache_start_point]
                # search_trigger_data = data_cache[6][:search_point - data_cache_start_point]
                # search_trigger_data = search_trigger_data.reshape(1, -1)
                # print(search_trigger_data)
                # print(search_trigger_data.shape)
                trial_start_index_list = np.where(np.isin(search_trigger_data, self.__trial_start_trigger))[0].tolist()
                trial_data_list = list[np.ndarray]()
                for trial_start_index in trial_start_index_list:
                    # 可能有多个trial_start_point在搜索范围内，亦即包含多个试次内容
                    trial_data_list.append(data_cache[:, trial_start_index:trial_start_index + trial_point])

                # 得到截取好的trial数据，进行处理
                for trial_data in trial_data_list:
                    result = self.__calculate(trial_data)
                    print(result)
                    await self._proxy.report(AlgorithmResultObject(result=result))  # 需要注意，必须使用异步报告（添加await）
                # 检索点之前的数据可全部删除,只保留搜索点之后的数据以备继续搜索使用
                search_point_offset = search_point - data_cache_start_point
                data_cache = data_cache[:, search_point_offset:]
                # 修改数据起始点
                data_cache_start_point += search_point_offset
        finally:
            # 退出时记得清理类属性内缓存数据，以备再次启动
            pass

    def __calculate(self, trial_data: np.ndarray) -> str:
        # 数据处理方法，返回需要为报告算法结果
        return str(self.fbcca.fit(trial_data)[0])
