import asyncio
from collections import namedtuple
from typing import Union

import logging

from Algorithm.api.model.AlgorithmRPCServiceModel import AlgorithmReportMessageModel, AlgorithmDataMessageModel
from Common.model.CommonMessageModel import DataMessageModel, ControlPackageModel, ResultPackageModel, \
    ExceptionPackageModel, EventPackageModel
from Task.challenge.interface.ChallengeInterface import ChallengeInterface
from Task.common.enum.TaskEventEnum import TaskEventEnum
from Task.strategies.interface.StrategyInterface import StrategyInterface


class TimeoutTrigger:
    def __init__(self, timeout_trigger_name: str, source_label: str, timeout_limit: float,
                 timeout_trigger_event_set: set[float],
                 outer_strategy):
        self.__timeout_trigger_name: str = timeout_trigger_name
        self.__source_label: str = source_label
        self.__timeout_limit: float = timeout_limit
        self.__timeout_trigger_event_set: set[float]() = timeout_trigger_event_set
        self.__outer_strategy: FinalModeStrategy = outer_strategy
        self.__logger = logging.getLogger("taskLogger")

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
        await self.__outer_strategy.trigger_timeout_notification(algorithm_data_message_model)


class FinalModeStrategy(StrategyInterface):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger("taskLogger")
        self.__TrialMarkTuple = namedtuple("SendTrialModel", ["trial_id", "block_id", "subject_id"])
        self.__send_trial_mark_tuple_set = set[self.__TrialMarkTuple]()
        self.__challenge_strategy_config_dict = dict[str, Union[str, dict]]()
        self.__timeout_trigger_set: set[TimeoutTrigger] = set[TimeoutTrigger]()

    async def initial(self, config_dict: dict[str, Union[str, dict]]) -> None:
        pass

    async def update(self, config_dict: dict[str, dict[str, Union[str, dict]]]) -> None:
        pass

    async def startup(self) -> None:
        self._event_manager.subscribe(TaskEventEnum.ALGORITHM_DISCONNECT.value, self.on_algorithm_disconnect)
        self._event_manager.subscribe(TaskEventEnum.APPLICATION_EXIT.value, self.on_application_exit)

    async def shutdown(self) -> None:
        self._event_manager.unsubscribe(TaskEventEnum.ALGORITHM_DISCONNECT.value, self.on_algorithm_disconnect)
        self._event_manager.unsubscribe(TaskEventEnum.APPLICATION_EXIT.value, self.on_application_exit)

    async def receive_message(self, algorithm_data_message_model: AlgorithmDataMessageModel) \
            -> Union[AlgorithmDataMessageModel, None]:
        self.__logger.info(f"strategies before:{algorithm_data_message_model.package}")
        if isinstance(algorithm_data_message_model.package, EventPackageModel):
            for timeout_trigger in self.__timeout_trigger_set:
                timeout_trigger.start_timer(algorithm_data_message_model)
        self.__logger.info(f"strategies:{algorithm_data_message_model.package}")
        return await self._challenge.receive_message(algorithm_data_message_model)

    async def receive_report(self, algorithm_report_message_model: AlgorithmReportMessageModel):
        if isinstance(algorithm_report_message_model.package, ResultPackageModel):
            await self._challenge.receive_report(algorithm_report_message_model)
            await self._message_forwarder.send_report(
                DataMessageModel(package=algorithm_report_message_model.package)
            )
            score_package_model_list = await self._challenge.get_score()
            for score_package_model in score_package_model_list:
                trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                         block_id=score_package_model.block_id,
                                                         subject_id=score_package_model.subject_id)
                # 如果之前未发送过成绩，则发送成绩，反之不发送
                if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                    await self._message_forwarder.send_report(
                        DataMessageModel(package=score_package_model)
                    )
                    self.__send_trial_mark_tuple_set.add(trial_mark_tuple)
                    self.__logger.info(f"算法报告,发送成绩:\n{score_package_model}")

        elif isinstance(algorithm_report_message_model.package, ExceptionPackageModel):
            await self._message_forwarder.send_report(
                DataMessageModel(package=algorithm_report_message_model.package)
            )

    async def trigger_timeout_notification(self, algorithm_data_message_model: AlgorithmDataMessageModel):
        self.__logger.debug(f"事件超时触发{algorithm_data_message_model}")
        await self._challenge.timeout_trigger(algorithm_data_message_model)
        score_package_model_list = await self._challenge.get_score()
        for score_package_model in score_package_model_list:
            trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                     block_id=score_package_model.block_id,
                                                     subject_id=score_package_model.subject_id)
            # 如果之前未发送过成绩，则发送成绩，反之不发送
            if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                await self._message_forwarder.send_report(
                    DataMessageModel(package=score_package_model)
                )
                self.__send_trial_mark_tuple_set.add(trial_mark_tuple)
                self.__logger.info(f"算法超时,发送成绩:\n{score_package_model}")

    async def on_algorithm_disconnect(self) -> None:
        self.__logger.info("收到算法断开连接事件")
        # 往赛题中发送一个结束包
        await self._challenge.receive_report(
            AlgorithmReportMessageModel(package=ControlPackageModel(end_flag=True))
        )
        # 从赛题端再获取一个成绩
        score_package_model_list = await self._challenge.get_score()
        for score_package_model in score_package_model_list:
            trial_mark_tuple = self.__TrialMarkTuple(trial_id=score_package_model.trial_id,
                                                     block_id=score_package_model.block_id,
                                                     subject_id=score_package_model.subject_id)
            # 如果之前未发送过成绩，则发送成绩，反之不发送
            if trial_mark_tuple not in self.__send_trial_mark_tuple_set:
                await self._message_forwarder.send_report(
                    DataMessageModel(package=score_package_model)
                )
                self.__send_trial_mark_tuple_set.add(trial_mark_tuple)

        # # 初赛需要关闭算法系统，决赛并不需要
        # await self._core_controller.shutdown_and_close_algorithm_system()
        # await self._core_controller.exit()

    async def on_application_exit(self) -> None:
        # 收到应用退出事件，则关闭算法系统（此状态为手动触发状态）
        await self._core_controller.shutdown_and_close_algorithm_system()

    async def set_challenge(self, challenge: ChallengeInterface) -> None:
        # 设置当前策略所属的赛题
        self._challenge = challenge
        # 加载赛题配置信息
        self.__challenge_strategy_config_dict = await self._challenge.get_to_strategy_config()

        # 开始加载定时器配置信息
        timeout_setting_dict = self.__challenge_strategy_config_dict.get(
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
                        outer_strategy=self
                    )
                )
