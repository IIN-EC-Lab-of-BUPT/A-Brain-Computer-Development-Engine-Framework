import asyncio
import importlib
import os

import logging
import sys
from collections import namedtuple
from typing import Union

import yaml

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from ApplicationFramework.api.model.MessageBindingModel import MessageBindingModel
from Common.converter.CommonMessageConverter import CommonMessageConverter
from Common.model.CommonMessageModel import EventPackageModel, DataMessageModel, ResultPackageModel, \
    ExceptionPackageModel
from ProcessHub.api.message.MessageKeyEnum import MessageKeyEnum
from ProcessHub.bci_competition_task.interface.BCICompetitionTaskInterface import BCICompetitionTaskInterface
from ProcessHub.challenge.interface.ChallengeInterface import ChallengeInterface
from ProcessHub.orchestrator.model.SourceModel import SourceModel


class TimeoutTrigger:
    def __init__(self, timeout_trigger_name: str, source_label: str, timeout_limit: float,
                 timeout_trigger_event_set: set[float],
                 outer_obj):
        self.__timeout_trigger_name: str = timeout_trigger_name
        self.__source_label: str = source_label
        self.__timeout_limit: float = timeout_limit
        self.__timeout_trigger_event_set: set[float]() = timeout_trigger_event_set
        self.__outer_obj: BCICompetitionTaskFinal = outer_obj
        self.__logger = logging.getLogger("processHubLogger")

    def start_timer(self, algorithm_data_message_model: AlgorithmDataMessageModel) -> None:
        if not isinstance(algorithm_data_message_model.package, EventPackageModel) or \
                algorithm_data_message_model.source_label != self.__source_label:
            return
        event_model = algorithm_data_message_model.package
        # 查找符合要求的事件
        matching_event_tuple_list = [(event_model.event_position[index], event_data)
                                     for index, event_data in enumerate(event_model.event_data)
                                     if float(event_data) in self.__timeout_trigger_event_set]
        if matching_event_tuple_list is None or len(matching_event_tuple_list) == 0:
            return
        event_model = EventPackageModel()
        event_model.event_position, event_model.event_data = zip(*matching_event_tuple_list)
        algorithm_data_message_model_new = AlgorithmDataMessageModel(
            source_label=algorithm_data_message_model.source_label,
            timestamp=algorithm_data_message_model.timestamp,
            package=event_model
        )
        if self.__timeout_limit is not None:
            # 启动异步定时器
            asyncio.create_task(self.__delay_trigger(algorithm_data_message_model_new))
            self.__logger.debug(f"启动超时计时器{algorithm_data_message_model_new}")

    async def __delay_trigger(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        await asyncio.sleep(self.__timeout_limit)
        await self.__outer_obj.trigger_timeout_notification(algorithm_data_message_model)


class BCICompetitionTaskFinal(BCICompetitionTaskInterface):

    def __init__(self):
        super().__init__()
        # 自动注入
        # self._algorithm_connector: AlgorithmConnectorInterface
        # self._component_framework: ComponentFrameworkApplicationInterface
        self.__default_report_topic: str = None
        self.__timeout_trigger_set: set[TimeoutTrigger] = set[TimeoutTrigger]()
        self.__TrialMarkTuple = namedtuple("SendTrialModel", ["trial_id", "block_id", "subject_id"])
        self.__send_trial_mark_tuple_set = set[self.__TrialMarkTuple]()
        self.__timeout_trigger_set: set[TimeoutTrigger] = set[TimeoutTrigger]()
        self.__challenge_class_name: str = None
        self.__challenge_class_file: str = None
        self.__current_challenge: ChallengeInterface = None
        self.__logger = logging.getLogger("processHubLogger")

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        self.__logger.debug(f"{algorithm_data_message_model.source_label}收到消息"
                            f"{type(algorithm_data_message_model.package)}")
        if isinstance(algorithm_data_message_model.package, EventPackageModel):
            for timeout_trigger in self.__timeout_trigger_set:
                timeout_trigger.start_timer(algorithm_data_message_model)
        preprocessed_message_model = await self.__current_challenge.receive_message(algorithm_data_message_model)
        await self._algorithm_connector.send_data(preprocessed_message_model)
        self.__logger.debug(f"{algorithm_data_message_model.source_label}转发消息"
                            f"{type(preprocessed_message_model.package)}")

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        self.__logger.debug(f"收到报告{type(algorithm_report_message_model)}")
        if isinstance(algorithm_report_message_model.package, ResultPackageModel):
            await self.__current_challenge.receive_report(algorithm_report_message_model)
            await self._component_framework.send_message(
                MessageKeyEnum.REPORT.value,
                CommonMessageConverter.model_to_protobuf(
                    DataMessageModel(package=algorithm_report_message_model.package)
                ).SerializeToString()
            )
            score_package_model_list = await self.__current_challenge.get_score()
            for score_package_model in score_package_model_list:
                trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                         block_id=score_package_model.block_id,
                                                         subject_id=score_package_model.subject_id)
                # 如果之前未发送过成绩，则发送成绩，反之不发送
                if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                    await self._component_framework.send_message(
                        MessageKeyEnum.REPORT.value,
                        CommonMessageConverter.model_to_protobuf(
                            DataMessageModel(package=score_package_model)).SerializeToString()
                    )
                    self.__send_trial_mark_tuple_set.add(trial_mark_tuple)
                    self.__logger.info(f"算法报告,发送成绩:\n{score_package_model}")

        elif isinstance(algorithm_report_message_model.package, ExceptionPackageModel):
            await self._component_framework.send_message(
                MessageKeyEnum.REPORT.value,
                CommonMessageConverter.model_to_protobuf(
                    DataMessageModel(package=algorithm_report_message_model.package)).SerializeToString()
            )

    async def trigger_timeout_notification(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        self.__logger.debug(f"事件超时触发{algorithm_data_message_model}")
        await self.__current_challenge.timeout_trigger(algorithm_data_message_model)
        score_package_model_list = await self.__current_challenge.get_score()
        for score_package_model in score_package_model_list:
            trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                     block_id=score_package_model.block_id,
                                                     subject_id=score_package_model.subject_id)
            # 如果之前未发送过成绩，则发送成绩，反之不发送
            if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                await self._component_framework.send_message(
                    MessageKeyEnum.REPORT.value,
                    CommonMessageConverter.model_to_protobuf(
                        DataMessageModel(package=score_package_model)).SerializeToString()
                )
                self.__send_trial_mark_tuple_set.add(trial_mark_tuple)
                self.__logger.info(f"算法超时,发送成绩:\n{score_package_model}")

    async def get_source_list(self) -> list[SourceModel]:
        return await self.__current_challenge.get_source_list()

    async def initial(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'BCICompetitionTaskFinalConfig.yml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict: dict = yaml.safe_load(f)
        challenge_dict = config_dict.get('challenge', dict())
        self.__challenge_class_file = challenge_dict.get('challenge_class_file', "")
        self.__challenge_class_name = challenge_dict.get('challenge_class_name', "")

        message_key_topic_dict = config_dict.get('message_key_topic_dict', dict())
        self.__default_report_topic = message_key_topic_dict.get(MessageKeyEnum.REPORT.value, None)

    async def startup(self):
        # 绑定结果报告message_key,topic
        await self._component_framework.bind_message(
            MessageBindingModel(message_key=MessageKeyEnum.REPORT.value, topic=self.__default_report_topic)
        )

        # 加载赛题
        self.__current_challenge = self.__load_challenge(self.__challenge_class_file, self.__challenge_class_name)
        self.__current_challenge.set_component_framework(self._component_framework)
        await self.__current_challenge.initial()
        await self.__current_challenge.startup()

        # 向算法端发送配置信息
        to_algorithm_config = await self.__current_challenge.get_to_algorithm_config()
        await self._algorithm_connector.push_algorithm_config(to_algorithm_config)

    async def shutdown(self):
        await self.__current_challenge.shutdown()
        self.__current_challenge = None

    def __load_challenge(self, challenge_class_file: str, challenge_class_name: str) -> ChallengeInterface:
        self.__logger.debug('加载赛题: ' + challenge_class_file + ':' + challenge_class_name)
        workspace_path = os.getcwd()
        absolute_challenge_class_file = os.path.join(workspace_path, challenge_class_file)
        module_name = os.path.splitext(os.path.basename(absolute_challenge_class_file))[0]
        # 获取赛题模块所在的目录
        module_dir = os.path.dirname(absolute_challenge_class_file)
        if module_dir not in sys.path:
            sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        challenge_class = getattr(module, challenge_class_name)
        instance = challenge_class()
        return instance

    async def __load_challenge_config(self) -> None:
        # 加载赛题配置信息
        challenge_strategy_config_dict = await self.__current_challenge.get_to_strategy_config()
        # 开始加载定时器配置信息
        timeout_setting_dict = challenge_strategy_config_dict.get(
            'timeout_setting', dict[str, Union[str, dict]]())
        # 创建超时计时器对象
        for timeout_trigger_name in timeout_setting_dict:
            timeout_trigger_parameter: dict = timeout_setting_dict.get(timeout_trigger_name, dict())
            if timeout_trigger_parameter is not None:
                self.__timeout_trigger_set.add(
                    TimeoutTrigger(
                        timeout_trigger_name=timeout_trigger_name,
                        source_label=timeout_trigger_parameter.get('source_label', ""),
                        timeout_limit=timeout_trigger_parameter.get('timeout_limit', 0),
                        timeout_trigger_event_set=set(float(timeout_trigger_event)
                                                      for timeout_trigger_event in
                                                      timeout_trigger_parameter.get('timeout_trigger_events', set())
                                                      ),
                        outer_obj=self
                    )
                )
