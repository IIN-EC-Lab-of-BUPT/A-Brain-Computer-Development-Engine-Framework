import os
import random
from typing import Union
import asyncio
import dataclasses
import logging
import math
import random
from typing import Union

import numpy as np
import yaml
import time
from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from Common.model.CommonMessageModel import ScorePackageModel, ResultPackageModel, DataPackageModel, DevicePackageModel, \
    EventPackageModel, ImpedancePackageModel, InformationPackageModel, ControlPackageModel, ReportSourceInformationModel
from Task.challenge.interface.ChallengeInterface import ChallengeInterface
from Task.common.model.SourceModel import SourceModel


@dataclasses.dataclass
class TrialRecord:
    trigger: int = None
    pos_list: dict[str, int] = None
    subject_id: str = ''
    block_id: str = ''
    trial_id: str = ''
    report_list: list = None
    calculate_flag: bool = False


@dataclasses.dataclass
class EventModel:
    event_position: float = None
    event_data: str = None


@dataclasses.dataclass
class ResultTimeRecord:
    package: Union[ResultPackageModel] = None
    timestamp: float = None


class ChallengeSSVEP(ChallengeInterface):

    def __init__(self):
        super().__init__()
        self.__source_list: list[SourceModel] = list()
        self.__config_dict: dict[str, Union[str, dict]] = None
        self.__current_trial_id = 0
        self.__current_result_model: ResultPackageModel = None

        self.subject_current = None  # 当前被试编号
        self.block_current = None  # 当前block编号

        self.event_record_current = {}  # 缓存当前block收到的事件
        self.trial_record = []  # 顺序存储当前block发生的事件
        self._waiting_idx = 0  # 当前block待分类的事件索引

        self.trial_time = 4  # 一个trial的刺激时长，建议写到配置文件中，需与赛题说明一致
        self._right_count = 0  # 当前block中算法正确汇报个数记录
        self._time_count = 0  # 当前block中算法平均汇报时间记录
        self.sample_rate = {}  # 记录各个数据源数据的采样率

        self.__logger = logging.getLogger("taskLogger")
        # self.initial()

        # 结果记录，非必须
        self.result_record_all = {}  # 所有结果记录；key值是不同被试的编号
        self.result_record_person_current = {}  # 当前被试结果记录；key值是block编号
        self.result_record_current = []  # 当前block结果记录

        self._score_list = []

        self.trial_result_record_list = []

    # def initial(self):
    #     try:
    #         # 假设设置信息已经注入到对象中，直接读取对象属性
    #         sources = self._config['sources'].keys()
    #     except KeyError:
    #         # 否则手动从配置文件中读取
    #         with open('./Task/challenge/SSVEP/ChallengeSSVEP.yml', 'rb') as f:
    #             config = yaml.load(f, Loader=yaml.FullLoader)
    #             sources = config['sources'].keys()
    #     # 初始化私有事件记录字典
    #     for sr in sources:
    #         self.event_record_current[sr] = []

    async def initial(self):
        current_file_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(current_file_path)
        challenge_config_file_name = 'ChallengeSSVEP.yml'
        challenge_config_path = os.path.join(directory_path, challenge_config_file_name)
        with open(challenge_config_path, 'r', encoding='utf-8') as f:
            self.__config_dict = yaml.safe_load(f)
        # # 加载source配置信息
        source_dict = self.__config_dict.get('sources', dict[str, dict[str, str]]())
        for source_label, source_topic in source_dict.items():
            self.__source_list.append(SourceModel(source_label, source_topic))
        # 假设设置信息已经注入到对象中，直接读取对象属性
        sources = self.__config_dict['sources'].keys()
        # 初始化私有事件记录字典
        for sr in sources:
            self.event_record_current[sr] = []

    async def startup(self):
        # 启动时执行的逻辑
        pass

    async def shutdown(self):
        # 关闭时执行的逻辑
        pass

    async def update(self, config_dict: dict[str, Union[str, dict]]):
        pass

    async def get_to_algorithm_config(self) -> dict[str, Union[str, dict]]:
        return self.__config_dict.get('challenge_to_algorithm_config', dict[str, Union[str, dict]]())

    async def get_source_list(self) -> list[SourceModel]:
        return self.__source_list

    async def get_to_strategy_config(self) -> dict[str, Union[str, dict]]:
        return self.__config_dict.get('strategy_config', dict[str, Union[str, dict]]())

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) \
            -> Union[AlgorithmDataMessageModel, None]:
        """
        需要针对algorithm_data_message_model中不同来源，不同类型的数据包(DevicePackageModel,EventPackageModel
        DataPackageModel,ImpedancePackageModel，InformationPackageModel，ControlPackageModel)进行预处理
        :param algorithm_data_message_model:
        :return:
        """
        # await asyncio.sleep(0.001)
        match algorithm_data_message_model.package:
            case DataPackageModel():
                return self._deal_data_msg(algorithm_data_message_model)

            case DevicePackageModel():
                return self._deal_device_msg(algorithm_data_message_model)

            case EventPackageModel():
                self.__logger.info("EventPackageModel{}".format(algorithm_data_message_model.package))
                return self._deal_event_msg(algorithm_data_message_model)

            case ImpedancePackageModel():
                return self._deal_impedance_msg(algorithm_data_message_model)

            case InformationPackageModel():
                self.__logger.info("InformationPackageModel{}".format(algorithm_data_message_model.package))
                return await self._deal_information_msg(algorithm_data_message_model)

            case ControlPackageModel():
                return self._deal_control_msg(algorithm_data_message_model)

    def _deal_data_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        return msg

    def _deal_device_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        data = msg.package
        if self.sample_rate.get(msg.source_label, None) is not None:
            assert self.sample_rate[msg.source_label] == data.sample_rate
        else:
            self.sample_rate[msg.source_label] = data.sample_rate
        return msg

    def _deal_event_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        data = msg.package
        for pos, event in zip(data.event_position, data.event_data):
            if float(event) < 41:
                temp = EventModel()
                temp.event_position = int(pos)
                temp.event_data = event
                self.event_record_current[msg.source_label].append(temp)
                self._update_trial_record()
        return msg

    def _deal_impedance_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        return msg

    async def _deal_information_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        data = msg.package
        if data.subject_id == self.subject_current:
            if data.block_id != self.block_current:
                await self._block_end()
                self.block_current = data.block_id
        else:
            await self._block_end()
            self._person_end()
            self.subject_current = data.subject_id
            self.block_current = data.block_id
        self.__logger.info(f"Challenge got information msg: block_id: {data.block_id}, subject_id: {data.subject_id}")
        return msg

    def _deal_control_msg(self, msg: AlgorithmDataMessageModel) -> AlgorithmDataMessageModel:
        return msg

    async def _block_end(self):
        if self.block_current:
            self.result_record_person_current[self.block_current] = self.result_record_current
            self.result_record_current = []
            #todo

            await self.initial()
            self._waiting_idx = 0
            self._right_count = 0
            self._time_count = 0
            # 规定一个block至少调用get_score方法一次
            self.trial_record = []

    def _person_end(self):
        if self.subject_current:
            # 保存当前被试的结果记录
            self.result_record_all[self.subject_current] = self.result_record_person_current
            self.result_record_person_current = {}

    def _update_trial_record(self):
        # 用于统计不同数据源的event个数是否相等的变量
        count = -1
        _trial_record = TrialRecord()
        _trial_record.pos_list = {}
        for key, value in self.event_record_current.items():
            self.__logger.info(f"self.event_record_current: {self.event_record_current}")
            if count == -1:
                # 以遍历到的第一个数据源做参照
                count = len(value)
                # 初始化私有trial 记录
                _trial_record.trigger = value[-1].event_data
                _trial_record.pos_list[key] = value[-1].event_position
                _trial_record.trial_id = count
                _trial_record.subject_id = self.subject_current
                _trial_record.block_id = self.block_current
                _trial_record.report_list = []
                _trial_record.calculate_flag = False
            elif len(value) != count:
                # 当前数据源与第一个数据源的event数量不一致
                return
            else:
                assert _trial_record.trigger == value[-1].event_data
                # 记录当前数据源对应的数据位置
                _trial_record.pos_list[key] = value[-1].event_position
        self.trial_record.append(_trial_record)

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel) -> None:
        """

        :param algorithm_report_message_model:
        :return:
        """

        self.__logger.debug(f"receive_report{algorithm_report_message_model}")
        match algorithm_report_message_model.package:
            # 只需要处理ResultPackageModel类型数据包即可
            case ResultPackageModel():
                pos = algorithm_report_message_model.package.report_source_information[0].position
                for m in range(len(self.trial_record))[::-1]:
                    trial_pos = self.trial_record[m].pos_list[
                        algorithm_report_message_model.package.report_source_information[0].source_label]
                    if pos > trial_pos:
                        self.__current_result_model = algorithm_report_message_model.package
                        _result_model = ResultTimeRecord()
                        _result_model.package = ResultPackageModel(**vars(algorithm_report_message_model.package))
                        _result_model.timestamp = time.time()
                        self.trial_record[m].report_list.append(_result_model)
                        if not self.trial_record[m].calculate_flag:
                            self._update_score(self.trial_record[m])
                            self.trial_record[m].calculate_flag = True
                        self.result_record_current.append(_result_model)
                        self.__logger.info(f"Challenge reports result: {_result_model}")
                        break
            case ControlPackageModel():
                # 需要处理ControlPackageModel类型数据包
                control_package_model: ControlPackageModel = algorithm_report_message_model.package
                end_flag = control_package_model.end_flag

    def _update_score(self, _trial_model: TrialRecord):
        if _trial_model.report_list:
            #属于正常汇报
            _result_model = _trial_model.report_list[0].package
            _result_model.trial_time = max(
                [(sp.position - _trial_model.pos_list[sp.source_label]) / self.sample_rate[sp.source_label] for sp in
                 _result_model.report_source_information])
            if 0 < _result_model.trial_time <= self.trial_time:
                # 正常汇报
                #TODO
                self._right_count += int(
                    float(_result_model.result) == float(_trial_model.trigger))
                self._time_count += _result_model.trial_time
                self._waiting_idx += 1
                # idx = self._waiting_idx - 1
                self._score_list.append(ScorePackageModel(show_text=f'{_result_model.result}',
                                                          score=self._get_score(),
                                                          trial_time=self._time_count,  #这里是trial的时间，并不是计分的时间
                                                          trial_id=str(_trial_model.trial_id),
                                                          block_id=str(_trial_model.block_id),
                                                          subject_id=str(_trial_model.subject_id)))

            else:
                # 虚警
                pass
        else:
            # 第二种情况，timeout触发超时汇报
            self._waiting_idx += 1
            self._time_count += self.trial_time
            self._score_list.append(ScorePackageModel(show_text='timeout',
                                                      score=self._get_score(),
                                                      trial_time=self._time_count,  #这里是trial的时间，并不是计分的时间
                                                      trial_id=str(_trial_model.trial_id),
                                                      block_id=str(_trial_model.block_id),
                                                      subject_id=str(_trial_model.subject_id)))


    async def timeout_trigger(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        # 超时触发逻辑
        #先找到timeout的归属trial，再判断当前trial是否已经计入score_list，如果没有，说明需要加一个timeout_report，并更新分数，如果有，则不操作
        self.__logger.info("timeout_trigger{}".format(algorithm_data_message_model))
        match algorithm_data_message_model.package:
            # 只需要处理ResultPackageModel类型数据包即可
            case EventPackageModel():
                for pos in algorithm_data_message_model.package.event_position:
                    for m in range(len(self.trial_record))[::-1]:
                        if self.trial_record[m].pos_list[algorithm_data_message_model.source_label] == pos:
                            # 遍历到当前trial
                            # 在timeout时未计算，提交超时结果
                            if not self.trial_record[m].calculate_flag and not self.trial_record[m].report_list:
                                self._update_score(self.trial_record[m])
                                self.trial_record[m].calculate_flag = True
                                _result_model = ResultTimeRecord()
                                _result_model.package = ResultPackageModel()
                                _result_model.package.result = 'timeout'
                                _result_model.package.report_source_information = [ReportSourceInformationModel(source_label=algorithm_data_message_model.source_label)]
                                _result_model.timestamp = algorithm_data_message_model.timestamp
                                self.trial_record[m].report_list.append(_result_model)
                                self.result_record_current.append(_result_model)
                            # trial内有正常汇报，timeout_trigger不会更新score_list
                            break
        pass

    async def get_score(self) -> list[ScorePackageModel]:
        """
        返回当前block成绩
        :return:
        """
        return self._score_list

    def _get_score(self) -> float:
        return self._itr(self._right_count / self._waiting_idx, self._time_count / self._waiting_idx)

    @staticmethod
    def _itr(p, t, n=40):
        t = t + 0.5
        if p < 0 or p > 1:
            return -1
        elif p < 1 / n:
            return 0
        elif p == 1:
            return math.log2(n) * 60 / t
        else:
            return (math.log2(n) + p * math.log2(p) + (1 - p) * math.log2((1 - p) / (n - 1))) * 60 / t
